# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from io import BytesIO
from typing import Iterator, Optional
from urllib.parse import urlsplit, quote
from contextlib import contextmanager
from datetime import timedelta, timezone
import mimetypes
from exchangelib import (
        Folder, OAUTH2, Account, Message, Identity, Credentials, Configuration,
        IMPERSONATION, ExtendedProperty, OAuth2Credentials, CalendarItem,
        EWSDateTime, EWSTimeZone)
from exchangelib.errors import (
        ErrorServerBusy, ErrorItemNotFound, ErrorNonExistentMailbox)
from exchangelib.protocol import BaseProtocol
from exchangelib.attachments import FileAttachment, ItemAttachment
from exchangelib.items import MeetingRequest, Message
from exchangelib.items.calendar_item import RECURRING_MASTER

from ..utilities.backoff import DefaultRetrier
from .core import Source, Handle, FileResource, Resource
from .derived import DerivedSource


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

    def handles(self, sm, **kwargs) -> Iterator['EWSMailHandle']:
        account = sm.open(self)

        def relevant_mails(relevant_folders):
            for folder in relevant_folders:
                for mail in self._relevant_mails(
                        folder, "id", "subject", "web_client_read_form_query_string"):
                    wcs = mail.web_client_read_form_query_string
                    yield EWSMailHandle(
                        self,
                        "{0}.{1}".format(folder.id, mail.id),
                        mail.subject or "(no subject)",
                        folder.name,
                        mail.entry_id.hex(),
                        wcs if wcs.startswith(("http://", "https://",)) else None,
                    )

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

    @staticmethod
    def _retrieve_folder(account, folder_id):
        # exchangelib>=4.0.0 requires that you pass a Folder object to
        # the function that... returns a Folder object?... okay, fine,
        # let's do that...
        folder_object = Folder(id=folder_id)
        folder = account.root.get_folder(folder_object)
        if folder:
            return folder
        else:
            raise ErrorItemNotFound("Folder not found")

    def check(self) -> bool:
        folder_id, mail_id = self._ids

        try:
            account = self._get_cookie()

            def _retrieve_message():
                folder = self._retrieve_folder(account, folder_id)
                return folder.all().only("message_id").get(id=mail_id)

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
                folder = self._retrieve_folder(account, folder_id)
                return folder.get(id=mail_id)
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

    def compute_content_identifier(self):
        return self.get_message_object().message_id.strip("<>")


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
        web_link: Optional[str],
    ):
        super().__init__(source, path)
        self._mail_subject = mail_subject
        self._folder_name = folder_name
        self._entry_id = entry_id
        self._web_link = web_link

    @property
    def presentation_name(self):
        return f"\"{self._mail_subject}\""

    @property
    def presentation_place(self):
        return f"folder {self._folder_name} of account {self.source.address}"

    @property
    def presentation_url(self):
        if self._web_link:
            return self._web_link
        elif self.source._server == OFFICE_365_ENDPOINT:
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
            web_link=self._web_link,
        )

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return EWSMailHandle(
            Source.from_json_object(obj["source"]),
            obj["path"],
            obj["mail_subject"],
            obj.get("folder_name"),
            obj.get("entry_id"),
            obj.get("web_link"),
        )


# Max range is 2 years so default to ± 1 year
_DEFAULT_DAYS_BACK = 365
_DEFAULT_DAYS_FUTURE = 365

DUMMY_MIME = "application/vnd.os2.datascanner.ewscalendaritem"


class EWSCalendarSource(EWSAccountSource):
    """A Source representing the calendar folders of a single Exchange mailbox.

    Reuses all authentication and account-creation logic from EWSAccountSource,
    but targets IPF.Appointment folders and yields EWSCalendarHandles.

    Recurring series are expanded via a CalendarView so that individual
    occurrences (and exceptions with modified content) are each scanned
    separately. The recurring master is also yielded as an additional handle.

    The date window used to expand recurring series is configurable via
    `days_back` and `days_forward` constructor arguments.

    When `scan_attachments` is True, the EWSCalendarItemSource derived from
    each handle will also yield handles for any FileAttachments and
    ItemAttachments found on the item.
    """

    type_label = "ews_calendar"
    yields_independent_sources = True

    eq_properties = EWSAccountSource.eq_properties + (
            "_days_back", "_days_forward", "_scan_attachments")

    def __init__(
            self, domain, server, admin_user, admin_password, user,
            client_id=None, tenant_id=None, client_secret=None,
            days_back: int = _DEFAULT_DAYS_BACK,
            days_forward: int = _DEFAULT_DAYS_FUTURE,
            scan_attachments: bool = False):
        super().__init__(
                domain, server, admin_user, admin_password, user,
                client_id=client_id, tenant_id=tenant_id,
                client_secret=client_secret)
        self._days_back = days_back
        self._days_forward = days_forward
        self._scan_attachments = scan_attachments

    @classmethod
    def _relevant_folders(cls, account: Account) -> Iterator[Folder]:
        for container in account.msg_folder_root.walk():
            if (container.folder_class != "IPF.Appointment"
                    or container.total_count == 0):
                continue
            yield container

    @classmethod
    def _calendar_view_items(
            cls, folder: Folder, start, end, *fields) -> Iterator[CalendarItem]:
        """Yield individual occurrences and exceptions via a CalendarView.

        A CalendarView expands recurring series so each occurrence within
        [start, end] is returned as a discrete item. Modified occurrences
        (exceptions) carry their own subject, body, location, etc., which
        may differ from the master — important for GDPR scanning.

        Single (non-recurring) items that fall within the window are also
        included here.
        """
        view = folder.view(start=start, end=end)
        if fields:
            view = view.only("id", *fields)
        yield from (item for item in view if isinstance(item, CalendarItem))

    @classmethod
    def _recurring_masters(
            cls, folder: Folder, *fields) -> Iterator[CalendarItem]:
        """Yield only recurring masters from a folder.

        Masters are not returned by a CalendarView, but their template
        content (default subject, body, location) should still be scanned
        because an occurrence may inherit it without overriding it.
        """
        queryset = folder.all().filter(type=RECURRING_MASTER)
        if fields:
            queryset = queryset.only("id", *fields)
        yield from (item for item in queryset if isinstance(item, CalendarItem))

    def handles(self, sm, **kwargs) -> Iterator['EWSCalendarHandle']:
        from exchangelib import EWSDateTime, EWSTimeZone

        account = sm.open(self)
        utc = EWSTimeZone.from_timezone(timezone.utc)
        now = EWSDateTime.now(tz=utc)
        window_start = now - timedelta(days=self._days_back)
        window_end = now + timedelta(days=self._days_forward)

        _fields = ("subject", "start", "end", "location", "type")

        import logging
        logger = logging.getLogger(__name__)

        for folder in self._relevant_folders(account):
            # Pass 1 — individual occurrences and single items via CalendarView
            try:
                for item in self._calendar_view_items(
                        folder, window_start, window_end, *_fields):
                    try:
                        yield EWSCalendarHandle(
                            self,
                            "{0}.{1}".format(folder.id, item.id),
                            item.subject or "(no subject)",
                            folder.name,
                            item.start,
                            item.end,
                            item.location,
                            item.type,
                        )
                    except Exception:
                        logger.exception(
                            "Failed to construct EWSCalendarHandle for item"
                            " %s in folder %s", getattr(item, "id", "?"), folder.name)
            except Exception:
                logger.exception(
                    "Failed during CalendarView iteration for folder %s", folder.name)

            # Pass 2 — recurring masters (template content)
            try:
                for item in self._recurring_masters(folder, *_fields):
                    try:
                        yield EWSCalendarHandle(
                            self,
                            "{0}.{1}".format(folder.id, item.id),
                            item.subject or "(no subject)",
                            folder.name,
                            item.start,
                            item.end,
                            item.location,
                            item.type,
                        )
                    except Exception:
                        logger.exception(
                            "Failed to construct EWSCalendarHandle for master"
                            " %s in folder %s", getattr(item, "id", "?"), folder.name)
            except Exception:
                logger.exception(
                    "Failed during recurring master iteration for folder %s", folder.name)

    def censor(self):
        return EWSCalendarSource(
                self._domain, self._server, None, None, self._user,
                None, self._tenant_id, None,
                self._days_back, self._days_forward,
                self._scan_attachments)

    def to_json_object(self):
        return super().to_json_object() | {
            "days_back": self._days_back,
            "days_forward": self._days_forward,
            "scan_attachments": self._scan_attachments,
        }

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        return EWSCalendarSource(
                obj["domain"], obj["server"], obj["admin_user"],
                obj["admin_password"], obj["user"],
                client_id=obj.get("client_id"),
                tenant_id=obj.get("tenant_id"),
                client_secret=obj.get("client_secret"),
                days_back=obj.get("days_back", _DEFAULT_DAYS_BACK),
                days_forward=obj.get("days_forward", _DEFAULT_DAYS_FUTURE),
                scan_attachments=obj.get("scan_attachments", False))


class EWSCalendarResource(Resource):
    """Lightweight resource for the calendar item container handle.

    Returns DUMMY_MIME so the pipeline knows to expand this handle via
    EWSCalendarItemSource rather than attempting a direct conversion.
    """

    def check(self) -> bool:
        folder_id, item_id = self.handle.relative_path.split(".", maxsplit=1)
        try:
            account = self._get_cookie()

            def _retrieve_item():
                folder = EWSMailResource._retrieve_folder(account, folder_id)
                return folder.all().only("id").get(id=item_id)

            item = DefaultRetrier(ErrorServerBusy).run(_retrieve_item)
            return not isinstance(
                    item, (ErrorItemNotFound, ErrorNonExistentMailbox))
        except (ErrorItemNotFound, ErrorNonExistentMailbox):
            return False

    def compute_type(self):
        return DUMMY_MIME


class EWSCalendarHandle(Handle):
    """A Handle identifying a single calendar item within an Exchange mailbox.
    """
    type_label = "ews_calendar"
    resource_type = EWSCalendarResource

    def __init__(
        self,
        source: EWSCalendarSource,
        path: str,
        subject: str,
        folder_name: str,
        start,
        end,
        location: Optional[str],
        item_type: Optional[str],
    ):
        super().__init__(source, path)
        self._subject = subject
        self._folder_name = folder_name
        self._start = start
        self._end = end
        self._location = location
        self._item_type = item_type

    @property
    def presentation_name(self):
        label = f" ({self._item_type})" if self._item_type else ""
        return f"\"{self._subject}\"{label}"

    @property
    def presentation_place(self):
        parts = [
            f"calendar folder {self._folder_name}",
            f"of account {self.source.address}",
        ]
        if self._location:
            parts.insert(1, f"(location: {self._location})")
        return " ".join(parts)

    @property
    def presentation_url(self):
        return None

    @property
    def sort_key(self):
        """Returns a string formatted as:
        DOMAIN/ACCOUNT/FOLDER/START_DATETIME/SUBJECT"""
        account, domain = self.source.address.split("@", 1)
        start_str = self._start.isoformat() if self._start else ""
        return (
            f"{domain}/{account}/"
            f"{self._folder_name.removeprefix('/') or '(unknown folder)'}/"
            f"{start_str}/{self._subject}"
        )

    def guess_type(self):
        return DUMMY_MIME

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            subject=self._subject,
            folder_name=self._folder_name,
            start=self._start.isoformat() if self._start else None,
            end=self._end.isoformat() if self._end else None,
            location=self._location,
            item_type=self._item_type,
        )

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        def _parse_dt(value):
            return EWSDateTime.from_string(value) if value else None

        return EWSCalendarHandle(
            Source.from_json_object(obj["source"]),
            obj["path"],
            obj["subject"],
            obj.get("folder_name"),
            _parse_dt(obj.get("start")),
            _parse_dt(obj.get("end")),
            obj.get("location"),
            obj.get("item_type"),
        )

@Source.mime_handler(DUMMY_MIME)
class EWSCalendarItemSource(DerivedSource):
    """A DerivedSource that expands an EWSCalendarHandle into scannable handles.

    Always yields an EWSCalendarContentHandle for the item's iCalendar content.
    When the parent EWSCalendarSource has scan_attachments=True, also yields
    EWSCalendarFileAttachmentHandle and EWSCalendarItemAttachmentHandle for any
    attachments on the item.
    """
    type_label = "ews_calendar_item"

    def _generate_state(self, sm):
        yield sm.open(self.handle.source)

    def handles(self, sm, **kwargs):
        # Always yield the iCalendar content handle
        yield EWSCalendarContentHandle(self, "content")

        if not self.handle.source._scan_attachments:
            return

        account = sm.open(self)
        folder_id, item_id = self.handle.relative_path.split(".", maxsplit=1)

        def _fetch_attachments():
            folder = EWSMailResource._retrieve_folder(account, folder_id)
            return folder.all().only("id", "attachments").get(id=item_id)

        item = DefaultRetrier(ErrorServerBusy, fuzz=0.25).run(_fetch_attachments)

        for idx, attachment in enumerate(item.attachments or []):
            if isinstance(attachment, FileAttachment):
                yield EWSCalendarFileAttachmentHandle(
                    self,
                    str(idx),
                    attachment.name or f"attachment_{idx}",
                    attachment.content_type,
                    attachment.size,
                )
            elif isinstance(attachment, ItemAttachment):
                yield EWSCalendarItemAttachmentHandle(
                    self,
                    str(idx),
                    attachment.name or f"item_attachment_{idx}",
                )


class EWSCalendarContentResource(FileResource):
    """Fetches and streams the iCalendar (text/calendar) content of a calendar
    item via its EWS mime_content field."""

    def __init__(self, handle, sm):
        super().__init__(handle, sm)
        self._item = None

    def _generate_metadata(self):
        yield "email-account", self.handle.source.handle.source.address
        yield from super()._generate_metadata()

    # We fetch the body field (HTML or plain text) rather than mime_content,
    # so the existing text/html and text/plain converters can handle the output
    # without any special iCalendar parsing. size is omitted because it reflects
    # the full EWS item size, not the body length; we return a best-effort value
    # from the encoded body instead.
    _FETCH_FIELDS = ("id", "body", "last_modified_time", "datetime_created")

    def _get_item(self) -> CalendarItem:
        if not self._item:
            account = self._get_cookie()
            folder_id, item_id = (
                    self.handle.source.handle.relative_path.split(".", maxsplit=1))

            def _fetch():
                folder = EWSMailResource._retrieve_folder(account, folder_id)
                return folder.all().only(*self._FETCH_FIELDS).get(id=item_id)

            self._item = DefaultRetrier(
                    ErrorServerBusy, fuzz=0.25).run(_fetch)
        return self._item

    def check(self) -> bool:
        # Delegate to the parent container handle's resource
        return self.handle.source.handle.follow(
                self._sm).check()

    @contextmanager
    def make_stream(self):
        encoded = str(self._get_item().body).encode()
        with BytesIO(encoded) as fp:
            yield fp

    def get_size(self):
        # body length is a reasonable proxy; the full EWS item size is not
        # available without fetching additional fields
        return len(str(self._get_item().body).encode())

    def get_last_modified(self):
        o = self._get_item()
        return o.last_modified_time or o.datetime_created

    def compute_type(self):
        body = self._get_item().body
        return (
            "text/html"
            if getattr(body, "body_type", None) == "HTML"
            else "text/plain"
        )


@Handle.stock_json_handler("ews_calendar_content")
class EWSCalendarContentHandle(Handle):
    """A Handle for the iCalendar content of a calendar item.

    Always has the fixed relative path "content" since there is exactly one
    content stream per calendar item. The source is the EWSCalendarItemSource
    that produced it.
    """
    type_label = "ews_calendar_content"
    resource_type = EWSCalendarContentResource

    @property
    def presentation_name(self):
        return self.source.handle.presentation_name

    @property
    def presentation_place(self):
        return self.source.handle.presentation_place

    @property
    def presentation_url(self):
        return None

    @property
    def sort_key(self):
        return self.source.handle.sort_key

    def guess_type(self):
        return "text/calendar"


class EWSCalendarFileAttachmentResource(FileResource):
    """Fetches and streams the raw bytes of a FileAttachment on a calendar item."""

    def __init__(self, handle, sm):
        super().__init__(handle, sm)
        self._attachment = None

    def _generate_metadata(self):
        yield "email-account", self.handle.source.handle.source.address
        yield from super()._generate_metadata()

    def _get_attachment(self) -> FileAttachment:
        if not self._attachment:
            account = self._get_cookie()
            folder_id, item_id = (
                    self.handle.source.handle.relative_path.split(".", maxsplit=1))
            idx = int(self.handle.relative_path)

            def _fetch():
                folder = EWSMailResource._retrieve_folder(account, folder_id)
                item = folder.all().only("id", "attachments").get(id=item_id)
                return item.attachments[idx]

            self._attachment = DefaultRetrier(
                    ErrorServerBusy, fuzz=0.25).run(_fetch)
        return self._attachment

    def check(self) -> bool:
        try:
            att = self._get_attachment()
            return isinstance(att, FileAttachment)
        except (ErrorItemNotFound, ErrorNonExistentMailbox, IndexError):
            return False

    @contextmanager
    def make_stream(self):
        with BytesIO(self._get_attachment().content) as fp:
            yield fp

    def get_size(self):
        return self._get_attachment().size

    def get_last_modified(self):
        return self.handle.source.handle.follow(
                self._sm).get_last_modified()

    def compute_type(self):
        return self.handle._content_type or "application/octet-stream"


class EWSCalendarFileAttachmentHandle(Handle):
    """A Handle identifying a file attachment on a calendar item.
    """
    type_label = "ews_calendar_file_attachment"
    resource_type = EWSCalendarFileAttachmentResource

    def __init__(
        self,
        source: EWSCalendarItemSource,
        path: str,
        name: str,
        content_type: Optional[str],
        size: Optional[int],
    ):
        super().__init__(source, path)
        self._name = name
        self._content_type = content_type
        self._size = size

    @property
    def presentation_name(self):
        return self._name

    @property
    def presentation_place(self):
        parent = self.source.handle
        return f"attachment of {parent.presentation_name} in {parent.presentation_place}"

    @property
    def presentation_url(self):
        return None

    @property
    def sort_key(self):
        return f"{self.source.handle.sort_key}/attachments/{self._name}"

    def guess_type(self):
        if self._content_type:
            return self._content_type
        guessed, _ = mimetypes.guess_type(self._name)
        return guessed or "application/octet-stream"

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            name=self._name,
            content_type=self._content_type,
            size=self._size,
        )

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return EWSCalendarFileAttachmentHandle(
            Source.from_json_object(obj["source"]),
            obj["path"],
            obj["name"],
            obj.get("content_type"),
            obj.get("size"),
        )


class EWSCalendarItemAttachmentResource(FileResource):
    def __init__(self, handle, sm):
        super().__init__(handle, sm)
        self._attachment = None

    def _generate_metadata(self):
        yield "email-account", self.handle.source.handle.source.address
        yield from super()._generate_metadata()

    def _get_attachment(self) -> ItemAttachment:
        if not self._attachment:
            account = self._get_cookie()
            folder_id, item_id = (
                    self.handle.source.handle.relative_path.split(".", maxsplit=1))
            idx = int(self.handle.relative_path)

            def _fetch():
                folder = EWSMailResource._retrieve_folder(account, folder_id)
                item = folder.all().only("id", "attachments").get(id=item_id)
                return item.attachments[idx]

            self._attachment = DefaultRetrier(
                    ErrorServerBusy, fuzz=0.25).run(_fetch)
        return self._attachment

    def check(self) -> bool:
        try:
            att = self._get_attachment()
            return isinstance(att, ItemAttachment)
        except (ErrorItemNotFound, ErrorNonExistentMailbox, IndexError):
            return False

    @contextmanager
    def make_stream(self):
        with BytesIO(self._get_attachment().item.mime_content) as fp:
            yield fp

    def get_size(self):
        return self._get_attachment().item.size

    def get_last_modified(self):
        return self.handle.source.handle.follow(
                self._sm).get_last_modified()

    def compute_type(self):
        embedded = self._get_attachment().item
        if isinstance(embedded, (Message, MeetingRequest)):
            return "message/rfc822"
        elif isinstance(embedded, CalendarItem):
            return "text/calendar"
        return "application/octet-stream"


class EWSCalendarItemAttachmentHandle(Handle):
    """A Handle identifying an ItemAttachment (embedded Exchange item) on a
    calendar item.
    """
    type_label = "ews_calendar_item_attachment"
    resource_type = EWSCalendarItemAttachmentResource

    def __init__(
        self,
        source: EWSCalendarItemSource,
        path: str,
        name: str,
    ):
        super().__init__(source, path)
        self._name = name

    @property
    def presentation_name(self):
        return self._name

    @property
    def presentation_place(self):
        parent = self.source.handle
        return f"embedded item of {parent.presentation_name} in {parent.presentation_place}"

    @property
    def presentation_url(self):
        return None

    @property
    def sort_key(self):
        return f"{self.source.handle.sort_key}/attachments/{self._name}"

    def guess_type(self):
        return "application/octet-stream"

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            name=self._name,
        )

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return EWSCalendarItemAttachmentHandle(
            Source.from_json_object(obj["source"]),
            obj["path"],
            obj["name"],
        )