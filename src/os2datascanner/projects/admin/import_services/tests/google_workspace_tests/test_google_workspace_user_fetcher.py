import pytest
from unittest.mock import Mock
from ...google_workspace_client import GoogleWorkspaceClient


@pytest.mark.django_db
class TestGoogleWorkspaceUsers:

    def test_fetch_users(self):
        """
        Verifies that fetch_users returns correct user data
        when the client provides a list of users.
        """

        # Arrange
        mock_directory = Mock()
        mock_directory.users.return_value.list.return_value.execute.return_value = {
            "users": [
                {
                    "id": "user_001",
                    "primaryEmail": "alice.smith@example.com",
                    "name": {
                        "givenName": "Alice",
                        "familyName": "Smith",
                        "fullName": "Alice Smith",
                    },
                    "orgUnitPath": "/Engineering/Backend",
                }
            ],
            "nextPageToken": None
        }

        service_account_info = {"type": "service_account", "project_id": "test"}
        client = GoogleWorkspaceClient(
            service_account_info=service_account_info,
            admin_email="admin@example.com",
        )
        client.directory = mock_directory
        client.customer_id = "test_customer"

        # Act
        users = list(client.list_users())

        # Assert
        assert len(users) == 1
        assert users[0]["id"] == "user_001"
        assert users[0]["primaryEmail"] == "alice.smith@example.com"
        assert users[0]["name"]["givenName"] == "Alice"
