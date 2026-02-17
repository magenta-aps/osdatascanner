# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

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
