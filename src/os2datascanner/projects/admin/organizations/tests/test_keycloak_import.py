import datetime
import pytest
from os2datascanner.projects.admin.import_services.models import LDAPConfig
from ..models import Account, OrganizationalUnit, Alias, Position
from .. import keycloak_actions
from ...adminapp.models.scannerjobs.scanner_helpers import CoveredAccount


@pytest.fixture
def TEST_CORP():
    return [
        {
            "id": "4f533264-6174-6173-6361-6e6e65720000",
            "username": "ted@test.invalid",
            "firstName": "Ted",
            "lastName": "Testsen",
            "attributes": {
                "LDAP_ENTRY_DN": [
                    "CN=Ted Testsen,OU=Testers,O=Test Corp."
                ],
                "LDAP_ID": ["144a7466-cbf4-4532-96b8-6d4109df074a"],
                "group_dn": "CN=Group 2,O=Test Corp."
            }
        },
        {
            "id": "4f533264-6174-6173-6361-6e6e65720001",
            "username": "todd@test.invalid",
            "firstName": "Todd",
            "lastName": "Testsen",
            "attributes": {
                "LDAP_ENTRY_DN": [
                    "CN=Todd Testsen,OU=Testers,O=Test Corp."
                ],
                "LDAP_ID": ["144a7466-cbf4-4532-96b8-6d4109df074b"],
                "group_dn": "CN=Group A,O=Test Corp."
            }
        },
        {
            "id": "4f533264-6174-6173-6361-6e6e65720001",
            "username": "todd@test.invalid",
            "firstName": "Todd",
            "lastName": "Testsen",
            "attributes": {
                "LDAP_ENTRY_DN": [
                    "CN=Todd Testsen,OU=Testers,O=Test Corp."
                ],
                "LDAP_ID": ["144a7466-cbf4-4532-96b8-6d4109df074b"],
                "group_dn": "CN=Group 1,O=Test Corp."
            }
        },
        {
            "id": "4f533264-6174-6173-6361-6e6e65720002",
            "username": "thad@test.invalid",
            "firstName": "Thad",
            "lastName": "Testsen",
            "attributes": {
                "LDAP_ENTRY_DN": [
                    "CN=Thad Testsen,OU=Testers,O=Test Corp."
                ],
                "LDAP_ID": ["144a7466-cbf4-4532-96b8-6d4109df074c"],
                "group_dn": "CN=Group A,O=Test Corp."
            }
        },
        {
            "attributes": {
                "LDAP_ENTRY_DN": [
                    "CN=secret_backdoor,OU=Testers,O=Test Corp."
                ],
                "LDAP_ID": ["144a7466-cbf4-4532-96b8-6d4109df074d"],
                "group_dn": "CN=Group A,O=Test Corp."
            }
        },
        {
            "id": "4f533264-6174-6173-6361-6e6e65720003",
            "username": "root@test.invalid",
            "attributes": {
                "LDAP_ENTRY_DN": [
                    "CN=root,OU=Testers,O=Test Corp."
                ],
                "LDAP_ID": ["144a7466-cbf4-4532-96b8-6d4109df074e"],
                "group_dn": "CN=Group A,O=Test Corp."
            }
        },
    ]


@pytest.fixture
def TEST_CORP_TWO():
    return [
        {
            "id": "4f533264-6174-6173-6361-6e6e65720010",
            "username": "ursula@test.invalid",
            "firstName": "Ursula",
            "lastName": "Testsen",
            "email": "ursulas@brevdue.dk",
            "attributes": {
                "LDAP_ENTRY_DN": [
                    "CN=Ursula Testsen,OU=TheUCorp,O=Test Corp."
                ],
                "LDAP_ID": ["144a7466-cbf4-4532-96b8-6d4109df0740"],
                "group_dn": "CN=Group 1,O=Test Corp."
            }
        },
        {
            "id": "4f533264-6174-6173-6361-6e6e65720010",
            "username": "ursula@test.invalid",
            "firstName": "Ursula",
            "lastName": "Testsen",
            "email": "ursulas@brevdue.dk",
            "attributes": {
                "LDAP_ENTRY_DN": [
                    "CN=Ursula Testsen,OU=TheUCorp,O=Test Corp."
                ],
                "LDAP_ID": ["144a7466-cbf4-4532-96b8-6d4109df0740"],
                "group_dn": "CN=Group 2,O=Test Corp."
            }
        },
        {
            "id": "4f533264-6174-6173-6361-6e6e65720011",
            "username": "ulrich@test.invalid",
            "firstName": "Ulrich",
            "lastName": "Testsen",
            "email": "ulrichs@brevdue.dk",
            "attributes": {
                "LDAP_ENTRY_DN": [
                    "CN=Ulrich Testsen,OU=TheUCorp,O=Test Corp."
                ],
                "LDAP_ID": ["144a7466-cbf4-4532-96b8-6d4109df0741"],
                "group_dn": "CN=Group 1,O=Test Corp."
            }
        },
        {
            "id": "4f533264-6174-6173-6361-6e6e65720011",
            "username": "ulrich@test.invalid",
            "firstName": "Ulrich",
            "lastName": "Testsen",
            "email": "ulrichs@brevdue.dk",
            "attributes": {
                "LDAP_ENTRY_DN": [
                    "CN=Ulrich Testsen,OU=TheUCorp,O=Test Corp."
                ],
                "LDAP_ID": ["144a7466-cbf4-4532-96b8-6d4109df0741"],
                "group_dn": "CN=Group 2,O=Test Corp."
            }
        },
    ]


@pytest.mark.django_db
class TestKeycloakImport:

    @pytest.fixture(autouse=True)
    def ldap_import_config(self, test_org):
        # A very minimalistic LDAPConfig
        return LDAPConfig.objects.create(organization=test_org,
                                         hide_units_on_import=False,
                                         last_modified=datetime.datetime(
                                                       2025, 9, 2, 12,
                                                       0, 0,
                                                       tzinfo=datetime.timezone.utc),
                                         _ldap_password="topsecret",
                                         search_scope=1,
                                         )

    # SECTION: perform_import_raw

    def perform_ou_import(self, remote, org):
        importer = keycloak_actions.KeycloakImporter(None)
        importer.org = org

        importer.perform_import_raw(
                remote,
                keycloak_actions.keycloak_dn_selector)

    def perform_group_import(self, remote, org):
        importer = keycloak_actions.KeycloakImporter(None)
        importer.org = org

        importer.perform_import_raw(
                remote,
                keycloak_actions.keycloak_group_dn_selector)

    def test_ou_import(self, TEST_CORP, test_org):
        """It should be possible to import users into a LDAP OU-based hierarchy
        from Keycloak's JSON output."""
        self.perform_ou_import(TEST_CORP, test_org)

        for tester in TEST_CORP:
            if "id" not in tester:
                continue
            account = Account.objects.get(uuid=tester["id"])
            assert tester['username'] == account.username, "user import failure"

    def test_ou_import_not_hidden(self, TEST_CORP, test_org):
        # Arrange: Fixtures

        # Act: Import
        self.perform_ou_import(TEST_CORP, test_org)

        # Assert: Check configuration and verify that no hidden units were created
        assert not test_org.importservice.hide_units_on_import
        assert not OrganizationalUnit.objects.filter(hidden=True).exists()
        assert OrganizationalUnit.objects.filter(hidden=False).exists()

    def test_ou_import_all_hidden(self, TEST_CORP, test_org, ldap_import_config):
        # Arrange
        ldap_import_config.hide_units_on_import = True
        ldap_import_config.save()

        # Act: Import
        self.perform_ou_import(TEST_CORP, test_org)

        # Assert: Check configuration and verify that only hidden units were created
        assert test_org.importservice.hide_units_on_import
        assert OrganizationalUnit.objects.filter(hidden=True).exists()
        assert not OrganizationalUnit.objects.filter(hidden=False).exists()

    def test_existing_ou_visible_new_hidden_ou_import(
            self, TEST_CORP, test_org, ldap_import_config):
        # Arrange: Import once, change config and add a new entry
        self.perform_ou_import(TEST_CORP, test_org)

        ldap_import_config.hide_units_on_import = True
        ldap_import_config.save()

        TEST_CORP.append(
            {
                "id": "1f111111-6174-6173-6361-6e6e99999999",
                "username": "Casper@the.ghost",
                "firstName": "Casper",
                "lastName": "The Ghost",
                "attributes": {
                    "LDAP_ENTRY_DN": [
                        "CN=Casper The Ghost,OU=Hide and seekers,O=Test Corp."
                        ],
                    "LDAP_ID": ["144a7466-6174-6173-6361-6d4109df074a"],
                    "group_dn": "CN=Hide and seekers group,O=Test Corp."
                    }
                }
        )

        # Act: Import again
        self.perform_ou_import(TEST_CORP, test_org)

        # Assert: Verify existing units are still visible and the new one is hidden
        assert OrganizationalUnit.objects.filter(name="Hide and seekers", hidden=True).exists()
        assert OrganizationalUnit.objects.filter(hidden=False).exists()

    def test_group_import(self, TEST_CORP, test_org):
        """It should be possible to import users into a group-based hierarchy
        from Keycloak's JSON output."""
        self.perform_group_import(TEST_CORP, test_org)

        for tester in TEST_CORP:
            if "id" not in tester:
                continue
            account = Account.objects.get(uuid=tester["id"])
            assert tester['username'] == account.username, "username incorrectly imported"

            group = tester.get("attributes", {}).get("group_dn", None)
            assert account.units.filter(imported_id=group).exists(), "user not in group"

    def test_group_import_not_hidden(self, TEST_CORP, test_org):
        # Arrange: Fixtures

        # Act: Import
        self.perform_group_import(TEST_CORP, test_org)

        # Assert: Check configuration and verify that no hidden units were created
        assert not test_org.importservice.hide_units_on_import
        assert not OrganizationalUnit.objects.filter(hidden=True).exists()
        assert OrganizationalUnit.objects.filter(hidden=False).exists()

    def test_group_import_all_hidden(self, TEST_CORP, test_org, ldap_import_config):
        # Arrange
        ldap_import_config.hide_units_on_import = True
        ldap_import_config.save()

        # Act: Import
        self.perform_group_import(TEST_CORP, test_org)

        # Assert: Check configuration and verify that only hidden units were created
        assert test_org.importservice.hide_units_on_import
        assert OrganizationalUnit.objects.filter(hidden=True).exists()
        assert not OrganizationalUnit.objects.filter(hidden=False).exists()

    def test_existing_ou_visible_new_hidden_group_import(
            self, TEST_CORP, test_org, ldap_import_config):
        # Arrange: Import once, change config and add a new entry
        self.perform_group_import(TEST_CORP, test_org)

        ldap_import_config.hide_units_on_import = True
        ldap_import_config.save()

        TEST_CORP.append(
            {
                "id": "1f111111-6174-6173-6361-6e6e99999999",
                "username": "Casper@the.ghost",
                "firstName": "Casper",
                "lastName": "The Ghost",
                "attributes": {
                    "LDAP_ENTRY_DN": [
                        "CN=Casper The Ghost,OU=Hide and seekers,O=Test Corp."
                        ],
                    "LDAP_ID": ["144a7466-6174-6173-6361-6d4109df074a"],
                    "group_dn": "CN=Hide and seekers group,O=Test Corp."
                    }
                }
        )

        # Act: Import again
        self.perform_group_import(TEST_CORP, test_org)

        # Assert: Verify existing units are still visible and the new one is hidden
        assert OrganizationalUnit.objects.filter(
            name="Hide and seekers group", hidden=True).exists()
        assert OrganizationalUnit.objects.filter(hidden=False).exists()

    def test_removal(self, TEST_CORP, test_org):
        """Removing a user from Keycloak's JSON output should also remove that
        user from the database."""
        self.perform_ou_import(TEST_CORP, test_org)

        thads = list(Account.objects.filter(first_name="Thad"))

        self.perform_ou_import(
            [
                tester
                for tester in TEST_CORP
                if tester.get("firstName") != "Thad"
            ],
            test_org
        )

        for thad in thads:
            with pytest.raises(Account.DoesNotExist):
                thad.refresh_from_db()

    def test_group_change_ou(self, TEST_CORP, test_org):
        """Changing the LDAP DN of a user in a group-based hierarchy should
        change their properties without affecting their positions."""
        self.perform_group_import(TEST_CORP, test_org)

        todds = list(Account.objects.filter(first_name="Todd"))

        for tester in TEST_CORP:
            if tester.get("firstName") == "Todd":
                tester["attributes"]["LDAP_ENTRY_DN"] = [
                        f"CN=Todd {tester['lastName']},"
                        "OU=Experimenters,O=Test Corp."]

        self.perform_group_import(TEST_CORP, test_org)

        for todd in todds:
            todd.refresh_from_db()
            assert "OU=Experimenters" in todd.distinguished_name, "DN did not change"

    def test_change_group(self, TEST_CORP, test_org):
        """It should be possible to move a user from one group to another."""
        self.perform_group_import(TEST_CORP, test_org)

        teds = list(Account.objects.filter(first_name="Ted"))

        for ted in teds:
            ted.units.get(imported_id="CN=Group 2,O=Test Corp.")
            with pytest.raises(OrganizationalUnit.DoesNotExist):
                ted.units.get(imported_id="CN=Group 1,O=Test Corp.")

        for tester in TEST_CORP:
            if tester.get("firstName") == "Ted":
                tester["attributes"]["group_dn"] = "CN=Group 1,O=Test Corp."

        self.perform_group_import(TEST_CORP, test_org)

        for ted in teds:
            ted.refresh_from_db()
            ted.units.get(imported_id="CN=Group 1,O=Test Corp.")
            with pytest.raises(OrganizationalUnit.DoesNotExist):
                ted.units.get(imported_id="CN=Group 2,O=Test Corp.")

    def test_remove_ou(self, TEST_CORP, test_org):
        """Removing every user from a group or organisational unit should
        remove its representation in the database."""
        self.perform_group_import(TEST_CORP, test_org)

        OrganizationalUnit.objects.get(imported_id="CN=Group 2,O=Test Corp.")

        for tester in TEST_CORP:
            if tester["attributes"]["group_dn"] == "CN=Group 2,O=Test Corp.":
                tester["attributes"]["group_dn"] = None

        self.perform_group_import(TEST_CORP, test_org)

        with pytest.raises(OrganizationalUnit.DoesNotExist):
            OrganizationalUnit.objects.get(
                    imported_id="CN=Group 2,O=Test Corp.")

    def test_import_user_in_multiple_groups_should_only_get_one_email_alias(
            self, TEST_CORP_TWO, test_org):
        """ A user can be a member of multiple groups, but it is still only one
        user, and should result in only one email-alias (given that the user
        has an email attribute)"""
        self.perform_group_import(TEST_CORP_TWO, test_org)

        ursula_aliases = Alias.objects.filter(_value="ursulas@brevdue.dk")

        assert ursula_aliases.count() == 1, "Either duplicate or no email aliases for user created"

    def test_delete_user_relation_to_group(self, TEST_CORP_TWO, test_org):
        self.perform_group_import(TEST_CORP_TWO, test_org)

        ursula = TEST_CORP_TWO[0]
        account = Account.objects.get(uuid=ursula["id"])

        assert Position.objects.filter(
            account=account).count() == 2, "Position not correctly created"

        # Now only member of one group instead of two.
        TEST_CORP_TWO[0]["attributes"]["group_dn"] = None

        # Import again
        self.perform_group_import(TEST_CORP_TWO, test_org)

        assert Position.objects.filter(
            account=account).count() == 1, "Position not updated correctly"

        # The OU should still exist though, as there is still a user with a
        # connection to it.
        assert OrganizationalUnit.objects.filter(
            imported_id="CN=Group 1,O=Test Corp.").exists(), "OU doesn't exist but should"

        # Delete Ulrich from the TEST_CORP_TWO
        del TEST_CORP_TWO[2:3]

        # Import again
        self.perform_group_import(TEST_CORP_TWO, test_org)

        # The OU should now not exist as there is no user with a connection to
        # it.
        assert not OrganizationalUnit.objects.filter(
            imported_id="CN=Group 1,O=Test Corp.").exists(), "OU is not deleted"

    def test_property_update(self, TEST_CORP, test_org):
        """Changing a user's name should update the corresponding properties in
        the database."""
        self.perform_ou_import(TEST_CORP, test_org)

        for user in Account.objects.filter(organization=test_org):
            assert user.first_name != "Tadeusz", "premature or invalid property update(?)"

        for tester in TEST_CORP:
            try:
                # The hero of the Polish epic poem Pan Tadeusz, since you ask
                # (the first line of which is "O Lithuania, my homeland!")
                tester["firstName"] = "Tadeusz"
                tester["lastName"] = "Soplica"
            except ValueError:
                pass

        self.perform_ou_import(TEST_CORP, test_org)

        for user in Account.objects.filter(organization=test_org):
            assert (user.first_name, user.last_name) == (
                "Tadeusz", "Soplica"), "property update failed"

    def test_import_and_creation_of_managers(self, TEST_CORP, test_org):
        """It should be possible to add managers based on the Keycloak output."""

        importer = keycloak_actions.KeycloakImporter(None)
        importer.org = test_org
        importer.account_manager_positions = {
            TEST_CORP[0]["attributes"]["LDAP_ENTRY_DN"][0]: [TEST_CORP[0]["attributes"]["group_dn"]]
        }

        importer.perform_import_raw(
            TEST_CORP,
            keycloak_actions.keycloak_group_dn_selector,
            do_manager_import=True
        )

        # Get Ted Testsen
        account = Account.objects.get(uuid=TEST_CORP[0]["id"])

        # Get Group 1.
        unit = OrganizationalUnit.objects.get(imported_id=TEST_CORP[0]["attributes"]["group_dn"])

        manager = Position.managers.get(account=account, unit=unit)

        assert manager == account.positions.get(role="manager", unit=unit), "manager not imported"

    def test_empty_manager_update(self, TEST_CORP, test_org):
        """It should be possible to remove managers based on the Keycloak output.
        If there are none remotely, but local managers still exist, they should be deleted."""

        # Import, create manager Position for Ted Testsen
        importer = keycloak_actions.KeycloakImporter(None)
        importer.org = test_org
        importer.account_manager_positions = {
            TEST_CORP[0]["attributes"]["LDAP_ENTRY_DN"][0]: [TEST_CORP[0]["attributes"]["group_dn"]]
        }

        importer.perform_import_raw(
            TEST_CORP,
            keycloak_actions.keycloak_group_dn_selector,
            do_manager_import=True
        )

        # Import again, with no managers
        importer.reset()
        importer.perform_import_raw(
            TEST_CORP,
            keycloak_actions.keycloak_group_dn_selector,
            do_manager_import=True
        )

        # Get manager account
        account = Account.objects.get(uuid=TEST_CORP[0]["id"])
        unit = OrganizationalUnit.objects.get(imported_id=TEST_CORP[0]["attributes"]["group_dn"])

        assert Position.managers.filter(
            account=account, unit=unit).exists() is False, "manager not removed"

    def test_change_ou(self, TEST_CORP, test_org, basic_scanner, basic_scanstatus):
        """When a user is moved between ou's, they should still be imported as the same user.
        They shouldn't be deleted and recreated, as this also deletes CoveredAccounts etc."""
        self.perform_ou_import(TEST_CORP, test_org)

        ted = Account.objects.get(first_name="Ted")
        CoveredAccount.objects.create(
            account=ted,
            scanner=basic_scanner,
            scan_status=basic_scanstatus,
        )

        for tester in TEST_CORP:
            if tester.get("firstName") == "Ted":
                tester["attributes"]["LDAP_ENTRY_DN"] = ["CN=Ted Testsen,OU=TheUCorp,O=Test Corp."]

        self.perform_ou_import(TEST_CORP, test_org)
        ted = Account.objects.get(first_name="Ted")

        assert CoveredAccount.objects.filter(account=ted).exists()
