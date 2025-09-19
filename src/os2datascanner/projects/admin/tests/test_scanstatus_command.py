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
