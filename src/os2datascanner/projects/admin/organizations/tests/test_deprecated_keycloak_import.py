import datetime

import pytest
from copy import deepcopy

from os2datascanner.projects.admin.import_services.models import LDAPConfig
from ..models import Account, OrganizationalUnit, Alias, Position
from .. import keycloak_actions

TEST_CORP = [
    {
        "id": "4f533264-6174-6173-6361-6e6e65720000",
        "username": "ted@test.invalid",
        "firstName": "Ted",
        "lastName": "Testsen",
        "attributes": {
            "LDAP_ENTRY_DN": [
                "CN=Ted Testsen,OU=Testers,O=Test Corp."
            ],
            "memberOf": [
                "CN=Group 2,O=Test Corp."
            ]
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
            "memberOf": [
                "CN=Group 1,O=Test Corp.",
                "CN=Group A,O=Test Corp."
            ]
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
            "memberOf": [
                "CN=Group A,O=Test Corp."
            ]
        }
    },
    {
        "id": "4f533264-6174-6173-6361-6e6e65720003",
        "username": "root@test.invalid",
        "attributes": {
            "LDAP_ENTRY_DN": [
                "CN=root,OU=Testers,O=Test Corp."
            ],
            "memberOf": [
                "CN=Group A,O=Test Corp."
            ]
        }
    },
    {
        "attributes": {
            "LDAP_ENTRY_DN": [
                "CN=secret_backdoor,OU=Testers,O=Test Corp."
            ],
            "memberOf": [
                "CN=Group A,O=Test Corp."
            ]
        }
    },
]

TEST_CORP_TWO = [
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
            "memberOf": [
                "CN=Group 1,O=Test Corp.",
                "CN=Group 2,O=Test Corp."
            ]
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
            "memberOf": [
                "CN=Group 1,O=Test Corp.",
                "CN=Group 2,O=Test Corp."
            ]
        }
    },

]


@pytest.mark.django_db
class TestDeprecatedKeycloakImportTest:
    """As of #60117 we don't import memberOf attributes, but instead give
    users an attribute 'group_dn'. However, until clients update their LDAP configuration,
    they will still use the old memberOf based logic. Therefore, these tests have been preserved,
    to ensure the deprecated logic still works."""

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

    def test_ou_import(self, test_org):
        """It should be possible to import users into an LDAP OU-based hierarchy
        from Keycloak's JSON output."""
        keycloak_actions.perform_import_raw(
            test_org, TEST_CORP,
            keycloak_actions.keycloak_dn_selector
        )

        for tester in TEST_CORP:
            if "id" not in tester:
                continue
            account = Account.objects.get(uuid=tester["id"])
            assert tester["username"] == account.username, "user import failure"

    def test_group_import(self, test_org):
        """It should be possible to import users into a group-based hierarchy
        from Keycloak's JSON output."""
        keycloak_actions.perform_import_raw(
            test_org, TEST_CORP,
            keycloak_actions.keycloak_group_dn_selector
        )

        for tester in TEST_CORP:
            if "id" not in tester:
                continue
            account = Account.objects.get(uuid=tester["id"])
            assert tester["username"] == account.username

            for group in tester.get("attributes", {}).get("memberOf", []):
                assert account.units.filter(imported_id=group).exists()

    def test_removal(self, test_org):
        """Removing a user from Keycloak's JSON output should also remove that
        user from the database."""
        self.test_ou_import(test_org)

        thads = list(Account.objects.filter(first_name="Thad"))

        keycloak_actions.perform_import_raw(
            test_org,
            [t for t in TEST_CORP if t.get("firstName") != "Thad"],
            keycloak_actions.keycloak_dn_selector
        )

        for thad in thads:
            with pytest.raises(Account.DoesNotExist):
                thad.refresh_from_db()

    def test_group_change_ou(self, test_org):
        """Changing the LDAP DN of a user in a group-based hierarchy should
        change their properties without affecting their positions."""
        self.test_group_import(test_org)

        todds = list(Account.objects.filter(first_name="Todd"))

        NEW_CORP = deepcopy(TEST_CORP)
        for tester in NEW_CORP:
            if tester.get("firstName") == "Todd":
                tester["attributes"]["LDAP_ENTRY_DN"] = [
                    f"CN=Todd {tester['lastName']},OU=Experimenters,O=Test Corp."
                ]

        keycloak_actions.perform_import_raw(
            test_org, NEW_CORP,
            keycloak_actions.keycloak_group_dn_selector
        )

        for todd in todds:
            todd.refresh_from_db()
            assert "OU=Experimenters" in todd.imported_id

    def test_change_group(self, test_org):
        """It should be possible to move a user from one group to another."""
        self.test_group_import(test_org)

        teds = list(Account.objects.filter(first_name="Ted"))

        for ted in teds:
            ted.units.get(imported_id="CN=Group 2,O=Test Corp.")
            with pytest.raises(OrganizationalUnit.DoesNotExist):
                ted.units.get(imported_id="CN=Group 1,O=Test Corp.")

        NEW_CORP = deepcopy(TEST_CORP)
        for tester in NEW_CORP:
            if tester.get("firstName") == "Ted":
                tester["attributes"]["memberOf"] = ["CN=Group 1,O=Test Corp."]

        keycloak_actions.perform_import_raw(
            test_org, NEW_CORP,
            keycloak_actions.keycloak_group_dn_selector
        )

        for ted in teds:
            ted.refresh_from_db()
            ted.units.get(imported_id="CN=Group 1,O=Test Corp.")
            with pytest.raises(OrganizationalUnit.DoesNotExist):
                ted.units.get(imported_id="CN=Group 2,O=Test Corp.")

    def test_remove_ou(self, test_org):
        """Removing every user from a group or organisational unit should
        remove its representation in the database."""
        self.test_group_import(test_org)

        OrganizationalUnit.objects.get(imported_id="CN=Group 2,O=Test Corp.")

        NEW_CORP = deepcopy(TEST_CORP)
        for tester in NEW_CORP:
            try:
                tester["attributes"]["memberOf"].remove("CN=Group 2,O=Test Corp.")
            except ValueError:
                pass

        keycloak_actions.perform_import_raw(
            test_org, NEW_CORP,
            keycloak_actions.keycloak_group_dn_selector
        )

        with pytest.raises(OrganizationalUnit.DoesNotExist):
            OrganizationalUnit.objects.get(imported_id="CN=Group 2,O=Test Corp.")

    def test_import_user_in_multiple_groups_should_only_get_one_email_alias(self, test_org):
        """ A user can be a memberOf multiple groups, but it is still only one
        user, and should result in only one email-alias (given that the user
        has an email attribute)"""
        keycloak_actions.perform_import_raw(
            test_org, TEST_CORP_TWO,
            keycloak_actions.keycloak_group_dn_selector
        )

        ursula_aliases = Alias.objects.filter(_value="ursulas@brevdue.dk")
        assert ursula_aliases.count() == 1

    def test_delete_user_relation_to_group(self, test_org):
        keycloak_actions.perform_import_raw(
            test_org, TEST_CORP_TWO,
            keycloak_actions.keycloak_group_dn_selector
        )

        ursula = TEST_CORP_TWO[0]
        account = Account.objects.get(uuid=ursula["id"])
        assert Position.objects.filter(account=account).count() == 2

        NEW_CORP = deepcopy(TEST_CORP_TWO)
        # Now only member of one group instead of two.
        NEW_CORP[0]["attributes"]["memberOf"] = ["CN=Group 2,O=Test Corp."]

        # Import again
        keycloak_actions.perform_import_raw(
            test_org, NEW_CORP,
            keycloak_actions.keycloak_group_dn_selector
        )

        assert Position.objects.filter(account=account).count() == 1
        # The OU should still exist though, as there is still a user with a
        # connection to it.
        assert OrganizationalUnit.objects.filter(
            imported_id="CN=Group 1,O=Test Corp.").exists()

        # Delete Ulrich from the TEST_CORP_TWO
        del NEW_CORP[1]

        # Import again
        keycloak_actions.perform_import_raw(
            test_org, NEW_CORP,
            keycloak_actions.keycloak_group_dn_selector
        )

        # The OU should now not exist as there is no user with a connection to
        # it.
        assert not OrganizationalUnit.objects.filter(
            imported_id="CN=Group 1,O=Test Corp.").exists()

    def test_property_update(self, test_org):
        """Changing a user's name should update the corresponding properties in
        the database."""
        self.test_ou_import(test_org)

        for acc in Account.objects.filter(organization=test_org):
            assert acc.first_name != "Tadeusz"

        NEW_CORP = deepcopy(TEST_CORP)
        for tester in NEW_CORP:
            # The hero of the Polish epic poem Pan Tadeusz, since you ask
            # (the first line of which is "O Lithuania, my homeland!")
            tester["firstName"] = "Tadeusz"
            tester["lastName"] = "Soplica"

        keycloak_actions.perform_import_raw(
            test_org, NEW_CORP,
            keycloak_actions.keycloak_group_dn_selector
        )

        for acc in Account.objects.filter(organization=test_org):
            assert (acc.first_name, acc.last_name) == ("Tadeusz", "Soplica")
