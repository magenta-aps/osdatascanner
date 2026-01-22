import pytest
import sys

from datetime import timedelta
from django.conf import settings
from django.test import override_settings
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy

from os2datascanner.utils.system_utilities import time_now

from os2datascanner.projects.report.tests.test_utilities import create_reports_for

from ..reportapp.models.documentreport import DocumentReport
from ..reportapp.models.scanner_reference import ScannerReference
from ..reportapp.utils import create_alias_and_match_relations
from ..reportapp.views.report_views import (
    UserReportView, RemediatorView, UndistributedView,
    UserArchiveView, RemediatorArchiveView, UndistributedArchiveView)
from ..organizations.models import Account

from importlib import reload, import_module

from django.urls import clear_url_caches


def reload_urlconf(urlconf=None):
    clear_url_caches()
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        reload(sys.modules[urlconf])
    else:
        import_module(urlconf)


@pytest.fixture(autouse=True)
def override_archive_tab_feature_flag():
    settings.ARCHIVE_TAB = True


@pytest.mark.django_db
class TestUserReportView:

    def test_double_relation_report_filter(
            self,
            egon_account,
            egon_email_alias,
            egon_upn_alias,
            rf):
        # Arrange
        create_reports_for(egon_email_alias, num=10)
        create_alias_and_match_relations(egon_upn_alias)

        # Act
        response = self.get_userreport_response(rf,
                                                egon_account,
                                                params='&sensitivity_checkbox=on')

        scanner_job_choice = response.context_data.get('scannerjob_choices')[0]
        source_type_choice = response.context_data.get('source_type_choices')[0]
        # This is a generator that returns tuples.
        sensitivity_choice = next(response.context_data.get("sensitivity_choices"))

        # Assert
        assert scanner_job_choice.total == 10
        assert source_type_choice.get("total") == 10
        assert sensitivity_choice[1] == 10

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
        params = '?retention=true'
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
            egon_email_alias,
            olsenbanden_organization):
        # Arrange
        # Enable retention policy
        olsenbanden_organization.retention_policy = True
        olsenbanden_organization.retention_days = 30
        olsenbanden_organization.save()
        params = '?retention=false'
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

    @pytest.mark.parametrize('num_new,num_old', [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (10, 0),
        (0, 10),
        (10, 10),
    ])
    def test_all_matches_shown_with_no_retention_policy(
            self,
            num_new,
            num_old,
            rf,
            egon_account,
            egon_email_alias):
        # Arrange
        # Retention_policy is set to false by default
        create_reports_for(egon_email_alias, num=num_new, datasource_last_modified=time_now())
        create_reports_for(
            egon_email_alias,
            num=num_old,
            datasource_last_modified=time_now() -
            timedelta(
                days=31))

        # Act
        qs = self.userreport_get_queryset(rf, egon_account)

        # Assert
        assert qs.count() == num_old + num_new

    def test_scannerjob_choices(
            self,
            egon_account,
            egon_email_alias,
            scan_olsenbanden_org,
            scan_olsenbanden_org_withheld,
            scan_kun_egon,
            scan_kun_egon_withheld,
            scan_owned_by_olsenbanden,
            rf):

        create_reports_for(
            egon_email_alias,
            num=1,
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
        response = self.get_userreport_response(rf,
                                                egon_account,
                                                params='&sensitivity_checkbox=on')
        choices = list(response.context_data.get('scannerjob_choices'))

        # Assert
        assert len(choices) == 2
        assert scan_olsenbanden_org in choices
        assert scan_olsenbanden_org_withheld not in choices
        assert scan_kun_egon in choices
        assert scan_kun_egon_withheld not in choices
        assert scan_owned_by_olsenbanden not in choices

    @pytest.mark.parametrize("org_perm", [True, False])
    def test_smb_mass_deletion_buttons_filter_source_type(self, client, egon_account, org_perm,
                                                          olsenbanden_organization):
        olsenbanden_organization.smb_delete_permission = org_perm
        olsenbanden_organization.save()
        client.force_login(egon_account.user)
        response = client.get(reverse_lazy("index") + "?source_type=smbc")
        assert response.context.get("show_smb_mass_delete_button", False) == org_perm

    @pytest.mark.parametrize("org_perm", [True, False])
    def test_smb_mass_deletion_buttons_all_same_source_type(self, client, egon_account,
                                                            egon_email_alias, org_perm,
                                                            olsenbanden_organization):
        olsenbanden_organization.smb_delete_permission = org_perm
        olsenbanden_organization.save()
        create_reports_for(egon_email_alias, source_type="smbc")

        client.force_login(egon_account.user)
        response = client.get(reverse_lazy("index"))

        assert response.context.get("show_smb_mass_delete_button", False) == org_perm

    @pytest.mark.parametrize("org_perm", [True, False])
    def test_ews_mass_deletion_buttons_filter_source_type(self, client, egon_account, org_perm,
                                                          olsenbanden_organization):
        olsenbanden_organization.exchange_delete_permission = org_perm
        olsenbanden_organization.save()
        client.force_login(egon_account.user)
        response = client.get(reverse_lazy("index") + "?source_type=ews")

        assert response.context.get("show_ews_mass_delete_button", False) == org_perm

    @pytest.mark.parametrize("org_perm", [True, False])
    def test_ews_mass_deletion_buttons_all_same_source_type(self, client, egon_account,
                                                            egon_email_alias, org_perm,
                                                            olsenbanden_organization):
        olsenbanden_organization.exchange_delete_permission = org_perm
        olsenbanden_organization.save()
        create_reports_for(egon_email_alias, source_type="ews")

        client.force_login(egon_account.user)
        response = client.get(reverse_lazy("index"))

        assert response.context.get("show_ews_mass_delete_button", False) == org_perm

    @pytest.mark.parametrize("org_perm", [True, False])
    def test_msgraph_mail_mass_deletion_buttons_filter_source_type(self, client, egon_account,
                                                                   olsenbanden_organization,
                                                                   org_perm):
        olsenbanden_organization.outlook_delete_email_permission = org_perm
        olsenbanden_organization.save()
        client.force_login(egon_account.user)
        response = client.get(reverse_lazy("index") + "?source_type=msgraph-mail")

        assert response.context.get("show_msgraph_email_mass_delete_button", False) == org_perm

    @pytest.mark.parametrize("org_perm", [True, False])
    def test_msgraph_mail_mass_deletion_buttons_all_same_source_type(self, client, egon_account,
                                                                     egon_email_alias, org_perm,
                                                                     olsenbanden_organization):
        olsenbanden_organization.outlook_delete_email_permission = org_perm
        olsenbanden_organization.save()
        create_reports_for(egon_email_alias, source_type="msgraph-mail")

        client.force_login(egon_account.user)
        response = client.get(reverse_lazy("index"))

        assert response.context.get("show_msgraph_email_mass_delete_button", False) == org_perm

    @pytest.mark.parametrize("org_perm", [True, False])
    def test_msgraph_files_mass_deletion_buttons_filter_source_type(self, client, egon_account,
                                                                    olsenbanden_organization,
                                                                    org_perm):
        olsenbanden_organization.onedrive_delete_permission = org_perm
        olsenbanden_organization.save()
        client.force_login(egon_account.user)
        response = client.get(reverse_lazy("index") + "?source_type=msgraph-files")

        assert response.context.get("show_msgraph_file_mass_delete_button", False) == org_perm

    @pytest.mark.parametrize("org_perm", [True, False])
    def test_msgraph_files_mass_deletion_buttons_all_same_source_type(self, client, egon_account,
                                                                      egon_email_alias, org_perm,
                                                                      olsenbanden_organization):
        olsenbanden_organization.onedrive_delete_permission = org_perm
        olsenbanden_organization.save()
        create_reports_for(egon_email_alias, source_type="msgraph-files")

        client.force_login(egon_account.user)
        response = client.get(reverse_lazy("index"))

        assert response.context.get("show_msgraph_file_mass_delete_button", False) == org_perm

    @pytest.mark.parametrize("org_perm", [True, False])
    def test_gmail_email_mass_deletion_buttons_filter_source_type(self, client, egon_account,
                                                                  olsenbanden_organization,
                                                                  org_perm):
        olsenbanden_organization.gmail_delete_permission = org_perm
        olsenbanden_organization.save()
        client.force_login(egon_account.user)
        response = client.get(reverse_lazy("index") + "?source_type=gmail")

        assert response.context.get("show_gmail_mass_delete_button", False) == org_perm

    @pytest.mark.parametrize("org_perm", [True, False])
    def test_gmail_email_mass_deletion_buttons_all_same_source_type(self, client, egon_account,
                                                                    egon_email_alias, org_perm,
                                                                    olsenbanden_organization):
        olsenbanden_organization.gmail_delete_permission = org_perm
        olsenbanden_organization.save()
        create_reports_for(egon_email_alias, source_type="gmail")

        client.force_login(egon_account.user)
        response = client.get(reverse_lazy("index"))

        assert response.context.get("show_gmail_mass_delete_button", False) == org_perm

    @pytest.mark.parametrize("org_perm", [True, False])
    def test_gdrive_file_mass_deletion_buttons_filter_source_type(self, client, egon_account,
                                                                  olsenbanden_organization,
                                                                  org_perm):
        olsenbanden_organization.gdrive_delete_permission = org_perm
        olsenbanden_organization.save()
        client.force_login(egon_account.user)
        response = client.get(reverse_lazy("index") + "?source_type=googledrive")

        assert response.context.get("show_gdrive_mass_delete_button", False) == org_perm

    @pytest.mark.parametrize("org_perm", [True, False])
    def test_gdrive_file_mass_deletion_buttons_all_same_source_type(self, client, egon_account,
                                                                    egon_email_alias, org_perm,
                                                                    olsenbanden_organization):
        olsenbanden_organization.gdrive_delete_permission = org_perm
        olsenbanden_organization.save()
        create_reports_for(egon_email_alias, source_type="googledrive")

        client.force_login(egon_account.user)
        response = client.get(reverse_lazy("index"))

        assert response.context.get("show_gdrive_mass_delete_button", False) == org_perm

    @pytest.mark.parametrize("org_perm", [True, False])
    def test_mass_delete_button_respects_org_perm_for_source_type_all(self, client, egon_account,
                                                                      egon_email_alias, org_perm,
                                                                      olsenbanden_organization):
        # Arrange:
        olsenbanden_organization.outlook_delete_email_permission = org_perm
        olsenbanden_organization.save()
        create_reports_for(egon_email_alias, source_type="msgraph-mail", num=20)

        # Act:
        client.force_login(egon_account.user)
        response = client.get(reverse_lazy("index") + "?source_type=all")

        # Assert:
        assert response.context.get("show_msgraph_email_mass_delete_button", False) == org_perm

    def test_mass_deletion_buttons_all_different_source_type(self, client, egon_account,
                                                             egon_email_alias,
                                                             olsenbanden_organization):
        olsenbanden_organization.onedrive_delete_permission = True
        olsenbanden_organization.outlook_delete_email_permission = True
        olsenbanden_organization.save()
        create_reports_for(egon_email_alias, source_type="msgraph-files", num=2)
        create_reports_for(egon_email_alias, source_type="msgraph-mail", num=2)
        create_reports_for(egon_email_alias, source_type="smb", num=2)
        create_reports_for(egon_email_alias, source_type="ews", num=2)

        client.force_login(egon_account.user)
        response = client.get(reverse_lazy("index"))

        assert not response.context.get("show_msgraph_file_mass_delete_button", False)
        assert not response.context.get("show_msgraph_email_mass_delete_button", False)
        assert not response.context.get("show_smb_mass_delete_button", False)
        assert not response.context.get("show_ews_mass_delete_button", False)

    # # Helper methods

    def userreport_get_queryset(self, rf, account, params=''):
        request = rf.get('/' + params)
        request.user = account.user
        view = UserReportView()
        view.setup(request)
        qs = view.get_queryset()
        return qs

    def get_userreport_response(self, rf, account, params='', **kwargs):
        request = rf.get('/' + params)
        request.user = account.user
        return UserReportView.as_view()(request, **kwargs)


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

    def test_scannerjob_choices_remediator_matches(
            self,
            egon_account,
            egon_remediator_alias,
            rf):
        """When an account has a remediator alias connected to reports,
        their scanner should show up as a scannerjob option."""

        # Arrange
        egon_remediator_alias._value = 2
        egon_remediator_alias.save()
        create_reports_for(egon_remediator_alias, num=10, scanner_job_pk=1)

        # Act
        response = self.get_remediator_response(rf, egon_account)
        choices = list(response.context_data.get('scannerjob_choices'))

        # Assert
        assert len(choices) == 1
        assert choices[0].scanner_pk == 1

    def remediator_get_queryset(self, rf, account, params=''):
        request = rf.get('/remediator/' + params)
        request.user = account.user
        view = RemediatorView()
        view.setup(request)
        qs = view.get_queryset()
        return qs

    def get_remediator_response(self, rf, account, params='', **kwargs):
        request = rf.get('/remediator/' + params)
        request.user = account.user
        return RemediatorView.as_view()(request, **kwargs)


@pytest.mark.django_db
class TestUndistributedView:

    def test_undistributedview_without_permission(self, rf, egon_account):
        """A user without the correct permission should not be allowed access."""
        request = rf.get('/undistributed')
        request.user = egon_account.user
        with pytest.raises(PermissionDenied):
            UndistributedView.as_view()(request)

    def test_undistributedview_with_permission(self, rf, egon_account):
        """A user with the correct permission should be allowed access."""
        egon_account.user.user_permissions.add(Permission.objects.get(
            codename="view_withheld_results"))
        request = rf.get('/undistributed')
        request.user = egon_account.user
        response = UndistributedView.as_view()(request)
        assert response.status_code == 200

    def test_undistributedview_as_superuser(self, rf, superuser_account):
        """Superusers should be able to access the undistributed tab."""

        request = rf.get('/undistributed')
        request.user = superuser_account.user
        response = UndistributedView.as_view()(request)
        assert response.status_code == 200

    @pytest.mark.parametrize('num', [0, 1, 10])
    def test_undistributedview_queryset(self, rf, superuser_account, egon_email_alias, num):

        create_reports_for(egon_email_alias, num=num, only_notify_superadmin=True)

        qs = self.remediator_get_queryset(rf, superuser_account)

        assert qs.count() == num

    @pytest.mark.parametrize('num', [0, 1, 10])
    def test_undistributedview_with_problems(self, rf, superuser_account, egon_email_alias, num):

        create_reports_for(egon_email_alias, num=num, only_notify_superadmin=True)
        create_reports_for(
            egon_email_alias,
            problem=1,
            sensitivity=None,
            matched=False,
            only_notify_superadmin=True)

        qs = self.remediator_get_queryset(rf, superuser_account)

        assert qs.count() == num

    @pytest.mark.parametrize("has_permission", [True, False])
    def test_allow_handle_context_value(self, client, egon_account, has_permission):
        egon_account.user.user_permissions.add(
            Permission.objects.get(codename="view_withheld_results"))
        if has_permission:
            egon_account.user.user_permissions.add(
                Permission.objects.get(codename="handle_withheld_results"))

        client.force_login(egon_account.user)
        response = client.get(reverse_lazy("reports:undistributed"))

        assert response.status_code == 200
        assert response.context_data["allow_handle"] == has_permission

#     # Helper functions

    def remediator_get_queryset(self, rf, account, params=''):
        request = rf.get('/undistributed' + params)
        request.user = account.user
        view = UndistributedView()
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
        params = '?retention=true'
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
            egon_email_alias,
            olsenbanden_organization):
        # Arrange
        # Enable retention policy
        olsenbanden_organization.retention_policy = True
        olsenbanden_organization.retention_days = 30
        olsenbanden_organization.save()
        params = '?retention=false'
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

    def test_double_relation_archive_resolution_filter(
            self,
            egon_account,
            egon_email_alias,
            egon_upn_alias,
            rf):

        # Arrange
        create_reports_for(egon_email_alias, resolution_status=0, num=10)
        create_alias_and_match_relations(egon_upn_alias)

        # Act
        response = self.get_archive_response(rf, egon_account)
        resolution_status_choice = response.context_data.get('resolution_status_choices')[0]

        # Assert
        assert resolution_status_choice.get("total") == 10

    # Helper methods

    def userreport_get_queryset(self, rf, account, params=''):
        request = rf.get('/archive/reports' + params)
        request.user = account.user
        view = UserArchiveView()
        view.setup(request)
        qs = view.get_queryset()
        return qs

    def get_archive_response(self, rf, account, params='', **kwargs):
        request = rf.get('/' + params)
        request.user = account.user
        return UserArchiveView.as_view()(request, **kwargs)


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

    def test_undistributedarchiveview_without_permission(self, rf, egon_account):
        """A user without the correct permission should not be allowed access."""
        request = rf.get('/archive/undistributed')
        request.user = egon_account.user
        with pytest.raises(PermissionDenied):
            UndistributedArchiveView.as_view()(request)

    def test_undistributedarchiveview_with_permission(self, rf, egon_account):
        """A user with the correct permission should be allowed access."""
        egon_account.user.user_permissions.add(Permission.objects.get(
            codename="view_withheld_results"))
        request = rf.get('/archive/undistributed')
        request.user = egon_account.user
        response = UndistributedArchiveView.as_view()(request)
        assert response.status_code == 200

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


@pytest.mark.django_db
class TestDistributeMatchesView:
    url = reverse_lazy("distribute")
    headers = {"HTTP_HX-Request": "true"}

    def test_distribute_matches_with_permission(self, client, egon_account):
        egon_account.user.user_permissions.add(
            Permission.objects.get(codename="distribute_withheld_results"))
        client.force_login(egon_account.user)
        response = client.post(self.url, data={}, **self.headers)

        assert response.status_code == 200

    def test_distribute_matches_without_permission(self, client, egon_account):
        client.force_login(egon_account.user)
        response = client.post(self.url, data={}, **self.headers)

        assert response.status_code == 403

    def test_distribute_matches_no_htmx_header(self, client, egon_account):
        egon_account.user.user_permissions.add(
            Permission.objects.get(codename="distribute_withheld_results"))
        client.force_login(egon_account.user)
        response = client.post(self.url, data={})

        assert response.status_code == 400

    def test_distribute_single_scanner(self, client, egon_account, egon_email_alias):
        # Arrange
        create_reports_for(
            egon_email_alias,
            num=3,
            only_notify_superadmin=True,
            scanner_job_pk=1,
        )
        create_reports_for(
            egon_email_alias,
            num=4,
            only_notify_superadmin=True,
            scanner_job_pk=2,
        )
        egon_account.user.user_permissions.add(
            Permission.objects.get(codename="distribute_withheld_results"))
        client.force_login(egon_account.user)

        # Act
        client.post(self.url, data={"distribute-to": [1]}, **self.headers)

        # Assert
        assert ScannerReference.objects.get(
            scanner_pk=1).document_reports.filter(
            only_notify_superadmin=False).count() == 3
        assert ScannerReference.objects.get(
            scanner_pk=2).document_reports.filter(
            only_notify_superadmin=True).count() == 4

    def test_distribute_multiple_scanners(self, client, egon_account, egon_email_alias):
        # Arrange
        create_reports_for(
            egon_email_alias,
            num=3,
            only_notify_superadmin=True,
            scanner_job_pk=1,
        )
        create_reports_for(
            egon_email_alias,
            num=4,
            only_notify_superadmin=True,
            scanner_job_pk=2,
        )
        create_reports_for(
            egon_email_alias,
            num=5,
            only_notify_superadmin=True,
            scanner_job_pk=3,
        )
        egon_account.user.user_permissions.add(
            Permission.objects.get(codename="distribute_withheld_results"))
        client.force_login(egon_account.user)

        # Act
        client.post(self.url, data={"distribute-to": [1, 2]}, **self.headers)

        # Assert
        assert ScannerReference.objects.get(
            scanner_pk=1).document_reports.filter(
            only_notify_superadmin=False).count() == 3
        assert ScannerReference.objects.get(
            scanner_pk=2).document_reports.filter(
            only_notify_superadmin=False).count() == 4
        assert ScannerReference.objects.get(
            scanner_pk=3).document_reports.filter(
            only_notify_superadmin=True).count() == 5


@pytest.mark.django_db
class TestHandleMatchView:

    htmx_header = {"HTTP_HX-REQUEST": "true",
                   "content-type": "application/json; charset=UTF-8",
                   "authorization": "Bearer fake_token"}

    def test_handle_single_report_correct_account(self, egon_account, egon_email_alias, client):
        create_reports_for(egon_email_alias)

        report = egon_account.get_report(Account.ReportType.RAW).first()

        url = reverse_lazy("handle-match", kwargs={"pk": report.pk})
        data = {"action": DocumentReport.ResolutionChoices.REMOVED}

        client.force_login(egon_account.user)
        response = client.post(url, data=data, **self.htmx_header)

        reports = egon_account.get_report(Account.ReportType.RAW)

        assert response.status_code == 200
        assert report not in reports

    def test_handle_single_report_incorrect_account(self, egon_account, benny_email_alias, client):
        create_reports_for(benny_email_alias)
        report = benny_email_alias.account.get_report(Account.ReportType.RAW).first()

        url = reverse_lazy("handle-match", kwargs={"pk": report.pk})
        data = {"action": DocumentReport.ResolutionChoices.REMOVED}

        client.force_login(egon_account.user)
        response = client.post(url, data=data, **self.htmx_header)

        reports = benny_email_alias.account.get_report(Account.ReportType.RAW)

        assert response.status_code == 404
        assert report in reports

    @pytest.mark.parametrize("status", [choice for choice in DocumentReport.ResolutionChoices])
    def test_handle_single_report_different_states(self, client, status, egon_account,
                                                   egon_email_alias):
        create_reports_for(egon_email_alias)
        report = egon_account.get_report(Account.ReportType.RAW).first()

        url = reverse_lazy("handle-match", kwargs={"pk": report.pk})
        data = {"action": status}

        client.force_login(egon_account.user)
        response = client.post(url, data=data, **self.htmx_header)

        report.refresh_from_db()
        reports = egon_account.get_report(Account.ReportType.RAW)

        assert response.status_code == 200
        assert report not in reports
        assert report.resolution_status == status

    def test_revert_single_report(self, client, egon_account, egon_email_alias):
        create_reports_for(egon_email_alias,
                           resolution_status=DocumentReport.ResolutionChoices.REMOVED)
        report = egon_account.get_report(Account.ReportType.RAW, archived=True).first()

        url = reverse_lazy("handle-match", kwargs={"pk": report.pk})
        data = {}

        client.force_login(egon_account.user)
        response = client.post(url, data=data, **self.htmx_header)

        report.refresh_from_db()
        reports = egon_account.get_report(Account.ReportType.RAW, archived=True)

        assert response.status_code == 200
        assert report not in reports
        assert report.resolution_status is None

    def test_handle_multiple_reports_correct_account(self, client, egon_account, egon_email_alias):
        create_reports_for(egon_email_alias)
        drs = egon_account.get_report(Account.ReportType.RAW)[:5]

        url = reverse_lazy("mass-handle")
        data = {"action": DocumentReport.ResolutionChoices.REMOVED,
                "table-checkbox": [dr.pk for dr in drs]}

        client.force_login(egon_account.user)
        response = client.post(url, data=data, **self.htmx_header)

        reports = egon_account.get_report(Account.ReportType.RAW)

        assert response.status_code == 200
        assert all([dr not in reports for dr in drs])

    def test_handle_multiple_reports_incorrect_account(self, client, egon_account,
                                                       benny_email_alias):
        create_reports_for(benny_email_alias)
        drs = benny_email_alias.account.get_report(Account.ReportType.RAW)[:5]

        url = reverse_lazy("mass-handle")
        data = {"action": DocumentReport.ResolutionChoices.REMOVED,
                "table-checkbox": [dr.pk for dr in drs]}

        client.force_login(egon_account.user)
        response = client.post(url, data=data, **self.htmx_header)

        reports = benny_email_alias.account.get_report(Account.ReportType.RAW)

        assert response.status_code == 404
        assert all([dr in reports for dr in drs])

    @pytest.mark.parametrize("status", [status for status in DocumentReport.ResolutionChoices])
    def test_handle_multiple_reports_different_status(self, client, status, egon_account,
                                                      egon_email_alias):
        create_reports_for(egon_email_alias)
        drs = egon_account.get_report(Account.ReportType.RAW)[:5]

        url = reverse_lazy("mass-handle")
        data = {"action": status,
                "table-checkbox": [dr.pk for dr in drs]}

        client.force_login(egon_account.user)
        response = client.post(url, data=data, **self.htmx_header)

        drs = DocumentReport.objects.filter(pk__in=[dr.pk for dr in drs])
        reports = egon_account.get_report(Account.ReportType.RAW)

        assert response.status_code == 200
        assert all([dr not in reports for dr in drs])
        assert all([dr.resolution_status == status for dr in drs])

    def test_handle_withheld_report_superuser(self, client, egon_email_alias, superuser_account):
        create_reports_for(egon_email_alias, only_notify_superadmin=True)
        report = DocumentReport.objects.filter(only_notify_superadmin=True,
                                               resolution_status__isnull=True).first()

        url = reverse_lazy("handle-match", kwargs={"pk": report.pk})
        data = {"action": DocumentReport.ResolutionChoices.REMOVED}

        client.force_login(superuser_account.user)
        response = client.post(url, data=data, **self.htmx_header)

        reports = DocumentReport.objects.filter(only_notify_superadmin=True,
                                                resolution_status__isnull=True)

        assert response.status_code == 200
        assert report not in reports

    def test_handle_multiple_withheld_report_superuser(
            self, client, egon_email_alias, superuser_account):
        create_reports_for(egon_email_alias, only_notify_superadmin=True)
        drs = DocumentReport.objects.filter(only_notify_superadmin=True,
                                            resolution_status__isnull=True)[:5]

        url = reverse_lazy("mass-handle")
        data = {"action": DocumentReport.ResolutionChoices.REMOVED,
                "table-checkbox": [dr.pk for dr in drs]}

        client.force_login(superuser_account.user)
        response = client.post(url, data=data, **self.htmx_header)

        reports = DocumentReport.objects.filter(only_notify_superadmin=True,
                                                resolution_status__isnull=True)

        assert response.status_code == 200
        assert all([dr.pk not in reports for dr in drs])

    def test_handle_withheld_report_not_allowed(self, client, egon_email_alias, egon_account):
        # Arrange
        create_reports_for(egon_email_alias, only_notify_superadmin=True, num=1)
        report = DocumentReport.objects.get(only_notify_superadmin=True,
                                            resolution_status__isnull=True)
        url = reverse_lazy("handle-match", kwargs={"pk": report.pk})
        data = {"action": DocumentReport.ResolutionChoices.REMOVED}
        client.force_login(egon_account.user)

        # Act
        response = client.post(url, data=data, **self.htmx_header)

        # Assert
        assert response.status_code == 404

    def test_handle_multiple_withheld_report_not_allowed(
            self, client, egon_email_alias, egon_account):
        # Arrange
        create_reports_for(egon_email_alias, only_notify_superadmin=True, num=2)
        drs = DocumentReport.objects.filter(only_notify_superadmin=True,
                                            resolution_status__isnull=True)

        url = reverse_lazy("mass-handle")
        data = {"action": DocumentReport.ResolutionChoices.REMOVED,
                "table-checkbox": [dr.pk for dr in drs]}
        client.force_login(egon_account.user)

        # Act
        response = client.post(url, data=data, **self.htmx_header)

        # Assert
        assert response.status_code == 404

    def test_handle_own_withheld_with_permission(self, client, egon_email_alias, egon_account):
        # Arrange
        egon_account.user.user_permissions.add(Permission.objects.get(
            codename="handle_withheld_results"))

        create_reports_for(egon_email_alias, only_notify_superadmin=True, num=1)
        report = DocumentReport.objects.get(only_notify_superadmin=True,
                                            resolution_status__isnull=True)

        url = reverse_lazy("handle-match", kwargs={"pk": report.pk})
        data = {"action": DocumentReport.ResolutionChoices.REMOVED}

        client.force_login(egon_account.user)

        # Act
        response = client.post(url, data=data, **self.htmx_header)

        # Assert
        assert response.status_code == 200
        report.refresh_from_db()
        assert report.resolution_status == DocumentReport.ResolutionChoices.REMOVED

    def test_handle_multiple_own_withheld_with_permission(
            self, client, egon_email_alias, egon_account):

        # Arrange
        egon_account.user.user_permissions.add(Permission.objects.get(
            codename="handle_withheld_results"))

        create_reports_for(egon_email_alias, only_notify_superadmin=True, num=1)

        drs = DocumentReport.objects.filter(only_notify_superadmin=True,
                                            resolution_status__isnull=True)
        url = reverse_lazy("mass-handle")
        data = {"action": DocumentReport.ResolutionChoices.REMOVED,
                "table-checkbox": [dr.pk for dr in drs]}

        client.force_login(egon_account.user)

        # Act
        response = client.post(url, data=data, **self.htmx_header)

        # Assert
        assert response.status_code == 200
        assert all([dr.resolution_status == DocumentReport.ResolutionChoices.REMOVED
                    for dr in DocumentReport.objects.all()])

    def test_handle_other_withheld_with_permission(self, client, benny_email_alias, egon_account):
        # Arrange
        egon_account.user.user_permissions.add(Permission.objects.get(
            codename="handle_withheld_results"))

        create_reports_for(benny_email_alias, only_notify_superadmin=True, num=1)
        report = DocumentReport.objects.get(only_notify_superadmin=True,
                                            resolution_status__isnull=True)

        url = reverse_lazy("handle-match", kwargs={"pk": report.pk})
        data = {"action": DocumentReport.ResolutionChoices.REMOVED}

        client.force_login(egon_account.user)

        # Act
        response = client.post(url, data=data, **self.htmx_header)

        # Assert
        assert response.status_code == 200
        report.refresh_from_db()
        assert report.resolution_status == DocumentReport.ResolutionChoices.REMOVED

    def test_handle_multiple_other_withheld_with_permission(self, client,
                                                            benny_email_alias, egon_account):
        # Arrange
        egon_account.user.user_permissions.add(Permission.objects.get(
            codename="handle_withheld_results"))

        create_reports_for(benny_email_alias, only_notify_superadmin=True, num=2)

        drs = DocumentReport.objects.filter(only_notify_superadmin=True,
                                            resolution_status__isnull=True)
        url = reverse_lazy("mass-handle")
        data = {"action": DocumentReport.ResolutionChoices.REMOVED,
                "table-checkbox": [dr.pk for dr in drs]}

        client.force_login(egon_account.user)

        # Act
        response = client.post(url, data=data, **self.htmx_header)

        # Assert
        assert response.status_code == 200
        assert all([dr.resolution_status == DocumentReport.ResolutionChoices.REMOVED
                    for dr in DocumentReport.objects.all()])
