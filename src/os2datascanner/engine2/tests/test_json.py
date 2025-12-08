import pytest

from os2datascanner.engine2.model.core import (
        Source, Handle, SourceManager, UnknownSchemeError, DeserialisationError)
from os2datascanner.engine2.model.data import DataSource, DataHandle
from os2datascanner.engine2.model.ews import (
        EWSMailHandle, EWSAccountSource, OFFICE_365_ENDPOINT as CLOUD)
from os2datascanner.engine2.model.file import (
        FilesystemSource, FilesystemHandle)
from os2datascanner.engine2.model.http import WebSource, WebHandle
from os2datascanner.engine2.model.smbc import SMBCSource, SMBCHandle
from os2datascanner.engine2.model.msgraph.mail import (
        MSGraphMailSource, MSGraphMailAccountHandle,
        MSGraphMailAccountSource, MSGraphMailMessageHandle)
from os2datascanner.engine2.model.msgraph.files import (
        MSGraphFilesSource, MSGraphDriveHandle, MSGraphDriveSource, MSGraphFileHandle)
from os2datascanner.engine2.model.msgraph.lists import (
        MSGraphListItemHandle, MSGraphListHandle, MSGraphListSource, MSGraphListsSource)

from os2datascanner.engine2.model.derived.filtered import (
        GzipSource, FilteredHandle)
from os2datascanner.engine2.model.derived.libreoffice import (
        LibreOfficeSource, LibreOfficeObjectHandle)
from os2datascanner.engine2.model.derived.mail import (
        MailSource, MailPartHandle)
from os2datascanner.engine2.model.derived.pdf import (
        PDFSource, PDFPageHandle, PDFPageSource, PDFObjectHandle)
from os2datascanner.engine2.model.derived.tar import TarSource, TarHandle
from os2datascanner.engine2.model.derived.zip import ZipSource, ZipHandle


example_handles = [
    FilesystemHandle(
            FilesystemSource("/usr/share/common-licenses"),
            "GPL-3"),
    DataHandle(
            DataSource(b"This is a test", "text/plain"),
            "file"),
    DataHandle(
            DataSource(b"This is a test", "text/plain", "test.txt"),
            "test.txt"),
    FilteredHandle(
            GzipSource(
                    FilesystemHandle(
                            FilesystemSource("/usr/share/doc/coreutils"),
                            "changelog.Debian.gz")),
            "changelog.Debian"),
    SMBCHandle(
            SMBCSource(
                    "//SERVER/Resource", "username"),
            "~ocument.docx"),
    SMBCHandle(
            SMBCSource(
                    "//SERVER/Resource",
                    "username", "topsecret", "WORKGROUP8"),
            "~ocument.docx"),
    ZipHandle(
            ZipSource(
                    SMBCHandle(
                            SMBCSource(
                                    "//SERVER/Resource",
                                    "username", driveletter="W"),
                            "Confidential Documents.zip")),
            "doc/Personal Information.docx"),
    WebHandle(
            WebSource(
                    "https://secret.data.invalid/"),
            "lottery-numbers-for-next-week.txt"),
    TarHandle(
            TarSource(
                    FilesystemHandle(
                            FilesystemSource(
                                    "/home/user"),
                            "Downloads/data.tar.gz")),
            "data0.txt"),
    MailPartHandle(
            MailSource(
                    EWSMailHandle(
                            EWSAccountSource(
                                    domain="cloudy.example",
                                    server=CLOUD,
                                    admin_user="cloudministrator",
                                    admin_password="littlefluffy",
                                    user="claude"),
                            "SW5ib3hJRA==.TWVzc2dJRA==",
                            "Re: Castles in the sky",
                            "Inbox", "0000012345",
                            "https://outlook.office365.com/owa/?ItemID=abc")),
            "1/pictograph.jpeg",
            "image/jpeg"),
    PDFObjectHandle(
        PDFPageSource(
                    PDFPageHandle(
                            PDFSource(
                                    FilesystemHandle(
                                            FilesystemSource("/home/kiddw/Documents"),
                                            "1699 Gardiners trip/"
                                            "treasure_map.pdf")
                                        ),
                            "10")),
        "X-marks-the-spot_000-0.png"),
    LibreOfficeObjectHandle(
            LibreOfficeSource(
                    FilesystemHandle(
                            FilesystemSource("/media/user/USB STICK"),
                            "What I Did On My Holidays.doc")),
            "What I Did On My Holidays.html"),
    MSGraphMailMessageHandle(
            MSGraphMailAccountSource(
                    MSGraphMailAccountHandle(
                            MSGraphMailSource(
                                    "Not a real client ID value",
                                    "Not a real tenant ID value",
                                    "Not a very secret client secret",
                                    True),
                            "testuser@example.invalid")),
            "bWVzc2FnZQo=",
            "Re: Re: Re: Copy of FINAL (2) (EDITED).doc.docx",
            "https://example.invalid/view/bWVzc2FnZQo="),
    MSGraphFileHandle(
            MSGraphDriveSource(
                    MSGraphDriveHandle(
                            MSGraphFilesSource(
                                    "Not a real client ID value",
                                    "Not a real tenant ID value",
                                    "Not a very secret client secret"),
                            "1NOTAREALDR1VE1DENT1F1ER",
                            "Shared Documents and Conspiracies",
                            "Guy Fawkes")),
            "PLOTS/1605-11/GUNPWDER.WP"),
    MSGraphListItemHandle(
            MSGraphListSource(
                MSGraphListHandle(
                    MSGraphListsSource(
                        "Not a real client ID",
                        "Not a real tentant",
                        "not a real secret"
                        ),
                    "not a real path",
                    "not a real list name",
                    "not a real site")
            ),
            "Not a real path",
            "Not a real site",
            "Not a real id",
            "Not a real url",
            "Not a real item name"
    )

]


class TestJSON:
    @pytest.mark.parametrize("handle", example_handles)
    def test_json_round_trip(self, handle):
        json = handle.to_json_object()
        assert handle == handle.from_json_object(json)

    @pytest.mark.parametrize("handle", example_handles)
    def test_followable(self, handle):
        with SourceManager() as sm:
            try:
                handle.follow(sm)
            except TypeError:
                raise
            except Exception:
                pass

    def test_invalid_json(self):
        with pytest.raises(UnknownSchemeError):
            Source.from_json_object({
                "type": "gopher",
                "hostname": "gopher.invalid"
            })
        with pytest.raises(UnknownSchemeError):
            Handle.from_json_object({
                "type": "gopher",
                "source": {
                    "type": "gopher",
                    "hostname": "gopher.invalid"
                },
                "path": "/Reference"
            })

    def test_incomplete_json(self):
        with pytest.raises(DeserialisationError):
            Source.from_json_object({
                "hostname": "gopher.invalid"
            })
        with pytest.raises(DeserialisationError):
            Handle.from_json_object({
                "source": {
                    "type": "gopher",
                    "hostname": "gopher.invalid"
                },
                "path": "/Reference"
            })

    def test_double_json_registration(self):
        with pytest.raises(ValueError):
            @Source.json_handler("file")
            def handle_json(j):  # noqa
                pass
        with pytest.raises(ValueError):
            @Handle.json_handler("file")
            def handle_json(j):  # noqa
                pass

    def test_smb_backwards_compatibility(self):
        """ Checks that a json-handle from legacy type SMB turns into an appropriate SMBC"""
        assert (Handle.from_json_object({
            "type": "smb",
            "source": {
                "type": "smb",
                "unc": "//server/folder",
                "domain": "my_domain",
                "user": "dummy",
                "password": "<PASSWORD>"
            },
            "path": "path/to/file.txt"
            })) == (SMBCHandle(SMBCSource(unc="//server/folder",
                                          domain="my_domain",
                                          user="dummy",
                                          password="<PASSWORD>"), "path/to/file.txt"))
