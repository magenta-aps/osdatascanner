import pytest
from datetime import datetime, timezone
from uuid import uuid4

from more_itertools import one

from os2datascanner.core_organizational_structure.models.aliases import \
    AliasType
from os2datascanner.projects.admin.core.models import Client
from os2datascanner.projects.admin.organizations.models import Organization, \
    OrganizationalUnit, Account, Position, Alias
from os2datascanner.projects.admin.organizations.os2mo_import_actions import \
    perform_os2mo_import

from os2datascanner.projects.admin.import_services.models import OS2moConfiguration


@pytest.fixture
def mo_org_units_list():
    return [
        {
            "current": {
                "name": "Top level unit",
                "uuid": "23b6386a-6142-4495-975c-92ff41dd4100",
                "parent": None,
                "managers": [
                    {
                        "person": [
                            {
                                "uuid": "e57001bb-9bc1-40ae-bb89-657d115125b7",
                                "given_name": "Bruce",
                                "surname": "Lee",
                                "user_key": "bruce",
                                "addresses": [
                                    {
                                        "name": "bruce@kung.fu"
                                        },
                                    {
                                        "name": "bruce@kung.fu"
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                "engagements": [
                    {
                        "person": [
                            {
                                "uuid": "b5d2cc7b-6d57-4326-9336-ce3372b6887c",
                                "given_name": "Chuck",
                                "surname": "Norris",
                                "user_key": "chuck",
                                "addresses": [
                                    {
                                        "name": "chuck@karate.org"
                                        }
                                    ]
                                }
                            ]
                        },
                    {
                        "person": [
                            {
                                "uuid": "96badbf9-0197-4b17-a649-ff648f8426f1",
                                "given_name": "Jackie",
                                "surname": "Chan",
                                "user_key": "jackie",
                                "addresses": [
                                    {
                                        "name": "chan@kung.fu"
                                        },
                                    {
                                        "name": "chan@kung.fu"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            },
        {
            "current": {
                "name": "Unit 1",
                "uuid": "7fc7769e-00e1-4bad-aa8e-9ce91bde9f64",
                "parent": {
                    "name": "Top level unit",
                    "uuid": "23b6386a-6142-4495-975c-92ff41dd4100"
                    },
                "managers": [
                    {
                        "person": [
                            {
                                "uuid": "0d125092-701a-45d6-9062-a547f5c376ca",
                                "given_name": "Brandon",
                                "surname": "Lee",
                                "user_key": "brandon",
                                "addresses": [
                                    {
                                        "name": "brandon@kung.fu"
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                "engagements": [
                    {
                        "person": [
                            {
                                "uuid": "b5d2cc7b-6d57-4326-9336-ce3372b6887c",
                                "given_name": "Chuck",
                                "surname": "Norris",
                                "user_key": "chuck",
                                "addresses": [
                                    {
                                        "name": "chuck@karate.org"
                                        }
                                    ]
                                }
                            ]
                        },
                    {
                        "person": [
                            {
                                "uuid": "677e622b-653f-4aa2-9386-18113c8b8461",
                                "given_name": "Eddie",
                                "surname": "Murphy",
                                "user_key": "eddie",
                                "addresses": []
                                }
                            ]
                        }
                    ]
                }
            },
        {
            "current": {
                "name": "Unit 2",
                "uuid": "57e39d7b-63db-4bc3-a811-29cc02ceafb0",
                "parent": {
                    "name": "Top level unit",
                    "uuid": "23b6386a-6142-4495-975c-92ff41dd4100"
                    },
                "managers": [],
                "engagements": []
                }
            },
        {
            "current": {
                "name": "Unit 3",
                "uuid": "473ad333-c4d5-447c-a858-d03b021caba9",
                "parent": {
                    "name": "Top level unit",
                    "uuid": "23b6386a-6142-4495-975c-92ff41dd4100"
                    },
                "managers": [{"person": None}],  # Vacant manager
                "engagements": []
                }
            },
        {
            "current": {
                "name": "Unit 4",
                "uuid": "444ad987-c4d5-447c-a858-d03b021huga5",
                "parent": {
                    "name": "Top level unit",
                    "uuid": "23b6386a-6142-4495-975c-92ff41dd4100"
                    },
                "managers": [
                    {
                        "person": [
                            {
                                "uuid": "e57001bb-9bc1-40ae-bb89-657d115125b7",
                                "given_name": "Bruce",
                                "surname": "Lee",
                                "user_key": "bruce",
                                "addresses": [
                                    {
                                        "name": "bruce@kung.fu"
                                        },
                                    {
                                        "name": "bruce@kung.fu"
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                "engagements": []
                }
            }
        ]


@pytest.fixture
def dummy_client():
    return Client.objects.create(name="OS2datascanner test dummy_client")


@pytest.fixture
def mo_org(dummy_client):
    return Organization.objects.create(name="MO municipality", client=dummy_client)


@pytest.mark.django_db
class TestOS2moImport:

    @pytest.fixture(autouse=True)
    def os2mo_import_config(self, mo_org):
        return OS2moConfiguration.objects.create(organization=mo_org,
                                                 hide_units_on_import=False,
                                                 last_modified=datetime(
                                                       2025, 9, 2, 12,
                                                       0, 0,
                                                       tzinfo=timezone.utc)
                                                 )

    def import_from_list(self, import_list, org):

        # Test "Act" step included here
        perform_os2mo_import(import_list, org)

        top_level_unit = OrganizationalUnit.objects.get(name="Top level unit")
        unit1 = OrganizationalUnit.objects.get(name="Unit 1")
        unit2 = OrganizationalUnit.objects.get(name="Unit 2")
        unit3 = OrganizationalUnit.objects.get(name="Unit 3")
        unit4 = OrganizationalUnit.objects.get(name="Unit 4")

        return top_level_unit, unit1, unit2, unit3, unit4

    def test_ou_import(self, mo_org_units_list, mo_org):

        # Act
        top_level_unit, unit1, unit2, unit3, unit4 = self.import_from_list(
            mo_org_units_list, mo_org)

        # Arrange
        today = datetime.now().date()

        # Assert
        assert top_level_unit.imported_id == "23b6386a-6142-4495-975c-92ff41dd4100"
        assert top_level_unit.organization == mo_org
        assert top_level_unit.imported
        assert top_level_unit.last_import.date() == today
        assert top_level_unit.last_import_requested.date() == today
        assert top_level_unit.parent is None
        assert not top_level_unit.hidden

        assert unit1.imported_id == "7fc7769e-00e1-4bad-aa8e-9ce91bde9f64"
        assert unit1.organization == mo_org
        assert unit1.imported
        assert unit1.last_import.date() == today
        assert unit1.last_import_requested.date() == today
        assert unit1.parent.name == "Top level unit"
        assert not unit1.hidden

        assert unit2.imported_id == "57e39d7b-63db-4bc3-a811-29cc02ceafb0"
        assert unit2.organization == mo_org
        assert unit2.imported
        assert unit2.last_import.date() == today
        assert unit2.last_import_requested.date() == today
        assert unit2.parent.name == "Top level unit"
        assert not unit2.hidden

        assert unit3.imported_id == "473ad333-c4d5-447c-a858-d03b021caba9"
        assert unit3.organization == mo_org
        assert unit3.imported
        assert unit3.last_import.date() == today
        assert unit3.last_import_requested.date() == today
        assert unit3.parent.name == "Top level unit"
        assert not unit3.hidden

    def test_ou_import_all_hidden(self, mo_org_units_list, mo_org, os2mo_import_config):
        # Arrange: Set default config to hidden
        os2mo_import_config.hide_units_on_import = True
        os2mo_import_config.save()

        # Act: Import
        perform_os2mo_import(mo_org_units_list, mo_org)

        # Assert: Check configuration and verify that only hidden units were created
        assert mo_org.importservice.hide_units_on_import
        assert OrganizationalUnit.objects.filter(hidden=True).exists()
        assert not OrganizationalUnit.objects.filter(hidden=False).exists()

    def test_existing_ou_visible_new_hidden_ou_import(self, mo_org_units_list, mo_org,
                                                      os2mo_import_config):

        # Arrange: Import, set default config to hidden, add new unit
        perform_os2mo_import(mo_org_units_list, mo_org)
        os2mo_import_config.hide_units_on_import = True
        os2mo_import_config.save()
        mo_org_units_list.append(
            {
                "current": {
                    "name": "Hide and seekers",
                    "uuid": "99e99d7b-99db-4bc3-a811-29cc02aaaaa9",
                    "parent": {
                        "name": "Top level unit",
                        "uuid": "23b6386a-6142-4495-975c-92ff41dd4100"
                    },
                    "managers": [],
                    "engagements": []
                }
            }
        )

        # Act: Import again
        perform_os2mo_import(mo_org_units_list, mo_org)

        # Assert: Verify existing units are still visible and the new one is hidden
        assert OrganizationalUnit.objects.filter(name="Hide and seekers", hidden=True).exists()
        assert OrganizationalUnit.objects.filter(hidden=False).exists()

    def test_employee_import(self, mo_org, mo_org_units_list):
        # Act
        top_level_unit, unit1, unit2, unit3, _ = self.import_from_list(mo_org_units_list, mo_org)

        # Assert

        # Assuming results are ordered
        chuck, jackie = top_level_unit.get_employees()
        _chuck_again, eddie = unit1.get_employees()

        assert chuck.imported_id == "b5d2cc7b-6d57-4326-9336-ce3372b6887c"
        assert chuck.organization == mo_org
        assert chuck.username == "chuck"
        assert chuck.first_name == "Chuck"
        assert chuck.last_name == "Norris"
        assert chuck.email == "chuck@karate.org"

        assert jackie.imported_id == "96badbf9-0197-4b17-a649-ff648f8426f1"
        assert jackie.organization == mo_org
        assert jackie.username == "jackie"
        assert jackie.first_name == "Jackie"
        assert jackie.last_name == "Chan"
        assert jackie.email == "chan@kung.fu"

        assert eddie.imported_id == "677e622b-653f-4aa2-9386-18113c8b8461"
        assert eddie.organization == mo_org
        assert eddie.username == "eddie"
        assert eddie.first_name == "Eddie"
        assert eddie.last_name == "Murphy"
        assert eddie.email == ""

        assert unit2.get_employees().count() == 0
        assert unit3.get_employees().count() == 0

    def test_manager_import(self, mo_org, mo_org_units_list):
        # Act
        top_level_unit, unit1, unit2, unit3, _ = self.import_from_list(mo_org_units_list, mo_org)

        # Assert
        bruce = one(top_level_unit.get_managers())
        brandon = one(unit1.get_managers())

        assert bruce.imported_id == "e57001bb-9bc1-40ae-bb89-657d115125b7"
        assert bruce.organization == mo_org
        assert bruce.username == "bruce"
        assert bruce.first_name == "Bruce"
        assert bruce.last_name == "Lee"
        assert bruce.email == "bruce@kung.fu"

        assert brandon.imported_id == "0d125092-701a-45d6-9062-a547f5c376ca"
        assert brandon.organization == mo_org
        assert brandon.username == "brandon"
        assert brandon.first_name == "Brandon"
        assert brandon.last_name == "Lee"
        assert brandon.email == "brandon@kung.fu"

        assert unit2.get_managers().count() == 0
        assert unit3.get_managers().count() == 0

    def test_sequential_import_manager_positions(self, mo_org, mo_org_units_list):
        # Arrange
        top_level_unit, _, _, _, unit4 = self.import_from_list(mo_org_units_list, mo_org)

        # We'll verify here that Bruce is indeed manager of two OU's.
        bruce = Account.objects.get(username="bruce")
        bruce_manager_top_level_unit = Position.managers.get(
            unit=top_level_unit, account=bruce)
        bruce_manager_unit_4 = Position.managers.get(unit=unit4, account=bruce)

        # Act (Import again)
        perform_os2mo_import(mo_org_units_list, mo_org)

        # Assert (check that's still the case)
        assert bruce_manager_top_level_unit == Position.managers.get(
            unit=top_level_unit, account=bruce)
        assert bruce_manager_unit_4 == Position.managers.get(
            unit=unit4, account=bruce)

    def test_sequential_import_employee_positions(self, mo_org, mo_org_units_list):
        # Arrange
        top_level_unit, unit1, _, _, _ = self.import_from_list(mo_org_units_list, mo_org)

        # We'll verify here that Chuck is indeed employee of two OU's.
        chuck = Account.objects.get(username="chuck")
        chuck_employee_top_level_unit = Position.employees.get(
            unit=top_level_unit, account=chuck)
        chuck_employee_unit_1 = Position.employees.get(unit=unit1, account=chuck)

        # Act (Import again)
        perform_os2mo_import(mo_org_units_list, mo_org)

        # Assert (check that's still the case)
        assert chuck_employee_top_level_unit == Position.employees.get(
            unit=top_level_unit, account=chuck)
        assert chuck_employee_unit_1 == Position.employees.get(
            unit=unit1, account=chuck)

    def test_account_delete(self, mo_org, mo_org_units_list):
        # Arrange

        _, unit1, _, _, _ = self.import_from_list(mo_org_units_list, mo_org)

        # This person is not in MO
        imported_id = str(uuid4())
        jerry = Account.objects.create(
            imported_id=imported_id,
            imported=True,
            organization=mo_org,
            username="seinfeld",
            first_name="Jerry",
            last_name="Seinfeld",
            email="jerry@hollywood.com",
        )

        Position.objects.create(
            imported=True,
            account=jerry,
            unit=unit1,
            role="employee"
        )

        Position.objects.create(
            imported=True,
            account=jerry,
            unit=unit1,
            role="manager"
        )

        Alias.objects.create(
            imported_id=imported_id,
            imported=True,
            account=jerry,
            _alias_type=AliasType.EMAIL.value,
            _value="jerry@hollywood.com",
        )

        # Act
        perform_os2mo_import(mo_org_units_list, mo_org)

        # Assert
        with pytest.raises(Account.DoesNotExist):
            Account.objects.get(username="seinfeld")

        with pytest.raises(Position.DoesNotExist):
            Position.objects.get(account=jerry)

        with pytest.raises(Alias.DoesNotExist):
            Alias.objects.get(account=jerry)

    def test_deletion_of_parent_ou_and_creation_of_child(self, mo_org, mo_org_units_list):
        """
        As seen in #61857, the following can happen simultaneously:
            1. An OU is moved to the root.
            2. A child OU is created under that OU.
            3. The previous parent OU is deleted.
        In this case, the moved OU should have its parent set to None, the
        deleted OU should be deleted, and the child OU should be created
        without issue.
        """

        # Arrange
        _, unit1, _, _, _ = self.import_from_list(mo_org_units_list, mo_org)

        new_list = [
            {
                "current": {
                    "name": "Unit 1",
                    "uuid": "7fc7769e-00e1-4bad-aa8e-9ce91bde9f64",
                    "parent": None,
                    "managers": [
                        {
                            "person": [
                                {
                                    "uuid": "0d125092-701a-45d6-9062-a547f5c376ca",
                                    "given_name": "Brandon",
                                    "surname": "Lee",
                                    "user_key": "brandon",
                                    "addresses": [
                                        {
                                            "name": "brandon@kung.fu"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ],
                    "engagements": [
                        {
                            "person": [
                                {
                                    "uuid": "b5d2cc7b-6d57-4326-9336-ce3372b6887c",
                                    "given_name": "Chuck",
                                    "surname": "Norris",
                                    "user_key": "chuck",
                                    "addresses": [
                                        {
                                            "name": "chuck@karate.org"
                                            }
                                        ]
                                    }
                                ]
                            },
                        {
                            "person": [
                                {
                                    "uuid": "677e622b-653f-4aa2-9386-18113c8b8461",
                                    "given_name": "Eddie",
                                    "surname": "Murphy",
                                    "user_key": "eddie",
                                    "addresses": []
                                    }
                                ]
                            }
                        ]
                    }
                },
            {
                "current": {
                    "name": "Unit 5",
                    "uuid": "57e39d7b-63db-4bc3-a811-29cc02ceafb0",
                    "parent": {
                        "name": "Unit 1",
                        "uuid": "7fc7769e-00e1-4bad-aa8e-9ce91bde9f64"
                        },
                    "managers": [],
                    "engagements": []
                    }
                },
            ]

        # Act
        perform_os2mo_import(new_list, mo_org)

        # Assert
        unit1.refresh_from_db()

        # Parent unit is none
        assert unit1.parent is None

        # Top unit is deleted
        assert not OrganizationalUnit.objects.filter(name="Top level unit").exists()

        # Child is created
        assert OrganizationalUnit.objects.filter(name="Unit 5").exists()
