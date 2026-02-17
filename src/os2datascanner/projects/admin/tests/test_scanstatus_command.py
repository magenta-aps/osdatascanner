# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from django.core.management import call_command


@pytest.mark.django_db
class TestScanStatusCommand:

    def test_scanstatus_command(self, basic_scanstatus):
        """The command does not throw any errors when run on a status."""
        call_command("scanstatus", basic_scanstatus.pk)

    def test_completed_scanstatus_command(self, basic_scanstatus_completed):
        """The command does not throw any errors when run on a completed status"""
        call_command("scanstatus", basic_scanstatus_completed.pk)
