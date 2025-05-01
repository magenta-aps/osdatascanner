import pytest

from os2datascanner.engine2.model.ews import (
        EWSMailHandle, EWSAccountSource)
from os2datascanner.engine2.model.smbc import SMBCSource, SMBCHandle
from os2datascanner.engine2.model.data import DataSource, DataHandle
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
                    "secretary"),
            "notavalidfolderid.notavalidmailid",
            "Re: Re: Re: You may already have won! (was Fwd: Spam)",
            "Inbox", "notavalidentryid")

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
