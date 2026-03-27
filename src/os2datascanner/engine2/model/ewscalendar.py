# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import html
import structlog
from io import BytesIO
from typing import Iterator, Optional
from contextlib import contextmanager
from datetime import timedelta, timezone
import mimetypes
from exchangelib import Folder, Account, CalendarItem, EWSDateTime, EWSTimeZone  # noqa: E402
from exchangelib.attachments import FileAttachment, ItemAttachment, Attachment
from exchangelib.items.calendar_item import OCCURRENCE, EXCEPTION
from exchangelib.items import MeetingRequest, Message
from exchangelib.errors import (
        ErrorServerBusy, ErrorItemNotFound, ErrorNonExistentMailbox)

from ..utilities.backoff import DefaultRetrier
from .core import Source, Handle, FileResource, Resource
from .derived.derived import DerivedSource
from .ews import EWSAccountSource, _retrieve_folder
from ..rules.rule import Rule
from ..rules.utilities.analysis import compute_mss

DUMMY_MIME = "application/vnd.os2.datascanner.ewscalendaritem"

logger = structlog.get_logger("engine2")


def _web_link(item) -> Optional[str]:
    """Return the OWA URL for an EWS item, or None if unavailable."""
    wcs = getattr(item, "web_client_read_form_query_string", None)
    if wcs and wcs.startswith(("http://", "https://")):
        return wcs
    return None


class EWSCalendarSource(EWSAccountSource):
    """A Source representing the calendar folders of a single Exchange mailbox.

    Reuses all authentication and account-creation logic from EWSAccountSource,
    but targets IPF.Appointment folders and yields EWSCalendarHandles.

    All single items and recurring masters are yielded via a regular queryset
    with no date limit. Modified occurrences (exceptions) are discovered via
    CalendarView, paged in 2-year chunks from the Unix epoch to 2 years ahead.

    When `scan_attachments` is True, the EWSCalendarItemSource derived from
    each handle will also yield handles for any FileAttachments and
    ItemAttachments found on the item.
    """

    type_label = "ews-calendar"
    yields_independent_sources = True

    eq_properties = EWSAccountSource.eq_properties + ("_scan_attachments",)

    def __init__(
            self, domain, server, admin_user, admin_password, user,
            client_id=None, tenant_id=None, client_secret=None,
            scan_attachments: bool = True):
        super().__init__(
                domain, server, admin_user, admin_password, user,
                client_id=client_id, tenant_id=tenant_id,
                client_secret=client_secret)
        self._scan_attachments = scan_attachments

    @staticmethod
    def _relevant_folders(account: Account) -> Iterator[Folder]:
        for container in account.msg_folder_root.walk():
            if (container.folder_class != "IPF.Appointment"
                    or container.total_count == 0):
                continue
            yield container

    # web_client_read_form_query_string what a field name.
    _ITEM_FIELDS = (
        "subject", "start", "end", "type",
        "last_modified_time", "web_client_read_form_query_string",
    )

    @staticmethod
    def _non_occurrence_items(
            folder: Folder, cutoff=None) -> Iterator[CalendarItem]:
        """Yield all single items and recurring masters from a folder.

        A regular queryset returns both of these types without a date range
        limit, covering the full history of the folder in a single pass.
        Occurrences and exceptions are excluded here. Exceptions are handled
        separately via CalendarView since they are not returned by folder.all().
        """
        queryset = folder.all().only("id", *EWSCalendarSource._ITEM_FIELDS)
        if cutoff:
            queryset = queryset.filter(last_modified_time__gte=cutoff)
        yield from (
            item for item in queryset
            if isinstance(item, CalendarItem)
            and item.type not in (OCCURRENCE, EXCEPTION)
        )

    @staticmethod
    def _exception_items(
            folder: Folder, start, end, cutoff=None) -> Iterator[CalendarItem]:
        """Yield only exceptions (modified occurrences) via a CalendarView.

        Exceptions are the only item type not reachable via folder.all().
        They exist as modifications to a master and are only surfaced by
        a CalendarView expansion. Regular unmodified occurrences are
        intentionally excluded since their content is identical to the
        recurring master, which is already scanned by _non_occurrence_items.

        EWS limits a CalendarView to a 2-year span, so we page through chunks.
        """
        _TWO_YEARS = timedelta(days=2 * 365)
        chunk_start = start
        while chunk_start < end:
            chunk_end = min(chunk_start + _TWO_YEARS, end)
            view = (folder.view(start=chunk_start, end=chunk_end)
                    .only("id", *EWSCalendarSource._ITEM_FIELDS))
            yield from (
                item for item in view
                if isinstance(item, CalendarItem)
                and item.type == EXCEPTION
                and (not cutoff or item.last_modified_time >= cutoff)
            )
            chunk_start = chunk_end

    def handles(self, sm, *, rule: Rule | None = None, **kwargs) -> Iterator['EWSCalendarHandle']:  # noqa CCR001 Cognitive complexity
        account = sm.open(self)
        utc = EWSTimeZone.from_timezone(timezone.utc)
        now = EWSDateTime.now(tz=utc)
        # Exceptions (modified occurrences) require a CalendarView with an explicit
        # date range. Scan from the Unix epoch to 2 years forward to cover the full
        # calendar history. The 2-year forward horizon may need to become configurable.
        window_start = EWSDateTime(1970, 1, 1, 0, 0, tzinfo=utc)
        window_end = now + timedelta(days=2 * 365)

        cutoff = None
        for essential_rule in compute_mss(rule):
            if essential_rule.type_label == "last-modified":
                after = EWSDateTime.from_datetime(
                    essential_rule.after.astimezone(timezone.utc))
                cutoff = after if not cutoff else max(cutoff, after)

        for folder in self._relevant_folders(account):
            # Single items and recurring masters.
            # Catch broadly: exchangelib can raise many different error types
            # mid-iteration (throttling, transient server errors, malformed
            # responses). We log and move on so the remaining folders are
            # still scanned.
            try:
                for item in self._non_occurrence_items(folder, cutoff):
                    yield EWSCalendarHandle(
                        self,
                        "{0}.{1}".format(folder.id, item.id),
                        item.subject or "(no subject)",
                        folder.name,
                        item.start,
                        item.end,
                        item.type,
                        _web_link(item),
                    )
            except Exception:
                logger.exception(
                    "Failed during non-occurrence iteration for folder",
                    folder=folder.name)

            # Exceptions (modified occurrences) are invisible to folder.all()
            # and require a CalendarView, paged in 2-year chunks.
            try:
                for item in self._exception_items(
                        folder, window_start, window_end, cutoff):
                    yield EWSCalendarHandle(
                        self,
                        "{0}.{1}".format(folder.id, item.id),
                        item.subject or "(no subject)",
                        folder.name,
                        item.start,
                        item.end,
                        item.type,
                        _web_link(item),
                    )
            except Exception:
                logger.exception(
                    "Failed during exception iteration for folder",
                    folder=folder.name)

    def censor(self):
        return EWSCalendarSource(
                self._domain, self._server, None, None, self._user,
                None, self._tenant_id, None,
                self._scan_attachments)

    def to_json_object(self):
        return super().to_json_object() | {
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
                scan_attachments=obj.get("scan_attachments", True))


class EWSCalendarResource(Resource):
    """Lightweight resource for the calendar item container handle.

    Returns DUMMY_MIME so the pipeline knows to expand this handle via
    EWSCalendarItemSource rather than attempting a direct conversion.
    """

    _FETCH_FIELDS = ("last_modified_time", "datetime_created")

    def __init__(self, handle, sm):
        super().__init__(handle, sm)
        self._item = None

    def _get_item(self):
        if self._item is None:
            folder_id, item_id = self.handle.relative_path.split(".", maxsplit=1)
            account = self._get_cookie()

            def _retrieve_item():
                folder = _retrieve_folder(account, folder_id)
                return folder.all().only("id", *self._FETCH_FIELDS).get(id=item_id)

            self._item = DefaultRetrier(ErrorServerBusy).run(_retrieve_item)
        return self._item

    def check(self) -> bool:
        try:
            item = self._get_item()
            return not isinstance(
                    item, (ErrorItemNotFound, ErrorNonExistentMailbox))
        except (ErrorItemNotFound, ErrorNonExistentMailbox):
            return False

    def get_last_modified(self):
        item = self._get_item()
        return item.last_modified_time or item.datetime_created

    def compute_type(self):
        return DUMMY_MIME


class EWSCalendarHandle(Handle):
    """A Handle identifying a single calendar item within an Exchange mailbox.
    """
    type_label = "ews-calendar"
    resource_type = EWSCalendarResource

    def __init__(
        self,
        source: EWSCalendarSource,
        path: str,
        subject: str,
        folder_name: str,
        start,
        end,
        item_type: Optional[str],
        web_link: Optional[str] = None,
    ):
        super().__init__(source, path)
        self._subject = subject
        self._folder_name = folder_name
        self._start = start
        # end and item_type are not shown in the presentation but are kept so
        # they round-trip cleanly through JSON and remain available for
        # filtering or future display.
        self._end = end
        self._item_type = item_type
        self._web_link = web_link

    @property
    def presentation_name(self):
        start_str = self._start.strftime("%H:%M %-d/%-m/%y") if self._start else ""
        return f"[{start_str}] {self._subject}" if start_str else self._subject

    @property
    def presentation_place(self):
        return f"{self._folder_name} ({self.source.address})"

    @property
    def presentation_url(self):
        return self._web_link

    @property
    def sort_key(self):
        """Returns a string to sort by formatted as:
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
            item_type=self._item_type,
            web_link=self._web_link,
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
            obj.get("item_type"),
            web_link=obj.get("web_link"),
        )


@Source.mime_handler(DUMMY_MIME)
class EWSCalendarItemSource(DerivedSource):
    """A DerivedSource that expands an EWSCalendarHandle into scannable handles.

    Always yields an EWSCalendarContentHandle for the item's body content
    (HTML or plain text). When the parent EWSCalendarSource has
    scan_attachments=True, also yields EWSCalendarFileAttachmentHandle and
    EWSCalendarItemAttachmentHandle for any attachments on the item.
    """
    type_label = "ews-calendar-item"

    def _generate_state(self, sm):
        yield sm.open(self.handle.source)

    def handles(self, sm, **kwargs):
        # Always yield the content handle
        yield EWSCalendarContentHandle(self, "content")

        if not self.handle.source._scan_attachments:
            return

        account = sm.open(self)
        folder_id, item_id = self.handle.relative_path.split(".", maxsplit=1)

        def _fetch_attachments():
            folder = _retrieve_folder(account, folder_id)
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
    """Fetches and streams the body of a calendar item as HTML or plain text."""

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
    _FETCH_FIELDS = ("id", "subject", "body", "last_modified_time", "datetime_created")

    def _get_item(self) -> CalendarItem:
        if self._item is None:
            account = self._get_cookie()
            folder_id, item_id = (
                    self.handle.source.handle.relative_path.split(".", maxsplit=1))

            def _fetch():
                folder = _retrieve_folder(account, folder_id)
                return folder.all().only(*self._FETCH_FIELDS).get(id=item_id)

            self._item = DefaultRetrier(
                    ErrorServerBusy, fuzz=0.25).run(_fetch)
        return self._item

    def check(self) -> bool:
        # Delegate to the parent container handle's resource
        return self.handle.source.handle.follow(
                self._sm).check()

    def _build_content(self) -> bytes:
        item = self._get_item()
        subject = item.subject or ""
        body = str(item.body)
        if getattr(item.body, "body_type", None) == "HTML":
            prefix = f"<h1>{html.escape(subject)}</h1>" if subject else ""
        else:
            prefix = f"{subject}\n\n" if subject else ""
        return (prefix + body).encode()

    @contextmanager
    def make_stream(self):
        with BytesIO(self._build_content()) as fp:
            yield fp

    def get_size(self):
        return len(self._build_content())

    def get_last_modified(self):
        item = self._get_item()
        return item.last_modified_time or item.datetime_created

    def compute_type(self):
        body = self._get_item().body
        return (
            "text/html"
            if getattr(body, "body_type", None) == "HTML"
            else "text/plain"
        )


@Handle.stock_json_handler("ews-calendar-content")
class EWSCalendarContentHandle(Handle):
    """A Handle for the body content (HTML or plain text) of a calendar item.

    Always has the fixed relative path "content" since there is exactly one
    content stream per calendar item. The source is the EWSCalendarItemSource
    that produced it.
    """
    type_label = "ews-calendar-content"
    resource_type = EWSCalendarContentResource

    @property
    def presentation_name(self):
        return self.source.handle.presentation_name

    @property
    def presentation_place(self):
        return self.source.handle.presentation_place

    @property
    def presentation_url(self):
        return self.source.handle.presentation_url

    @property
    def sort_key(self):
        return self.source.handle.sort_key

    def guess_type(self):
        return "text/plain"


class _EWSCalendarAttachmentResource:
    """Mixin with common attachment-handling logic."""
    _attachment: Optional[Attachment] = None

    def _get_attachment(self) -> Attachment:
        if self._attachment is None:
            account = self._get_cookie()
            folder_id, item_id = (
                self.handle.source.handle.relative_path.split(".", maxsplit=1))
            idx = int(self.handle.relative_path)

            def _fetch():
                folder = _retrieve_folder(account, folder_id)
                item = folder.all().only("id", "attachments").get(id=item_id)
                return item.attachments[idx]

            self._attachment = DefaultRetrier(
                ErrorServerBusy, fuzz=0.25).run(_fetch)
        return self._attachment


class EWSCalendarFileAttachmentResource(_EWSCalendarAttachmentResource, FileResource):
    """Fetches and streams the raw bytes of a FileAttachment on a calendar item."""

    def _generate_metadata(self):
        yield "email-account", self.handle.source.handle.source.address
        yield from super()._generate_metadata()

    def _get_attachment(self) -> FileAttachment:
        return super()._get_attachment()

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
    type_label = "ews-calendar-file-attachment"
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


class EWSCalendarItemAttachmentResource(_EWSCalendarAttachmentResource, FileResource):
    def _generate_metadata(self):
        yield "email-account", self.handle.source.handle.source.address
        yield from super()._generate_metadata()

    def _get_attachment(self) -> ItemAttachment:
        return super()._get_attachment()

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
    type_label = "ews-calendar-item-attachment"
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
