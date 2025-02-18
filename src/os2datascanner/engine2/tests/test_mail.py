import os.path
import pytest

from os2datascanner.engine2.model.core import Source, SourceManager
from os2datascanner.engine2.model.file import (
        FilesystemHandle, FilesystemSource)
from os2datascanner.engine2.model.derived.mail import (
        MailSource, MailPartHandle, sanitise_path)

from os2datascanner.engine2.model.utilities.mail import decode_encoded_words


here_path = os.path.dirname(__file__)
test_data_path = os.path.join(here_path, "data", "mail")


test_subject = """SV: Ændret købsaftale på plads"""


encoded_subjects = {
    "utf-8-base64": "=?utf-8?b?U1Y6IMOGbmRyZXQga8O4YnNhZnRhbGUgcMOlIHBsYWRz?=",
    "latin-1-q": "=?iso-8859-1?q?SV=3A_=C6ndret_k=F8bsaftale_p=E5_plads?=",
    "utf-8-q-split": (
            "=?utf-8?q?SV=3A_=C3=86ndret?="
            "=?utf-8?q?_k=C3=B8bsaftale_p=C3=A5_plads?="
    ),
    "mixed-q-split": (
            "=?iso-8859-1?q?SV=3A_=C6ndret?="
            "=?utf-8?q?_k=C3=B8bsaftale_p=C3=A5_plads?=")
}


invalid_encoded_subjects = {
    "no-such-charset": (
            # UTF-8 declared with a nonexistent codec
            "=?ebcdic-gopher2010?b?"
            "U1Y6IMOGbmRyZXQga8O4YnNhZnRhbGUgcMOlIHBsYWRz?=",
            # (all of the codepoints here become two bytes in UTF-8, so they
            # get two replacement characters)
            "SV: ��ndret k��bsaftale p�� plads"),
    "lying-encoding": (
            # Latin-1 declared as UTF-8
            "=?utf-8?q?SV=3A_=C6ndret_k=F8bsaftale_p=E5_plads?=",
            "SV: �ndret k�bsaftale p� plads"),
}


class TestEngine2Mail:
    def test_eml_files(self):
        fs = FilesystemSource(test_data_path)
        with SourceManager() as sm:
            for h in fs.handles(sm):
                mail_source = Source.from_handle(h)
                assert isinstance(mail_source, MailSource)
                for h in mail_source.handles(sm):
                    assert isinstance(h, MailPartHandle)
                    r = h.follow(sm)
                    assert h.guess_type() == r.compute_type()

    def test_alternative_trimming(self):
        alternative_source = MailSource(
                FilesystemHandle.make_handle(
                        os.path.join(test_data_path, "alternative.eml")))
        with SourceManager() as sm:
            assert len(list(alternative_source.handles(sm))) == 1

    @pytest.mark.parametrize("value", encoded_subjects.values())
    def test_encoded_word_decoding(self, value):
        """Encoded-Word values can be decoded."""
        assert test_subject == decode_encoded_words(value)

    @pytest.mark.parametrize("pair", invalid_encoded_subjects.values())
    def test_encoded_word_failures(self, pair):
        """Broken Encoded-Word values can still be decoded (slightly)."""
        value, expected = pair
        assert decode_encoded_words(value) == expected

    @pytest.mark.parametrize("odd_path", [
        "1/2/1/",
        "/1/2/1/",
        "//1/2/1/"])
    def test_mail_path_sanitation(self, odd_path):
        assert sanitise_path(odd_path) == "1/2/1/"

    @pytest.mark.parametrize("odd_path", [
        "1/2/1/https://www.example.com/resources/U1F928.PDF",
        "1/2/1/files/U1F928.PDF",
        "/1/2/1/C:/Users/af/Downloads/U1F928.PDF",
        "//1/2/1///SHARE/Home/af/Files/U1F928.PDF"])
    def test_attachment_path_sanitation(self, odd_path):
        assert sanitise_path(odd_path) == "1/2/1/U1F928.PDF"
