import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from os2datascanner.engine2.rules.logical import OrRule
from os2datascanner.engine2.rules.dict_lookup import EmailHeaderRule


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
        exchange_scanner.userlist = userlist_file

        assert len(
            [source._user for source in exchange_scanner.generate_sources()]
            ) == len(expected)

    def test_construct_rule(self, exchange_scanner):
        # Arrange
        basic_rule = exchange_scanner.rule.make_engine2_rule()
        expected = OrRule(EmailHeaderRule("subject", basic_rule), basic_rule)

        # Act
        rule = exchange_scanner._construct_rule(force=False)

        # Assert
        assert rule == expected

    def test_construct_rule_scan_subject_false(self, exchange_scanner):
        # Arrange
        exchange_scanner.scan_subject = False
        basic_rule = exchange_scanner.rule.make_engine2_rule()

        # Act
        rule = exchange_scanner._construct_rule(force=False)

        # Assert
        assert rule == basic_rule
