import pytest
from datetime import datetime, timedelta

from django.core.exceptions import PermissionDenied
from django.test import override_settings
from django.utils import timezone
from django.urls import reverse
from django.conf import settings

from os2datascanner.projects.report.organizations.models.organizational_unit import (
    OrganizationalUnit)
from os2datascanner.projects.report.tests.test_utilities import create_reports_for

from ..reportapp.models.documentreport import DocumentReport
from ..reportapp.views.statistics_views import (
        UserStatisticsPageView, LeaderStatisticsPageView,
        DPOStatisticsPageView, DPOStatisticsCSVView)


@pytest.fixture(autouse=True)
def override_dpo_csv_export_feature_flag():
    settings.DPO_CSV_EXPORT = True


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

    # Helper functions

    def get_user_statisticspage_response(self, rf, account, params='', **kwargs):
        request = rf.get('/statistics/view/' + params)
        request.user = account.user
        return UserStatisticsPageView.as_view()(request, **kwargs)


@pytest.mark.django_db
class TestLeaderStatisticsPageView:

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

    # Helper functions

    def get_leader_statisticspage_response(self, rf, account, params='', **kwargs):
        request = rf.get(reverse('statistics-leader') + params)
        request.user = account.user
        return LeaderStatisticsPageView.as_view()(request, **kwargs)


@pytest.mark.django_db
class TestDPOStatisticsPageView:

    def test_statisticspage_created_timestamp_as_dpo(self, egon_dpo_position, egon_email_alias):

        create_reports_for(egon_email_alias, num=1)

        view = self.get_dpo_statisticspage_object()
        created_timestamp = view.matches[0].get('created_month')
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

        _, _, _, view.created_month, view.resolved_month = view.make_data_structures(view.matches)

        new_matches_by_month = view.count_new_matches_by_month(test_date)

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

        _, _, _, view.created_month, view.resolved_month = view.make_data_structures(view.matches)

        unhandled_by_month = view.count_unhandled_matches_by_month(test_date)

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

        assert response1.context_data.get('scannerjobs')[-1] == "1"
        assert response2.context_data.get('scannerjobs')[-1] == "2"

        assert response1.context_data.get('match_data').get(
            'unhandled').get('count') == scanner1_matches
        assert response2.context_data.get('match_data').get(
            'unhandled').get('count') == scanner2_matches

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

        assert response_ob.context_data.get('orgunits')[-1] == str(olsenbanden_ou.uuid)
        assert response_ke.context_data.get('orgunits')[-1] == str(kun_egon_ou.uuid)

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

        create_reports_for(egon_email_alias, num=egon_matches)
        create_reports_for(hulk_email_alias, num=hulk_matches)

        response = self.get_dpo_statisticspage_response(rf, egon_account)

        assert response.context_data.get('match_data').get('unhandled').get('count') == egon_matches

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
