import structlog

from io import BytesIO
from urllib.parse import urlsplit
from contextlib import contextmanager
from datetime import datetime, timezone
from dateutil.parser import isoparse
from requests import HTTPError

from ... import settings as engine2_settings
from ...rules.rule import Rule
from ..core import Handle, Source, Resource, FileResource, SourceManager
from ..derived.derived import DerivedSource
from .utilities import MSGraphSource, warn_on_httperror, MailFSBuilder

from os2datascanner.engine2.rules.utilities.analysis import compute_mss

logger = structlog.get_logger("engine2")


# TODO: This probably shouldn't be a thing, but has complicated consequences to remove?
class MSGraphMailSource(MSGraphSource):
    type_label = "msgraph-mail"

    eq_properties = MSGraphSource.eq_properties + ("_userlist",)

    def __init__(
            self,
            client_id,
            tenant_id,
            client_secret,
            scan_deleted_items_folder=True,
            scan_syncissues_folder=True,
            scan_attachments=True,
            userlist=None):
        super().__init__(client_id, tenant_id, client_secret)
        self._userlist = userlist
        self._scan_deleted_items_folder = scan_deleted_items_folder
        self._scan_syncissues_folder = scan_syncissues_folder
        self._scan_attachments = scan_attachments

    def handles(self, sm):  # noqa
        if self._userlist is None:
            for user in self._list_users(sm):
                pn = user["userPrincipalName"]  # e.g. dan@contoso.onmicrosoft.com
                # Getting a HTTP 404 response from the /messages endpoint means
                # that this user doesn't have a mail account at all
                with warn_on_httperror(f"mail check for {pn}"):
                    any_mails = sm.open(self).get(
                        "users/{0}/messages?$select=id&$top=1".format(pn)).json()
                    if not any_mails["value"]:
                        # This user has a mail account that contains no mails
                        continue
                    else:
                        yield MSGraphMailAccountHandle(self, pn)

        else:
            for pn in self._userlist:
                with warn_on_httperror(f"mail check for {pn}"):
                    any_mails = sm.open(self).get(
                        "users/{0}/messages?$select=id&$top=1".format(pn)).json()
                    if any_mails["value"]:
                        yield MSGraphMailAccountHandle(self, pn)

    def to_json_object(self):
        return dict(
                **super().to_json_object(),
                userlist=list(self._userlist) if self._userlist is not None else None,
                scan_deleted_items_folder=self.scan_deleted_items_folder,
                scan_syncissues_folder=self.scan_syncissues_folder,
                scan_attachments=self.scan_attachments)

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        userlist = obj.get("userlist")
        return MSGraphMailSource(
                client_id=obj["client_id"],
                tenant_id=obj["tenant_id"],
                client_secret=obj["client_secret"],
                userlist=frozenset(userlist) if userlist is not None else None,
                scan_deleted_items_folder=obj.get("scan_deleted_items_folder", True),
                scan_syncissues_folder=obj.get("scan_syncissues_folder", True),
                scan_attachments=obj.get("scan_attachments", True))

    def censor(self):
        return type(self)(None, self._tenant_id, None,
                          scan_deleted_items_folder=self.scan_deleted_items_folder,
                          scan_syncissues_folder=self.scan_syncissues_folder,
                          scan_attachments=self.scan_attachments)

    @property
    def scan_deleted_items_folder(self):
        return self._scan_deleted_items_folder

    @property
    def scan_syncissues_folder(self):
        return self._scan_syncissues_folder

    @property
    def scan_attachments(self):
        return self._scan_attachments


DUMMY_MIME = "application/vnd.os2.datascanner.graphmailaccount"


class MSGraphMailAccountResource(Resource):
    def check(self) -> bool:
        try:
            self._get_cookie().get(
                "users/{0}/messages?$select=id&$top=1".format(
                        self.handle.relative_path))
            return True
        except HTTPError as ex:
            if ex.response.status_code in (404, 410,):
                return False
            raise

    def compute_type(self):
        return DUMMY_MIME


@Handle.stock_json_handler("msgraph-mail-account")
class MSGraphMailAccountHandle(Handle):
    type_label = "msgraph-mail-account"
    resource_type = MSGraphMailAccountResource

    @property
    def presentation_name(self):
        return self.relative_path

    @property
    def presentation_place(self):
        return "Office 365"

    @property
    def sort_key(self):
        """ Returns a string to sort by formatted as:
            DOMAIN/ACCOUNT/MAIL_SUBJECT"""
        # We should probably look towards EWS implementation and see if you get/can get folder
        # the mail resides in and add this.
        account, domain = self.relative_path.split("@", 1)
        return f'{domain}/{account}/'

    def guess_type(self):
        return DUMMY_MIME


@Source.mime_handler(DUMMY_MIME)
class MSGraphMailAccountSource(DerivedSource):
    type_label = "msgraph-mail-account"
    derived_from = MSGraphMailAccountHandle

    def _generate_state(self, sm):
        yield sm.open(self.handle.source)

    def _append_msgraph_filters(
            self,
            pn: str,  # user principal name
            query: str,  # base query string
            sm: SourceManager,
            scan_deleted_items: bool,
            scan_sync_issues: bool,
            cutoff: datetime | None = None):
        filters = []
        # The base query gets everything, including the deleted and syncissues folders,
        # but we don't always want this.
        # That's why we filter them away from the base query,
        # meaning we check whether to filter away a folder,
        # not whether to include a folder.
        # The following logic is therefore reversed, and skips the steps if they are set to
        # true in the user-frontend

        if not scan_deleted_items:
            # Find folder id of deleted post for given mail account

            del_post_folder_id = sm.open(self).get(
                f"users/{pn}/mailFolders/deleteditems?$select=id").json().get("id")

            # Exclude deleted post by issuing a 'not equal to' (ne) filter query
            filters.append(f"parentFolderId ne '{del_post_folder_id}'")
        if not scan_sync_issues:
            # Find folder id of syncissues for given mail account
            # The syncissues folder is not guaranteed to be present, and requires a check
            try:
                sync_issue_folder_id = sm.open(self).get(
                    f"users/{pn}/mailFolders/syncissues?$select=id").json().get("id")

                filters.append(f"parentFolderId ne '{sync_issue_folder_id}'")
            except Exception:
                logger.warning("Syncissues folder does not exist", exc_info=True)

            # We've seen examples of conflicts being SyncIssues/Conflicts, but don't actually
            # know if one can exist without the other, so side with caution here.
            try:
                conflicts_folder_id = sm.open(self).get(
                    f"users/{pn}/mailFolders/conflicts?$select=id").json().get("id")

                filters.append(f"parentFolderId ne '{conflicts_folder_id}'")
            except Exception:
                logger.warning("Conflicts folder does not exist", exc_info=True)

        if cutoff:
            # Microsoft Graph requires all timestamps to be in UTC and doesn't
            # support any way of saying that other than "Z". ... groan...
            ts = cutoff.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            fs = f"(sentDateTime gt {ts} or lastModifiedDateTime gt {ts})"
            filters.append(fs)

        if filters:
            query += f"&$filter={' and '.join(filters)}"
        return query

    def handles(self, sm, *, rule: Rule | None = None):
        pn = self.handle.relative_path
        ps = engine2_settings.model["msgraph"]["page_size"]
        builder = MailFSBuilder(self, sm, pn)
        query = f"users/{pn}/messages?$select=id,subject,webLink,parentFolderId&$top={ps}"
        scan_deleted_items = self.handle.source.scan_deleted_items_folder
        scan_sync_issues = self.handle.source.scan_syncissues_folder

        cutoff = None
        for essential_rule in compute_mss(rule):
            # (we can't do isinstance() here without making a circular
            # dependency)
            if essential_rule.type_label == "last-modified":
                after = essential_rule.after
                cutoff = (after if not cutoff else max(cutoff, after))

        # Sort out filters for our query string.
        query = self._append_msgraph_filters(
                pn, query, sm, scan_deleted_items, scan_sync_issues, cutoff)

        result = sm.open(self).get(query).json()
        yield from (self._wrap(msg, builder) for msg in result["value"])
        # We want to get all emails for given account
        # This key takes us to the next page and is only present
        # as long as there is one.
        while '@odata.nextLink' in result:
            result = sm.open(self).follow_next_link(result["@odata.nextLink"]).json()
            yield from (self._wrap(msg, builder) for msg in result["value"])

    def _wrap(self, message, builder: MailFSBuilder):
        fid = message["parentFolderId"]
        folder = builder.build_path(fid)
        return MSGraphMailMessageHandle(
            self, message["id"], mail_subject=message["subject"],
            weblink=message["webLink"], folder=folder)

    @staticmethod
    def from_url(url):  # TODO: Question, is this method even used? I see no good way of getting
        # scan_deleted_items here.
        scheme, netloc, path, _, _ = urlsplit(url)
        auth, tenant_id = netloc.split("@", maxsplit=1)
        client_id, client_secret = auth.split(":", maxsplit=1)
        user = path[1:]
        return MSGraphMailAccountSource(
                MSGraphMailAccountHandle(
                        MSGraphMailSource(client_id, tenant_id, client_secret),
                        user))


class MSGraphMailMessageResource(FileResource):
    def __init__(self, handle, sm):
        super().__init__(handle, sm)
        self._message = None

    def _generate_metadata(self):
        yield "email-account", self.handle.source.handle.relative_path
        yield "outlook-categories", self.get_message_metadata().get("categories", None)
        yield from super()._generate_metadata()

    def check(self) -> bool:
        try:
            self._get_cookie().get(
                    self.make_object_path() + "?$select=id")
            return True
        except HTTPError as ex:
            if ex.response.status_code in (404, 410,):
                return False
            raise

    def make_object_path(self):
        return "users/{0}/messages/{1}".format(
                self.handle.source.handle.relative_path,
                self.handle.relative_path)

    def get_message_metadata(self):
        if not self._message:
            self._message = self._get_cookie().get(
                    self.make_object_path() + "?$select=lastModifiedDateTime,"
                                              "sentDateTime,isDraft,categories").json()
        return self._message

    @contextmanager
    def make_stream(self):
        response = self._get_cookie().get(
                self.make_object_path() + "/$value")
        with BytesIO(response.content) as fp:
            yield fp

    def get_size(self):
        # XXX: there's no obvious way to implement this, but is this a problem?
        # Do we really need it for anything?
        return 1024

    def get_last_modified(self):
        metadata = self.get_message_metadata()
        # Many outlook events (such as flagging or moving) will change lastModifiedDateTime, but
        # these operations aren't relevant for us, as we're only concerned with content, which
        # won't change
        # Hence, unless the email is a Draft, it makes the most sense to look at its sentDateTime.
        if metadata.get("isDraft"):
            timestamp = metadata.get("lastModifiedDateTime")
        else:
            timestamp = metadata.get("sentDateTime")

        return isoparse(timestamp) if timestamp else None

    def compute_type(self):
        return "message/rfc822"


class MSGraphMailMessageHandle(Handle):
    type_label = "msgraph-mail-message"
    resource_type = MSGraphMailMessageResource

    def __init__(self, source, path,  # noqa: R0913
                 mail_subject, weblink,
                 folder=None):
        super().__init__(source, path)
        self._mail_subject = mail_subject
        self._weblink = weblink
        self._folder = folder

    @property
    def presentation_name(self):
        return f"\"{self._mail_subject}\""

    @property
    def presentation_place(self):
        return f"\"{self._folder}\" of {str(self.source.handle)}" \
            if self._folder else f"{str(self.source.handle)}"

    @property
    def presentation_url(self):
        return self._weblink

    @property
    def sort_key(self):
        return self.source.handle.sort_key + (f"{self._folder or ''}/{self._mail_subject}")

    def guess_type(self):
        return "message/rfc822"

    @property
    def scan_attachments(self):
        return (self.source  # MSGraphMailAccountSource
                .handle  # MSGraphMailAccountHandle
                .source  # MSGraphMailSource
                .scan_attachments)

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            mail_subject=self._mail_subject,
            weblink=self._weblink,
            folder=self._folder
        )

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return MSGraphMailMessageHandle(
                Source.from_json_object(obj["source"]),
                obj["path"], obj["mail_subject"], obj["weblink"],
                obj.get("folder", None))
