import pytest

from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
class TestExchangeScanner:
    @pytest.mark.parametrize('userlist_file,expected', [
        (
            SimpleUploadedFile(
                    "userlist.txt",
                    b"egon\nbenny\nfrank"),
            ["egon", "benny", "frank"]
        ),
        (
            SimpleUploadedFile(
                    "utf_16_userlist.txt",
                    # chardet (as of version 5.0.0) *can't* identify UTF-16
                    # without a byte order mark, and Python's _le and _be
                    # codecs don't emit one
                    "egon\nbenny\nfrank".encode("utf_16")),
            ["egon", "benny", "frank"]
        ),
    ])
    def test_userlist_formats(
            self,
            exchange_scanner,
            userlist_file,
            expected):

        exchange_scanner.authentication.set_password("swordfish")

        exchange_scanner.userlist = userlist_file

        assert len(
            [source._user for source in exchange_scanner.generate_sources()]
            ) == len(expected)
