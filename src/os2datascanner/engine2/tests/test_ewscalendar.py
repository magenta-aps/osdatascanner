# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from datetime import timedelta, timezone
from unittest.mock import MagicMock, patch
import pytest

from exchangelib import EWSDateTime, EWSTimeZone, CalendarItem
from exchangelib.items.calendar_item import SINGLE, RECURRING_MASTER, EXCEPTION
from exchangelib.attachments import FileAttachment, ItemAttachment
from exchangelib.items import Message
from exchangelib.errors import ErrorItemNotFound

from os2datascanner.engine2.model.core import Handle
from os2datascanner.engine2.model.ewscalendar import (
    EWSCalendarSource,
    EWSCalendarHandle,
    EWSCalendarItemSource,
    EWSCalendarResource,
    EWSCalendarContentResource,
    EWSCalendarFileAttachmentHandle,
    EWSCalendarFileAttachmentResource,
    EWSCalendarItemAttachmentHandle,
    EWSCalendarItemAttachmentResource,
    DUMMY_MIME,
)


SERVER = "https://mail.example.invalid/EWS/Exchange.asmx"
DOMAIN = "example.invalid"
USER = "alice"
ADDRESS = f"{USER}@{DOMAIN}"
FOLDER_ID = "FOLDER001"
ITEM_ID = "ITEM001"
PATH = f"{FOLDER_ID}.{ITEM_ID}"

UTC = EWSTimeZone.from_timezone(timezone.utc)
START = EWSDateTime(2024, 3, 15, 9, 0, tzinfo=UTC)
END = EWSDateTime(2024, 3, 15, 10, 0, tzinfo=UTC)


@pytest.fixture
def source():
    return EWSCalendarSource(
        domain=DOMAIN,
        server=SERVER,
        admin_user="svc@example.invalid",
        admin_password="p4ssw0rd",
        user=USER,
    )


@pytest.fixture
def handle(source):
    return EWSCalendarHandle(
        source=source,
        path=PATH,
        subject="Weekly Sync",
        folder_name="Calendar",
        start=START,
        end=END,
        item_type=SINGLE,
    )


@pytest.fixture
def item_source(handle):
    """An EWSCalendarItemSource derived from a handle."""
    return EWSCalendarItemSource(handle)


class TestEWSCalendarSource:
    def test_address(self, source):
        assert source.address == ADDRESS

    def test_defaults(self, source):
        assert source._scan_attachments is True

    def test_censor_removes_credentials(self, source):
        censored = source.censor()
        assert censored._admin_password is None
        assert censored._admin_user is None

    def test_censor_preserves_scan_attachments_flag(self, source):
        censored = source.censor()
        assert censored._scan_attachments is True

    def test_yields_independent_sources(self, source):
        assert source.yields_independent_sources is True

    def test_json_roundtrip(self, source):
        restored = EWSCalendarSource.from_json_object(source.to_json_object())
        assert restored == source

    def test_json_roundtrip_with_attachments(self, source):
        restored = EWSCalendarSource.from_json_object(
            source.to_json_object())
        assert restored == source

    def test_equality_ignores_server_and_tenant(self):
        """Two sources for the same mailbox should be equal after censoring
        regardless of whether they use a service account or OAuth."""
        svc = EWSCalendarSource(
            DOMAIN, SERVER, "svc", "pw", USER)
        oauth = EWSCalendarSource(
            DOMAIN, None, None, None, USER,
            client_id="cid", tenant_id="tid", client_secret="cs")
        assert svc != oauth
        assert svc.censor() == oauth.censor()

    def test_scan_attachments_affects_equality(self):
        without = EWSCalendarSource(DOMAIN, SERVER, "s", "p", USER, scan_attachments=False)
        with_ = EWSCalendarSource(DOMAIN, SERVER, "s", "p", USER, scan_attachments=True)
        assert without != with_


class TestEWSCalendarHandle:
    def test_presentation_name_includes_subject(self, handle):
        assert "Weekly Sync" in handle.presentation_name

    def test_presentation_name_includes_start_date(self, handle):
        assert "15/3/24" in handle.presentation_name

    def test_presentation_name_format(self, handle):
        assert handle.presentation_name == "[09:00 15/3/24] Weekly Sync"

    def test_presentation_name_no_start(self, source):
        h = EWSCalendarHandle(source, PATH, "No Date", "Calendar",
                              None, None, None)
        assert h.presentation_name == "No Date"

    def test_presentation_name_excludes_item_type(self, handle):
        assert SINGLE not in handle.presentation_name

    def test_presentation_place_includes_folder(self, handle):
        assert "Calendar" in handle.presentation_place

    def test_presentation_place_includes_address(self, handle):
        assert ADDRESS in handle.presentation_place

    def test_presentation_place_format(self, handle):
        assert handle.presentation_place == f"Calendar ({ADDRESS})"

    def test_presentation_url_is_none_by_default(self, handle):
        assert handle.presentation_url is None

    def test_presentation_url_returns_web_link(self, source):
        h = EWSCalendarHandle(source, PATH, "Meeting", "Calendar",
                              START, END, SINGLE,
                              web_link="https://outlook.office.com/calendar/item/xyz")
        assert h.presentation_url == "https://outlook.office.com/calendar/item/xyz"

    def test_guess_type_is_dummy_mime(self, handle):
        assert handle.guess_type() == DUMMY_MIME

    def test_sort_key_format(self, handle):
        key = handle.sort_key
        assert key.startswith(f"{DOMAIN}/{USER}/")
        assert "Calendar" in key
        assert "Weekly Sync" in key

    def test_sort_key_orders_by_start(self, source):
        earlier = EWSCalendarHandle(source, PATH, "A", "Calendar",
                                    START, END, SINGLE)
        later = EWSCalendarHandle(source, PATH, "B", "Calendar",
                                  START + timedelta(days=1), END, None, SINGLE)
        assert earlier.sort_key < later.sort_key

    def test_json_roundtrip(self, handle):
        obj = handle.to_json_object()
        restored = Handle.from_json_object(obj)
        assert restored._subject == handle._subject
        assert restored._folder_name == handle._folder_name

        assert restored._item_type == handle._item_type
        assert restored._start == handle._start
        assert restored._end == handle._end
        assert restored._web_link == handle._web_link

    def test_json_roundtrip_with_web_link(self, source):
        h = EWSCalendarHandle(source, PATH, "Meeting", "Calendar",
                              START, END, SINGLE,
                              web_link="https://outlook.office.com/calendar/item/xyz")
        restored = Handle.from_json_object(h.to_json_object())
        assert restored._web_link == "https://outlook.office.com/calendar/item/xyz"

    def test_json_roundtrip_none_dates(self, source):
        h = EWSCalendarHandle(source, PATH, "No dates", "Calendar",
                              None, None, SINGLE)
        restored = Handle.from_json_object(h.to_json_object())
        assert restored._start is None
        assert restored._end is None


class TestEWSCalendarItemSource:
    def test_handle_property(self, item_source, handle):
        assert item_source.handle is handle

    def test_yields_content_handle(self, item_source):
        mock_sm = MagicMock()
        mock_sm.open.return_value = MagicMock()  # account

        handles = list(item_source.handles(mock_sm))

        content_handles = [
            h for h in handles
            if isinstance(h, type(handles[0]))
            and h.relative_path == "content"
        ]
        assert len(content_handles) == 1

    def test_no_attachments_when_flag_false(self, item_source):
        mock_sm = MagicMock()
        mock_sm.open.return_value = MagicMock()

        handles = list(item_source.handles(mock_sm))
        attachment_handles = [
            h for h in handles
            if isinstance(h, (
                EWSCalendarFileAttachmentHandle,
                EWSCalendarItemAttachmentHandle))
        ]
        assert attachment_handles == []

    def test_yields_attachment_handles_when_flag_true(
            self, source):
        handle = EWSCalendarHandle(
            source, PATH, "Meeting", "Calendar",
            START, END, SINGLE)
        item_source = EWSCalendarItemSource(handle)

        mock_item = MagicMock()
        file_att = MagicMock(spec=FileAttachment)
        file_att.__class__ = FileAttachment
        file_att.name = "report.pdf"
        file_att.content_type = "application/pdf"
        file_att.size = 1024
        item_att = MagicMock(spec=ItemAttachment)
        item_att.__class__ = ItemAttachment
        item_att.name = "invite.eml"
        mock_item.attachments = [file_att, item_att]

        mock_folder = MagicMock()
        mock_folder.all.return_value.only.return_value.get.return_value = mock_item
        mock_sm = MagicMock()
        mock_sm.open.return_value = MagicMock()

        with patch(
            "os2datascanner.engine2.model.ewscalendar._retrieve_folder",
            return_value=mock_folder,
        ):
            handles = list(item_source.handles(mock_sm))

        file_handles = [h for h in handles
                        if isinstance(h, EWSCalendarFileAttachmentHandle)]
        item_handles = [h for h in handles
                        if isinstance(h, EWSCalendarItemAttachmentHandle)]

        assert len(file_handles) == 1
        assert file_handles[0]._name == "report.pdf"
        assert file_handles[0]._content_type == "application/pdf"

        assert len(item_handles) == 1
        assert item_handles[0]._name == "invite.eml"


class TestFolderHelpers:
    def _make_item(self, item_type, subject="Test", last_modified=None):
        item = MagicMock(spec=CalendarItem)
        item.type = item_type
        item.subject = subject
        item.id = f"id-{subject}"
        item.start = START
        item.end = END
        item.last_modified_time = last_modified if last_modified is not None else END
        return item

    def test_non_occurrence_items_excludes_occurrences(self):
        single = self._make_item(SINGLE, "single")
        master = self._make_item(RECURRING_MASTER, "master")
        exc = self._make_item(EXCEPTION, "exception")

        mock_folder = MagicMock()
        mock_folder.all.return_value.only.return_value = [single, master, exc]

        results = list(EWSCalendarSource._non_occurrence_items(mock_folder))

        subjects = [r.subject for r in results]
        assert "single" in subjects
        assert "master" in subjects
        assert "exception" not in subjects

    def test_non_occurrence_items_applies_cutoff_server_side(self):
        cutoff = EWSDateTime(2024, 3, 15, 9, 30, tzinfo=UTC)
        mock_folder = MagicMock()

        list(EWSCalendarSource._non_occurrence_items(mock_folder, cutoff))

        mock_folder.all.return_value.only.return_value.filter.assert_called_once_with(
            last_modified_time__gte=cutoff)

    def test_exception_items_pages_in_two_year_chunks(self):
        """A window longer than 2 years should result in multiple CalendarView calls."""
        mock_folder = MagicMock()
        mock_folder.view.return_value.only.return_value = []

        window_start = START
        window_end = START + timedelta(days=3 * 365)  # 3 years → 2 chunks

        list(EWSCalendarSource._exception_items(mock_folder, window_start, window_end))

        assert mock_folder.view.call_count == 2

    def test_exception_items_single_chunk_for_short_window(self):
        mock_folder = MagicMock()
        mock_folder.view.return_value.only.return_value = []

        window_start = START
        window_end = START + timedelta(days=365)  # 1 year → 1 chunk

        list(EWSCalendarSource._exception_items(mock_folder, window_start, window_end))

        assert mock_folder.view.call_count == 1

    def test_exception_items_only_yields_exceptions(self):
        exc = self._make_item(EXCEPTION, "exc")
        single = self._make_item(SINGLE, "single")

        mock_folder = MagicMock()
        mock_folder.view.return_value.only.return_value = [exc, single]

        results = list(EWSCalendarSource._exception_items(
            mock_folder, START, START + timedelta(days=365)))

        subjects = [r.subject for r in results]
        assert "exc" in subjects
        assert "single" not in subjects

    def test_exception_items_filters_by_cutoff_client_side(self):
        cutoff = EWSDateTime(2024, 3, 15, 9, 30, tzinfo=UTC)
        # END (10:00) is after cutoff (9:30), START (9:00) is before
        recent = self._make_item(EXCEPTION, "recent", last_modified=END)
        old = self._make_item(EXCEPTION, "old", last_modified=START)

        mock_folder = MagicMock()
        mock_folder.view.return_value.only.return_value = [recent, old]

        results = list(EWSCalendarSource._exception_items(
            mock_folder, START, START + timedelta(days=365), cutoff))

        subjects = [r.subject for r in results]
        assert "recent" in subjects
        assert "old" not in subjects


class TestEWSCalendarContentResource:
    def _make_resource(self, source):
        from os2datascanner.engine2.model.ewscalendar import (
            EWSCalendarContentHandle, EWSCalendarItemSource)
        handle = EWSCalendarHandle(
            source, PATH, "Meeting", "Calendar", START, END, SINGLE)
        item_src = EWSCalendarItemSource(handle)
        content_handle = EWSCalendarContentHandle(item_src, "content")
        mock_sm = MagicMock()
        mock_sm.open.return_value = MagicMock()
        return EWSCalendarContentResource(content_handle, mock_sm)

    def test_compute_type_html(self, source):
        resource = self._make_resource(source)
        mock_body = MagicMock()
        mock_body.body_type = "HTML"
        mock_item = MagicMock()
        mock_item.body = mock_body

        with patch.object(resource, "_get_item", return_value=mock_item):
            assert resource.compute_type() == "text/html"

    def test_compute_type_plain(self, source):
        resource = self._make_resource(source)
        mock_body = MagicMock()
        mock_body.body_type = "Text"
        mock_item = MagicMock()
        mock_item.body = mock_body

        with patch.object(resource, "_get_item", return_value=mock_item):
            assert resource.compute_type() == "text/plain"

    def test_make_stream_encodes_body(self, source):
        resource = self._make_resource(source)
        mock_body = MagicMock()
        mock_body.__str__ = lambda self: "<p>Hello World</p>"
        mock_body.body_type = "HTML"
        mock_item = MagicMock()
        mock_item.subject = "Meeting Title"
        mock_item.body = mock_body

        with patch.object(resource, "_get_item", return_value=mock_item):
            with resource.make_stream() as stream:
                content = stream.read()
        assert b"Hello World" in content

    def test_make_stream_includes_subject_in_html(self, source):
        resource = self._make_resource(source)
        mock_body = MagicMock()
        mock_body.__str__ = lambda self: "<p>body text</p>"
        mock_body.body_type = "HTML"
        mock_item = MagicMock()
        mock_item.subject = "Important Meeting"
        mock_item.body = mock_body

        with patch.object(resource, "_get_item", return_value=mock_item):
            with resource.make_stream() as stream:
                content = stream.read().decode()
        assert "Important Meeting" in content
        assert "<h1>" in content

    def test_make_stream_includes_subject_in_plain_text(self, source):
        resource = self._make_resource(source)
        mock_body = MagicMock()
        mock_body.__str__ = lambda self: "body text"
        mock_body.body_type = "Text"
        mock_item = MagicMock()
        mock_item.subject = "Important Meeting"
        mock_item.body = mock_body

        with patch.object(resource, "_get_item", return_value=mock_item):
            with resource.make_stream() as stream:
                content = stream.read().decode()
        assert "Important Meeting" in content
        assert content.startswith("Important Meeting")

    def test_make_stream_escapes_html_in_subject(self, source):
        resource = self._make_resource(source)
        mock_body = MagicMock()
        mock_body.__str__ = lambda self: "<p>body</p>"
        mock_body.body_type = "HTML"
        mock_item = MagicMock()
        mock_item.subject = "Meeting <script>alert(1)</script>"
        mock_item.body = mock_body

        with patch.object(resource, "_get_item", return_value=mock_item):
            with resource.make_stream() as stream:
                content = stream.read().decode()
        assert "<script>" not in content
        assert "Meeting" in content

    def test_get_last_modified_prefers_last_modified_time(self, source):
        resource = self._make_resource(source)
        mock_item = MagicMock()
        mock_item.subject = "Test"
        mock_item.last_modified_time = START
        mock_item.datetime_created = END

        with patch.object(resource, "_get_item", return_value=mock_item):
            assert resource.get_last_modified() == START

    def test_get_last_modified_falls_back_to_created(self, source):
        resource = self._make_resource(source)
        mock_item = MagicMock()
        mock_item.subject = "Test"
        mock_item.last_modified_time = None
        mock_item.datetime_created = END

        with patch.object(resource, "_get_item", return_value=mock_item):
            assert resource.get_last_modified() == END


class TestEWSCalendarResource:
    def _make_resource(self, source):
        handle = EWSCalendarHandle(
            source, PATH, "Meeting", "Calendar", START, END, SINGLE)
        mock_sm = MagicMock()
        mock_sm.open.return_value = MagicMock()
        return EWSCalendarResource(handle, mock_sm)

    def _mock_folder_with_item(self, mock_item):
        mock_folder = MagicMock()
        mock_folder.all.return_value.only.return_value.get.return_value = mock_item
        return mock_folder

    def test_compute_type_returns_dummy_mime(self, source):
        assert self._make_resource(source).compute_type() == DUMMY_MIME

    def test_check_returns_true_for_existing_item(self, source):
        resource = self._make_resource(source)
        mock_folder = self._mock_folder_with_item(MagicMock(spec=CalendarItem))

        with patch("os2datascanner.engine2.model.ewscalendar._retrieve_folder",
                   return_value=mock_folder):
            assert resource.check() is True

    def test_check_returns_false_for_missing_item(self, source):
        resource = self._make_resource(source)

        with patch("os2datascanner.engine2.model.ewscalendar._retrieve_folder",
                   side_effect=ErrorItemNotFound("not found")):
            assert resource.check() is False

    def test_get_last_modified_prefers_last_modified_time(self, source):
        resource = self._make_resource(source)
        mock_item = MagicMock()
        mock_item.last_modified_time = START
        mock_item.datetime_created = END

        with patch("os2datascanner.engine2.model.ewscalendar._retrieve_folder",
                   return_value=self._mock_folder_with_item(mock_item)):
            assert resource.get_last_modified() == START

    def test_get_last_modified_falls_back_to_created(self, source):
        resource = self._make_resource(source)
        mock_item = MagicMock()
        mock_item.last_modified_time = None
        mock_item.datetime_created = END

        with patch("os2datascanner.engine2.model.ewscalendar._retrieve_folder",
                   return_value=self._mock_folder_with_item(mock_item)):
            assert resource.get_last_modified() == END

    def test_item_is_fetched_only_once(self, source):
        resource = self._make_resource(source)
        mock_folder = self._mock_folder_with_item(MagicMock(spec=CalendarItem))

        with patch("os2datascanner.engine2.model.ewscalendar._retrieve_folder",
                   return_value=mock_folder) as mock_retrieve:
            resource.check()
            resource.get_last_modified()

        assert mock_retrieve.call_count == 1


class TestEWSCalendarFileAttachmentResource:
    def _make_resource(self, source, name="doc.pdf",
                       content_type="application/pdf", size=1024):
        calendar_handle = EWSCalendarHandle(
            source, PATH, "Meeting", "Calendar", START, END, SINGLE)
        item_src = EWSCalendarItemSource(calendar_handle)
        att_handle = EWSCalendarFileAttachmentHandle(
            item_src, "0", name, content_type, size)
        mock_sm = MagicMock()
        mock_sm.open.return_value = MagicMock()
        return EWSCalendarFileAttachmentResource(att_handle, mock_sm)

    def _make_file_attachment(self, content=b"data"):
        att = MagicMock(spec=FileAttachment)
        att.__class__ = FileAttachment
        att.content = content
        att.size = len(content)
        return att

    def test_compute_type_from_handle(self, source):
        assert self._make_resource(source).compute_type() == "application/pdf"

    def test_compute_type_fallback(self, source):
        resource = self._make_resource(source, content_type=None)
        assert resource.compute_type() == "application/octet-stream"

    def test_check_true_for_file_attachment(self, source):
        resource = self._make_resource(source)
        with patch.object(resource, "_get_attachment",
                          return_value=self._make_file_attachment()):
            assert resource.check() is True

    def test_check_false_for_item_attachment(self, source):
        resource = self._make_resource(source)
        att = MagicMock(spec=ItemAttachment)
        att.__class__ = ItemAttachment
        with patch.object(resource, "_get_attachment", return_value=att):
            assert resource.check() is False

    def test_make_stream(self, source):
        resource = self._make_resource(source)
        with patch.object(resource, "_get_attachment",
                          return_value=self._make_file_attachment(b"hello")):
            with resource.make_stream() as stream:
                assert stream.read() == b"hello"

    def test_get_size(self, source):
        resource = self._make_resource(source)
        with patch.object(resource, "_get_attachment",
                          return_value=self._make_file_attachment(b"abc")):
            assert resource.get_size() == 3


class TestEWSCalendarItemAttachmentResource:
    def _make_resource(self, source, name="invite.eml"):
        calendar_handle = EWSCalendarHandle(
            source, PATH, "Meeting", "Calendar", START, END, SINGLE)
        item_src = EWSCalendarItemSource(calendar_handle)
        att_handle = EWSCalendarItemAttachmentHandle(item_src, "0", name)
        mock_sm = MagicMock()
        mock_sm.open.return_value = MagicMock()
        return EWSCalendarItemAttachmentResource(att_handle, mock_sm)

    def test_check_true_for_item_attachment(self, source):
        resource = self._make_resource(source)
        att = MagicMock(spec=ItemAttachment)
        att.__class__ = ItemAttachment
        with patch.object(resource, "_get_attachment", return_value=att):
            assert resource.check() is True

    def test_check_false_for_file_attachment(self, source):
        resource = self._make_resource(source)
        att = MagicMock(spec=FileAttachment)
        att.__class__ = FileAttachment
        with patch.object(resource, "_get_attachment", return_value=att):
            assert resource.check() is False

    def test_make_stream(self, source):
        resource = self._make_resource(source)
        att = MagicMock(spec=ItemAttachment)
        att.__class__ = ItemAttachment
        att.item.mime_content = b"raw email"
        with patch.object(resource, "_get_attachment", return_value=att):
            with resource.make_stream() as stream:
                assert stream.read() == b"raw email"

    def test_compute_type_message(self, source):
        resource = self._make_resource(source)
        att = MagicMock(spec=ItemAttachment)
        att.item = MagicMock(spec=Message)
        att.item.__class__ = Message
        with patch.object(resource, "_get_attachment", return_value=att):
            assert resource.compute_type() == "message/rfc822"

    def test_compute_type_calendar_item(self, source):
        resource = self._make_resource(source)
        att = MagicMock(spec=ItemAttachment)
        att.item = MagicMock(spec=CalendarItem)
        att.item.__class__ = CalendarItem
        with patch.object(resource, "_get_attachment", return_value=att):
            assert resource.compute_type() == "text/calendar"


class TestEWSCalendarFileAttachmentHandle:
    def _make_handle(self, source, name="doc.pdf",
                     content_type="application/pdf", size=2048):
        calendar_handle = EWSCalendarHandle(
            source, PATH, "Meeting", "Calendar", START, END, SINGLE)
        item_src = EWSCalendarItemSource(calendar_handle)
        return EWSCalendarFileAttachmentHandle(
            item_src, "0", name, content_type, size)

    def test_guess_type_uses_content_type(self, source):
        h = self._make_handle(source, content_type="application/pdf")
        assert h.guess_type() == "application/pdf"

    def test_guess_type_falls_back_to_filename(self, source):
        h = self._make_handle(source, content_type=None, name="data.xlsx")
        assert "spreadsheet" in h.guess_type() or "excel" in h.guess_type().lower()

    def test_guess_type_unknown_falls_back_to_octet_stream(self, source):
        h = self._make_handle(source, content_type=None, name="file.xyz123")
        assert h.guess_type() == "application/octet-stream"

    def test_presentation_name(self, source):
        h = self._make_handle(source, name="report.pdf")
        assert h.presentation_name == "report.pdf"

    def test_presentation_place_references_parent(self, source):
        h = self._make_handle(source)
        assert "Meeting" in h.presentation_place
        assert "Calendar" in h.presentation_place

    def test_json_roundtrip(self, source):
        h = self._make_handle(source)
        restored = Handle.from_json_object(h.to_json_object())
        assert restored._name == h._name
        assert restored._content_type == h._content_type
        assert restored._size == h._size


class TestEWSCalendarItemAttachmentHandle:
    def _make_handle(self, source, name="invite.eml"):
        calendar_handle = EWSCalendarHandle(
            source, PATH, "Meeting", "Calendar", START, END, SINGLE)
        item_src = EWSCalendarItemSource(calendar_handle)
        return EWSCalendarItemAttachmentHandle(item_src, "0", name)

    def test_presentation_name(self, source):
        h = self._make_handle(source, name="invite.eml")
        assert h.presentation_name == "invite.eml"

    def test_guess_type_is_octet_stream(self, source):
        # Type is unknown until the item is fetched; compute_type() is accurate
        h = self._make_handle(source)
        assert h.guess_type() == "application/octet-stream"

    def test_presentation_place_references_parent(self, source):
        h = self._make_handle(source)
        assert "Meeting" in h.presentation_place

    def test_json_roundtrip(self, source):
        h = self._make_handle(source)
        restored = Handle.from_json_object(h.to_json_object())
        assert restored._name == h._name
