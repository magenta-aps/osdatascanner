import pytest
import re

from django.core.management import call_command
from django.conf import settings

from .test_utilities import create_reports_for
from ..organizations.models.account import Account
from ..organizations.models.account_outlook_setting import AccountOutlookSetting, OutlookCategory
from ..reportapp.models.documentreport import DocumentReport

from ....core_organizational_structure.models.organization import (
    StatisticsPageConfigChoices, SupportContactChoices,
    DPOContactChoices, OutlookCategorizeChoices)


@pytest.mark.django_db
class TestDiagnosticsReportCommand:

    def test_command_runs(self, capfd):
        # Arrange
        expected_diagnostics = [
            "accounts",
            "aliases",
            "reports",
            "units",
            "organizations",
            "problems",
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
        ('DocumentReport', 'reports'),
        ('OrganizationalUnit', 'units'),
        ('Organization', 'organizations'),
        ('Problem', 'problems'),
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
    def test_count_accounts(self, egon_account, benny_account, kjeld_account, capfd):
        call_command("diagnostics", only=["Account"])

        match = re.search(r'Found a total of (\d+) accounts.', capfd.readouterr()[0])

        assert match.group(1) == "3"

    def test_count_accounts_without_username(
            self, egon_account, benny_account, kjeld_account, capfd):
        Account.objects.all().update(username="")

        call_command("diagnostics", only=["Account"])

        match = re.search(r'Found (\d+) accounts without a username.', capfd.readouterr()[0])

        assert match.group(1) == "3"

    def test_count_accounts_without_email(self, egon_account, benny_account, kjeld_account, capfd):
        Account.objects.all().update(email="")

        call_command("diagnostics", only=["Account"])

        match = re.search(r'Found (\d+) accounts with email = \'\'', capfd.readouterr()[0])

        assert match.group(1) == "3"

    def test_count_accounts_with_null_email(
            self,
            egon_account,
            benny_account,
            kjeld_account,
            capfd):
        Account.objects.all().update(email=None)

        call_command("diagnostics", only=["Account"])

        match = re.search(r'Found (\d+) accounts with email = None', capfd.readouterr()[0])

        assert match.group(1) == "3"

    def test_count_accounts_without_users(self, egon_account, benny_account, kjeld_account, capfd):
        Account.objects.all().update(user=None)

        call_command("diagnostics", only=["Account"])

        match = re.search(r'Found (\d+) accounts without a user.', capfd.readouterr()[0])

        assert match.group(1) == "3"

    def test_count_accounts_with_duplicate_usernames(
            self, egon_account, benny_account, kjeld_account, capfd):

        Account.objects.all().update(username="generic_username")

        call_command("diagnostics", only=["Account"])

        match = re.search(
            r'Found (\d+) cases of duplicate usernames \(disregarding case\): (\w+) \((\d+)\)',
            capfd.readouterr()[0])

        assert match.group(1) == "1"
        assert match.group(2) == "generic_username"
        assert match.group(3) == "3"

    def test_count_accounts_missing_categories(
            self, egon_account, benny_account, kjeld_account, capfd):

        settings.MSGRAPH_ALLOW_WRITE = True

        # The accounts already do not have any categories.
        # Make one for Benny and two for Egon.
        AccountOutlookSetting.objects.bulk_create([
            AccountOutlookSetting(account=benny_account),
            AccountOutlookSetting(account=egon_account)
        ])

        OutlookCategory.objects.bulk_create([
            OutlookCategory(
                name=OutlookCategory.OutlookCategoryNames.MATCH,
                account_outlook_setting=AccountOutlookSetting.objects.get(
                    account=benny_account),
                category_name="OSdatascanner Match"
            ),
            OutlookCategory(
                name=OutlookCategory.OutlookCategoryNames.MATCH,
                account_outlook_setting=AccountOutlookSetting.objects.get(
                    account=egon_account),
                category_name="OSdatascanner Match"
            ),
            OutlookCategory(
                name=OutlookCategory.OutlookCategoryNames.FALSE_POSITIVE,
                account_outlook_setting=AccountOutlookSetting.objects.get(
                    account=egon_account),
                category_name="OSdatascanner False Positive"
            )
        ])

        call_command("diagnostics", only=["Account"])

        match = re.search(
            r'Found (\d+) accounts missing one or more Outlook categories',
            capfd.readouterr()[0])

        assert match.group(1) == "2"

    # Aliases
    def test_count_aliases(
            self,
            egon_email_alias,
            benny_email_alias,
            kjeld_email_alias,
            egon_sid_alias, capfd):
        call_command("diagnostics", only=["Alias"])

        match = re.search(r'Found a total of (\d+) aliases.', capfd.readouterr()[0])

        assert match.group(1) == "4"

    def test_count_aliases_with_no_account(
            self,
            egon_email_alias,
            benny_email_alias,
            kjeld_email_alias,
            egon_sid_alias, capfd):
        egon_email_alias.account = None
        egon_email_alias.save(prevent_mismatch=False)

        call_command("diagnostics", only=["Alias"])

        match = re.search(r'Found (\d+) aliases with no account.', capfd.readouterr()[0])

        assert match.group(1) == "1"

    def test_count_aliases_with_mismatched_account_user(
            self,
            egon_email_alias,
            benny_email_alias,
            kjeld_email_alias,
            egon_sid_alias,
            benny_account, capfd):
        egon_email_alias.user = benny_account.user
        egon_email_alias.save(prevent_mismatch=False)

        call_command("diagnostics", only=["Alias"])

        match = re.search(
            r'Found (\d+) aliases with mismatched accounts and users',
            capfd.readouterr()[0])

        assert match.group(1) == "1"

    # Problems
    @pytest.mark.parametrize('num1,num2', [
        (0, 1),
        (0, 10),
        (1, 0),
        (10, 0),
        (10, 10),
        (1, 10),
        (10, 1),
        (1, 1)
    ])
    def test_count_problems(self, egon_email_alias, num1, num2, capfd):
        create_reports_for(egon_email_alias, num=num1, problem=1)
        create_reports_for(egon_email_alias, num=num2, problem=2)

        call_command("diagnostics", only=["Problem"])

        match = re.search(
            r'Found (\d+) different problems \((\d+) problems in total\)',
            capfd.readouterr()[0])

        assert match.group(1) == str(bool(num1) + bool(num2))
        assert match.group(2) == str(num1 + num2)

    def test_problem_list(self, egon_email_alias, capfd):
        create_reports_for(egon_email_alias, num=21, problem=1)

        reports = DocumentReport.objects.all()

        for i, report in enumerate(reports):
            if i <= 6:
                report.raw_problem["message"] = "Most common message"
                report.save()
            elif i <= 11:
                report.raw_problem["message"] = "Second most common message"
                report.save()
            elif i <= 15:
                report.raw_problem["message"] = "Third most common message"
                report.save()
            elif i <= 18:
                report.raw_problem["message"] = "Fourth most common message"
                report.save()
            elif i <= 20:
                report.raw_problem["message"] = "Fifth most common message"
                report.save()
            else:
                report.raw_problem["message"] = "Least most common message"
                report.save()

        call_command("diagnostics", only=["Problem"])

        matches = re.findall(r'\((\d+) counts\) (.+)', capfd.readouterr()[0])

        assert matches == [
            ("7", "Most common message"),
            ("5", "Second most common message"),
            ("4", "Third most common message"),
            ("3", "Fourth most common message"),
            ("2", "Fifth most common message")
        ]

    # Reports
    def test_count_reports(self, egon_email_alias, capfd):
        create_reports_for(egon_email_alias, num=10, problem=1, matched=False)
        create_reports_for(egon_email_alias, num=5)
        create_reports_for(egon_email_alias, num=5, resolution_status=0)

        call_command("diagnostics", only=["DocumentReport"])

        match = re.search(
            r'Found (\d+) reports in total, (\d+) of which contain matches, '
            r'(\d+) of which are unhandled',
            capfd.readouterr()[0])

        assert match.group(1) == "20"
        assert match.group(2) == "10"
        assert match.group(3) == "5"

    def test_reports_resolution_status_figure(self, egon_email_alias, capfd):
        for status in DocumentReport.ResolutionChoices.choices:
            create_reports_for(egon_email_alias, num=5, resolution_status=status[0])

        call_command("diagnostics", only=["DocumentReport"])

        out = capfd.readouterr()[0]

        fp_match = re.search(r'Falsk positiv\s*\[\s*(\d+)\]', out)
        other_match = re.search(r'Andet\s*\[\s*(\d+)\]', out)
        edited_match = re.search(r'Redigeret\s*\[\s*(\d+)\]', out)
        jour_match = re.search(r'Slettet og journaliseret\s*\[\s*(\d+)\]', out)
        del_match = re.search(r'Slettet\s*\[\s*(\d+)\]', out)

        assert fp_match.group(1) == "5"
        assert other_match.group(1) == "5"
        assert edited_match.group(1) == "5"
        assert jour_match.group(1) == "5"
        assert del_match.group(1) == "5"

    def test_reports_scannerjob_figure(self, egon_email_alias, capfd):
        create_reports_for(
            egon_email_alias,
            num=5,
            scanner_job_pk=11,
            scanner_job_name="Scanner One")
        create_reports_for(
            egon_email_alias,
            num=8,
            scanner_job_pk=22,
            scanner_job_name="Scanner Two")
        create_reports_for(
            egon_email_alias,
            num=11,
            scanner_job_pk=33,
            scanner_job_name="Scanner Three")

        call_command("diagnostics", only=["DocumentReport"])

        out = capfd.readouterr()[0]

        matches = re.search(
            r'Matches come from the following scannerjobs:'
            r'\n(.+)\((\d+)\)\s*\[\s*(\d+)].*'
            r'\n(.+)\((\d+)\)\s*\[\s*(\d+)].*'
            r'\n(.+)\((\d+)\)\s*\[\s*(\d+)].*',
            out)

        assert matches.group(1) == "Scanner Three "
        assert matches.group(2) == "33"
        assert matches.group(3) == "11"

        assert matches.group(4) == "Scanner Two "
        assert matches.group(5) == "22"
        assert matches.group(6) == "8"

        assert matches.group(7) == "Scanner One "
        assert matches.group(8) == "11"
        assert matches.group(9) == "5"

    def test_count_reports_no_created_timestamp(self, egon_email_alias, capfd):
        create_reports_for(egon_email_alias, num=10)

        DocumentReport.objects.update(created_timestamp=None)

        call_command("diagnostics", only=["DocumentReport"])

        match = re.search(
            r'Found (\d+) reports without a \'created_timestamp\'.',
            capfd.readouterr()[0])

        assert match.group(1) == "10"

    def test_count_reports_no_resolution_time(self, egon_email_alias, capfd):
        create_reports_for(egon_email_alias, num=10, resolution_status=0)

        DocumentReport.objects.update(resolution_time=None)

        call_command("diagnostics", only=["DocumentReport"])

        match = re.search(
            r'Found (\d+) handled reports without a \'resolution_time\'.',
            capfd.readouterr()[0])

        assert match.group(1) == "10"

    def test_count_reports_no_both_timestamps(self, egon_email_alias, capfd):
        create_reports_for(egon_email_alias, num=10, resolution_status=0)

        DocumentReport.objects.update(created_timestamp=None, resolution_time=None)

        call_command("diagnostics", only=["DocumentReport"])

        match = re.search(
            r'Found (\d+) handled reports without both a \'created_timestamp\' '
            r'and a \'resolution_time\'.',
            capfd.readouterr()[0])

        assert match.group(1) == "10"

    def test_count_reports_impossible_timestamps(self, egon_email_alias, capfd):
        create_reports_for(egon_email_alias, num=10, resolution_status=0)

        DocumentReport.objects.update(
            created_timestamp="2024-08-15 13:58:00",
            resolution_time="2024-08-14 12:00:00")

        call_command("diagnostics", only=["DocumentReport"])

        match = re.search(
            r'Found (\d+) handled reports, where the \'resolution_time\' is '
            r'earlier than the \'created_timestamp\'.',
            capfd.readouterr()[0])

        assert match.group(1) == "10"

    def test_count_unrelated_reports(self, egon_email_alias, capfd):
        create_reports_for(egon_email_alias, num=10)

        for report in DocumentReport.objects.iterator():
            report.alias_relation.clear()

        call_command("diagnostics", only=["DocumentReport"])

        match = re.search(
            r'Found (\d+) matched reports without a relation to an alias.',
            capfd.readouterr()[0])

        assert match.group(1) == "10"

    def test_count_reports_top_five_accounts(
            self,
            capfd,
            bøffen_email_alias,
            egon_email_alias,
            benny_email_alias,
            kjeld_email_alias,
            yvonne_email_alias,
            børge_email_alias):
        create_reports_for(egon_email_alias, num=10)
        create_reports_for(benny_email_alias, num=8)
        create_reports_for(kjeld_email_alias, num=6)
        create_reports_for(yvonne_email_alias, num=4)
        create_reports_for(børge_email_alias, num=2)
        create_reports_for(bøffen_email_alias, num=1)  # Sixth -- should not be shown

        call_command("diagnostics", only=["DocumentReport"])

        match = re.findall(r'([\wæøå]+):\s*(\d+)\s*matched reports', capfd.readouterr()[0])

        assert match == [
            ("manden_med_planen", "10"),
            ("skide_godt", "8"),
            ("jensen123", "6"),
            ("yvonne", "4"),
            ("børge", "2")
        ]

    # Units
    def test_count_units(self, capfd, olsenbanden_ou, kjelds_hus, børges_værelse):
        call_command("diagnostics", only=["OrganizationalUnit"])

        match = re.search(r'Found (\d+) units.', capfd.readouterr()[0])

        assert match.group(1) == "3"

    # Organizations
    def test_count_organizations(self, capfd, olsenbanden_organization, marvel_organization):
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
        ('Onedrive delete permission', 'onedrive_delete_permission', True, 'True'),
        ('Onedrive delete permission', 'onedrive_delete_permission', False, 'False'),
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
            olsenbanden_organization,
            label,
            setting,
            value,
            out):
        setattr(olsenbanden_organization, setting, value)
        olsenbanden_organization.save()

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
            self, capfd, olsenbanden_organization, setting, value):
        olsenbanden_organization.support_contact_method = setting.value
        olsenbanden_organization.support_value = value
        olsenbanden_organization.save()

        call_command("diagnostics", only=["Organization"])

        log = capfd.readouterr()[0]

        match = re.search(r'Support Contact Method: (.+)\n', log)

        assert match.group(1) == setting.label

    # Settings
    @pytest.mark.parametrize('setting', [
        True, False
    ])
    def test_settings_debug(self, capfd, setting):
        settings.DEBUG = setting

        call_command("diagnostics", only=["Settings"])

        match = re.search(r'WARNING: DEBUG is ON for this installation!', capfd.readouterr()[0])

        assert bool(match) == setting

    @pytest.mark.parametrize('setting,value', [
        ('KEYCLOAK_ENABLED', True),
        ('KEYCLOAK_ENABLED', False),
        ('SAML2_ENABLED', True),
        ('SAML2_ENABLED', False),
        ('HANDLE_DROPDOWN', True),
        ('HANDLE_DROPDOWN', False),
        ('ALLOW_CONTACT_MAGENTA', True),
        ('ALLOW_CONTACT_MAGENTA', False),
        ('ARCHIVE_TAB', True),
        ('ARCHIVE_TAB', False),
        ('MSGRAPH_ALLOW_WRITE', True),
        ('MSGRAPH_ALLOW_WRITE', False),
        ('LOG_LEVEL', 'DEBUG'),
        ('LOG_LEVEL', 'INFO'),
        ('LOG_LEVEL', 'WARNING'),
        ('LOG_LEVEL', 'ERROR'),
        ('LOG_LEVEL', 'CRITICAL'),
        ('LOG_LEVEL', 'OFF'),
    ])
    def test_settings_overview(self, capfd, setting, value):
        setattr(settings, setting, value)

        call_command("diagnostics", only=["Settings"])

        match = re.search(setting + r' = (.+)\n', capfd.readouterr()[0])

        assert match.group(1).strip("'") == str(value)
