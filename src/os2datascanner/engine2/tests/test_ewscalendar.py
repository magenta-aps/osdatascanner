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

from os2datascanner.engine2.model.core import Handle
from os2datascanner.engine2.model.ewscalendar import (
    EWSCalendarSource,
    EWSCalendarHandle,
    EWSCalendarItemSource,
    EWSCalendarContentResource,
    EWSCalendarFileAttachmentHandle,
    EWSCalendarItemAttachmentHandle,
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
def source_with_attachments():
    return EWSCalendarSource(
        domain=DOMAIN,
        server=SERVER,
        admin_user="svc@example.invalid",
        admin_password="p4ssw0rd",
        user=USER,
        scan_attachments=True,
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
        location="Room 42",
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

    def test_censor_preserves_scan_attachments_flag(self, source_with_attachments):
        censored = source_with_attachments.censor()
        assert censored._scan_attachments is True

    def test_yields_independent_sources(self, source):
        assert source.yields_independent_sources is True

    def test_json_roundtrip(self, source):
        restored = EWSCalendarSource.from_json_object(source.to_json_object())
        assert restored == source

    def test_json_roundtrip_with_attachments(self, source_with_attachments):
        restored = EWSCalendarSource.from_json_object(
            source_with_attachments.to_json_object())
        assert restored == source_with_attachments

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

    def test_presentation_name_includes_item_type(self, handle):
        assert SINGLE in handle.presentation_name

    def test_presentation_name_no_item_type(self, source):
        h = EWSCalendarHandle(source, PATH, "No Type", "Calendar",
                              START, END, None, None)
        assert h.presentation_name == '"No Type"'

    def test_presentation_place_includes_folder(self, handle):
        assert "Calendar" in handle.presentation_place

    def test_presentation_place_includes_address(self, handle):
        assert ADDRESS in handle.presentation_place

    def test_presentation_place_includes_location(self, handle):
        assert "Room 42" in handle.presentation_place

    def test_presentation_place_no_location(self, source):
        h = EWSCalendarHandle(source, PATH, "No Loc", "Calendar",
                              START, END, None, SINGLE)
        assert "location" not in h.presentation_place.lower()

    def test_presentation_url_is_none(self, handle):
        assert handle.presentation_url is None

    def test_guess_type_is_dummy_mime(self, handle):
        assert handle.guess_type() == DUMMY_MIME

    def test_sort_key_format(self, handle):
        key = handle.sort_key
        assert key.startswith(f"{DOMAIN}/{USER}/")
        assert "Calendar" in key
        assert "Weekly Sync" in key

    def test_sort_key_orders_by_start(self, source):
        earlier = EWSCalendarHandle(source, PATH, "A", "Calendar",
                                    START, END, None, SINGLE)
        later = EWSCalendarHandle(source, PATH, "B", "Calendar",
                                  START + timedelta(days=1), END, None, SINGLE)
        assert earlier.sort_key < later.sort_key

    def test_json_roundtrip(self, handle):
        obj = handle.to_json_object()
        restored = Handle.from_json_object(obj)
        assert restored._subject == handle._subject
        assert restored._folder_name == handle._folder_name
        assert restored._location == handle._location
        assert restored._item_type == handle._item_type
        assert restored._start == handle._start
        assert restored._end == handle._end

    def test_json_roundtrip_none_dates(self, source):
        h = EWSCalendarHandle(source, PATH, "No dates", "Calendar",
                              None, None, None, SINGLE)
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
            self, source_with_attachments):
        handle = EWSCalendarHandle(
            source_with_attachments, PATH, "Meeting", "Calendar",
            START, END, None, SINGLE)
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
    def _make_item(self, item_type, subject="Test"):
        item = MagicMock(spec=CalendarItem)
        item.type = item_type
        item.subject = subject
        item.id = f"id-{subject}"
        item.start = START
        item.end = END
        item.location = None
        return item

    def test_non_occurrence_items_excludes_occurrences(self, source):
        single = self._make_item(SINGLE, "single")
        master = self._make_item(RECURRING_MASTER, "master")
        exc = self._make_item(EXCEPTION, "exception")

        mock_folder = MagicMock()
        mock_folder.all.return_value.only.return_value = [single, master, exc]

        results = list(source._non_occurrence_items(
            mock_folder, "subject", "start", "end", "location", "type"))

        subjects = [r.subject for r in results]
        assert "single" in subjects
        assert "master" in subjects
        assert "exception" not in subjects

    def test_exception_items_pages_in_two_year_chunks(self, source):
        """A window longer than 2 years should result in multiple
        CalendarView calls."""
        mock_folder = MagicMock()
        mock_folder.view.return_value.filter.return_value.only.return_value = []

        window_start = START
        window_end = START + timedelta(days=3 * 365)  # 3 years → 2 chunks

        list(source._exception_items(
            mock_folder, window_start, window_end,
            "subject", "start", "end", "location", "type"))

        assert mock_folder.view.call_count == 2

    def test_exception_items_single_chunk_for_short_window(self, source):
        mock_folder = MagicMock()
        mock_folder.view.return_value.filter.return_value.only.return_value = []

        window_start = START
        window_end = START + timedelta(days=365)  # 1 year → 1 chunk

        list(source._exception_items(
            mock_folder, window_start, window_end,
            "subject", "start", "end", "location", "type"))

        assert mock_folder.view.call_count == 1


class TestEWSCalendarContentResource:
    def _make_resource(self, source):
        from os2datascanner.engine2.model.ewscalendar import (
            EWSCalendarContentHandle, EWSCalendarItemSource)
        handle = EWSCalendarHandle(
            source, PATH, "Meeting", "Calendar", START, END, None, SINGLE)
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
        mock_item = MagicMock()
        mock_item.body = mock_body

        with patch.object(resource, "_get_item", return_value=mock_item):
            with resource.make_stream() as stream:
                content = stream.read()
        assert b"Hello World" in content

    def test_get_last_modified_prefers_last_modified_time(self, source):
        resource = self._make_resource(source)
        mock_item = MagicMock()
        mock_item.last_modified_time = START
        mock_item.datetime_created = END

        with patch.object(resource, "_get_item", return_value=mock_item):
            assert resource.get_last_modified() == START

    def test_get_last_modified_falls_back_to_created(self, source):
        resource = self._make_resource(source)
        mock_item = MagicMock()
        mock_item.last_modified_time = None
        mock_item.datetime_created = END

        with patch.object(resource, "_get_item", return_value=mock_item):
            assert resource.get_last_modified() == END


class TestEWSCalendarFileAttachmentHandle:
    def _make_handle(self, source, name="doc.pdf",
                     content_type="application/pdf", size=2048):
        calendar_handle = EWSCalendarHandle(
            source, PATH, "Meeting", "Calendar", START, END, None, SINGLE)
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
        from os2datascanner.engine2.model.core import Handle
        h = self._make_handle(source)
        restored = Handle.from_json_object(h.to_json_object())
        assert restored._name == h._name
        assert restored._content_type == h._content_type
        assert restored._size == h._size


class TestEWSCalendarItemAttachmentHandle:
    def _make_handle(self, source, name="invite.eml"):
        calendar_handle = EWSCalendarHandle(
            source, PATH, "Meeting", "Calendar", START, END, None, SINGLE)
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
        from os2datascanner.engine2.model.core import Handle
        h = self._make_handle(source)
        restored = Handle.from_json_object(h.to_json_object())
        assert restored._name == h._name
