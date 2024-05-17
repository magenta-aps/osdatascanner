import pytest
from django.urls import reverse_lazy

from ..models.usererrorlog import UserErrorLog


@pytest.mark.django_db
class TestExportUserErrorLog:
    url = reverse_lazy('export-error-log')

    @pytest.fixture(autouse=True)
    def enable_user_error_log(self, settings):
        settings.USERERRORLOG = True  # Need to override, it's False by default in pipeline

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

        client.force_login(user)
        response = client.get(self.url)
        streamed_rows = [row for row in response.streaming_content]

        assert response.status_code == 200
        assert len(streamed_rows) == 1

    def test_csv_export_usererrorlog_anonymous_user(self, client):
        """An anonymous user should be redirected."""
        response = client.get(self.url)
        assert response.status_code == 302
