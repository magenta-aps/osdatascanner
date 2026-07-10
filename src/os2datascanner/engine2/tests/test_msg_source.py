import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from os2datascanner.engine2.conversions import convert
from os2datascanner.engine2.model.core import Source, SourceManager
from os2datascanner.engine2.model.derived.libreoffice import LibreOfficeSource
from os2datascanner.engine2.model.derived.mail import MailPartHandle
from os2datascanner.engine2.model.derived.msg import (
    MsgSource, UnsupportedMsgClassError, _msg_to_email_message)
from os2datascanner.engine2.model.file import FilesystemHandle
from os2datascanner.engine2.rules.cpr import CPRRule

DATA_DIR = Path(__file__).parent / "data" / "msg"


class TestMsgSource:

    def test_mime_routing(self):
        """Files with .msg extension route to MsgSource."""
        handle = FilesystemHandle.make_handle("/fake/path/test.msg")
        source = Source.from_handle(handle)
        assert isinstance(source, MsgSource)

    def test_cpr_found_in_body(self):
        """CPR numbers in a real Outlook .msg body are found when the file is scanned."""
        handle = FilesystemHandle.make_handle(str(DATA_DIR / "cpr-in-body.msg"))
        source = MsgSource(handle)
        rule = CPRRule(modulus_11=False, ignore_irrelevant=False)

        with SourceManager() as sm:
            results = []
            for h in source.handles(sm):
                resource = h.follow(sm)
                rep = convert(resource, rule.operates_on)
                if rep:
                    results.extend(rule.match(rep))

        assert any(r["match"] == "0601XXXXXX" for r in results)

    def test_cpr_found_in_attachment(self):
        """CPR numbers in a .msg attachment are found via a real .msg file."""
        handle = FilesystemHandle.make_handle(
            str(DATA_DIR / "cpr-in-attachment.msg"))
        source = MsgSource(handle)
        rule = CPRRule(modulus_11=False, ignore_irrelevant=False)

        with SourceManager() as sm:
            results = []
            for h in source.handles(sm):
                resource = h.follow(sm)
                rep = convert(resource, rule.operates_on)
                if rep:
                    results.extend(rule.match(rep))

        assert any(r["match"] == "2105XXXXXX" for r in results)

    def test_cpr_found_in_non_utf8_html_body(self):
        """A .msg file whose HTML body is not UTF-8 encoded (e.g. windows-1252,
        as written by some Outlook clients) is still scanned correctly instead
        of crashing with a UnicodeDecodeError."""
        handle = FilesystemHandle.make_handle(
            str(DATA_DIR / "non-utf8-html-body.msg"))
        source = MsgSource(handle)
        rule = CPRRule(modulus_11=False, ignore_irrelevant=False)

        with SourceManager() as sm:
            results = []
            for h in source.handles(sm):
                resource = h.follow(sm)
                rep = convert(resource, rule.operates_on)
                if rep:
                    results.extend(rule.match(rep))

        assert any(r["match"] == "1111XXXXXX" for r in results)

    def test_non_email_msg_raises_clearly(self):
        """Non-email .msg types (contacts, appointments, tasks) raise UnsupportedMsgClassError."""
        mock_msg = MagicMock(spec=["classType", "close", "__enter__", "__exit__"])
        mock_msg.classType = "IPM.Contact"
        mock_msg.__enter__.return_value = mock_msg
        mock_msg.__exit__.return_value = False

        with patch("os2datascanner.engine2.model.derived.msg._extract_msg.openMsg",
                   return_value=mock_msg):
            with pytest.raises(UnsupportedMsgClassError, match="IPM.Contact"):
                _msg_to_email_message("/fake/contact.msg")

    def test_libreoffice_fallback(self):
        """LibreOfficeSource delegates to MsgSource when it encounters a .msg file."""
        handle = FilesystemHandle.make_handle(str(DATA_DIR / "cpr-in-body.msg"))
        source = LibreOfficeSource(handle)
        with SourceManager() as sm:
            handles = list(source.handles(sm))
        assert len(handles) >= 1
        assert all(isinstance(h, MailPartHandle) for h in handles)
