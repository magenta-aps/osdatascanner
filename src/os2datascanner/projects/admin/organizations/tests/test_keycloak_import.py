import pytest

from ..models import Account, OrganizationalUnit, Alias, Position
from ..models.aliases import AliasType
from .. import keycloak_actions

from os2datascanner.utils.ldap import RDN, LDAPNode


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
                "group_dn": "CN=Group A,O=Test Corp."
            }
        },
        {
            "attributes": {
                "LDAP_ENTRY_DN": [
                    "CN=secret_backdoor,OU=Testers,O=Test Corp."
                ],
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
                "group_dn": "CN=Group 2,O=Test Corp."
            }
        },
    ]


keycloak_to_account_translation = {
    "lastName": "last_name",
    "username": "username",
    "firstName": "first_name",
    "email": "email"
}


@pytest.fixture
def unit_dn():
    return "CN=Unit,OU=Parent,OU=Ancestor,O=Test Corp."


@pytest.fixture
def ulla_dict():
    return {
                "username": "ulla@invalid.test",
                "firstName": "Ulla",
                "lastName": "Testen",
                "email": "ursulas@brevdue.dk",
                "attributes": {
                    "LDAP_ENTRY_DN": [
                        "CN=Ulla Testsen,OU=TheUCorp,O=Test Corp."
                    ]
                }
            }


@pytest.fixture
def ulla(ulla_dict, test_org):
    return Account.objects.create(
        username=ulla_dict['username'],
        first_name=ulla_dict['firstName'],
        last_name=ulla_dict['lastName'],
        email=ulla_dict['email'],
        organization=test_org,
        imported_id=ulla_dict['attributes']['LDAP_ENTRY_DN'][0],
    )


@pytest.fixture
def ulla_imported_email_alias(ulla):
    return Alias.objects.create(
        account=ulla,
        _alias_type="email",
        _value="ulla@invalid.test",
        imported=True,
        imported_id=(ulla.imported_id + keycloak_actions.EMAIL_ALIAS_IMPORTED_ID_SUFFIX))


@pytest.fixture
def ulla_non_imported_email_alias(ulla):
    return Alias.objects.create(
        account=ulla,
        _alias_type="email",
        _value="ulla_second@invalid.test",
        imported=False)


@pytest.fixture
def ulf_dict():
    return {
                "username": "ulf@invalid.test",
                "firstName": "Ulf",
                "lastName": "Testen",
                "attributes": {
                    "LDAP_ENTRY_DN": [
                        "CN=Ulf Testsen,OU=TheUCorp,O=Test Corp."
                    ],
                    "objectSid": [
                        "AQUAAAAAAAUVAAAAWJ8iy3PGcdkusl9JeCMAAA=="
                    ]
                }
            }


@pytest.fixture
def ulf(ulf_dict, test_org):
    return Account.objects.create(
        username=ulf_dict['username'],
        first_name=ulf_dict['firstName'],
        last_name=ulf_dict['lastName'],
        organization=test_org,
        imported_id=ulf_dict['attributes']['LDAP_ENTRY_DN'][0],
        email=""
    )


@pytest.fixture
def account_dn_managed_units_paths(TEST_CORP):
    return {TEST_CORP[0]["attributes"]["LDAP_ENTRY_DN"][0]: [
                RDN.dn_to_sequence(TEST_CORP[0]["attributes"]["group_dn"])]
            }


@pytest.mark.django_db
class TestKeycloakImport:

    # SECTION: helper_functions

    def test_path_to_unit_with_existing_unit(self, unit_dn, test_org, bingoklubben):
        """Using _path_to_unit where the given path already has an associated unit in the dict
        should return that unit and indicate that it isn't new."""
        seq = RDN.dn_to_sequence(unit_dn)

        result, new = keycloak_actions._path_to_unit(test_org, seq, {seq: bingoklubben})

        assert new is False
        assert result == bingoklubben

    def test_path_to_unit_info(self, unit_dn, test_org):
        """Testing that the attributes of a unit created in _path_to_unit are correct."""
        seq = RDN.dn_to_sequence(unit_dn)

        unit, new = keycloak_actions._path_to_unit(test_org, seq, {})

        assert new

        for attr_name, expected in [("imported_id", unit_dn),
                                    ("name", "Unit"),
                                    ("parent", None),
                                    ("organization", test_org),
                                    # MPTT tree fields shouldn't be set during this method
                                    ("lft", 0),
                                    ("rght", 0),
                                    ("tree_id", 0),
                                    ("level", 0), ]:
            assert getattr(unit, attr_name) == expected

    def test_path_to_unit_find_parent(self, unit_dn, test_org):
        """Running _path_to_unit with a units parent in the dict,
        should correctly set the unit.parent attribute."""
        seq = RDN.dn_to_sequence(unit_dn)

        parent_seq = seq[:-1]
        parent = OrganizationalUnit()

        unit, new = keycloak_actions._path_to_unit(test_org, seq, {parent_seq: parent})

        assert unit.parent == parent

    def test_path_to_unit_multiple_ancestors(self, unit_dn, test_org):
        """If a unit has multiple ancestors, the one closest should be found."""
        seq = RDN.dn_to_sequence(unit_dn)

        parent = OrganizationalUnit()
        ancestor = OrganizationalUnit()
        unit_dict = {
            seq[:-2]: parent,
            seq[:-3]: ancestor
        }
        unit, new = keycloak_actions._path_to_unit(test_org, seq, unit_dict)

        assert unit.parent == parent

    def test_get_accounts_with_missing_attributes(self, TEST_CORP, test_org):
        """Running _get_accounts where a node is missing important fields (id, username, attributes)
        shouldn't return that accounts, but should still return the rest."""

        nodes = []
        expected = []
        for acc in TEST_CORP:
            account, new = Account.objects.get_or_create(
                imported_id=acc['attributes']['LDAP_ENTRY_DN'][0], organization=test_org)
            if new and all(n in acc for n in ("id", "attributes", "username",)):
                expected.append(account)

            if new:
                node = LDAPNode.make(acc.get("username", ""), *(), **acc)
                nodes.append(node)

        def iterator(nodes):
            for node in nodes:
                path = RDN.dn_to_sequence(node.properties['attributes']['LDAP_ENTRY_DN'][0])
                yield path, node, node

        result = [acc for acc, _, _ in keycloak_actions._get_accounts(iterator(nodes))]

        assert expected == result

    def test_update_alias_updates_value(self, ulla, ulla_imported_email_alias):
        """Given a value that doesn't match the current the value of an alias,
        _update_alias() should update the value to the new value."""

        new_mail = "new@email.com"
        alias_id = ulla_imported_email_alias.imported_id
        results = list(keycloak_actions._update_alias(ulla, new_mail, AliasType.EMAIL, alias_id))

        assert results == [
            (keycloak_actions.Action.KEEP, ulla_imported_email_alias),
            (keycloak_actions.Action.UPDATE, (ulla_imported_email_alias, ("_value",)))
        ]
        # Check that returned alias, has expected value
        assert results[0][1]._value == new_mail

    def test_update_alias_deletes_aliases(self, ulla, ulla_imported_email_alias,
                                          ulla_non_imported_email_alias):
        """When _update_alias is given an account, and no value for its aliases,
        it should indicate that every corresponding imported alias should be deleted."""
        alias_id = ulla_imported_email_alias.imported_id
        results = list(keycloak_actions._update_alias(ulla, None, AliasType.EMAIL, alias_id))

        assert len(results) == 1
        for action, alias in results:
            assert action == keycloak_actions.Action.DELETE
            assert alias in {ulla_imported_email_alias}
            assert alias not in {ulla_non_imported_email_alias}

    def test_account_to_node(self, ulf):
        node = keycloak_actions._account_to_node(ulf)

        ulf_path = RDN.dn_to_sequence(ulf.imported_id)

        assert node.label == (ulf_path[-1],)
        assert node.properties['firstName'] == ulf.first_name
        assert node.properties['lastName'] == ulf.last_name
        assert node.properties['attributes']["LDAP_ENTRY_DN"][0] == ulf.imported_id

    def test_update_account_adds_missing_alias(self, ulf, ulf_dict):
        path = RDN.dn_to_sequence(ulf_dict['attributes']['LDAP_ENTRY_DN'][0])
        node = LDAPNode.make(ulf_dict['username'], *(), **ulf_dict)

        results = list(keycloak_actions._update_account(ulf, path, node))

        assert len(results) == 1

        action, alias = results[0]
        assert action == keycloak_actions.Action.ADD
        assert alias.account == ulf
        assert alias._alias_type == AliasType.SID

        expected_sid = keycloak_actions._convert_sid(ulf_dict['attributes']['objectSid'][0])
        assert alias.value == expected_sid

        expected_iid = (ulf_dict['attributes']['LDAP_ENTRY_DN'][0]
                        + keycloak_actions.SID_ALIAS_IMPORTED_ID_SUFFIX)
        assert alias.imported_id == expected_iid

    @pytest.mark.parametrize("attr_name,value", [('username', "new_name"),
                                                 ('firstName', "mot"),
                                                 ('lastName', "Testesen"),
                                                 ('email', "new@mail.com"), ])
    def test_update_account_attributes(self, ulla, ulla_dict, attr_name, value):
        """When the given Account and node, doesn't have that same value for a property,
        _update_account should update Accounts value, and an UPDATE Action should be returned."""
        ulla_dict[attr_name] = value

        path = RDN.dn_to_sequence(ulla_dict['attributes']['LDAP_ENTRY_DN'][0])
        node = LDAPNode.make(ulla_dict['username'], *(), **ulla_dict)

        results = list(keycloak_actions._update_account(ulla, path, node))

        # Results also contains an action for email alias. Ignore it
        results.pop(0)

        assert len(results) == 1
        action, (account, (attr,)) = results[0]
        assert action == keycloak_actions.Action.UPDATE
        assert account == ulla
        keycloak_to_account_translation = {
            "lastName": "last_name",
            "username": "username",
            "firstName": "first_name",
            "email": "email"
        }
        assert attr == keycloak_to_account_translation[attr_name]

        assert getattr(account, attr) == value

    @pytest.mark.parametrize("attr_name", ['firstName', 'lastName', 'email'])
    def test_update_account_missing_attributes(self, ulla, ulla_dict, attr_name):
        """When the given node is missing an attribute, _update_account should update the accounts
        corresponding value to "" and return an UPDATE Action."""
        del ulla_dict[attr_name]

        path = RDN.dn_to_sequence(ulla_dict['attributes']['LDAP_ENTRY_DN'][0])
        node = LDAPNode.make(ulla_dict['username'], *(), **ulla_dict)

        results = list(keycloak_actions._update_account(ulla, path, node))
        # Results will also contain an email alias, except if the email was just deleted.
        # Ignore this alias
        if attr_name != 'email':
            results.pop(0)

        assert len(results) == 1
        action, (account, (attr,)) = results[0]
        assert action == keycloak_actions.Action.UPDATE
        assert account == ulla
        assert attr == keycloak_to_account_translation[attr_name]

        assert getattr(account, attr) == ""

    def test_update_account_position(self, ulla, bingoklubben):
        """If an account isn't already an employee of the given unit,
        _update_account_position should return an ADD Action with a corresponding Alias object."""
        action = keycloak_actions._update_account_position(ulla, {}, bingoklubben)

        assert action[0] == keycloak_actions.Action.ADD
        position = action[1]
        assert position.account == ulla
        assert position.unit == bingoklubben
        assert position.imported

    # SECTION: perform_import_raw

    def perform_ou_import(self, remote, org):
        keycloak_actions.perform_import_raw(
                org, remote,
                keycloak_actions.keycloak_dn_selector)

    def perform_group_import(self, remote, org):
        keycloak_actions.perform_import_raw(
                org, remote,
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

    def test_removal(self, TEST_CORP, test_org):
        """Removing a user from Keycloak's JSON output should also remove that
        user from the database."""
        self.perform_ou_import(TEST_CORP, test_org)

        thads = list(Account.objects.filter(first_name="Thad"))

        keycloak_actions.perform_import_raw(
                test_org, [
                        tester
                        for tester in TEST_CORP
                        if tester.get("firstName") != "Thad"],
                keycloak_actions.keycloak_dn_selector)

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

        keycloak_actions.perform_import_raw(
                test_org, TEST_CORP,
                keycloak_actions.keycloak_group_dn_selector)

        for todd in todds:
            todd.refresh_from_db()
            assert "OU=Experimenters" in todd.imported_id, "DN did not change"

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

        keycloak_actions.perform_import_raw(
                test_org, TEST_CORP,
                keycloak_actions.keycloak_group_dn_selector)

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

        keycloak_actions.perform_import_raw(
                test_org, TEST_CORP,
                keycloak_actions.keycloak_group_dn_selector)

        with pytest.raises(OrganizationalUnit.DoesNotExist):
            OrganizationalUnit.objects.get(
                    imported_id="CN=Group 2,O=Test Corp.")

    def test_import_user_in_multiple_groups_should_only_get_one_email_alias(
            self, TEST_CORP_TWO, test_org):
        """ A user can be a member of multiple groups, but it is still only one
        user, and should result in only one email-alias (given that the user
        has an email attribute)"""
        keycloak_actions.perform_import_raw(
            test_org, TEST_CORP_TWO,
            keycloak_actions.keycloak_group_dn_selector)

        ursula_aliases = Alias.objects.filter(_value="ursulas@brevdue.dk")

        assert ursula_aliases.count() == 1, "Either duplicate or no email aliases for user created"

    def test_delete_user_relation_to_group(self, TEST_CORP_TWO, test_org):
        keycloak_actions.perform_import_raw(
            test_org, TEST_CORP_TWO,
            keycloak_actions.keycloak_group_dn_selector)

        ursula = TEST_CORP_TWO[0]
        account = Account.objects.get(uuid=ursula["id"])

        assert Position.objects.filter(
            account=account).count() == 2, "Position not correctly created"

        # Now only member of one group instead of two.
        TEST_CORP_TWO[0]["attributes"]["group_dn"] = None

        # Import again
        keycloak_actions.perform_import_raw(
            test_org, TEST_CORP_TWO,
            keycloak_actions.keycloak_group_dn_selector)

        assert Position.objects.filter(
            account=account).count() == 1, "Position not updated correctly"

        # The OU should still exist though, as there is still a user with a
        # connection to it.
        assert OrganizationalUnit.objects.filter(
            imported_id="CN=Group 1,O=Test Corp.").exists(), "OU doesn't exist but should"

        # Delete Ulrich from the TEST_CORP_TWO
        del TEST_CORP_TWO[2:3]

        # Import again
        keycloak_actions.perform_import_raw(
            test_org, TEST_CORP_TWO,
            keycloak_actions.keycloak_group_dn_selector)

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

        keycloak_actions.perform_import_raw(
                test_org, TEST_CORP,
                keycloak_actions.keycloak_group_dn_selector)

        for user in Account.objects.filter(organization=test_org):
            assert (user.first_name, user.last_name) == (
                "Tadeusz", "Soplica"), "property update failed"

    def test_import_and_creation_of_managers(
            self, account_dn_managed_units_paths, TEST_CORP, test_org):
        """It should be possible to add managers based on the Keycloak output."""

        keycloak_actions.perform_import_raw(
            test_org, TEST_CORP,
            keycloak_actions.keycloak_group_dn_selector,
            account_dn_managed_units_paths=account_dn_managed_units_paths,
            do_manager_import=True)

        # Get Ted Testsen
        account = Account.objects.get(uuid=TEST_CORP[0]["id"])

        # Get Group 1.
        unit = OrganizationalUnit.objects.get(imported_id=TEST_CORP[0]["attributes"]["group_dn"])

        manager = Position.managers.get(account=account, unit=unit)

        assert manager == account.positions.get(role="manager", unit=unit), "manager not imported"

    def test_empty_manager_update(self, account_dn_managed_units_paths, TEST_CORP, test_org):
        """It should be possible to remove managers based on the Keycloak output.
        If there are none remotely, but local managers still exist, they should be deleted."""

        # Import, create manager Position for Ted Testsen
        keycloak_actions.perform_import_raw(
            test_org, TEST_CORP,
            keycloak_actions.keycloak_group_dn_selector,
            account_dn_managed_units_paths=account_dn_managed_units_paths,
            do_manager_import=True)

        # Import again, with no managers
        keycloak_actions.perform_import_raw(
            test_org, TEST_CORP,
            keycloak_actions.keycloak_group_dn_selector,
            account_dn_managed_units_paths={},
            do_manager_import=True)

        # Get manager account
        account = Account.objects.get(uuid=TEST_CORP[0]["id"])
        unit = OrganizationalUnit.objects.get(imported_id=TEST_CORP[0]["attributes"]["group_dn"])

        assert Position.managers.filter(
            account=account, unit=unit).exists() is False, "manager not removed"
