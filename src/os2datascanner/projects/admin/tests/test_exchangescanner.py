from parameterized import parameterized

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from os2datascanner.engine2.rules.dummy import AlwaysMatchesRule
from ..adminapp.models.rules import CustomRule
from ..adminapp.models.authentication import Authentication
from ..adminapp.models.scannerjobs.exchangescanner import ExchangeScanner


class ExchangeScannerTests(TestCase):
    @parameterized.expand([
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
    def test_userlist_formats(self, userlist_file, expected):
        rule = CustomRule.objects.create(
                name="ul_format_test_rule",
                _rule=AlwaysMatchesRule().to_json_object())
        es = ExchangeScanner.objects.create(name="ul_format_test", rule=rule)

        es.authentication = Authentication()
        es.userlist = userlist_file
        self.assertCountEqual(
                (source._user for source in es.generate_sources()),
                expected,
                "userlist file was not handled correctly")
