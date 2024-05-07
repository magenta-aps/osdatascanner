from io import BytesIO
from typing import Iterator
from urllib.parse import urlsplit, quote
from contextlib import contextmanager
from exchangelib import (
        Folder, OAUTH2, Account, Message, Identity, Credentials, Configuration,
        IMPERSONATION, ExtendedProperty, OAuth2Credentials)
from exchangelib.errors import (
        ErrorServerBusy, ErrorItemNotFound, ErrorNonExistentMailbox)
from exchangelib.protocol import BaseProtocol

from ..utilities.backoff import DefaultRetrier
from .core import Source, Handle, FileResource


BaseProtocol.SESSION_POOLSIZE = 1


# An "entry ID" is the special identifier used to open something in the Outlook
# rich client (after converting it to a hexadecimal string). This property can
# be retrieved over the EWS protocol, but exchangelib doesn't do so by default;
# make sure that it does by explicitly registering the property details

class EntryID(ExtendedProperty):
    property_tag = 4095
    property_type = 'Binary'


Message.register("entry_id", EntryID)


OFFICE_365_ENDPOINT = "https://outlook.office365.com/EWS/Exchange.asmx"
# XXX: actually use Microsoft Graph to do this properly (deeplink URLs are
# available through an email's "webLink" property)
_OFFICE_365_DEEPLINK = (
        "https://outlook.office365.com/owa/?ItemID={0}"
        "&exvsurl=1&viewmodel=ReadMessageItem")


def _make_o365_deeplink(outlook_message_id):
    return _OFFICE_365_DEEPLINK.format(quote(outlook_message_id, safe=''))


def _dictify_headers(headers):
    if headers:
        d = InsensitiveDict()
        for mh in headers:
            n, v = mh.name, mh.value
            if n not in d:
                d[n] = v
            else:
                if isinstance(d[n], list):
                    d[n].append(v)
                else:
                    d[n] = [d[n], v]
        return d
    else:
        return None


class InsensitiveDict(dict):
    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __setitem__(self, key, value):
        return super().__setitem__(key.lower(), value)


class EWSAccountSource(Source):
    type_label = "ews"

    # Ordinarily we would also include _tenant_id and _server in here, but one
    # of them is only used with Microsoft Graph and the other one is only used
    # with basic authentication. If we include neither of them, then we can
    # make EWSMailHandles that are compatible with both! (Anyway, _domain by
    # itself should be enough to uniquely identify the target system...)
    eq_properties = (
            "_domain", "_user",
            "_admin_user", "_admin_password",
            "_client_id", "_client_secret")

    def __init__(
            self, domain, server, admin_user, admin_password, user,
            client_id=None, tenant_id=None, client_secret=None):
        self._domain = domain
        self._server = (
                server if client_secret is None
                # If we have a Microsoft Graph client, then ignore the server
                # field and hard-code the Office 365 endpoint
                else OFFICE_365_ENDPOINT)
        self._user = user

        self._admin_user = admin_user or None
        self._admin_password = admin_password or None

        self._client_id = client_id
        self._tenant_id = tenant_id
        self._client_secret = client_secret

    def _make_credentials(self):
        match (self._admin_password, self._client_secret):
            case (None, None):
                raise ValueError(
                        "no authentification details available (are you"
                        " trying to open a censored EWSAccountSource?)")
            case (str() as s, None) if s:
                return Credentials(
                        username=self._admin_user,
                        password=self._admin_password)
            case (None, str() as s) if s:
                return OAuth2Credentials(
                        client_id=self._client_id,
                        client_secret=self._client_secret,
                        tenant_id=self._tenant_id,
                        identity=Identity(
                                primary_smtp_address=self.address))
            case _:
                raise ValueError(
                        "EWSAccountSource expects either a service account"
                        " or a Microsoft Graph client, but not both")

    @property
    def user(self):
        return self._user

    @property
    def domain(self):
        return self._domain

    @property
    def address(self):
        return "{0}@{1}".format(self.user, self.domain)

    def _generate_state(self, sm):
        match self._make_credentials():
            case Credentials() as c:
                account = Account(
                        primary_smtp_address=self.address,
                        credentials=c,
                        config=Configuration(
                                service_endpoint=self._server,
                                credentials=c if self._server else None),
                        autodiscover=not bool(self._server),
                        access_type=IMPERSONATION)
            case OAuth2Credentials() as c:
                account = Account(
                        primary_smtp_address=self.address,
                        config=Configuration(
                                service_endpoint=self._server,
                                credentials=c,
                                auth_type=OAUTH2))
            case _:
                raise ValueError("Couldn't make an Account object")

        try:
            yield account
        finally:
            # XXX: we should, in principle, close account.protocol here, but
            # exchangelib seems to keep a reference to it internally and so
            # waits forever if we do
            pass

    def censor(self):
        return EWSAccountSource(
                self._domain, self._server, None, None, self._user,
                None, self._tenant_id, None)

    @classmethod
    def _relevant_folders(cls, account: Account) -> Iterator[Folder]:
        for container in account.msg_folder_root.walk():
            if (container.folder_class != "IPF.Note"
                    or container.total_count == 0):
                continue
            yield container

    @classmethod
    def _relevant_mails(cls, folder: Folder, *fields) -> Iterator[Message]:
        queryset = folder.all()
        if fields:
            queryset = queryset.only("entry_id", *fields)
        # A "relevant" mail is anything that we can understand as a Message
        # and that has had an Outlook entry ID assigned
        yield from (
                mail for mail in queryset
                if isinstance(mail, Message) and hasattr(mail, "entry_id"))

    def handles(self, sm) -> Iterator['EWSMailHandle']:
        account = sm.open(self)

        def relevant_mails(relevant_folders):
            for folder in relevant_folders:
                for mail in self._relevant_mails(folder, "id", "subject"):
                    yield EWSMailHandle(
                        self,
                        "{0}.{1}".format(folder.id, mail.id),
                        mail.subject or "(no subject)",
                        folder.name,
                        mail.entry_id.hex())

        yield from relevant_mails(self._relevant_folders(account))

    def to_json_object(self):
        return super().to_json_object() | {
            "domain": self._domain,
            "server": self._server,
            "admin_user": self._admin_user,
            "admin_password": self._admin_password,
            "user": self._user,

            "client_id": self._client_id,
            "tenant_id": self._tenant_id,
            "client_secret": self._client_secret
        }

    @staticmethod
    def from_url(url):
        scheme, netloc, path, _, _ = urlsplit(url)
        auth, domain = netloc.split("@", maxsplit=1)
        au, ap = auth.split(":", maxsplit=1)
        return EWSAccountSource(
                domain=domain,
                server=OFFICE_365_ENDPOINT,
                admin_user="{0}@{1}".format(au, domain),
                admin_password=ap,
                user=path[1:])

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        return EWSAccountSource(
                obj["domain"], obj["server"], obj["admin_user"],
                obj["admin_password"], obj["user"],

                client_id=obj.get("client_id"),
                tenant_id=obj.get("tenant_id"),
                client_secret=obj.get("client_secret"))


class EWSMailResource(FileResource):
    def __init__(self, handle, sm):
        super().__init__(handle, sm)
        self._mr = None
        self._ids = self.handle.relative_path.split(".", maxsplit=1)
        self._message = None

    def _generate_metadata(self):
        yield "email-account", self.handle.source.address
        yield from super()._generate_metadata()

    def check(self) -> bool:
        folder_id, mail_id = self._ids

        try:
            account = self._get_cookie()

            def _retrieve_message():
                # exchangelib>=4.0.0 requires that you pass a Folder object to
                # the function that... returns a Folder object?... okay, fine,
                # let's do that...
                folder_object = Folder(id=folder_id)
                return account.root.get_folder(
                        folder_object).all().only("message_id").get(id=mail_id)

            m = DefaultRetrier(ErrorServerBusy).run(_retrieve_message)
            # exchangelib is slightly inconsistent about whether it *returns*
            # or *raises* exceptions, so we err on the side of caution here
            return not isinstance(
                    m, (ErrorItemNotFound, ErrorNonExistentMailbox,))
        except (ErrorItemNotFound, ErrorNonExistentMailbox,):
            return False

    def get_message_object(self):
        if not self._message:
            folder_id, mail_id = self._ids
            account = self._get_cookie()

            def _retrieve_message():
                folder_object = Folder(id=folder_id)
                return account.root.get_folder(folder_object).get(id=mail_id)
            self._message = DefaultRetrier(
                    ErrorServerBusy, fuzz=0.25).run(_retrieve_message)
        return self._message

    @contextmanager
    def make_stream(self):
        with BytesIO(self.get_message_object().mime_content) as fp:
            yield fp

    # XXX: actually make these values navigable

    def get_size(self):
        return self.get_message_object().size

    def get_last_modified(self):
        o = self.get_message_object()
        oldest_stamp = max(filter(
                lambda ts: ts is not None,
                [o.datetime_created, o.datetime_received, o.datetime_sent]))
        return oldest_stamp

    def compute_type(self):
        return "message/rfc822"


class EWSMailHandle(Handle):
    type_label = "ews"
    resource_type = EWSMailResource

    def __init__(
        self,
        source: EWSAccountSource,
        path: str,
        mail_subject: str,
        folder_name: str,
        entry_id: int,
    ):
        super().__init__(source, path)
        self._mail_subject = mail_subject
        self._folder_name = folder_name
        self._entry_id = entry_id

    @property
    def presentation_name(self):
        return f"\"{self._mail_subject}\""

    @property
    def presentation_place(self):
        return f"folder {self._folder_name} of account {self.source.address}"

    @property
    def presentation_url(self):
        # There appears to be no way to extract a webmail URL from an arbitrary
        # EWS server (and why should there be?), so at present we only support
        # web links to Office 365 mails
        if self.source._server == OFFICE_365_ENDPOINT:
            message_id = self.relative_path.split(".", maxsplit=1)[1]
            return _make_o365_deeplink(message_id)
        elif self._entry_id:
            # ... although, if we have an entry ID, then we can at least try to
            # point Outlook at the relevant mail
            return "outlook:{0}".format(self._entry_id)
        else:
            return None

    @property
    def sort_key(self):
        """ Returns a string to sort by formatted as:
        DOMAIN/ACCOUNT/INBOX/MAIL_SUBJECT"""
        account, domain = self.source.address.split("@", 1)

        return f'{domain}/{account}/' \
               f'{self._folder_name.removeprefix("/") or "(unknown folder)"}/{self._mail_subject}'

    def guess_type(self):
        return "message/rfc822"

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            mail_subject=self._mail_subject,
            folder_name=self._folder_name,
            entry_id=self._entry_id,
        )

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return EWSMailHandle(Source.from_json_object(
            obj["source"]),
            obj["path"], obj["mail_subject"],
            obj.get("folder_name"), obj.get("entry_id"))
