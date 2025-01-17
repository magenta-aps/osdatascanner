import pytest
from django.urls import reverse_lazy
from django.contrib.auth.models import Permission
from datetime import timedelta, datetime

from ..models.usererrorlog import UserErrorLog
from ..models.scannerjobs.scanner_helpers import ScanStatus


@pytest.mark.django_db
class TestExportUserErrorLog:
    url = reverse_lazy('export-error-log')

    @pytest.fixture
    def error_logs(self, test_org, basic_scanstatus):

        err_logs = []
        for i in range(10):
            err_logs.append(UserErrorLog(
                scan_status=basic_scanstatus,
                organization=test_org,
                path=f"({i}) This is the way!",
                error_message="Something is wrong :(", )
            )

        UserErrorLog.objects.bulk_create(err_logs)

    def test_csv_export_usererrorlog_as_org_admin(
            self,
            error_logs,
            user_admin,
            client,
            test_org2,
            basic_scanstatus2):
        """Admins for an organization should be able to export the usererrorlogs
        from their own organization."""

        # Grant permission for viewing usererrorlog list
        user_admin.user_permissions.add(Permission.objects.get(codename='export_usererrorlog'))

        UserErrorLog.objects.create(
            scan_status=basic_scanstatus2,
            organization=test_org2,
            path="You can't see me",
            error_message="Something is wrong :(")

        client.force_login(user_admin)
        response = client.get(self.url)
        streamed_rows = [row for row in response.streaming_content]

        assert response.status_code == 200
        assert len(streamed_rows) == 10 + 1

    def test_csv_export_usererrorlog_unprivileged_user(self, error_logs, user, client):
        """A user unrelated to an organization should only get header values."""

        # Grant permission for viewing usererrorlog list
        user.user_permissions.add(Permission.objects.get(codename='export_usererrorlog'))

        client.force_login(user)
        response = client.get(self.url)
        streamed_rows = [row for row in response.streaming_content]

        assert response.status_code == 200
        assert len(streamed_rows) == 1

    def test_csv_export_usererrorlog_anonymous_user(self, client):
        """An anonymous user should be redirected."""
        response = client.get(self.url)
        assert response.status_code == 302

    def test_csv_export_user_without_permission(self, client, user_admin):
        """A user without permission to view usererrorlogs should get a 403
        status code."""
        client.force_login(user_admin)
        response = client.get(self.url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestExportCompletedScanStatus:
    url = reverse_lazy('export-status-completed')

    @pytest.fixture()
    def completed_statuses(self, basic_scanner):
        stati = []
        now = datetime.today()
        for i in range(1, 11):
            status = ScanStatus(
                scanner=basic_scanner,
                scan_tag=basic_scanner._construct_scan_tag().to_json_object(),
                total_objects=i,
                scanned_objects=i,
                explored_sources=i,
                total_sources=i)
            status.scan_tag['time_stamp'] = (now + timedelta(seconds=5 * i)).isoformat()
            stati.append(status)

        ScanStatus.objects.bulk_create(stati)

    def test_csv_export_completed_scans_as_org_admin(
            self,
            user_admin,
            completed_statuses,
            client,
            basic_scanner2):
        """Admins for an organization should be able to export the completed scans
        from their own organization."""
        # Arrange
        # Create status from other org
        ScanStatus(
            scanner=basic_scanner2,
            scan_tag=basic_scanner2._construct_scan_tag().to_json_object(),
            total_objects=1,
            scanned_objects=1,
            explored_sources=1,
            total_sources=1,
        )
        # Grant permission for exporting completed scan statuses
        user_admin.user_permissions.add(
            Permission.objects.get(
                codename='export_completed_scanstatus'))
        client.force_login(user_admin)

        # Act
        response = client.get(self.url)
        streamed_rows = [row for row in response.streaming_content]

        # Assert
        assert response.status_code == 200
        assert len(streamed_rows) == 10 + 1

    def test_csv_export_completed_scans_unprivileged_user(self, user, completed_statuses, client):
        """A user unrelated to an organization should only get header values."""
        # Arrange
        # Grant permission for exporting completed scan statuses
        user.user_permissions.add(Permission.objects.get(codename='export_completed_scanstatus'))
        client.force_login(user)

        # Act
        response = client.get(self.url)
        streamed_rows = [row for row in response.streaming_content]

        # Assert
        assert response.status_code == 200
        assert len(streamed_rows) == 1

    def test_csv_export_completed_scans_anonymous_user(self, client):
        """An anonymous user should be redirected."""
        # Act
        response = client.get(self.url)

        # Assert
        assert response.status_code == 302

    def test_csv_export_completed_scans_user_without_permission(
            self, user_admin, completed_statuses, client):
        """A user without permission to export completed scans should get a 403 status code."""
        client.force_login(user_admin)
        response = client.get(self.url)
        assert response.status_code == 403
