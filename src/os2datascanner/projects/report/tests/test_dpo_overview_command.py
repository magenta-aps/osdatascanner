import pytest
import random

from django.core.management import call_command

from os2datascanner.projects.report.organizations.models import OrganizationalUnit, Organization
from os2datascanner.projects.report.reportapp.models.scanner_reference import ScannerReference
from .test_utilities import create_reports_for


@pytest.mark.django_db
class TestDPOOverviewCommand:

    def test_dpo_overview_command(self, olsenbanden_organization, egon_email_alias):
        """The command does not throw errors."""
        create_reports_for(egon_email_alias)
        call_command("dpo_overview")

    def test_dpo_overview_command_no_reports(self, olsenbanden_organization):
        """Even with no reports, the command should not throw errors."""
        call_command("dpo_overview")

    def test_dpo_overview_command_org_unit_mismatch(self, olsenbanden_organization, avengers_ou):
        """Calling the command with an OU from a different organization should raise an
        exception."""
        with pytest.raises(OrganizationalUnit.DoesNotExist):
            call_command("dpo_overview", organization=olsenbanden_organization.uuid,
                         unit=avengers_ou.uuid)

    def test_dpo_overview_command_org_scanner_mismatch(self, olsenbanden_organization, scan_marvel):
        """Calling the command with a scanner from a different organization should raise an
        exception."""
        with pytest.raises(ScannerReference.DoesNotExist):
            call_command("dpo_overview", organization=olsenbanden_organization.uuid,
                         scanner=scan_marvel.scanner_pk)

    @pytest.mark.parametrize("case_func", [
        lambda s: s.upper(),
        lambda s: s.lower(),
        # Mixed case
        lambda s: "".join([random.choice((x.upper(), x.lower())) for x in s])
    ])
    def test_dpo_overview_command_organization_name(self, olsenbanden_organization, case_func):
        """Calling the command using the organization's name should work. All cases should work."""
        call_command("dpo_overview", organization=case_func(olsenbanden_organization.name))

    def test_dpo_overview_command_invalid_name(self, olsenbanden_organization):
        """Calling the command with the wrong name you should an appropriate error."""
        with pytest.raises(Organization.DoesNotExist):
            call_command("dpo_overview", organization="ThisIsDefinitelyNotTheNameOfTheOrganization")
