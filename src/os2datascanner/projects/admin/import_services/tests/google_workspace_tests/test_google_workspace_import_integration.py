import pytest
import json
import uuid
from unittest.mock import patch, MagicMock
from ...models.google_workspace_import_job import GoogleWorkspaceImportJob
from .....grants.models import GoogleApiGrant


def fake_authenticate(self):
    """Mock authenticate to avoid actual Google API calls."""
    mock_directory = MagicMock()
    self.directory = mock_directory
    self.customer_id = "test_customer"


@pytest.mark.django_db
@patch("os2datascanner.projects.admin.import_services.google_workspace_client.GoogleWorkspaceClient.authenticate", new=fake_authenticate)  # noqa
@patch("os2datascanner.projects.admin.import_services.google_workspace_client.GoogleWorkspaceClient.list_organizational_units")  # noqa
@patch("os2datascanner.projects.admin.import_services.google_workspace_client.GoogleWorkspaceClient.list_users")  # noqa
def test_google_workspace_import_counts_entities_correctly(
        mock_list_users,
        mock_list_ous,
        test_org):
    """
    Tests that a full Google Workspace import correctly maps and counts
    organizational units (OUs), and users.
    """

    # Arrange
    org = test_org

    grant = GoogleApiGrant.objects.create(
        service_account=json.dumps({
            "type": "service_account",
            "project_id": "fake-project",
            "private_key_id": "fake_key_id",
            "private_key": "-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----\n",
            "client_email": "fake@fakeproject.iam.gserviceaccount.com",
            "client_id": "1234567890",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/fake%40fakeproject.iam.gserviceaccount.com"  # noqa
        }),
        organization=org
    )

    # valid UUIDs
    root_id = str(uuid.uuid4())
    team_id = str(uuid.uuid4())

    mock_list_ous.return_value = [
        {
            "orgUnitId": root_id,
            "name": "Root",
            "orgUnitPath": "/",
            "parentOrgUnitId": None
        },
        {
            "orgUnitId": team_id,
            "name": "Team",
            "orgUnitPath": "/Team",
            "parentOrgUnitId": root_id
        },
    ]

    mock_list_users.return_value = iter([
        {
            "primaryEmail": "alice@example.com",
            "name": {"givenName": "Alice", "familyName": "Andersson"},
            "orgUnitPath": "/Team",
        }
    ])

    job = GoogleWorkspaceImportJob.objects.create(
        organization=org,
        grant=grant,
        delegated_admin_email="admin@example.com",
    )

    # Act
    result = job.run()

    # Assert
    assert result == {
        "ous": 2,
        "users": 1,
        "ou_positions": 1,
        "aliases": 0
    }
