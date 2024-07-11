import pytest

from datetime import timedelta
from django.conf import settings
from django.test import override_settings

from os2datascanner.utils.system_utilities import time_now

from os2datascanner.projects.report.tests.test_utilities import create_reports_for

from ..reportapp.models.documentreport import DocumentReport
from ..reportapp.views.report_views import (
    UserReportView, RemediatorView,
    UserArchiveView, RemediatorArchiveView, UndistributedArchiveView)


@pytest.fixture(autouse=True)
def override_archive_tab_feature_flag():
    settings.ARCHIVE_TAB = True


@pytest.mark.django_db
class TestUserReportView:

    @pytest.mark.parametrize('num', [0, 1, 10])
    def test_userreportview_as_default_role_with_matches(
            self, num, rf, egon_account, egon_email_alias):
        # Arrange
        create_reports_for(egon_email_alias, num=num)

        # Act
        qs = self.userreport_get_queryset(rf, egon_account)

        # Assert
        assert qs.count() == num

    @pytest.mark.parametrize('num_email,num_sid', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (10, 0),
        (0, 10),
        (10, 10),
    ])
    def test_userreportview_as_default_role_with_matches_multiple_aliases(
            self, num_email, num_sid, rf, egon_account, egon_email_alias, egon_sid_alias):
        # Arrange
        create_reports_for(egon_email_alias, num=num_email)
        create_reports_for(egon_sid_alias, num=num_sid)

        # Act
        qs = self.userreport_get_queryset(rf, egon_account)

        # Assert
        assert qs.count() == num_email + num_sid

    @pytest.mark.parametrize('num1,num2', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (10, 0),
        (0, 10),
        (10, 10),
    ])
    def test_userreportview_as_default_role_with_matches_filter_by_scannerjob(
            self, num1, num2, rf, egon_account, egon_email_alias):
        # Arrange
        params = '?scannerjob=2'
        create_reports_for(egon_email_alias, num=num1, scanner_job_pk=1)
        create_reports_for(egon_email_alias, num=num2, scanner_job_pk=2)

        # Act
        qs = self.userreport_get_queryset(rf, egon_account, params=params)

        # Assert
        assert qs.count() == num2

    @pytest.mark.parametrize('num750,num1000', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (10, 0),
        (0, 10),
        (10, 10),
    ])
    def test_userreportview_as_default_role_with_matches_filter_by_sensitivity(
            self, num750, num1000, rf, egon_account, egon_email_alias):
        # Arrange
        params = '?sensitivities=1000'
        create_reports_for(egon_email_alias, num=num750, sensitivity=750)
        create_reports_for(egon_email_alias, num=num1000, sensitivity=1000)

        # Act
        qs = self.userreport_get_queryset(rf, egon_account, params=params)

        # Assert
        assert qs.count() == num1000

    @pytest.mark.parametrize('num_2_1000,other_num', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (10, 0),
        (0, 10),
        (10, 10),
    ])
    def test_userreportview_as_default_role_with_matches_filter_by_scannerjob_and_sensitivity(
            self,
            num_2_1000,
            other_num,
            rf,
            egon_account,
            egon_email_alias):
        # Arrange
        params = '?scannerjob=2&sensitivities=1000'
        create_reports_for(egon_email_alias, num=other_num, scanner_job_pk=1, sensitivity=750)
        create_reports_for(egon_email_alias, num=other_num, scanner_job_pk=1, sensitivity=1000)
        create_reports_for(egon_email_alias, num=other_num, scanner_job_pk=2, sensitivity=750)
        create_reports_for(egon_email_alias, num=num_2_1000, scanner_job_pk=2, sensitivity=1000)

        # Act
        qs = self.userreport_get_queryset(rf, egon_account, params=params)

        # Assert
        assert qs.count() == num_2_1000

    @pytest.mark.parametrize('num_new,num_old', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (10, 0),
        (0, 10),
        (10, 10),
    ])
    def test_userreportview_as_default_role_with_matches_filter_by_datasource_age_true(
            self,
            num_new,
            num_old,
            rf,
            egon_account,
            egon_email_alias):
        # Arrange
        params = '?30-days=true'
        create_reports_for(egon_email_alias, num=num_new, datasource_last_modified=time_now())
        create_reports_for(
            egon_email_alias,
            num=num_old,
            datasource_last_modified=time_now() -
            timedelta(
                days=31))

        # Act
        qs = self.userreport_get_queryset(rf, egon_account, params=params)

        # Assert
        assert qs.count() == num_old + num_new

    @pytest.mark.parametrize('num_new,num_old', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (10, 0),
        (0, 10),
        (10, 10),
    ])
    def test_userreportview_as_default_role_with_matches_filter_by_datasource_age_false(
            self,
            num_new,
            num_old,
            rf,
            egon_account,
            egon_email_alias):
        # Arrange
        params = '?30-days=false'
        create_reports_for(egon_email_alias, num=num_new, datasource_last_modified=time_now())
        create_reports_for(
            egon_email_alias,
            num=num_old,
            datasource_last_modified=time_now() -
            timedelta(
                days=31))

        # Act
        qs = self.userreport_get_queryset(rf, egon_account, params=params)

        # Assert
        assert qs.count() == num_old

    @pytest.mark.parametrize('include_shared,unshared_num,shared_num', [
        ('true', 0, 0),
        ('true', 1, 0),
        ('true', 0, 1),
        ('true', 1, 1),
        ('true', 10, 0),
        ('true', 0, 10),
        ('true', 10, 10),
        ('false', 0, 0),
        ('false', 0, 1),
        ('false', 1, 0),
        ('false', 1, 1),
        ('false', 10, 0),
        ('false', 0, 10),
        ('false', 10, 10),
    ])
    def test_userreportview_personal_and_shared_aliases(
            self,
            include_shared,
            unshared_num,
            shared_num,
            rf,
            egon_account,
            egon_email_alias,
            egon_shared_email_alias):
        """Results from shared aliases should not be presented along with
        personal results in the report module if the 'include-shared' parameter
        is false."""
        # Arrange
        params = f'?include-shared={include_shared}'
        create_reports_for(egon_email_alias, num=unshared_num)
        create_reports_for(egon_shared_email_alias, num=shared_num)

        # Act
        qs = self.userreport_get_queryset(rf, egon_account, params=params)

        # Assert
        if include_shared == 'true':
            assert qs.count() == unshared_num + shared_num
        else:
            assert qs.count() == unshared_num

    # # Helper methods

    def userreport_get_queryset(self, rf, account, params=''):
        request = rf.get('/' + params)
        request.user = account.user
        view = UserReportView()
        view.setup(request)
        qs = view.get_queryset()
        return qs


@pytest.mark.django_db
class TestRemediatorView:

    def test_remediatorview_as_non_remediator(self, egon_account, rf):
        """Accessing the RemediatorView with no remediator alias should redirect the user
        to the main page."""

        request = rf.get('/remediator/')
        request.user = egon_account.user
        response = RemediatorView.as_view()(request)

        assert response.status_code == 302

    def test_remediatorview_as_remediator(self, rf, egon_account, egon_remediator_alias):
        """Remediators should be able to access the remediatorview."""

        request = rf.get('/remediator/')
        request.user = egon_account.user
        response = RemediatorView.as_view()(request)

        assert response.status_code == 200

    @pytest.mark.parametrize('personal_num,remediator_num', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (10, 0),
        (0, 10),
        (10, 10),
    ])
    def test_remediatorview_queryset(
            self,
            personal_num,
            remediator_num,
            rf,
            egon_account,
            egon_remediator_alias,
            egon_email_alias):
        """Remediators should have access to all reports related to a remediator."""
        # Arrange
        create_reports_for(egon_remediator_alias, num=remediator_num)
        create_reports_for(egon_email_alias, num=personal_num)

        # Act
        qs = self.remediator_get_queryset(rf, egon_account)

        # Assert
        assert qs.count() == remediator_num

    def test_remediatorview_as_superuser_but_not_remediator(
            self, superuser_account, rf, egon_remediator_alias):
        """Accessing the RemediatorView as a superuser is allowed, but
        will not show any results."""

        create_reports_for(egon_remediator_alias, num=10)

        request = rf.get('/remediator/')
        request.user = superuser_account.user
        response = RemediatorView.as_view()(request)

        qs = self.remediator_get_queryset(rf, superuser_account)

        # The superuser should be able to access the page ...
        assert response.status_code == 200
        # But should not see any results
        assert qs.count() == 0

    def remediator_get_queryset(self, rf, account, params=''):
        request = rf.get('/remediator/' + params)
        request.user = account.user
        view = RemediatorView()
        view.setup(request)
        qs = view.get_queryset()
        return qs


@pytest.mark.django_db
class TestUserArchiveView:

    def test_userarchiveview_as_default_role_with_no_matches(self, rf, egon_account):
        qs = self.userreport_get_queryset(rf, egon_account)
        assert qs.exists() is False

    @pytest.mark.parametrize('num', [0, 1, 10])
    def test_userarchiveview_as_default_role_with_matches(
            self, egon_account, rf, egon_email_alias, num):

        create_reports_for(egon_email_alias, num=num)

        qs = self.userreport_get_queryset(rf, egon_account)

        # We should not see any reports yet
        assert qs.count() == 0

        DocumentReport.objects.update(resolution_status=0)

        # Now we should see all existing reports, since they are handled
        assert qs.count() == num

    @pytest.mark.parametrize('email_num,sid_num', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (10, 0),
        (0, 10),
        (10, 10),
    ])
    def test_userarchiveview_as_default_role_with_matches_multiple_aliases(
            self, email_num, sid_num, rf, egon_account, egon_sid_alias, egon_email_alias):
        create_reports_for(egon_sid_alias, num=sid_num)
        create_reports_for(egon_email_alias, num=email_num)

        qs = self.userreport_get_queryset(rf, egon_account)

        # We should not see any reports yet
        assert qs.count() == 0

        DocumentReport.objects.update(resolution_status=0)
        # No need to define the queryset again, as it is lazily evaluated.
        assert qs.count() == sid_num + email_num

    @pytest.mark.parametrize('num1,num2', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (10, 0),
        (0, 10),
        (10, 10),
    ])
    def test_userarchiveview_as_default_role_with_matches_filter_by_scannerjob(
            self, num1, num2, rf, egon_account, egon_email_alias):
        # Arrange
        params = '?scannerjob=2'
        create_reports_for(egon_email_alias, num=num1, scanner_job_pk=1, resolution_status=0)
        create_reports_for(egon_email_alias, num=num2, scanner_job_pk=2, resolution_status=0)

        # Act
        qs = self.userreport_get_queryset(rf, egon_account, params=params)

        # Assert
        assert qs.count() == num2

    @pytest.mark.parametrize('num750,num1000', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (10, 0),
        (0, 10),
        (10, 10),
    ])
    def test_userarchiveview_as_default_role_with_matches_filter_by_sensitivity(
            self, num750, num1000, rf, egon_account, egon_email_alias):
        # Arrange
        params = '?sensitivities=1000'
        create_reports_for(egon_email_alias, num=num750, sensitivity=750, resolution_status=0)
        create_reports_for(egon_email_alias, num=num1000, sensitivity=1000, resolution_status=0)

        # Act
        qs = self.userreport_get_queryset(rf, egon_account, params=params)

        # Assert
        assert qs.count() == num1000

    @pytest.mark.parametrize('num_2_1000,other_num', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (10, 0),
        (0, 10),
        (10, 10),
    ])
    def test_userarchiveview_as_default_role_with_matches_filter_by_scannerjob_and_sensitivity(
            self,
            num_2_1000,
            other_num,
            rf,
            egon_account,
            egon_email_alias):
        # Arrange
        params = '?scannerjob=2&sensitivities=1000'
        create_reports_for(
            egon_email_alias,
            num=other_num,
            scanner_job_pk=1,
            sensitivity=750,
            resolution_status=0)
        create_reports_for(
            egon_email_alias,
            num=other_num,
            scanner_job_pk=1,
            sensitivity=1000,
            resolution_status=0)
        create_reports_for(
            egon_email_alias,
            num=other_num,
            scanner_job_pk=2,
            sensitivity=750,
            resolution_status=0)
        create_reports_for(
            egon_email_alias,
            num=num_2_1000,
            scanner_job_pk=2,
            sensitivity=1000,
            resolution_status=0)

        # Act
        qs = self.userreport_get_queryset(rf, egon_account, params=params)

        # Assert
        assert qs.count() == num_2_1000

    @pytest.mark.parametrize('num_new,num_old', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (10, 0),
        (0, 10),
        (10, 10),
    ])
    def test_userarchiveview_as_default_role_with_matches_filter_by_datasource_age_true(
            self,
            num_new,
            num_old,
            rf,
            egon_account,
            egon_email_alias):
        # Arrange
        params = '?30-days=true'
        create_reports_for(
            egon_email_alias,
            num=num_new,
            datasource_last_modified=time_now(),
            resolution_status=0)
        create_reports_for(
            egon_email_alias,
            num=num_old,
            datasource_last_modified=time_now() -
            timedelta(
                days=31),
            resolution_status=0)

        # Act
        qs = self.userreport_get_queryset(rf, egon_account, params=params)

        # Assert
        assert qs.count() == num_old + num_new

    @pytest.mark.parametrize('num_new,num_old', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (10, 0),
        (0, 10),
        (10, 10),
    ])
    def test_userarchiveview_as_default_role_with_matches_filter_by_datasource_age_false(
            self,
            num_new,
            num_old,
            rf,
            egon_account,
            egon_email_alias):
        # Arrange
        params = '?30-days=false'
        create_reports_for(
            egon_email_alias,
            num=num_new,
            datasource_last_modified=time_now(),
            resolution_status=0)
        create_reports_for(
            egon_email_alias,
            num=num_old,
            datasource_last_modified=time_now() -
            timedelta(
                days=31),
            resolution_status=0)

        # Act
        qs = self.userreport_get_queryset(rf, egon_account, params=params)

        # Assert
        assert qs.count() == num_old

    @pytest.mark.parametrize('include_shared,unshared_num,shared_num', [
        ('true', 0, 0),
        ('true', 1, 0),
        ('true', 0, 1),
        ('true', 1, 1),
        ('true', 10, 0),
        ('true', 0, 10),
        ('true', 10, 10),
        ('false', 0, 0),
        ('false', 0, 1),
        ('false', 1, 0),
        ('false', 1, 1),
        ('false', 10, 0),
        ('false', 0, 10),
        ('false', 10, 10),
    ])
    def test_userarchiveview_personal_and_shared_aliases(
            self,
            include_shared,
            unshared_num,
            shared_num,
            rf,
            egon_account,
            egon_email_alias,
            egon_shared_email_alias):
        """Results from shared aliases should not be presented along with
        personal results in the report module if the 'include-shared' parameter
        is false."""
        # Arrange
        params = f'?include-shared={include_shared}'
        create_reports_for(egon_email_alias, num=unshared_num, resolution_status=0)
        create_reports_for(egon_shared_email_alias, num=shared_num, resolution_status=0)

        # Act
        qs = self.userreport_get_queryset(rf, egon_account, params=params)

        # Assert
        if include_shared == 'true':
            assert qs.count() == unshared_num + shared_num
        else:
            assert qs.count() == unshared_num

    # Helper methods

    def userreport_get_queryset(self, rf, account, params=''):
        request = rf.get('/archive/reports' + params)
        request.user = account.user
        view = UserArchiveView()
        view.setup(request)
        qs = view.get_queryset()
        return qs


@pytest.mark.django_db
class TestRemediatorArchiveView:

    def test_remediatorarchiveview_not_enabled(self, rf, egon_account, egon_remediator_alias):
        """If the archive tab is not enabled in the configurations, the view
        should redirect the user, even if they are a remediator."""
        settings.ARCHIVE_TAB = False

        request = rf.get('/archive/remediator/')
        request.user = egon_account.user
        response = RemediatorArchiveView.as_view()(request)
        assert response.status_code == 302

    @override_settings(ARCHIVE_TAB=True)
    def test_remediatorarchiveview_as_non_remediator(self, rf, egon_account):
        """Accessing the RemediatorView with no role should redirect the user
        to the main page."""

        request = rf.get('/archive/remediator/')
        request.user = egon_account.user
        response = RemediatorArchiveView.as_view()(request)
        assert response.status_code == 302

    @override_settings(ARCHIVE_TAB=True)
    def test_remediatorarchiveview_as_remediator(
            self,
            rf,
            egon_account,
            egon_remediator_alias):
        """Remediators should be able to access the remediator archive tab."""
        request = rf.get('/archive/remediator/')
        request.user = egon_account.user
        response = RemediatorArchiveView.as_view()(request)
        assert response.status_code == 200

    @override_settings(ARCHIVE_TAB=True)
    @pytest.mark.parametrize('personal_num,remediator_num', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (10, 0),
        (0, 10),
        (10, 10),
    ])
    def test_remediatorarchiveview_queryset(
            self,
            personal_num,
            remediator_num,
            rf,
            egon_account,
            egon_remediator_alias,
            egon_email_alias):
        """Remediators should have access to all reports related to a remediator."""
        # Arrange
        create_reports_for(egon_remediator_alias, num=remediator_num)
        create_reports_for(egon_email_alias, num=personal_num)

        # Act
        qs = self.remediator_get_queryset(rf, egon_account)

        # Assert
        # Remediator should not see any results yet ...
        assert qs.count() == 0

        DocumentReport.objects.update(resolution_status=0)

        # But now they should!
        assert qs.count() == remediator_num

    @override_settings(ARCHIVE_TAB=True)
    def test_remediatorview_as_superuser_but_not_remediator(
            self, superuser_account, rf, egon_remediator_alias):
        """Accessing the RemediatorView as a superuser is allowed, but
        will not show any results."""

        create_reports_for(egon_remediator_alias, num=10, resolution_status=0)

        request = rf.get('/remediator/')
        request.user = superuser_account.user
        response = RemediatorView.as_view()(request)

        qs = self.remediator_get_queryset(rf, superuser_account)

        # The superuser should be able to access the page ...
        assert response.status_code == 200
        # But should not see any results
        assert qs.count() == 0

#     # Helper functions

    def remediator_get_queryset(self, rf, account, params=''):
        request = rf.get('/archive/remediator' + params)
        request.user = account.user
        view = RemediatorArchiveView()
        view.setup(request)
        qs = view.get_queryset()
        return qs


@pytest.mark.django_db
class TestUndistibutedArchiveView:

    def test_undistributedarchiveview_as_default_role(self, rf, egon_account):
        """A user without superuser privileges should be redirected when trying
        to access this view."""
        request = rf.get('/archive/undistributed')
        request.user = egon_account.user
        response = UndistributedArchiveView.as_view()(request)
        assert response.status_code == 302

    def test_undistributedarchiveview_as_superuser(self, rf, superuser_account):
        """Superusers should be able to access the undistributed archive tab."""

        request = rf.get('/archive/undistributed')
        request.user = superuser_account.user
        response = UndistributedArchiveView.as_view()(request)
        assert response.status_code == 200

    @pytest.mark.parametrize('num', [0, 1, 10])
    def test_undistributedarchiveview_queryset(self, rf, superuser_account, egon_email_alias, num):

        create_reports_for(egon_email_alias, num=num, only_notify_superadmin=True)

        qs = self.remediator_get_queryset(rf, superuser_account)

        # Superuser should not see any results yet ...
        assert qs.count() == 0

        DocumentReport.objects.update(resolution_status=0)

        # But now they should!
        assert qs.count() == num

#     # Helper functions

    def remediator_get_queryset(self, rf, account, params=''):
        request = rf.get('/archive/undistributed' + params)
        request.user = account.user
        view = UndistributedArchiveView()
        view.setup(request)
        qs = view.get_queryset()
        return qs
