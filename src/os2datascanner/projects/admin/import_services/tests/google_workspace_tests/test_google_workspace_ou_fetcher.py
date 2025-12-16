import pytest
from unittest.mock import MagicMock
from ...google_workspace_client import GoogleWorkspaceClient


@pytest.mark.django_db
def test_fetch_ou_list_flattens_nested_structure():
    """
    Tests that fetch_ou_list() flattens nested organizational units
    into a single flat list of all OUs.
    """

    service_account_info = {"type": "service_account", "project_id": "test"}
    client = GoogleWorkspaceClient(
        service_account_info=service_account_info,
        admin_email="admin@example.com",
    )

    # Arrange
    mock_directory = MagicMock()
    mock_directory.orgunits.return_value.list.return_value.execute.return_value = {
        "organizationUnits": [
            {
                "orgUnitId": "A",
                "name": "Dept A",
                "orgUnitPath": "/A",
                "parentOrgUnitId": None,
            },
            {
                "orgUnitId": "B",
                "name": "Dept B",
                "orgUnitPath": "/A/B",
                "parentOrgUnitId": "A",
            },
            {
                "orgUnitId": "C",
                "name": "Dept C",
                "orgUnitPath": "/C",
                "parentOrgUnitId": None,
            },
        ],
        "nextPageToken": None
    }

    client.directory = mock_directory
    client.customer_id = "test_customer"

    # Act
    result = client.list_organizational_units()

    # Assert
    dept_b = next(ou for ou in result if ou["orgUnitId"] == "B")
    assert dept_b["parentOrgUnitId"] == "A"
