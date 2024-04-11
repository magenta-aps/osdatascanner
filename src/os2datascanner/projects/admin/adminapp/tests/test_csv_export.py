import pytest
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

from os2datascanner.projects.admin.adminapp.models.rules import CustomRule

from tests.test_utilities import dummy_rule_dict
from ...organizations.models import Organization
from ..models.usererrorlog import UserErrorLog
from ..models.scannerjobs.scanner import Scanner, ScanStatus
from ...core.models import Administrator, Client


@pytest.mark.django_db
class TestExportUserErrorLog:
    url = reverse_lazy('export-error-log')

    @pytest.fixture(autouse=True)
    def enable_user_error_log(self, settings):
        settings.USERERRORLOG = True  # Need to override, it's False by default in pipeline

    @pytest.fixture(autouse=True)
    def test_org(self):
        client = Client.objects.create(name='test_client')
        return Organization.objects.create(name='test_org', client=client)

    @pytest.fixture
    def user(self):
        return get_user_model().objects.create(username='mr_userman', password='hunter2')

    @pytest.fixture
    def admin(self, test_org):
        admin_user = get_user_model().objects.create(username='hagrid', password='shelob')
        Administrator.objects.create(user=admin_user, client=test_org.client)
        return admin_user

    @pytest.fixture
    def error_logs(self, test_org):
        org = test_org
        rule = CustomRule.objects.create(**dummy_rule_dict)
        scanner = Scanner.objects.create(
            name=f"SomeScanner-{org.name}",
            organization=org,
            rule=rule
        )
        status = ScanStatus.objects.create(
            scanner=scanner,
            scan_tag=scanner._construct_scan_tag().to_json_object())

        err_logs = []
        for i in range(10):
            err_logs.append(UserErrorLog(
                scan_status=status,
                organization=org,
                path=f"({i}) This is the way!",
                error_message="Something is wrong :(", )
            )

        UserErrorLog.objects.bulk_create(err_logs)

    def test_csv_export_usererrorlog_as_org_admin(self, error_logs, admin, admin_client):
        """Admins for an organization should be able to export the usererrorlogs
        from their own organization."""

        # Creating some errors for another client, the user should not be able
        # to see these.
        other_client = Client.objects.create(name='other_client')
        other_org = Organization.objects.create(name='other_org', client=other_client)

        scanner = Scanner.objects.create(
            name=f"SomeScanner-{other_org.name}",
            organization=other_org,
            rule=CustomRule.objects.first())
        status = ScanStatus.objects.create(
            scanner=scanner,
            scan_tag=scanner._construct_scan_tag().to_json_object())
        UserErrorLog.objects.create(
            scan_status=status,
            organization=other_org,
            path="You can't see me",
            error_message="Something is wrong :(")

        admin_client.force_login(admin)
        response = admin_client.get(self.url)
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
