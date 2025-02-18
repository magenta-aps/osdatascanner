import pytest

from os2datascanner.engine2.model.msgraph.calendar import MSGraphCalendarEventHandle


@pytest.fixture
def handle():
    return MSGraphCalendarEventHandle(
            source=None,
            path="path/to/event",
            event_subject="Event subject",
            weblink="https://example.com/event",
            start={
                "dateTime": "2023-03-13T09:00:00.000",
                "timeZone": "UTC"})


class TestMSGraphCalendarEventHandle:
    def test_start(self, handle):
        assert handle.start == "09:00 13/3/23"

    def test_presentation_name(self, handle):
        assert handle.presentation_name == "[09:00 13/3/23] Event subject"

    def test_presentation_url(self, handle):
        assert handle.presentation_url == "https://example.com/event"
