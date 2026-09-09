# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from os2datascanner.engine2.model.ews import (
        EWSMailHandle, EWSAccountSource)
from os2datascanner.engine2.model.smbc import SMBCSource, SMBCHandle
from os2datascanner.engine2.model.data import DataSource, DataHandle
from os2datascanner.engine2.model.http import WebSource, WebHandle
from os2datascanner.engine2.model.derived.libreoffice import (
        LibreOfficeSource, LibreOfficeObjectHandle)
from os2datascanner.engine2.model.derived.zip import ZipSource, ZipHandle
from os2datascanner.engine2.model.derived.filtered import (
        GzipSource, FilteredHandle)


class TestCensor:
    @pytest.mark.parametrize("handle", [
        SMBCHandle(
                SMBCSource(
                        "//SERVER/Resource", "username"),
                "~ocument.docx"),
        SMBCHandle(
                SMBCSource(
                        "//SERVER/Resource",
                        "username", "topsecret", "WORKGROUP8"),
                "~ocument.docx"),
    ])
    def test_smbc_censoring(self, handle):
        handle = handle.censor()

        assert handle.source._domain is None
        assert handle.source._password is None
        assert handle.source._user is None

    def test_ews_censoring(self):
        handle = EWSMailHandle(
            EWSAccountSource(
                "internet.invalid",
                "mail.internet.invalid",
                "administrator", "h4ckme",
                "secretary"
            ),
            "notavalidfolderid.notavalidmailid",
            "Re: Re: Re: You may already have won! (was Fwd: Spam)",
            "Inbox",
            "notavalidentryid",
            "https://outlook.office365.com/owa/?ItemID=abc",
        )

        censored_handle = handle.censor()

        assert censored_handle.source._admin_user is None
        assert censored_handle.source._admin_password is None
        assert handle._mail_subject == censored_handle._mail_subject
        assert handle._folder_name == censored_handle._folder_name
        assert handle._entry_id == censored_handle._entry_id

    @pytest.mark.parametrize("handle", [
        ZipHandle(
                ZipSource(
                        SMBCHandle(
                                SMBCSource(
                                        "//SERVER/Resource",
                                        "username", driveletter="W"),
                                "Confidential Documents.zip")),
                "doc/Personal Information.docx"),
        FilteredHandle(
                GzipSource(
                        SMBCHandle(
                                SMBCSource(
                                        "//SERVER/usr", "username"),
                                "share/doc/coreutils"
                                "/changelog.Debian.gz")),
                "changelog.Debian"),
    ])
    def test_nested_censoring(self, handle):
        assert handle.source.handle.source._user is not None
        handle = handle.censor()
        assert handle.source.handle.source._user is None

    def test_top_source_mapping(self):
        share = SMBCSource("//SERVER/Resource", "username", driveletter="W")
        zh = ZipHandle(
                ZipSource(
                        SMBCHandle(
                                share, "Confidential Documents.zip")),
                "doc/Personal Information.docx")
        assert zh.censor() == zh.remap({share: share.censor()})
        assert zh == zh.censor().remap({share.censor(): share})

    def test_intermediate_source_mapping(self):
        share = SMBCSource("//SERVER/Resource", "username", driveletter="W")
        zs = ZipSource(SMBCHandle(share, "Confidential Documents.zip"))
        zh = ZipHandle(zs, "doc/Personal Information.docx")
        assert zh.censor() == zh.remap({zs: zs.censor()})
        assert zh == zh.censor().remap({zs.censor(): zs})

    def test_data_censoring(self):
        handle = DataHandle(
                DataSource(
                        b"VGhpcyBpcyBhIHRlc3Qgb2YgdGhlIEVtZXJnZW5jeSBCcm9hZGNh"
                        b"c3QgU3lzdGVtLgo=", "text/plain", "test.txt"),
                "test.txt")
        censored_handle = handle.censor()
        assert censored_handle.source._content is None
        assert handle.source.mime == censored_handle.source.mime
        assert handle.source.name == censored_handle.source.name


class TestWebCensor:
    """A WebSource's URLs can carry credentials as userinfo, and the censored
    Source is what the report module presents and links to."""

    def test_userinfo_is_removed(self):
        source = WebSource("https://svend:hemmelighed@intranet.invalid/docs")

        censored = source.censor()

        assert censored.url == "https://intranet.invalid/docs"

    def test_userinfo_is_removed_from_every_url(self):
        source = WebSource(
                "https://svend:hemmelighed@intranet.invalid",
                sitemap="https://svend:hemmelighed@intranet.invalid/sitemap.xml",
                exclude=["https://svend:hemmelighed@intranet.invalid/private"])

        censored = source.censor()

        assert "hemmelighed" not in str(censored.to_json_object())

    def test_other_properties_survive(self):
        source = WebSource(
                "https://svend:hemmelighed@intranet.invalid",
                sitemap_trusted=True, extended_hints=True, always_crawl=True)

        censored = source.censor()

        assert censored._sitemap_trusted
        assert censored._extended_hints
        assert censored._always_crawl

    def test_a_handle_keeps_its_path(self):
        handle = WebHandle(
                WebSource("https://svend:hemmelighed@intranet.invalid"),
                "docs/Personal Information.docx")

        censored = handle.censor()

        assert censored.relative_path == handle.relative_path
        assert "hemmelighed" not in censored.presentation_url

    def test_a_handle_presents_no_credentials(self):
        """A Handle is interpolated into log lines by every pipeline stage,
        which the exporter's censoring never sees."""
        handle = WebHandle(
                WebSource("http://user:topsecretpwd@nginx"),
                "Sundhedsjournal.doc")

        assert "topsecretpwd" not in handle.presentation_url
        assert "topsecretpwd" not in handle.presentation_name
        assert "topsecretpwd" not in str(handle)

    def test_a_derived_handle_presents_no_credentials(self):
        """Derived Handles build their presentation from the Handle they were
        derived from, so the leaf URL must already be free of credentials."""
        handle = LibreOfficeObjectHandle(
                LibreOfficeSource(
                        WebHandle(
                                WebSource("http://user:topsecretpwd@nginx"),
                                "Sundhedsjournal.doc")),
                "Sundhedsjournal.html")

        assert "topsecretpwd" not in str(handle)

    def test_a_true_url_hint_presents_no_credentials(self):
        handle = WebHandle(
                WebSource("http://nginx"), "a.doc",
                hints={"true_url": "http://user:topsecretpwd@nginx/b.doc"})

        assert "topsecretpwd" not in handle.presentation_url

    def test_the_fetched_url_keeps_its_credentials(self):
        """WebResource requests WebHandle._url, so credentials must survive
        there for an authenticated scan to work at all."""
        handle = WebHandle(
                WebSource("http://user:topsecretpwd@nginx"), "a.doc")

        assert handle._url == "http://user:topsecretpwd@nginx/a.doc"

    @pytest.mark.parametrize("url", [
        "https://intranet.invalid",
        "https://intranet.invalid/docs?q=a@b#fragment",
        "http://intranet.invalid:8080/~svend",
    ])
    def test_a_credential_free_source_is_unchanged(self, url):
        """Censoring must not perturb the crunched form of the Sources already
        in the wild: it is the primary key of their DocumentReports and
        ScheduledCheckups."""
        source = WebSource(url)

        assert source.censor().crunch() == source.crunch()
