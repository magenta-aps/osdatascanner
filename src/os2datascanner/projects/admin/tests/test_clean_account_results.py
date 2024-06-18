import pytest
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.mark.django_db
class TestCleanAccountResults:

    def call_command(self, *args, **kwargs):
        err = StringIO()
        call_command(
            "cleanup_account_results",
            *args,
            stdout=StringIO(),
            stderr=err,
            **kwargs
        )

        return err.getvalue()

    def test_invalid_account(self, basic_scanner):
        """Calling the command with an invalid username should raise a
        CommandError."""

        with pytest.raises(CommandError):
            self.call_command(
                accounts=["invalidAccount"],
                scanners=[basic_scanner.pk]
            )

    def test_invalid_scanner(self, oluf):
        """Calling the command with an invalid scanner pk should raise a
        CommandError."""

        with pytest.raises(CommandError):
            self.call_command(
                accounts=[oluf.username],
                scanners=[100]
            )

    def test_running_scanner(self, oluf, basic_scanner, basic_scanstatus):
        """Calling the command specifying a running scanner should write
        something to stderr."""

        with pytest.raises(CommandError):
            self.call_command(
                accounts=[oluf.username],
                scanners=[basic_scanner.pk]
            )
