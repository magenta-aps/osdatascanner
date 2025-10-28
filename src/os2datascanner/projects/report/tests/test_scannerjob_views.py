import pytest

from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Permission

from .test_utilities import create_reports_for
from ..reportapp.views.scannerjob_views import ScannerjobListView
from ..reportapp.models.documentreport import DocumentReport


@pytest.mark.django_db
class TestScannerjobListView:

    def test_scannerjoblistview_non_superuser_no_permission(self, egon_account, rf):
        """A non-superuser without permission can't see the list of scannerjobs."""
        with pytest.raises(PermissionDenied):
            self.get_scannerjoblistview_response(rf, egon_account)

    def test_scannerjoblistview_non_superuser_permission(self, egon_account, rf):
        """A non-superuser with permission can see the list of scannerjobs."""
        egon_account.user.user_permissions.add(
            Permission.objects.get(codename="view_scannerjob_list"))
        response = self.get_scannerjoblistview_response(rf, egon_account)
        assert response.status_code == 200

    def test_scannerjoblistview_superuser(self, superuser_account, rf):
        """A superuser can see the list of scannerjobs."""
        response = self.get_scannerjoblistview_response(rf, superuser_account)
        assert response.status_code == 200

    def test_superuser_only_own_organization(
            self,
            superuser_account,
            egon_email_alias,
            hulk_email_alias,
            rf):
        """Superusers should only see scannerjobs from their own organization."""
        # Create some reports for Egon and Hulk, different organizations
        create_reports_for(
            egon_email_alias,
            num=10,
            scanner_job_pk=51,
            scanner_job_name="Scanner 1")
        create_reports_for(
            egon_email_alias,
            num=10,
            scanner_job_pk=52,
            scanner_job_name="Scanner 2")
        create_reports_for(
            hulk_email_alias,
            num=10,
            scanner_job_pk=53,
            scanner_job_name="Scanner A")

        response = self.get_scannerjoblistview_response(rf, superuser_account)
        scanners = [scanner.scanner_pk for scanner in response.context_data["scannerjobs"]]

        assert 51 in scanners
        assert 52 in scanners
        assert 53 not in scanners

    @pytest.mark.parametrize("handled,unhandled", [
        (1, 0),
        (10, 0),
        (0, 1),
        (0, 10),
        (10, 10)
    ])
    def test_correct_numbers_in_overview(self, rf, superuser_account, handled, unhandled,
                                         egon_email_alias):
        create_reports_for(
            egon_email_alias,
            num=unhandled,
        )
        create_reports_for(
            egon_email_alias,
            num=handled,
            resolution_status=1
        )

        response = self.get_scannerjoblistview_response(rf, superuser_account)

        scanners = response.context_data["scannerjobs"]

        assert len(scanners) == 1
        scanner = scanners[0]

        assert scanner.handled == handled
        assert scanner.unhandled == unhandled
        assert scanner.total == handled + unhandled

    # Helper functions

    def get_scannerjoblistview_response(self, rf, account, params='', **kwargs):
        request = rf.get(reverse_lazy('scannerjobs') + params)
        request.user = account.user
        return ScannerjobListView.as_view()(request, **kwargs)


@pytest.mark.django_db
class TestScannerjobDeleteView:
    def test_delete_scannerjobs_non_superuser_no_permission(self, client, egon_account,
                                                            egon_email_alias):
        """A non-superuser without permission can't delete scannerjobs."""
        create_reports_for(egon_email_alias, num=10, scanner_job_pk=10)
        response = self.post_scannerjobdeleteview_response(client, egon_account, 10)
        assert response.status_code == 403

    def test_delete_scannerjobs_non_superuser_permission(self, client, egon_account,
                                                         egon_email_alias):
        """A non-superuser with permission can delete scannerjobs."""
        create_reports_for(egon_email_alias, num=10, scanner_job_pk=10)
        egon_account.user.user_permissions.add(
            Permission.objects.get(codename="delete_documentreports"))
        response = self.post_scannerjobdeleteview_response(client, egon_account, 10)
        assert response.status_code == 302

    def test_delete_scannerjobs_superuser(self, client, superuser_account, egon_email_alias):
        """A superuser can delete scannerjobs."""
        create_reports_for(egon_email_alias, num=10, scanner_job_pk=10)
        response = self.post_scannerjobdeleteview_response(client, superuser_account, 10)
        assert response.status_code == 302

    def test_superuser_delete_from_own_organization(
            self, client, superuser_account, egon_email_alias):
        """A superuser can delete scannerjobs from own organization."""
        create_reports_for(
            egon_email_alias,
            num=10,
            scanner_job_pk=51,
            scanner_job_name="Scanner 1")
        create_reports_for(
            egon_email_alias,
            num=10,
            scanner_job_pk=52,
            scanner_job_name="Scanner 2")
        create_reports_for(
            egon_email_alias,
            num=10,
            scanner_job_pk=53,
            scanner_job_name="Scanner 3")

        self.post_scannerjobdeleteview_response(client, superuser_account, 52)

        assert DocumentReport.objects.filter(scanner_job__scanner_pk=51).count() == 10
        assert DocumentReport.objects.filter(scanner_job__scanner_pk=52).count() == 0
        assert DocumentReport.objects.filter(scanner_job__scanner_pk=53).count() == 10

    def test_superuser_delete_from_other_organization(
            self, client, superuser_account, egon_email_alias, hulk_email_alias):
        """Superusers cannot delete scannerjobs from other organizations."""
        # Create some reports for Egon and Hulk, different organizations
        create_reports_for(
            egon_email_alias,
            num=10,
            scanner_job_pk=51,
            scanner_job_name="Scanner 1")
        create_reports_for(
            egon_email_alias,
            num=10,
            scanner_job_pk=52,
            scanner_job_name="Scanner 2")
        create_reports_for(
            hulk_email_alias,
            num=10,
            scanner_job_pk=53,
            scanner_job_name="Scanner A")

        # Issuing a delete for a scannerjob from another organization.
        self.post_scannerjobdeleteview_response(client, superuser_account, 53)

        # No reports should be deleted
        assert DocumentReport.objects.filter(scanner_job__scanner_pk=53).count() == 10

    # Helper functions

    def post_scannerjobdeleteview_response(self, client, account, pk, **kwargs):
        client.force_login(account.user)
        response = client.post(reverse_lazy('delete_scannerjob', kwargs={'pk': pk}))
        return response
