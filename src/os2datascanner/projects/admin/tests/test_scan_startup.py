# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner_helpers import (
        ScheduledCheckup)


from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
from os2datascanner.engine2.model import http
from os2datascanner.engine2.pipeline import messages

from os2datascanner.projects.admin.adminapp.models.scannerjobs.webscanner import WebScanner
from os2datascanner.engine2.rules.logical import AndRule


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

    def test_webscan_checkup_rule(
            self, *,
            web_scanner,
            web_scanner_execution,
            ws_page_1):
        template = web_scanner._construct_scan_spec_template(None, False)

        checkup, = web_scanner._yield_checkups(template, False, False)
        assert isinstance(checkup, messages.ConversionMessage)
        assert checkup.handle == ws_page_1.handle

        match checkup.progress.rule:
            case AndRule([LastModifiedRule(after=ws_page_1.interested_after),
                          RegexRule()]):
                pass
            case c:
                pytest.fail(
                        "expected one LastModifiedRule and a dummy,"
                        f" but got {c}")

    def test_webscan_checkups(
            self, *,
            web_scanner: WebScanner,
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
