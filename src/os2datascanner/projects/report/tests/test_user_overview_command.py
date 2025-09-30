import pytest

from django.core.management import call_command

from .test_utilities import create_reports_for


@pytest.mark.django_db
class TestUserOverviewCommand:

    def test_user_overview_command(self, egon_account, egon_email_alias):
        """The command does not throw errors when called."""
        create_reports_for(egon_email_alias)

        call_command("user_overview", egon_account.username)

    def test_user_overview_command_no_results(self, egon_account):
        """The command does not throw errors when called for an account with no results."""
        call_command("user_overview", egon_account.username)
