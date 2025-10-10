import pytest
import csv
from datetime import datetime, timedelta

from django.core.exceptions import PermissionDenied
from django.test import override_settings
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import Permission
from django.http import Http404

from os2datascanner.projects.report.organizations.models.organizational_unit import (
    OrganizationalUnit)
from os2datascanner.projects.report.organizations.models.account import Account
from os2datascanner.projects.report.tests.test_utilities import create_reports_for

from os2datascanner.projects.report.organizations.models.aliases import Alias, AliasType
from ..reportapp.models.documentreport import DocumentReport
from ..reportapp.models.scanner_reference import ScannerReference
from ..reportapp.utils import create_alias_and_match_relations
from ..reportapp.views.statistics_views import (
        UserStatisticsPageView, LeaderUnitsStatisticsPageView, LeaderUnitsStatisticsCSVView,
        DPOStatisticsPageView, DPOStatisticsCSVView, LeaderAccountsStatisticsCSVView,
        LeaderAccountsStatisticsPageView)
from ....core_organizational_structure.models.organization import LeaderTabConfigChoices


@pytest.fixture(autouse=True)
def override_dpo_csv_export_feature_flag():
    settings.DPO_CSV_EXPORT = True
    settings.LEADER_CSV_EXPORT = True


@pytest.mark.django_db
class TestUserStatisticsPageView:

    def test_own_userstatisticspage_without_privileges(self, egon_account, rf):
        """A User with an Account can see their personal statistics."""
        response = self.get_user_statisticspage_response(rf, egon_account)
        assert response.status_code == 200

    def test_other_userstatisticspage_without_privileges(self, egon_account, benny_account, rf):
        """A User with an Account can't see the statistics of an unrelated
        user."""
        with pytest.raises(PermissionDenied):
            self.get_user_statisticspage_response(rf, egon_account, pk=benny_account.pk)

    def test_double_relation_total_count(self, egon_account, egon_email_alias, egon_upn_alias, rf):
        # Arrange
        create_reports_for(egon_email_alias, num=10)
        # Create UPN alias relations too
        create_alias_and_match_relations(egon_upn_alias)
        # Act
        response = self.get_user_statisticspage_response(rf, egon_account)

        # Assert
        match_count = response.context_data.get("scannerjobs")[0].total
        assert match_count == 10

    def test_double_relation_week_count(self, egon_account, egon_email_alias, egon_upn_alias, rf):
        # Arrange
        create_reports_for(egon_email_alias, num=10)
        # Create UPN alias relations too
        create_alias_and_match_relations(egon_upn_alias)
        # Act
        response = self.get_user_statisticspage_response(rf, egon_account)

        # Assert
        match_count = response.context_data.get("matches_by_week")[0].get("matches")
        assert match_count == 10

    def test_reports_different_org(self, marvel_organization, egon_account, egon_email_alias, rf):
        # Arrange
        create_reports_for(egon_email_alias, num=10, scanner_job_pk=1)
        ScannerReference.objects.filter(scanner_pk=1).update(organization=marvel_organization)
        # Act
        response = self.get_user_statisticspage_response(rf, egon_account)

        # Assert
        match_count = response.context_data.get("matches_by_week")[0].get("matches")
        assert match_count == 0

    def test_scannerjobs(
            self,
            egon_account,
            egon_email_alias,
            scan_olsenbanden_org,
            scan_olsenbanden_org_withheld,
            scan_kun_egon,
            scan_kun_egon_withheld,
            scan_owned_by_olsenbanden,
            rf):

        create_reports_for(egon_email_alias, num=1,
                           scanner_job_name=scan_kun_egon.scanner_name,
                           scanner_job_pk=scan_kun_egon.pk)
        create_reports_for(egon_email_alias, num=1,
                           scanner_job_name=scan_olsenbanden_org.scanner_name,
                           scanner_job_pk=scan_olsenbanden_org.pk)
        create_reports_for(egon_email_alias, num=1,
                           scanner_job_name=scan_kun_egon_withheld.scanner_name,
                           scanner_job_pk=scan_kun_egon_withheld.pk,
                           only_notify_superadmin=scan_kun_egon_withheld.only_notify_superadmin
                           )
        create_reports_for(
            egon_email_alias,
            num=1,
            scanner_job_name=scan_olsenbanden_org_withheld.scanner_name,
            scanner_job_pk=scan_olsenbanden_org_withheld.pk,
            only_notify_superadmin=scan_olsenbanden_org_withheld.only_notify_superadmin)
        # Act

        # Act
        response = self.get_user_statisticspage_response(rf, egon_account)
        choices = list(response.context_data.get('scannerjobs'))

        # Assert
        assert len(choices) == 2
        assert scan_olsenbanden_org in choices
        assert scan_olsenbanden_org_withheld not in choices
        assert scan_kun_egon in choices
        assert scan_kun_egon_withheld not in choices
        assert scan_owned_by_olsenbanden not in choices

    def test_delete_without_permissions(self, rf, egon_account):
        # Arrange: Is just the egon_account fixture, no permissions.

        # Act / Assert
        with pytest.raises(PermissionDenied):
            self.post_delete_user_statisticspage_response(rf, egon_account, "", "")

    def test_delete_with_permissions(self, rf, egon_account, egon_email_alias):

        # Arrange
        scanner_pk = 1
        scanner_name = "Scan af Egon"

        create_reports_for(
            egon_email_alias, num=10,
            scanner_job_pk=scanner_pk, scanner_job_name=scanner_name
        )

        egon_account.user.user_permissions.add(Permission.objects.get(
            codename="delete_documentreport")
        )

        # Verify that we indeed have results
        assert egon_email_alias.reports.filter(
            scanner_job__scanner_pk=scanner_pk,
            scanner_job__scanner_name=scanner_name).count() == 10

        # Act
        response = self.post_delete_user_statisticspage_response(rf, egon_account,
                                                                 scanner_name, scanner_pk)

        # Assert
        assert response.status_code == 200
        assert egon_email_alias.reports.filter(
            scanner_job__scanner_pk=scanner_pk,
            scanner_job__scanner_name=scanner_name).count() == 0

    # Helper functions

    def get_user_statisticspage_response(self, rf, account, params='', **kwargs):
        request = rf.get('/statistics/view/' + params)
        request.user = account.user
        return UserStatisticsPageView.as_view()(request, **kwargs)

    def post_delete_user_statisticspage_response(self, rf, account,
                                                 scanner_name, scanner_pk, **kwargs):

        request = rf.post(
            f"/statistics/user/{account.pk}",
            {
                "pk": scanner_pk,
                "name": scanner_name
            }
        )
        request.user = account.user
        return UserStatisticsPageView.as_view()(request, pk=account.pk, **kwargs)


@pytest.mark.django_db
class TestLeaderAccountsStatisticsPageView:

    def test_leader_statisticspage_as_manager(self, rf, egon_account, benny_account):
        """A user who is a manager for another user should
        be able to access the leader overview page."""

        benny_account.manager = egon_account
        benny_account.save()

        egon_account.refresh_from_db()

        response = self.get_leader_statisticspage_response(rf, egon_account)

        assert response.status_code == 200

    def test_leader_statisticspage_as_superuser(self, superuser_account, rf):
        """A superuser should be able to access the leader overview page."""

        response = self.get_leader_statisticspage_response(rf, superuser_account)

        assert response.status_code == 200

    def test_leader_statisticspage_with_no_privileges(self, egon_account, rf):
        """A user with no privileges should not be able to access the leader
        overview page."""

        response = self.get_leader_statisticspage_response(rf, egon_account)

        assert response.status_code == 403

    def test_leader_export_as_manager(self, rf, egon_account, benny_account):
        """A user who is a manager for another user should
        be able to export leader data."""

        benny_account.manager = egon_account
        benny_account.save()

        egon_account.refresh_from_db()

        response = self.get_leader_statistics_csv_response(rf, egon_account)

        assert response.status_code == 200

    def test_leader_export_as_superuser(self, superuser_account, rf):
        """A superuser should be able to export leader data."""

        response = self.get_leader_statistics_csv_response(rf, superuser_account)

        assert response.status_code == 200

    def test_leader_export_with_no_privileges(self, egon_account, rf):
        """A user with no privileges should not be able to export leader data."""

        response = self.get_leader_statistics_csv_response(rf, egon_account)

        assert response.status_code == 403

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_old_matches_column_enabled(
            self,
            egon_account,
            benny_account,
            kjeld_account,
            olsenbanden_organization,
            rf):
        """When org.retention_policy is True, Old matches should appear as a column."""
        benny_account.manager = egon_account
        benny_account.save()
        kjeld_account.manager = egon_account
        kjeld_account.save()

        egon_account.refresh_from_db()

        olsenbanden_organization.retention_policy = True
        olsenbanden_organization.save()

        response = self.get_leader_statistics_csv_response(rf, egon_account)
        reader = csv.DictReader(line.decode() for line in response.streaming_content)

        retention_days = olsenbanden_organization.retention_days
        assert f"Results older than {retention_days} days" in reader.fieldnames

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_old_matches_column_disabled(
            self,
            egon_account,
            benny_account,
            kjeld_account,
            olsenbanden_organization,
            rf):
        """When org.retention_policy is False, Old matches should not appear as a column."""
        benny_account.manager = egon_account
        benny_account.save()
        kjeld_account.manager = egon_account
        kjeld_account.save()

        egon_account.refresh_from_db()

        olsenbanden_organization.retention_policy = False
        olsenbanden_organization.save()

        response = self.get_leader_statistics_csv_response(rf, egon_account)
        reader = csv.DictReader(line.decode() for line in response.streaming_content)

        retention_days = olsenbanden_organization.retention_days
        assert f"Results older than {retention_days} days" not in reader.fieldnames

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_status_bad(
            self,
            egon_account,
            kjeld_account,
            kjeld_email_alias,
            rf):
        """A user with status BAD, should have the string 'Not accepted' in their status column."""
        create_reports_for(kjeld_email_alias)
        kjeld_account.manager = egon_account
        kjeld_account.save()

        egon_account.refresh_from_db()

        response = self.get_leader_statistics_csv_response(rf, egon_account)
        rows = list(csv.DictReader(line.decode() for line in response.streaming_content))
        # Ignore everyone, but Kjeld
        rows = [row for row in rows if row['First name'] == "Kjeld"]

        assert len(rows) == 1
        assert rows[0]['Status'] == "Not accepted"

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_status_completed(
            self,
            egon_account,
            kjeld_account,
            rf):
        """A user with status GOOD, should have the string 'Completed' in their status column."""
        kjeld_account.manager = egon_account
        kjeld_account.save()

        egon_account.refresh_from_db()

        response = self.get_leader_statistics_csv_response(rf, egon_account)
        rows = list(csv.DictReader(line.decode() for line in response.streaming_content))
        # Ignore everyone, but Kjeld
        rows = [row for row in rows if row['First name'] == "Kjeld"]

        assert len(rows) == 1
        assert rows[0]['Status'] == "Completed"

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_without_withheld_matches_permission(
            self,
            egon_account,
            benny_account,
            rf):
        """When a user doesn't have the permission to see withheld results,
        Withheld matches shouldn't appear as a column."""
        benny_account.manager = egon_account
        benny_account.save()

        response = self.get_leader_statistics_csv_response(rf, egon_account)
        reader = csv.DictReader(line.decode() for line in response.streaming_content)

        assert "Withheld matches" not in reader.fieldnames

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_with_withheld_matches_permission(
            self,
            egon_account,
            benny_account,
            rf):
        """When a user does have the permission to see withheld results,
        Withheld matches should appear as a column."""
        benny_account.manager = egon_account
        benny_account.save()
        egon_account.user.user_permissions.add(Permission.objects.get(
            codename="see_withheld_documentreport"))

        response = self.get_leader_statistics_csv_response(rf, egon_account)
        reader = csv.DictReader(line.decode() for line in response.streaming_content)

        assert "Withheld matches" in reader.fieldnames

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_withheld_matches_superuser(
            self,
            superuser_account,
            rf):
        """When a superuser exports leader data, Withheld matches should appear as a column."""
        response = self.get_leader_statistics_csv_response(rf, superuser_account)
        reader = csv.DictReader(line.decode() for line in response.streaming_content)

        assert "Withheld matches" in reader.fieldnames

    def test_leader_accounts_page_scanner_choices(
                self,
                rf,
                egon_account,
                benny_account,
                benny_email_alias,
            ):
        # Arrange
        benny_account.manager = egon_account
        benny_account.save()
        create_reports_for(benny_email_alias, scanner_job_pk=1)
        create_reports_for(benny_email_alias, scanner_job_pk=2)

        # Act
        response = self.get_leader_statisticspage_response(rf, egon_account)
        choices = response.context_data['scannerjob_choices']

        # Assert
        assert choices.count() == 2
        assert choices.filter(scanner_pk=1).exists()
        assert choices.filter(scanner_pk=2).exists()

    def test_leader_accounts_page_scanner_choices_not_employee(
                self,
                rf,
                egon_account,
                benny_account,
                benny_email_alias,
                kjeld_email_alias,
            ):
        # Arrange
        benny_account.manager = egon_account
        benny_account.save()
        create_reports_for(benny_email_alias, scanner_job_pk=1)
        create_reports_for(kjeld_email_alias, scanner_job_pk=2)

        # Act
        response = self.get_leader_statisticspage_response(rf, egon_account)
        choices = response.context_data['scannerjob_choices']

        # Assert
        assert choices.count() == 1
        assert choices.filter(scanner_pk=1).exists()
        assert not choices.filter(scanner_pk=2).exists()

    def test_leader_accounts_page_scanner_choices_withheld(
                self,
                rf,
                egon_account,
                benny_account,
                benny_email_alias,
            ):
        # Arrange
        benny_account.manager = egon_account
        benny_account.save()
        create_reports_for(benny_email_alias, scanner_job_pk=1, only_notify_superadmin=False)
        create_reports_for(benny_email_alias, scanner_job_pk=2, only_notify_superadmin=True)

        # Act
        response = self.get_leader_statisticspage_response(rf, egon_account)
        choices = response.context_data['scannerjob_choices']

        # Assert
        assert choices.count() == 1
        assert choices.filter(scanner_pk=1).exists()
        assert not choices.filter(scanner_pk=2).exists()

    # Helper functions
    def get_leader_statisticspage_response(self, rf, account, params='', **kwargs):
        request = rf.get(reverse('statistics-leader-accounts') + params)
        request.user = account.user
        return LeaderAccountsStatisticsPageView.as_view()(request, **kwargs)

    def get_leader_statistics_csv_response(self, rf, account, params='', **kwargs):
        request = rf.get(reverse('statistics-leader-accounts-export') + params)
        request.user = account.user
        return LeaderAccountsStatisticsCSVView.as_view()(request, **kwargs)


@pytest.mark.django_db
class TestLeaderUnitsStatisticsPageView:

    def test_leader_statisticspage_as_manager(self, rf, egon_account, egon_manager_position):
        """A user with a 'manager'-position to an organizational unit should
        be able to access the leader overview page."""

        response = self.get_leader_statisticspage_response(rf, egon_account)

        assert response.status_code == 200

    def test_leader_statisticspage_as_superuser(self, superuser_account, rf):
        """A superuser should be able to access the leader overview page."""

        response = self.get_leader_statisticspage_response(rf, superuser_account)

        assert response.status_code == 200

    def test_leader_statisticspage_with_no_privileges(self, egon_account, rf):
        """A user with no privileges should not be able to access the leader
        overview page."""

        response = self.get_leader_statisticspage_response(rf, egon_account)

        assert response.status_code == 403

    def test_leader_statisticspage_view_all(self, rf, egon_account,
                                            olsenbanden_ou,
                                            egon_manager_position,
                                            olsenbanden_ou_positions,
                                            harrys_skur_positions_egon_lead_harry_employee):

        # Specific OU selection, should contain 3 employees.
        response = self.get_leader_statisticspage_response(rf, egon_account,
                                                           params=f"?org_unit={olsenbanden_ou.pk}")
        assert response.context_data.get("employee_count") == 3

        # view all, should be 4 employees.
        # olsenbanden OU + 1 employee in Harrys Skur.
        response = self.get_leader_statisticspage_response(rf, egon_account,
                                                           params="?view_all=on")
        assert response.context_data.get("employee_count") == 4

    def test_leader_statisticspage_scanner_filter(
                self,
                rf,
                superuser_account,
                børges_værelse,
                børges_værelse_ou_positions,
                børge_email_alias,
            ):
        # Arrange
        create_reports_for(børge_email_alias, num=3, scanner_job_pk=1)
        create_reports_for(børge_email_alias, num=4, scanner_job_pk=2)

        # Act
        response = self.get_leader_statisticspage_response(
            rf,
            superuser_account,
            params=f"?org_unit={børges_værelse.pk}&scannerjob=1",
        )
        børge = response.context_data['employees'].first()

        # Assert
        assert børge.unhandled_results == 3

    def test_leader_statisticspage_scanner_no_filter(
                self,
                rf,
                superuser_account,
                børges_værelse,
                børges_værelse_ou_positions,
                børge_email_alias,
            ):
        # Arrange
        create_reports_for(børge_email_alias, num=3, scanner_job_pk=1)
        create_reports_for(børge_email_alias, num=4, scanner_job_pk=2)

        # Act
        response = self.get_leader_statisticspage_response(
            rf,
            superuser_account,
            params=f"?org_unit={børges_værelse.pk}",
        )
        børge = response.context_data['employees'].first()

        # Assert
        assert børge.unhandled_results == 7

    def test_leader_statisticspage_scanner_filter_all(
                self,
                rf,
                superuser_account,
                børges_værelse,
                børges_værelse_ou_positions,
                børge_email_alias,
            ):
        # Arrange
        create_reports_for(børge_email_alias, num=3, scanner_job_pk=1)
        create_reports_for(børge_email_alias, num=4, scanner_job_pk=2)

        # Act
        response = self.get_leader_statisticspage_response(
            rf,
            superuser_account,
            params=f"?org_unit={børges_værelse.pk}&scannerjob=all",
        )
        børge = response.context_data['employees'].first()

        # Assert
        assert børge.unhandled_results == 7

    def test_leader_statisticspage_scanner_filter_404(
                self,
                rf,
                superuser_account,
                børges_værelse,
                børges_værelse_ou_positions,
                børge_email_alias,
            ):
        # Arrange
        create_reports_for(børge_email_alias, num=3, scanner_job_pk=1)
        create_reports_for(børge_email_alias, num=4, scanner_job_pk=2)

        # Act & Assert
        with pytest.raises(Http404):
            self.get_leader_statisticspage_response(
                rf,
                superuser_account,
                params=f"?org_unit={børges_værelse.pk}&scannerjob=3",
            )

    def test_leader_units_page_scanner_choices_match_connection(
                self,
                rf,
                superuser_account,
                børges_værelse,
                børges_værelse_ou_positions,
                børge_email_alias,
            ):
        # Arrange
        create_reports_for(børge_email_alias, scanner_job_pk=1)
        create_reports_for(børge_email_alias, scanner_job_pk=2)

        # Act
        response = self.get_leader_statisticspage_response(
            rf,
            superuser_account,
            params="?view_all=on",
        )
        choices = response.context_data['scannerjob_choices']

        # Assert
        assert choices.count() == 2
        assert choices.filter(scanner_pk=1).exists()
        assert choices.filter(scanner_pk=2).exists()

    def test_leader_units_page_scanner_choices_match_connection_not_employee(
                self,
                rf,
                superuser_account,
                børges_værelse,
                børges_værelse_ou_positions,
                børge_email_alias,
                egon_email_alias,
            ):
        # Arrange
        create_reports_for(børge_email_alias, scanner_job_pk=1)
        create_reports_for(egon_email_alias, scanner_job_pk=2)

        # Act
        response = self.get_leader_statisticspage_response(
            rf,
            superuser_account,
            params="?view_all=on",
        )
        choices = response.context_data['scannerjob_choices']

        # Assert
        assert choices.count() == 1
        assert choices.filter(scanner_pk=1).exists()
        assert not choices.filter(scanner_pk=2).exists()

    def test_leader_units_page_scanner_choices_org_unit_connection(
                self,
                rf,
                superuser_account,
                børges_værelse,
            ):
        # Arrange
        sr = ScannerReference.objects.create(
            scanner_pk=1,
            organization=børges_værelse.organization,
        )
        sr.org_units.add(børges_værelse)

        # Act
        response = self.get_leader_statisticspage_response(
            rf,
            superuser_account,
            params=f"?org_unit={børges_værelse.pk}",
        )
        choices = response.context_data['scannerjob_choices']

        # Assert
        assert choices.count() == 1

    def test_leader_units_page_scanner_choices_org_unit_connection_not_descendant(
                self,
                rf,
                superuser_account,
                børges_værelse,
                kun_egon_ou,
            ):
        # Arrange
        sr = ScannerReference.objects.create(
            scanner_pk=1,
            organization=kun_egon_ou.organization,
        )
        sr.org_units.add(kun_egon_ou)

        # Act
        response = self.get_leader_statisticspage_response(
            rf,
            superuser_account,
            params=f"?org_unit={børges_værelse.pk}",
        )
        choices = response.context_data['scannerjob_choices']

        # Assert
        assert choices.count() == 0

    def test_leader_units_page_scanner_choices_withheld(
                self,
                rf,
                egon_account,
                kun_egon_ou,
                egon_email_alias,
            ):
        # Arrange
        create_reports_for(egon_email_alias, scanner_job_pk=1, only_notify_superadmin=True)
        create_reports_for(egon_email_alias, scanner_job_pk=2, only_notify_superadmin=False)

        # Act
        response = self.get_leader_statisticspage_response(
            rf,
            egon_account,
            params="?view_all=on",
        )
        choices = response.context_data['scannerjob_choices']

        # Assert
        assert choices.count() == 1
        assert not choices.filter(scanner_pk=1).exists()
        assert choices.filter(scanner_pk=2).exists()

    def test_leader_export_as_manager(self, rf, egon_account, egon_manager_position):
        """A user with a 'manager'-position to an organizational unit should
        be able to export leader data."""

        response = self.get_leader_statistics_csv_response(rf, egon_account)

        assert response.status_code == 200

    def test_leader_export_as_superuser(self, superuser_account, rf):
        """A superuser should be able to export leader data."""

        response = self.get_leader_statistics_csv_response(rf, superuser_account)

        assert response.status_code == 200

    def test_leader_export_with_no_privileges(self, egon_account, rf):
        """A user with no privileges should not be able to export leader data."""

        response = self.get_leader_statistics_csv_response(rf, egon_account)

        assert response.status_code == 403

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    @pytest.mark.parametrize('egon_matches,benny_matches,kjeld_matches', [
        (0, 0, 0),
        (1, 0, 0),
        (0, 1, 1),
        (1, 1, 1),
        (0, 10, 10),
        (10, 0, 0),
        (10, 10, 10),
    ])
    def test_leader_csv_export(
            self,
            egon_account,
            benny_account,
            kjeld_account,
            egon_manager_position,
            egon_email_alias,
            benny_email_alias,
            kjeld_email_alias,
            olsenbanden_ou_positions,
            olsenbanden_ou,
            rf,
            egon_matches,
            benny_matches,
            kjeld_matches):
        """It should be possible to filter exported leader data based on orgunit."""

        create_reports_for(egon_email_alias, num=egon_matches)
        create_reports_for(benny_email_alias, num=benny_matches)
        create_reports_for(kjeld_email_alias, num=kjeld_matches)

        for acc in [egon_account, benny_account, kjeld_account]:
            acc.save()

        response = self.get_leader_statistics_csv_response(rf, egon_account)
        rows = sorted(csv.DictReader(line.decode() for line in response.streaming_content),
                      key=lambda row: row['First name'])

        assert len(rows) == 3
        benny_row, egon_row, kjeld_row = rows
        assert benny_row['First name'] == "Benny"
        assert int(benny_row['Matches']) == benny_matches
        assert egon_row['First name'] == "Egon"
        assert int(egon_row['Matches']) == egon_matches
        assert kjeld_row['First name'] == "Kjeld"
        assert int(kjeld_row['Matches']) == kjeld_matches

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_export_orgunit_filter(
            self,
            egon_account,
            benny_account,
            egon_manager_position,
            egon_email_alias,
            benny_email_alias,
            olsenbanden_ou_positions,
            olsenbanden_ou,
            kun_egon_ou,
            rf):
        """It should be possible to filter exported leader data based on orgunit."""

        create_reports_for(egon_email_alias)
        create_reports_for(benny_email_alias)

        for acc in [egon_account, benny_account]:
            acc.save()

        response = self.get_leader_statistics_csv_response(
            rf, egon_account, params=f"?org_unit={str(kun_egon_ou.uuid)}")
        rows = list(csv.DictReader(line.decode() for line in response.streaming_content))

        assert len(rows) == 1
        assert rows[0]['First name'] == "Egon"

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_export_orgunit_descendants(
            self,
            egon_account,
            kjeld_account,
            børge_account,
            egon_manager_position,
            egon_email_alias,
            kjeld_email_alias,
            børge_email_alias,
            olsenbanden_ou,
            olsenbanden_ou_positions,
            kjelds_hus_ou_positions,
            børges_værelse_ou_positions,
            rf):
        """When exporting data for a ou, it should include every descendant ou as well."""
        create_reports_for(egon_email_alias)
        create_reports_for(kjeld_email_alias)
        create_reports_for(børge_email_alias)

        for acc in [egon_account, kjeld_account, børge_account]:
            acc.save()

        response = self.get_leader_statistics_csv_response(
            rf, egon_account, params=f"?org_unit={str(olsenbanden_ou.uuid)}")
        rows = list(csv.DictReader(line.decode() for line in response.streaming_content))

        # We ignore Benny and Yvonne, since we haven't given them any matches
        names = {row['First name'] for row in rows if int(row['Matches']) > 0}
        assert {"Egon", "Kjeld", "Børge"} == names

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_orgunit_export(
            self,
            egon_account,
            egon_manager_position,
            kjeld_account,
            kjeld_email_alias,
            olsenbanden_ou,
            olsenbanden_ou_positions,
            kjelds_hus_ou_positions,
            rf):
        """When exporting data, every ou of the users should be included."""
        create_reports_for(kjeld_email_alias)
        kjeld_account.save()

        response = self.get_leader_statistics_csv_response(
            rf, egon_account, params=f"?org_unit={str(olsenbanden_ou.uuid)}")
        rows = list(csv.DictReader(line.decode() for line in response.streaming_content))
        # Ignore everyone, but Kjeld
        rows = [row for row in rows if row['First name'] == "Kjeld"]

        assert len(rows) == 1
        assert rows[0]['Organizational units'].count("Olsen-banden") == 1
        assert rows[0]['Organizational units'].count("Kjelds Hus") == 1

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_ignore_irrelevant_orgunits(
            self,
            kjeld_account,
            kjeld_manager_position,
            kjeld_email_alias,
            kjelds_hus,
            olsenbanden_ou_positions,
            kjelds_hus_ou_positions,
            rf):
        """When exporting data, only orgunits that are descendants of the chosen orgunit
        should be included in the orgunit-lists."""
        create_reports_for(kjeld_email_alias)
        kjeld_account.save()

        response = self.get_leader_statistics_csv_response(
            rf, kjeld_account, params=f"?org_unit={str(kjelds_hus.uuid)}")
        rows = list(csv.DictReader(line.decode() for line in response.streaming_content))
        # Ignore everyone, but Kjeld
        rows = [row for row in rows if row['First name'] == "Kjeld"]

        assert len(rows) == 1
        assert "Olsen-banden" not in rows[0]['Organizational units']
        assert "Kjelds Hus" in rows[0]['Organizational units']

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_old_matches_column_enabled(
            self,
            egon_account,
            egon_manager_position,
            olsenbanden_ou,
            olsenbanden_ou_positions,
            olsenbanden_organization,
            rf):
        """When org.retention_policy is True, Old matches should appear as a column."""
        olsenbanden_organization.retention_policy = True
        olsenbanden_organization.save()
        response = self.get_leader_statistics_csv_response(
            rf, egon_account, params=f"?org_unit={str(olsenbanden_ou.uuid)}")
        reader = csv.DictReader(line.decode() for line in response.streaming_content)

        retention_days = olsenbanden_organization.retention_days
        assert f"Results older than {retention_days} days" in reader.fieldnames

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_old_matches_column_disabled(
            self,
            egon_account,
            egon_manager_position,
            olsenbanden_ou,
            olsenbanden_ou_positions,
            olsenbanden_organization,
            rf):
        """When org.retention_policy is False, Old matches should appear as a column."""
        olsenbanden_organization.retention_policy = False
        olsenbanden_organization.save()
        response = self.get_leader_statistics_csv_response(
            rf, egon_account, params=f"?org_unit={str(olsenbanden_ou.uuid)}")
        reader = csv.DictReader(line.decode() for line in response.streaming_content)

        retention_days = olsenbanden_organization.retention_days
        assert f"Results older than {retention_days} days" not in reader.fieldnames

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_status_bad(
            self,
            egon_account,
            egon_manager_position,
            kjeld_account,
            kjeld_email_alias,
            olsenbanden_ou,
            olsenbanden_ou_positions,
            kjelds_hus_ou_positions,
            rf):
        """A user with status BAD, should have the string 'Completed' in their status column."""
        create_reports_for(kjeld_email_alias)
        kjeld_account.save()

        response = self.get_leader_statistics_csv_response(
            rf, egon_account, params=f"?org_unit={str(olsenbanden_ou.uuid)}")
        rows = list(csv.DictReader(line.decode() for line in response.streaming_content))
        # Ignore everyone, but Kjeld
        rows = [row for row in rows if row['First name'] == "Kjeld"]

        assert len(rows) == 1
        assert rows[0]['Status'] == "Not accepted"

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_status_completed(
            self,
            egon_account,
            egon_manager_position,
            kjeld_account,
            kjeld_email_alias,
            olsenbanden_ou,
            olsenbanden_ou_positions,
            kjelds_hus_ou_positions,
            rf):
        """A user with status GOOD, should have the string 'Completed' in their status column."""
        response = self.get_leader_statistics_csv_response(
            rf, egon_account, params=f"?org_unit={str(olsenbanden_ou.uuid)}")
        rows = list(csv.DictReader(line.decode() for line in response.streaming_content))
        # Ignore everyone, but Kjeld
        rows = [row for row in rows if row['First name'] == "Kjeld"]

        assert len(rows) == 1
        assert rows[0]['Status'] == "Completed"

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_without_withheld_matches_permission(
            self,
            egon_account,
            egon_manager_position,
            rf):
        """When a user doesn't have the permission to see withheld results,
        Withheld matches shouldn't appear as a column."""
        response = self.get_leader_statistics_csv_response(rf, egon_account)
        reader = csv.DictReader(line.decode() for line in response.streaming_content)

        assert "Withheld matches" not in reader.fieldnames

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_with_withheld_matches_permission(
            self,
            egon_account,
            egon_manager_position,
            rf):
        """When a user does have the permission to see withheld results,
        Withheld matches should appear as a column."""
        egon_account.user.user_permissions.add(Permission.objects.get(
            codename="see_withheld_documentreport"))

        response = self.get_leader_statistics_csv_response(rf, egon_account)
        reader = csv.DictReader(line.decode() for line in response.streaming_content)

        assert "Withheld matches" in reader.fieldnames

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_leader_csv_withheld_matches_superuser(
            self,
            superuser_account,
            rf):
        """When a superuser exports leader data, Withheld matches should appear as a column."""
        response = self.get_leader_statistics_csv_response(rf, superuser_account)
        reader = csv.DictReader(line.decode() for line in response.streaming_content)

        assert "Withheld matches" in reader.fieldnames

    def test_organization_tab_settings_units(self, client, superuser_account,
                                             olsenbanden_organization):
        """If only account-unit manager relations are enabled in the organization settings,
        only the /units-URL should be accessible."""
        olsenbanden_organization.leadertab_config = LeaderTabConfigChoices.UNITS
        olsenbanden_organization.save()

        client.force_login(superuser_account.user)
        unit_response = client.get(reverse("statistics-leader-units"))
        account_response = client.get(reverse("statistics-leader-accounts"))

        assert unit_response.status_code == 200
        assert account_response.status_code == 302

    # Helper functions

    def get_leader_statisticspage_response(self, rf, account, params='', **kwargs):
        request = rf.get(reverse('statistics-leader-units') + params)
        request.user = account.user
        return LeaderUnitsStatisticsPageView.as_view()(request, **kwargs)

    def get_leader_statistics_csv_response(self, rf, account, params='', **kwargs):
        request = rf.get(reverse('statistics-leader-units-export') + params)
        request.user = account.user
        return LeaderUnitsStatisticsCSVView.as_view()(request, **kwargs)


@pytest.mark.django_db
class TestDPOStatisticsPageView:

    def test_statisticspage_created_timestamp_as_dpo(self, egon_dpo_position, egon_email_alias):

        create_reports_for(egon_email_alias, num=1)

        view = self.get_dpo_statisticspage_object()
        matches = view.base_query()
        created_timestamp = matches[0].get('created_month')
        now = timezone.now().date()

        # If a document report has no created_timestamp it is assigned the date 1970/1/1.
        assert created_timestamp in {
            timezone.datetime(
                year=now.year,
                month=now.month,
                day=1).date(),
            timezone.datetime(
                1970,
                1,
                1).date()}

    @pytest.mark.parametrize('month_matches,test_date', [
        ((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), datetime(2020, 11, 28, 14, 21, 59)),
        ((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), datetime(2020, 11, 28, 14, 21, 59)),
        ((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1), datetime(2020, 11, 28, 14, 21, 59)),
        ((1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), datetime(2020, 11, 28, 14, 21, 59)),
        ((10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10), datetime(2020, 11, 28, 14, 21, 59)),
        ((10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), datetime(2020, 11, 28, 14, 21, 59)),
        ((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10), datetime(2020, 11, 28, 14, 21, 59)),
        ((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), datetime(2022, 5, 15, 12, 0, 0)),
        ((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), datetime(2022, 5, 15, 12, 0, 0)),
        ((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1), datetime(2022, 5, 15, 12, 0, 0)),
        ((1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), datetime(2022, 5, 15, 12, 0, 0)),
        ((10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10), datetime(2022, 5, 15, 12, 0, 0)),
        ((10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), datetime(2022, 5, 15, 12, 0, 0)),
        ((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10), datetime(2022, 5, 15, 12, 0, 0)),
        ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), datetime(2022, 1, 15, 12, 0, 0)),
        ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), datetime(2022, 2, 15, 12, 0, 0)),
        ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), datetime(2022, 3, 15, 12, 0, 0)),
        ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), datetime(2022, 4, 15, 12, 0, 0)),
        ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), datetime(2022, 6, 15, 12, 0, 0)),
        ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), datetime(2022, 7, 15, 12, 0, 0)),
        ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), datetime(2022, 8, 15, 12, 0, 0)),
        ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), datetime(2022, 9, 15, 12, 0, 0)),
        ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), datetime(2022, 10, 15, 12, 0, 0)),
        ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), datetime(2022, 12, 15, 12, 0, 0)),
    ])
    def test_statisticspage_count_new_matches_by_month_as_dpo(
            self, egon_dpo_position, egon_email_alias, month_matches, test_date):

        # Create fake reports
        for i, month in enumerate(month_matches):
            date = timezone.make_aware(test_date) - timedelta(days=(31*(11-i)))
            create_reports_for(egon_email_alias, num=month, created_at=date)

        view = self.get_dpo_statisticspage_object()

        matches = view.base_query()

        _, _, _, created_month, _ = view.make_data_structures(matches)

        new_matches_by_month = view.count_new_matches_by_month(matches, created_month,
                                                               current_date=test_date)

        if month_matches == (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0):
            assert len(new_matches_by_month) == 0
        else:
            assert len(month_matches) == len(new_matches_by_month)

        for month, matches in zip(month_matches, new_matches_by_month):
            assert month == matches[1]

    @pytest.mark.parametrize('month_unhandled', [
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
        (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10),
        (10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10),
    ])
    def test_statisticspage_count_unhandled_matches_by_month(
            self, egon_dpo_position, egon_email_alias, month_unhandled):

        test_date = timezone.make_aware(datetime(2021, 4, 28, 12, 0, 0))

        for i, month in enumerate(month_unhandled):
            date = test_date - timedelta(days=(31*(11-i)))
            if i == 0:
                create_reports_for(egon_email_alias, num=month, created_at=date)
            elif month > month_unhandled[i-1]:
                create_reports_for(egon_email_alias, num=month -
                                   month_unhandled[i-1], created_at=date)
            else:
                pks_to_update = DocumentReport.objects.filter(
                    resolution_status__isnull=True).values_list(
                    'pk', flat=True)[:month_unhandled[i-1]-month]
                DocumentReport.objects.filter(
                    pk__in=pks_to_update).update(
                    resolution_status=DocumentReport.ResolutionChoices.OTHER,
                    resolution_time=date)

        view = self.get_dpo_statisticspage_object()

        matches = view.base_query()

        _, _, _, created_month, resolved_month = view.make_data_structures(matches)

        unhandled_by_month = view.count_unhandled_matches_by_month(matches, created_month,
                                                                   resolved_month,
                                                                   current_date=test_date)

        if month_unhandled == (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0):
            assert len(unhandled_by_month) == 0
        else:
            assert len(month_unhandled) == len(unhandled_by_month)

        for month, unhandled in zip(month_unhandled, unhandled_by_month):
            assert month == unhandled[1]

    @pytest.mark.parametrize('scanner1_matches,scanner2_matches', [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
        (0, 10),
        (10, 0),
        (10, 10),
    ])
    def test_filter_by_scannerjob(
            self,
            rf,
            egon_dpo_position,
            egon_email_alias,
            egon_account,
            scanner1_matches,
            scanner2_matches):
        """Filtering by scannerjob should only return the reports associated
        with a specific scannerjob."""

        create_reports_for(egon_email_alias, num=scanner1_matches, scanner_job_pk=1)
        create_reports_for(egon_email_alias, num=scanner2_matches, scanner_job_pk=2)

        response1 = self.get_dpo_statisticspage_response(rf, egon_account, params='?scannerjob=1')
        response2 = self.get_dpo_statisticspage_response(rf, egon_account, params='?scannerjob=2')

        assert response1.context_data.get('chosen_scannerjob') == "1"
        assert response2.context_data.get('chosen_scannerjob') == "2"

        assert response1.context_data.get('match_data').get(
            'unhandled').get('count') == scanner1_matches
        assert response2.context_data.get('match_data').get(
            'unhandled').get('count') == scanner2_matches

    def test_double_relation_ou_filtering(self, rf, egon_account, egon_email_alias,
                                          egon_upn_alias, egon_dpo_position, olsenbanden_ou,
                                          olsenbanden_ou_positions):

        # Arrange
        # 5 handled, 5 unhandled
        create_reports_for(egon_email_alias, num=5)
        create_reports_for(egon_email_alias, num=5, resolution_status=0)
        create_alias_and_match_relations(egon_upn_alias)

        # Act
        response_ctx = self.get_dpo_statisticspage_response(
            rf, egon_account, params=f'?orgunit={str(olsenbanden_ou.uuid)}').context_data

        match_unhandled_count = response_ctx.get("match_data").get("unhandled").get("count")
        match_handled_count = response_ctx.get("match_data").get("handled").get("count")
        resolution_status_count = response_ctx.get("resolution_status").get(0).get("count")
        unhandled_by_month = response_ctx.get("unhandled_matches_by_month")
        new_matches_by_month = response_ctx.get("new_matches_by_month")
        other_monthly_progress = response_ctx.get("other_monthly_progress")
        unhandled_by_source_count = response_ctx.get("unhandled_by_source").get(
            "other").get("count")
        total_by_source_count = response_ctx.get("total_by_source").get("other").get("count")

        assert match_unhandled_count == 5
        assert match_handled_count == 5
        assert resolution_status_count == 5
        assert other_monthly_progress == 10
        assert unhandled_by_source_count == 5
        assert total_by_source_count == 10
        # This one is dynamic / depends on month, there should just be 5 _somewhere_
        assert any(value == 5 for _, value in unhandled_by_month)
        # Same as above, but 10. (5 handled 5 unhandled, but still "new")
        assert any(value == 10 for _, value in new_matches_by_month)

    def test_personal_and_shared_alias(self, rf, egon_account, egon_email_alias, egon_upn_alias,
                                       egon_dpo_position, benny_account, olsenbanden_ou,
                                       olsenbanden_ou_positions):
        """ It can occur that somebody has a shared alias with a value of someone
        else's non-shared alias. In that case, one report should still only count as one -
         and of course, be counted as the personal one. """

        # Arrange
        # 5 handled, 5 unhandled
        create_reports_for(egon_email_alias, num=5)
        create_reports_for(egon_email_alias, num=5, resolution_status=0)

        # Create a shared alias for benny, with the value of egon's.
        benny_shared_alias = Alias.objects.create(account=benny_account,
                                                  user=benny_account.user,
                                                  _alias_type=AliasType.EMAIL,
                                                  _value=egon_email_alias.value,
                                                  shared=True)
        # Create relations
        create_alias_and_match_relations(egon_upn_alias)
        create_alias_and_match_relations(benny_shared_alias)

        # Act
        response_ctx = self.get_dpo_statisticspage_response(
            rf, egon_account, params=f'?orgunit={str(olsenbanden_ou.uuid)}').context_data

        match_unhandled_count = response_ctx.get("match_data").get("unhandled").get("count")
        match_handled_count = response_ctx.get("match_data").get("handled").get("count")
        resolution_status_count = response_ctx.get("resolution_status").get(0).get("count")
        unhandled_by_month = response_ctx.get("unhandled_matches_by_month")
        new_matches_by_month = response_ctx.get("new_matches_by_month")
        other_monthly_progress = response_ctx.get("other_monthly_progress")
        unhandled_by_source_count = response_ctx.get("unhandled_by_source").get(
            "other").get("count")
        total_by_source_count = response_ctx.get("total_by_source").get("other").get("count")

        assert match_unhandled_count == 5
        assert match_handled_count == 5
        assert resolution_status_count == 5
        assert other_monthly_progress == 10
        assert unhandled_by_source_count == 5
        assert total_by_source_count == 10
        # This one is dynamic / depends on month, there should just be 5 _somewhere_
        assert any(value == 5 for _, value in unhandled_by_month)
        # Same as above, but 10. (5 handled 5 unhandled, but still "new")
        assert any(value == 10 for _, value in new_matches_by_month)

    def test_only_shared_alias(self, rf, egon_account, egon_dpo_position,
                               olsenbanden_ou, olsenbanden_ou_positions):
        """ Shared results shouldn't count, if the account that has the 'non-shared'
        one isn't included in the queryset. """

        # Arrange

        # Create a shared alias for egon, with the value of egon's.
        egon_shared_alias = Alias.objects.create(account=egon_account,
                                                 user=egon_account.user,
                                                 _alias_type=AliasType.EMAIL,
                                                 _value="sharedmail@vstkom.com",
                                                 shared=True)

        # 5 handled, 5 unhandled
        create_reports_for(egon_shared_alias, num=5)
        create_reports_for(egon_shared_alias, num=5, resolution_status=0)

        # Create relations
        create_alias_and_match_relations(egon_shared_alias)

        # Act
        response_ctx = self.get_dpo_statisticspage_response(
            rf, egon_account, params=f'?orgunit={str(olsenbanden_ou.uuid)}').context_data

        match_unhandled_count = response_ctx.get("match_data").get("unhandled").get("count")
        match_handled_count = response_ctx.get("match_data").get("handled").get("count")
        resolution_status_count = response_ctx.get("resolution_status").get(0).get("count")
        unhandled_by_month = response_ctx.get("unhandled_matches_by_month")
        new_matches_by_month = response_ctx.get("new_matches_by_month")
        other_monthly_progress = response_ctx.get("other_monthly_progress")
        unhandled_by_source_count = response_ctx.get("unhandled_by_source").get(
            "other").get("count")
        total_by_source_count = response_ctx.get("total_by_source").get("other").get("count")

        assert match_unhandled_count == 0
        assert match_handled_count == 0
        assert resolution_status_count == 0
        assert other_monthly_progress == 0
        assert unhandled_by_source_count == 0
        assert total_by_source_count == 0
        assert all(value == 0 for _, value in unhandled_by_month)
        assert all(value == 0 for _, value in new_matches_by_month)

    @pytest.mark.parametrize('egon_matches,benny_matches,kjeld_matches', [
        (0, 0, 0),
        (1, 0, 0),
        (0, 1, 1),
        (1, 1, 1),
        (0, 10, 10),
        (10, 0, 0),
        (10, 10, 10),
    ])
    def test_filter_by_orgunit(
            self,
            rf,
            egon_account,
            egon_dpo_position,
            egon_email_alias,
            benny_email_alias,
            kjeld_email_alias,
            olsenbanden_organization,
            olsenbanden_ou,
            olsenbanden_ou_positions,
            kun_egon_ou,
            egon_matches,
            benny_matches,
            kjeld_matches):
        """Filtering by organizational units should only return results from
        users with employee positions in that unit."""

        create_reports_for(egon_email_alias, num=egon_matches)
        create_reports_for(benny_email_alias, num=benny_matches)
        create_reports_for(kjeld_email_alias, num=kjeld_matches)

        response_ob = self.get_dpo_statisticspage_response(
            rf, egon_account, params=f'?orgunit={str(olsenbanden_ou.uuid)}')
        response_ke = self.get_dpo_statisticspage_response(
            rf, egon_account, params=f'?orgunit={str(kun_egon_ou.uuid)}')

        assert response_ob.context_data.get('chosen_orgunit') == str(olsenbanden_ou.uuid)
        assert response_ke.context_data.get('chosen_orgunit') == str(kun_egon_ou.uuid)

        assert response_ob.context_data.get('match_data').get('unhandled').get(
            'count') == egon_matches + benny_matches + kjeld_matches
        assert response_ke.context_data.get('match_data').get(
            'unhandled').get('count') == egon_matches

    @pytest.mark.parametrize('egon_matches', [0, 1, 10])
    def test_filter_by_orgunit_with_multiple_positions(
            self, egon_account, rf, kun_egon_ou, egon_email_alias, egon_matches):
        """If an account is related to a ou through multiple positions, their
        results should only appear in the DPO overview once."""

        # Arrange
        create_reports_for(egon_email_alias, num=egon_matches)

        # Act
        response_ob = self.get_dpo_statisticspage_response(
              rf, egon_account, params=f'?orgunit={str(kun_egon_ou.uuid)}')

        # Assert
        assert response_ob.context_data.get('match_data').get(
            'unhandled').get('count') == egon_matches

    @pytest.mark.parametrize('børge_matches,kjeld_matches', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (0, 10),
        (10, 0),
        (10, 10),
    ])
    def test_filter_descendant_orgunits(
            self,
            børges_værelse_ou_positions,
            rf,
            olsenbanden_ou,
            olsenbanden_ou_positions,
            børge_matches,
            kjeld_matches,
            børge_email_alias,
            kjeld_email_alias,
            superuser_account):
        """When filtering for an orgunit, we should see results from that unit
        and all its descendants."""

        # Arrange
        create_reports_for(børge_email_alias, num=børge_matches)
        create_reports_for(kjeld_email_alias, num=kjeld_matches)

        # Act
        response = self.get_dpo_statisticspage_response(
            rf, superuser_account, params=f'?orgunit={str(olsenbanden_ou.uuid)}')

        # Assert
        assert response.context_data.get('match_data').get(
            'unhandled').get('count') == børge_matches + kjeld_matches

    @pytest.mark.parametrize('kjeld_matches, yvonne_matches', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (0, 10),
        (10, 0),
        (10, 10),
    ])
    def test_filter_descendant_orgunits_with_multiple_positions(
            self,
            rf,
            kjeld_email_alias,
            yvonne_email_alias,
            olsenbanden_ou_positions,
            kjelds_hus_ou_positions,
            olsenbanden_ou,
            kjeld_matches,
            yvonne_matches,
            superuser_account):
        """When an account is related to an OU and that OU's child OU, their
        results should only be counted once."""

        # Arrange
        create_reports_for(kjeld_email_alias, num=kjeld_matches)
        create_reports_for(yvonne_email_alias, num=yvonne_matches)

        # Act
        response = self.get_dpo_statisticspage_response(
            rf, superuser_account, params=f'?orgunit={str(olsenbanden_ou.uuid)}')

        # Assert
        assert response.context_data.get('match_data').get(
            'unhandled').get('count') == kjeld_matches + yvonne_matches

    @pytest.mark.parametrize('egon_matches,hulk_matches', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (0, 10),
        (10, 0),
        (10, 10),
    ])
    def test_access_from_different_organization(
            self,
            egon_account,
            egon_dpo_position,
            egon_email_alias,
            hulk_email_alias,
            rf,
            egon_matches,
            hulk_matches):
        """A user should only be able to see results from their own organization."""

        create_reports_for(egon_email_alias, num=egon_matches, scanner_job_pk=1)
        create_reports_for(hulk_email_alias, num=hulk_matches, scanner_job_pk=2)

        response = self.get_dpo_statisticspage_response(rf, egon_account)

        assert response.context_data.get('match_data').get('unhandled').get('count') == egon_matches

    @pytest.mark.parametrize('account_name,expected_count', [
        ('admin', 3),
        ('manden_med_planen', 2),
        ('the_hulk', 1),
    ])
    def test_scannerjob_choices(
                self,
                rf,
                account_name,
                expected_count,
                superuser_account,
                egon_account,
                egon_dpo_position,
                hulk_account,
                hulk_dpo_position,
                olsenbanden_organization,
                marvel_organization,
                scan_marvel,
                scan_olsenbanden_org,
                scan_kun_egon
            ):
        """The available scannerjob choices should be those owned by your organization,
        except if you are a superuser, in which case every scanner should be available."""
        # Arrange
        account = Account.objects.get(username=account_name)

        # Act
        response = self.get_dpo_statisticspage_response(rf, account)
        scanner_choices = list(response.context_data.get('scannerjob_choices'))

        # Assert
        assert len(scanner_choices) == expected_count

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    @pytest.mark.parametrize('egon_matches,benny_matches,kjeld_matches', [
        (0, 0, 0),
        (1, 0, 0),
        (0, 1, 1),
        (1, 1, 1),
        (0, 10, 10),
        (10, 0, 0),
        (10, 10, 10),
    ])
    def test_dpo_with_access_to_csv_export(
            self,
            egon_account,
            egon_dpo_position,
            egon_email_alias,
            benny_email_alias,
            kjeld_email_alias,
            olsenbanden_ou_positions,
            olsenbanden_ou,
            rf,
            egon_matches,
            benny_matches,
            kjeld_matches):
        """A dpo should be able to export data from their own orgunit."""

        create_reports_for(egon_email_alias, num=egon_matches)
        create_reports_for(benny_email_alias, num=benny_matches)
        create_reports_for(kjeld_email_alias, num=kjeld_matches)

        response = self.get_dpo_statistics_csv_response(
            rf, egon_account, params=f'?orgunit={str(olsenbanden_ou.uuid)}')
        Headers, _line1, line2, *_ = response.streaming_content

        assert f"unhandled,{egon_matches+benny_matches+kjeld_matches}" in str(line2)

    def test_dpo_without_access_to_csv_export(
            self, kun_egon_ou, benny_dpo_position, benny_account, rf):
        """A dpo shouldn't be able to export data from another orgunit."""

        with pytest.raises(OrganizationalUnit.DoesNotExist):
            self.get_dpo_statistics_csv_response(
                rf, benny_account, params=f'?orgunit={str(kun_egon_ou.uuid)}')

    def test_csv_export_without_privileges(self, egon_account, rf):
        """A user with no privileges should not be able to export dpo data,
        and should instead be redirected to main page."""

        response = self.get_dpo_statistics_csv_response(rf, egon_account)

        assert response.status_code == 302

    @override_settings(DPO_CSV_EXPORT=False)
    def test_csv_export_feature_flag(self, egon_account, rf):
        """When the feature flag DPO_CSV_EXPORT is off,
        a user should be met with PermissionDenied."""

        with pytest.raises(PermissionDenied):
            self.get_dpo_statistics_csv_response(rf, egon_account)

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    @pytest.mark.parametrize('scanner1_matches,scanner2_matches', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (0, 10),
        (10, 0),
        (10, 10),
    ])
    def test_csv_export_single_scannerjob(
            self,
            egon_account,
            rf,
            egon_dpo_position,
            egon_email_alias,
            scanner1_matches,
            scanner2_matches):
        """Exporting data from a single scannerjob, should only yield data from that scannerjob."""

        create_reports_for(egon_email_alias, num=scanner1_matches, scanner_job_pk=1)
        create_reports_for(egon_email_alias, num=scanner2_matches, scanner_job_pk=2)

        response = self.get_dpo_statistics_csv_response(rf, egon_account, params='?scannerjob=1')
        Headers, _line1, line2, *_ = response.streaming_content

        assert f"unhandled,{scanner1_matches}" in str(line2)

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    @pytest.mark.parametrize('egon_matches,benny_matches,kjeld_matches', [
        (0, 0, 0),
        (1, 0, 0),
        (0, 1, 1),
        (1, 1, 1),
        (0, 10, 10),
        (10, 0, 0),
        (10, 10, 10),
    ])
    def test_csv_export_scannerjob_and_orgunit_filter(
            self,
            egon_account,
            egon_dpo_position,
            egon_email_alias,
            benny_email_alias,
            kjeld_email_alias,
            olsenbanden_ou_positions,
            olsenbanden_ou,
            kun_egon_ou,
            rf,
            egon_matches,
            benny_matches,
            kjeld_matches):
        """Exporting data from an orgunit and scannerjob, should only contain relevant data."""

        create_reports_for(egon_email_alias, num=egon_matches, scanner_job_pk=1)
        create_reports_for(benny_email_alias, num=benny_matches, scanner_job_pk=1)
        create_reports_for(kjeld_email_alias, num=kjeld_matches, scanner_job_pk=1)
        create_reports_for(egon_email_alias, num=egon_matches, scanner_job_pk=2)
        create_reports_for(benny_email_alias, num=benny_matches, scanner_job_pk=2)
        create_reports_for(kjeld_email_alias, num=kjeld_matches, scanner_job_pk=2)

        response = self.get_dpo_statistics_csv_response(
            rf, egon_account, params=f"?scannerjob=1&orgunit={str(kun_egon_ou.uuid)}")
        Headers, _line1, line2, *_ = response.streaming_content

        assert f'unhandled,{egon_matches}' in str(line2)

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    @pytest.mark.parametrize('egon_matches,benny_matches,kjeld_matches', [
        (0, 0, 0),
        (1, 0, 0),
        (0, 1, 1),
        (1, 1, 1),
        (0, 10, 10),
        (10, 0, 0),
        (10, 10, 10),
    ])
    def test_superuser_export_entire_organization(
            self,
            rf,
            superuser_account,
            olsenbanden_ou_positions,
            egon_email_alias,
            benny_email_alias,
            kjeld_email_alias,
            egon_matches,
            benny_matches,
            kjeld_matches):
        """A superuser should be able to export data for their entire organization."""

        create_reports_for(egon_email_alias, num=egon_matches)
        create_reports_for(benny_email_alias, num=benny_matches)
        create_reports_for(kjeld_email_alias, num=kjeld_matches)

        explicit = self.get_dpo_statistics_csv_response(
            rf, superuser_account, params="?orgunit=all")
        implicit = self.get_dpo_statistics_csv_response(rf, superuser_account)

        Headers, _line1, line2_ex, *_ = explicit.streaming_content
        Headers, _line1, line2_im, *_ = implicit.streaming_content

        assert f'unhandled,{egon_matches+benny_matches+kjeld_matches}' in str(line2_ex)
        assert f'unhandled,{egon_matches+benny_matches+kjeld_matches}' in str(line2_im)

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    @pytest.mark.parametrize('egon_matches,benny_matches,kjeld_matches', [
        (0, 0, 0),
        (1, 0, 0),
        (0, 1, 1),
        (1, 1, 1),
        (0, 10, 10),
        (10, 0, 0),
        (10, 10, 10),
    ])
    def test_dpo_export_entire_organization(
            self,
            rf,
            egon_account,
            egon_dpo_position,
            egon_email_alias,
            benny_email_alias,
            kjeld_email_alias,
            egon_matches,
            benny_matches,
            kjeld_matches):
        """A dpo should be able to export data for their entire organization."""

        create_reports_for(egon_email_alias, num=egon_matches)
        create_reports_for(benny_email_alias, num=benny_matches)
        create_reports_for(kjeld_email_alias, num=kjeld_matches)

        explicit = self.get_dpo_statistics_csv_response(rf, egon_account, params="?orgunit=all")
        implicit = self.get_dpo_statistics_csv_response(rf, egon_account)

        Headers, _line1, line2_ex, *_ = explicit.streaming_content
        Headers, _line1, line2_im, *_ = implicit.streaming_content

        assert f'unhandled,{egon_matches+benny_matches+kjeld_matches}' in str(line2_ex)
        assert f'unhandled,{egon_matches+benny_matches+kjeld_matches}' in str(line2_im)

    def test_statisticspage_without_created_timestamp(
            self, rf, egon_dpo_position, egon_account, egon_email_alias):
        """The DPO page should still be accessible when document reports
           have no created_timestamp."""

        create_reports_for(egon_email_alias, num=1, created_at=None)

        response = self.get_dpo_statisticspage_response(rf, egon_account)

        assert response.status_code == 200

    def test_statisticspage_all_matches_older_than_a_year(
            self, rf, egon_account, egon_dpo_position, egon_email_alias):
        """When the created timestamp for all matches are older than a year,
           the DPO page should still be accessible."""

        more_than_a_year = timezone.datetime.now() - timedelta(days=367)
        create_reports_for(egon_email_alias, num=10, created_at=more_than_a_year)

        response = self.get_dpo_statisticspage_response(rf, egon_account)

        assert response.status_code == 200

    def test_progress_resolution_time_no_resolution_status(
            self, rf, egon_email_alias, egon_account, egon_dpo_position):
        """When calculating the progress, only reports with a resolution status should be
        counted as handled. Having a recent resolution time isn't enough."""

        # Arrange

        now = timezone.datetime.now()
        # 5 handled, 4 unhandled
        create_reports_for(egon_email_alias, num=4, created_at=now)
        create_reports_for(egon_email_alias, num=5, created_at=now, resolution_status=0)
        # Give all the reports a resolution time within the last 30 days.
        DocumentReport.objects.all().update(resolution_time=now)

        # Act
        response_ctx = self.get_dpo_statisticspage_response(rf, egon_account).context_data

        # Assert
        assert response_ctx['unhandled_by_source']['other']['count'] == 4
        assert response_ctx['total_by_source']['other']['count'] == 9
        assert response_ctx['other_monthly_progress'] == 4

    # StatisticsPageView()
    def get_dpo_statisticspage_object(self):
        # XXX: we don't use request for anything! Is this deliberate?
        # request = self.factory.get('/statistics')
        # request.user = self.kjeld
        view = DPOStatisticsPageView()
        return view

    def get_dpo_statisticspage_response(self, rf, account, params='', **kwargs):
        request = rf.get(reverse('statistics-dpo') + params)
        request.user = account.user
        return DPOStatisticsPageView.as_view()(request, **kwargs)

    def get_dpo_statistics_csv_response(self, rf, account, params='', **kwargs):
        request = rf.get(reverse('statistics-dpo-export') + params)
        request.user = account.user
        return DPOStatisticsCSVView.as_view()(request, **kwargs)
