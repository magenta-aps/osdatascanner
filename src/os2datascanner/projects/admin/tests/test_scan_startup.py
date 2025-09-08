import pytest

from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner_helpers import (
        ScheduledCheckup)


from os2datascanner.engine2.model import http
from os2datascanner.engine2.pipeline import messages


@pytest.mark.django_db
class TestScanStartup:
    def test_simple_scan_startup(self, web_scanner):
        assert (messages.ScanTagFragment.from_json_object(
                        web_scanner.run(dry_run=True))
                is not None)

    def test_webscan_source(
            self, *,
            web_scanner):
        template = web_scanner._construct_scan_spec_template(None, True)

        match list(web_scanner._yield_sources(template, True)):
            case [messages.ScanSpecMessage(
                    source=http.WebSource(url="http://www.example.com"))]:
                pass
            case c:
                pytest.fail(f"expected a list of one scan spec, but got {c}")

    def test_webscan_checkups(
            self, *,
            web_scanner,
            ws_page_1, ws_page_2, ws_page_3):
        template = web_scanner._construct_scan_spec_template(None, True)

        match list(web_scanner._yield_checkups(template, True, False)):
            case [messages.ConversionMessage(handle=ws_page_1.handle),
                  messages.ConversionMessage(handle=ws_page_2.handle),
                  messages.ConversionMessage(handle=ws_page_3.handle)]:
                pass
            case c:
                pytest.fail(
                        f"expected a list of three conversions, but got {c}")

    def test_webscan_checkups_irrelevant(
            self, *,
            web_scanner,
            ws_page_1, ws_irrelevant_page):
        template = web_scanner._construct_scan_spec_template(None, True)

        match list(web_scanner._yield_checkups(template, True, False)):
            case [messages.ConversionMessage(handle=ws_page_1.handle),
                  messages.ProblemMessage(handle=ws_irrelevant_page.handle,
                                          irrelevant=True)]:
                pass
            case c:
                pytest.fail(
                        "expected a list of one conversion and one problem,"
                        f" but got {c}")

        with pytest.raises(ScheduledCheckup.DoesNotExist):
            ws_irrelevant_page.refresh_from_db()
