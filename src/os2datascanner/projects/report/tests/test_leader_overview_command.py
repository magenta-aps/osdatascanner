import pytest
import re

from django.core.management import call_command

from os2datascanner.projects.report.organizations.models import Account


@pytest.mark.django_db
class TestLeaderOverviewCommand:

    def test_leader_overview_command(self, capfd, olsenbanden_organization, egon_account,
                                     benny_account, kjeld_account, hulk_account):
        """All accounts in the organization are shown"""
        call_command("leader_overview", olsenbanden_organization.uuid)

        usernames = re.findall(
            r'\n\|\s+(\w+)\s+\|',
            capfd.readouterr()[0])

        for acc in Account.objects.filter(organization=olsenbanden_organization):
            assert acc.username in usernames
        assert hulk_account.username not in usernames

    def test_leader_overview_command_orgunit(self, capfd, olsenbanden_organization,
                                             olsenbanden_ou_positions, olsenbanden_ou,
                                             yvonne_account, bøffen_account):
        """All accounts in the chosen unit are shown"""
        call_command("leader_overview", olsenbanden_organization.uuid, unit=olsenbanden_ou.uuid)

        usernames = re.findall(
            r'\n\|\s+(\w+)\s+\|',
            capfd.readouterr()[0])

        for acc in Account.objects.filter(positions__unit=olsenbanden_ou):
            assert acc.username in usernames
        assert yvonne_account.username not in usernames
        assert bøffen_account.username not in usernames

    def test_leader_overview_command_leader(self, capfd, egon_account, benny_account,
                                            kjeld_account, yvonne_account,
                                            olsenbanden_organization):
        """All accounts directly managed by the chosen account are shown"""
        call_command("leader_overview", olsenbanden_organization.uuid, leader=egon_account.username)

        usernames = re.findall(
            r'\n\|\s+(\w+)\s+\|',
            capfd.readouterr()[0])

        for acc in Account.objects.filter(manager=egon_account):
            assert acc.username in usernames
        assert yvonne_account.username not in usernames
