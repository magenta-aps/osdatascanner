import pytest
from unittest.mock import MagicMock

from ....organizations.models import Account
from ....organizations.models import OrganizationalUnit
from ....organizations.models.aliases import AliasType
from ...models.google_workspace_import_job import GoogleWorkspaceImportJob
from ....core.models import Client

from ....organizations.models import Organization


@pytest.mark.django_db
class TestGoogleWorkspaceUserMapper:

    @pytest.fixture
    def organization(self, client):
        """Create an organization for testing."""

        return Organization.objects.create(
            name="TestOrg",
            slug="testorg",
            client=client
        )

    @pytest.fixture
    def client(self):
        """Create a client."""
        return Client.objects.create(
            name="Test Client"
        )

    @pytest.fixture
    def ou_structure(self, organization):
        """
        Create an OU hierarchy.
        Used to test orgUnitPath matching.
        """
        root = OrganizationalUnit.objects.create(
            uuid="11111111-1111-1111-1111-111111111111",
            name="Root",
            organization=organization
        )
        sub = OrganizationalUnit.objects.create(
            uuid="22222222-2222-2222-2222-222222222222",
            name="Sub",
            parent=root,
            organization=organization
        )
        return root, sub

    @pytest.fixture
    def make_job(self, organization):
        return GoogleWorkspaceImportJob(
            organization=organization,
            delegated_admin_email="admin@example.com"
        )

    @pytest.fixture
    def make_account(self, organization):
        return Account.objects.create(
            username="user@test.com",
            email="user@test.com",
            organization=organization
        )

    def test_creates_account(self, organization, make_job):
        """Tests basic Account creation from user data."""

        # Arrange
        user_data = [{
            "primaryEmail": "user@test.com",
            "name": {"givenName": "John", "familyName": "Doe"},
        }]

        client = MagicMock()
        client.list_users.return_value = user_data

        # Act
        ((new_accounts, updates, account_map, imported_ids),
         raw_users) = make_job._fetch_and_map_users(client)

        # Assert
        assert len(new_accounts) == 1
        acc = new_accounts[0]
        assert acc.username == "user@test.com"
        assert acc.email == "user@test.com"
        assert acc.first_name == "John"
        assert acc.last_name == "Doe"
        assert acc.organization == organization
        assert len(updates) == 0

    def test_maps_aliases(self, organization, make_job, make_account):
        """Tests alias creation for accounts."""

        # Arrange
        user_data = [{
            "primaryEmail": "user@test.com",
            "aliases": ["alt1@test.com", "alt2@test.com"],
        }]

        account_map = {
            "user@test.com": make_account
        }

        # Act
        aliases, _ = make_job._create_user_aliases(user_data, account_map)

        # Assert
        values = {a._value for a in aliases}
        assert values == {"alt1@test.com", "alt2@test.com"}
        for a in aliases:
            assert a._alias_type == AliasType.EMAIL

    def test_ou_path_creates_position(self, organization, ou_structure, make_account, make_job):
        """Tests that orgUnitPath assigns the user to the correct OU."""

        # Arrange
        root, sub = ou_structure
        root.path = "/Root"
        sub.path = "/Root/Sub"
        root.save()
        sub.save()
        user_data = [{
            "primaryEmail": "user@test.com",
            "orgUnitPath": "/Root/Sub"
        }]

        account_map = {
            "user@test.com": make_account
        }

        # Act
        ou_map = {
            "google-ou:root-id": root,
            "google-ou:sub-id": sub
        }
        positions, _ = make_job._create_ou_positions(user_data, account_map, ou_map)

        # Assert
        assert len(positions) == 1
        assert positions[0].unit == sub
        assert positions[0].account == make_account

    def test_ou_path_not_found_creates_no_position(self, organization, make_job, make_account):
        """Tests that a bad orgUnitPath doesn't create a Position."""

        # Arrange
        user_data = [{
            "primaryEmail": "user@test.com",
            "orgUnitId": "non-existent-id"
        }]

        account_map = {
            "user@test.com": make_account
        }

        # Act
        positions, _ = make_job._create_ou_positions(user_data, account_map, {})

        # Assert
        assert positions == []

    def test_user_without_primary_email_is_skipped(self, organization, make_job):
        """Tests Position creation via group membership."""

        # Arrange
        user_data = [
            {"name": {"givenName": "No", "familyName": "Email"}},
            {"primaryEmail": "valid@test.com"},
        ]

        client = MagicMock()
        client.list_users.return_value = user_data

        # Act
        (new_accounts, _, _, _), _ = make_job._fetch_and_map_users(client)

        # Assert
        assert len(new_accounts) == 1
        assert new_accounts[0].username == "valid@test.com"

    def test_idempotent_import(self, organization, make_job):

        # Assert
        user_data = [{
            "primaryEmail": "user@test.com",
            "aliases": ["alias@test.com"]
        }]

        client = MagicMock()
        client.list_users.return_value = user_data

        # Act
        (new_accounts_1, updates_1, account_map_1, _), _ = make_job._fetch_and_map_users(client)

        # Assert
        assert len(new_accounts_1) == 1
        assert len(updates_1) == 0

        # Save the account to database
        new_accounts_1[0].save()

        # Second import - should update existing account
        (new_accounts_2, updates_2, account_map_2, _), _ = make_job._fetch_and_map_users(client)

        assert len(new_accounts_2) == 0  # No new accounts
        assert len(updates_2) == 1  # One account to update
        assert updates_2[0][0].username == "user@test.com"
