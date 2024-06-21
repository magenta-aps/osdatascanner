from datetime import datetime
from uuid import uuid4

import pytest
from django.test import TestCase
from more_itertools import one

from os2datascanner.core_organizational_structure.models.aliases import \
    AliasType
from os2datascanner.projects.admin.core.models import Client
from os2datascanner.projects.admin.organizations.models import Organization, \
    OrganizationalUnit, Account, Position, Alias
from os2datascanner.projects.admin.organizations.os2mo_import_actions import \
    perform_os2mo_import


MO_ORG_UNITS = [
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
    }
]


class OS2moImportTest(TestCase):
    dummy_client = None

    @classmethod
    def setUpClass(cls):
        cls.dummy_client = Client.objects.create(
            name="OS2datascanner test dummy_client")

    @classmethod
    def tearDownClass(cls):
        cls.dummy_client.delete()

    def setUp(self):
        self.org = Organization.objects.create(
            name="MO municipality",
            client=self.dummy_client)

        # Test "Act" step included here
        perform_os2mo_import(MO_ORG_UNITS, self.org)

        self.top_level_unit = OrganizationalUnit.objects.get(name="Top level unit")
        self.unit1 = OrganizationalUnit.objects.get(name="Unit 1")
        self.unit2 = OrganizationalUnit.objects.get(name="Unit 2")

    def tearDown(self):
        self.org.delete()

    def test_ou_import(self):
        # Arrange
        today = datetime.now().date()

        # Assert
        assert self.top_level_unit.imported_id == "23b6386a-6142-4495-975c-92ff41dd4100"
        assert self.top_level_unit.organization == self.org
        assert self.top_level_unit.imported
        assert self.top_level_unit.last_import.date() == today
        assert self.top_level_unit.last_import_requested.date() == today
        assert self.top_level_unit.parent is None

        assert self.unit1.imported_id == "7fc7769e-00e1-4bad-aa8e-9ce91bde9f64"
        assert self.unit1.organization == self.org
        assert self.unit1.imported
        assert self.unit1.last_import.date() == today
        assert self.unit1.last_import_requested.date() == today
        assert self.unit1.parent.name == "Top level unit"

        assert self.unit2.imported_id == "57e39d7b-63db-4bc3-a811-29cc02ceafb0"
        assert self.unit2.organization == self.org
        assert self.unit2.imported
        assert self.unit2.last_import.date() == today
        assert self.unit2.last_import_requested.date() == today
        assert self.unit2.parent.name == "Top level unit"

    def test_employee_import(self):
        # Assert

        # Assuming results are ordered
        chuck, jackie = self.top_level_unit.get_employees()
        _chuck_again, eddie = self.unit1.get_employees()

        assert chuck.imported_id == "b5d2cc7b-6d57-4326-9336-ce3372b6887c"
        assert chuck.organization == self.org
        assert chuck.username == "chuck"
        assert chuck.first_name == "Chuck"
        assert chuck.last_name == "Norris"
        assert chuck.email == "chuck@karate.org"

        assert jackie.imported_id == "96badbf9-0197-4b17-a649-ff648f8426f1"
        assert jackie.organization == self.org
        assert jackie.username == "jackie"
        assert jackie.first_name == "Jackie"
        assert jackie.last_name == "Chan"
        assert jackie.email == "chan@kung.fu"

        assert eddie.imported_id == "677e622b-653f-4aa2-9386-18113c8b8461"
        assert eddie.organization == self.org
        assert eddie.username == "eddie"
        assert eddie.first_name == "Eddie"
        assert eddie.last_name == "Murphy"
        assert eddie.email == ""

        assert len(self.unit2.get_employees()) == 0

    def test_manager_import(self):
        # Assert
        bruce = one(self.top_level_unit.get_managers())
        brandon = one(self.unit1.get_managers())

        assert bruce.imported_id == "e57001bb-9bc1-40ae-bb89-657d115125b7"
        assert bruce.organization == self.org
        assert bruce.username == "bruce"
        assert bruce.first_name == "Bruce"
        assert bruce.last_name == "Lee"
        assert bruce.email == "bruce@kung.fu"

        assert brandon.imported_id == "0d125092-701a-45d6-9062-a547f5c376ca"
        assert brandon.organization == self.org
        assert brandon.username == "brandon"
        assert brandon.first_name == "Brandon"
        assert brandon.last_name == "Lee"
        assert brandon.email == "brandon@kung.fu"

        assert len(self.unit2.get_managers()) == 0

    def test_account_delete(self):
        # Arrange

        # This person is not in MO
        imported_id = str(uuid4())
        jerry = Account.objects.create(
            imported_id=imported_id,
            imported=True,
            organization=self.org,
            username="seinfeld",
            first_name="Jerry",
            last_name="Seinfeld",
            email="jerry@hollywood.com",
        )

        Position.objects.create(
            imported=True,
            account=jerry,
            unit=self.unit1,
            role="employee"
        )

        Position.objects.create(
            imported=True,
            account=jerry,
            unit=self.unit1,
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
        perform_os2mo_import(MO_ORG_UNITS, self.org)

        # Assert
        with pytest.raises(Account.DoesNotExist):
            Account.objects.get(username="seinfeld")

        with pytest.raises(Position.DoesNotExist):
            Position.objects.get(account=jerry)

        with pytest.raises(Alias.DoesNotExist):
            Alias.objects.get(account=jerry)
