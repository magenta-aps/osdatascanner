import pytest

from django.core.management import call_command

from os2datascanner.projects.report.organizations.models import OrganizationalUnit
from os2datascanner.projects.report.reportapp.models.scanner_reference import ScannerReference
from .test_utilities import create_reports_for


@pytest.mark.django_db
class TestDPOOverviewCommand:

    def test_dpo_overview_command(self, olsenbanden_organization, egon_email_alias):
        """The command does not throw errors."""
        create_reports_for(egon_email_alias)
        call_command("dpo_overview", olsenbanden_organization.uuid)

    def test_dpo_overview_command_no_reports(self, olsenbanden_organization):
        """Even with no reports, the command should not throw errors."""
        call_command("dpo_overview", olsenbanden_organization.uuid)

    def test_dpo_overview_command_org_unit_mismatch(self, olsenbanden_organization, avengers_ou):
        """Calling the command with an OU from a different organization should raise an
        exception."""
        with pytest.raises(OrganizationalUnit.DoesNotExist):
            call_command("dpo_overview", olsenbanden_organization.uuid, unit=avengers_ou.uuid)

    def test_dpo_overview_command_org_scanner_mismatch(self, olsenbanden_organization, scan_marvel):
        """Calling the command with a scanner from a different organization should raise an
        exception."""
        with pytest.raises(ScannerReference.DoesNotExist):
            call_command("dpo_overview", olsenbanden_organization.uuid,
                         scanner=scan_marvel.scanner_pk)
