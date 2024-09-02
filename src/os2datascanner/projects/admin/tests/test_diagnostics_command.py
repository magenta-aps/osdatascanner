import pytest
import re

from django.core.management import call_command
from django.conf import settings

from ....core_organizational_structure.models.organization import (
    StatisticsPageConfigChoices, SupportContactChoices,
    DPOContactChoices, OutlookCategorizeChoices)
from ..organizations.models.account import Account
from .test_utilities import create_errors


@pytest.fixture
def temp_settings():
    return settings


@pytest.mark.django_db
class TestDiagnosticsCommand:

    def test_command_runs(self, capfd):
        # Arrange
        expected_diagnostics = [
            "accounts",
            "aliases",
            "errors",
            "units",
            "organizations",
            "rules",
            "settings"]

        # Act
        call_command("diagnostics")

        diagnostics_parts = re.findall(
            r'>> Running diagnostics on (\w+) ...',
            capfd.readouterr()[0])

        # Assert
        assert diagnostics_parts == expected_diagnostics

    @pytest.mark.parametrize('arg,expected', [
        ('Account', 'accounts'),
        ('Alias', 'aliases'),
        ('UserErrorLog', 'errors'),
        ('OrganizationalUnit', 'units'),
        ('Organization', 'organizations'),
        ('Rule', 'rules'),
        ('Settings', 'settings'),
    ])
    def test_partial_diagnostics(self, arg, expected, capfd):
        # Arrange
        expected_diagnostics = [expected]

        # Act
        call_command("diagnostics", only=[arg])

        diagnostics_parts = re.findall(
            r'>> Running diagnostics on (\w+) ...',
            capfd.readouterr()[0])

        # Assert
        assert diagnostics_parts == expected_diagnostics

    # Accounts

    def test_count_accounts(self, capfd, fritz, günther, hansi):
        hansi.imported = True
        hansi.save()

        call_command("diagnostics", only=["Account"])

        match = re.search(
            r'Found a total of (\d+) accounts. (\d+) are imported.',
            capfd.readouterr()[0])

        assert match.group(1) == "3"
        assert match.group(2) == "1"

    def test_count_accounts_without_username(
            self, fritz, günther, hansi, capfd):
        Account.objects.all().update(username="")

        call_command("diagnostics", only=["Account"])

        match = re.search(r'Found (\d+) accounts without a username.', capfd.readouterr()[0])

        assert match.group(1) == "3"

    def test_count_accounts_without_email(self, fritz, günther, hansi, capfd):
        Account.objects.all().update(email="")

        call_command("diagnostics", only=["Account"])

        match = re.search(r'Found (\d+) accounts with email = \'\'', capfd.readouterr()[0])

        assert match.group(1) == "3"

    def test_count_accounts_with_null_email(self, fritz, günther, hansi, capfd):
        Account.objects.all().update(email=None)

        call_command("diagnostics", only=["Account"])

        match = re.search(r'Found (\d+) accounts with email = None', capfd.readouterr()[0])

        assert match.group(1) == "3"

    def test_count_imported_accounts_no_positions(self, fritz, günther, hansi, capfd):
        hansi.imported = True
        hansi.units.clear()
        hansi.save()

        call_command("diagnostics", only=["Account"])

        match = re.search(
            r'Found (\d+) imported accounts without relation to an OrganizationalUnit.',
            capfd.readouterr()[0])

        assert match.group(1) == "1"

    # Aliases
    def test_count_aliases(
            self,
            fritz_email_alias,
            fritz_generic_alias,
            günther_email_alias,
            hansi_email_alias,
            capfd):
        call_command("diagnostics", only=["Alias"])

        match = re.search(r'Found a total of (\d+) aliases.', capfd.readouterr()[0])

        assert match.group(1) == "4"

    # Errors

    def test_count_errors(self, capfd, basic_scanstatus, test_org):
        for message in ["Message1", "Message2", "Message3"]:
            create_errors(
                num=10,
                error_message=message,
                scan_status=basic_scanstatus,
                organization=test_org)

        call_command("diagnostics", only=["UserErrorLog"])

        match = re.search(
            r'Found (\d+) different errors \((\d+) errors in total\).',
            capfd.readouterr()[0])

        assert match.group(1) == "3"
        assert match.group(2) == "30"

    def test_top_five_errors(self, capfd, basic_scanstatus, test_org):
        messages = [
            ("10", "Message1"),
            ("9", "Message2"),
            ("8", "Message3"),
            ("7", "Message4"),
            ("6", "Message5"),
            ("5", "Message6"),
        ]

        for num, message in messages:
            create_errors(
                num=int(num),
                error_message=message,
                scan_status=basic_scanstatus,
                organization=test_org)

        call_command("diagnostics", only=["UserErrorLog"])

        match = re.findall(r'\((\d+) counts\) (.*)\n', capfd.readouterr()[0])

        assert match == messages[:5]

    # Units

    def test_count_units(self, capfd, nisserne, familien_sand):
        call_command("diagnostics", only=["OrganizationalUnit"])

        match = re.search(r'Found (\d+) units.', capfd.readouterr()[0])

        assert match.group(1) == "2"

    # Organizations

    def test_count_organizations(self, capfd, test_org, test_org2):
        call_command("diagnostics", only=["Organization"])

        match = re.search(r'Found (\d+) organizations.', capfd.readouterr()[0])

        assert match.group(1) == "2"

    @pytest.mark.parametrize('org_name', [
        'os2datascanner_org',
        'osdatascanner_org'
    ])
    def test_os2datascanner_organization_warning(self, request, capfd, org_name):
        org = request.getfixturevalue(org_name)

        call_command("diagnostics", only=["Organization"])

        match = re.search(
            r'The organization with UUID ([\w-]+) is called \'(.+)\'. Should this be changed\?',
            capfd.readouterr()[0])

        assert match.group(1) == str(org.uuid)
        assert match.group(2) == org.name

    @pytest.mark.parametrize('label,setting,value,out', [
        ('Email', 'contact_email', 'hello@contact.com', 'hello@contact.com'),
        ('Phone', 'contact_phone', '+45 12 34 56 78', '+45 12 34 56 78'),
        ('Outlook delete email permission', 'outlook_delete_email_permission', True, 'True'),
        ('Outlook delete email permission', 'outlook_delete_email_permission', False, 'False'),
        ('Outlook categorize email permission', 'outlook_categorize_email_permission',
         OutlookCategorizeChoices.NONE.value,
         OutlookCategorizeChoices.NONE.label),
        ('Outlook categorize email permission', 'outlook_categorize_email_permission',
         OutlookCategorizeChoices.ORG_LEVEL.value,
         OutlookCategorizeChoices.ORG_LEVEL.label),
        ('Outlook categorize email permission', 'outlook_categorize_email_permission',
         OutlookCategorizeChoices.INDIVIDUAL_LEVEL.value,
         OutlookCategorizeChoices.INDIVIDUAL_LEVEL.label),
        ('OneDrive/SharePoint delete permission', 'onedrive_delete_permission', True, 'True'),
        ('OneDrive/SharePoint delete permission', 'onedrive_delete_permission', False, 'False'),
        ('Leadertab access', 'leadertab_access',
         StatisticsPageConfigChoices.MANAGERS.value,
         StatisticsPageConfigChoices.MANAGERS.label),
        ('Leadertab access', 'leadertab_access',
         StatisticsPageConfigChoices.DPOS.value,
         StatisticsPageConfigChoices.DPOS.label),
        ('Leadertab access', 'leadertab_access',
         StatisticsPageConfigChoices.SUPERUSERS.value,
         StatisticsPageConfigChoices.SUPERUSERS.label),
        ('Leadertab access', 'leadertab_access',
         StatisticsPageConfigChoices.NONE.value,
         StatisticsPageConfigChoices.NONE.label),
        ('DPO-tab access', 'dpotab_access',
         StatisticsPageConfigChoices.MANAGERS.value,
         StatisticsPageConfigChoices.MANAGERS.label),
        ('DPO-tab access', 'dpotab_access',
         StatisticsPageConfigChoices.DPOS.value,
         StatisticsPageConfigChoices.DPOS.label),
        ('DPO-tab access', 'dpotab_access',
         StatisticsPageConfigChoices.SUPERUSERS.value,
         StatisticsPageConfigChoices.SUPERUSERS.label),
        ('DPO-tab access', 'dpotab_access',
         StatisticsPageConfigChoices.NONE.value,
         StatisticsPageConfigChoices.NONE.label),
        ('Show Support Button', 'show_support_button', True, 'True'),
        ('Show Support Button', 'show_support_button', False, 'False'),
        ('Support Name', 'support_name', 'Mr. IT-guy', 'Mr. IT-guy'),
        ('Support Value', 'support_value', 'mr@it-guy.com', 'mr@it-guy.com'),
        ('DPO Contact Method', 'dpo_contact_method',
         DPOContactChoices.NONE.value, DPOContactChoices.NONE.label),
        ('DPO Contact Method', 'dpo_contact_method',
         DPOContactChoices.SINGLE_DPO.value, DPOContactChoices.SINGLE_DPO.label),
        ('DPO Contact Method', 'dpo_contact_method',
         DPOContactChoices.UNIT_DPO.value, DPOContactChoices.UNIT_DPO.label),
    ])
    def test_organization_overview(
            self,
            capfd,
            test_org,
            label,
            setting,
            value,
            out):
        setattr(test_org, setting, value)
        test_org.save()

        call_command("diagnostics", only=["Organization"])

        log = capfd.readouterr()[0]

        match = re.search(label + r': (.+)\n', log)

        assert match.group(1) == out

    @pytest.mark.parametrize('setting,value', [
        (SupportContactChoices.EMAIL, 'egon@olsenbanden.dk'),
        (SupportContactChoices.WEBSITE, 'https://olsenbanden.dk'),
        (SupportContactChoices.NONE, 'blablabla'),
    ])
    def test_support_contact_method_organization_overview(
            self, capfd, test_org, setting, value):
        test_org.support_contact_method = setting.value
        test_org.support_value = value
        test_org.save()

        call_command("diagnostics", only=["Organization"])

        log = capfd.readouterr()[0]

        match = re.search(r'Support Contact Method: (.+)\n', log)

        assert match.group(1) == setting.label

    # Rules

    def test_count_rules(self, capfd, basic_rule, org_rule):
        call_command("diagnostics", only=["Rule"])

        match = re.search(r'Found (\d+) custom rules:', capfd.readouterr()[0])

        # Remember the migration-created CPR rule
        assert match.group(1) == "3"

    # Maybe add a test for rule details ...

    # Settings

    @pytest.mark.parametrize('setting', [
        True, False
    ])
    def test_settings_debug(self, capfd, setting, temp_settings):
        temp_settings.DEBUG = setting

        call_command("diagnostics", only=["Settings"])

        match = re.search(r'WARNING: DEBUG is ON for this installation!', capfd.readouterr()[0])

        assert bool(match) == setting

    @pytest.mark.parametrize('setting,value', [
        ('EXCLUSION_RULES', True),
        ('EXCLUSION_RULES', False),
        ('ANALYSIS_PAGE', True),
        ('ANALYSIS_PAGE', False),
        ('AUTOMATIC_IMPORT_CLEANUP', True),
        ('AUTOMATIC_IMPORT_CLEANUP', False),
        ('MANUAL_PAGE', True),
        ('MANUAL_PAGE', False),
        ('USERERRORLOG', True),
        ('USERERRORLOG', False),
        # Scanners
        ('ENABLE_FILESCAN', True),
        ('ENABLE_FILESCAN', False),
        ('ENABLE_WEBSCAN', True),
        ('ENABLE_WEBSCAN', False),
        ('ENABLE_EXCHANGESCAN', True),
        ('ENABLE_EXCHANGESCAN', False),
        ('ENABLE_DROPBOXSCAN', True),
        ('ENABLE_DROPBOXSCAN', False),
        ('ENABLE_MSGRAPH_MAILSCAN', True),
        ('ENABLE_MSGRAPH_MAILSCAN', False),
        ('ENABLE_MSGRAPH_FILESCAN', True),
        ('ENABLE_MSGRAPH_FILESCAN', False),
        ('ENABLE_MSGRAPH_CALENDARSCAN', True),
        ('ENABLE_MSGRAPH_CALENDARSCAN', False),
        ('ENABLE_MSGRAPH_TEAMS_FILESCAN', True),
        ('ENABLE_MSGRAPH_TEAMS_FILESCAN', False),
        ('ENABLE_GOOGLEDRIVESCAN', True),
        ('ENABLE_GOOGLEDRIVESCAN', False),
        ('ENABLE_GMAILSCAN', True),
        ('ENABLE_GMAILSCAN', False),
        ('ENABLE_SBSYSSCAN', True),
        ('ENABLE_SBSYSSCAN', False),
        # Log level
        ('LOG_LEVEL', 'DEBUG'),
        ('LOG_LEVEL', 'INFO'),
        ('LOG_LEVEL', 'WARNING'),
        ('LOG_LEVEL', 'ERROR'),
        ('LOG_LEVEL', 'CRITICAL'),
        ('LOG_LEVEL', 'OFF'),
        # Other
        ('ENABLE_MINISCAN', True),
        ('ENABLE_MINISCAN', False),
        ('MINISCAN_REQUIRES_LOGIN', True),
        ('MINISCAN_REQUIRES_LOGIN', False),
        ('MINISCAN_FILE_SIZE_LIMIT', 12345),
        ('MINISCAN_FILE_SIZE_LIMIT', 0),
        ('MINISCAN_FILE_SIZE_LIMIT', 1048576)
    ])
    def test_settings_overview(self, capfd, setting, value, temp_settings):
        setattr(temp_settings, setting, value)

        call_command("diagnostics", only=["Settings"])

        match = re.search(setting + r' = (.+)\n', capfd.readouterr()[0])

        assert match.group(1).strip("'") == str(value)
