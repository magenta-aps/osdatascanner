import pytest

from django.test import TestCase
from django.utils import translation

from os2datascanner.core_organizational_structure.models.position import Role
from os2datascanner.projects.admin.organizations.models import (
    Account, Organization, OrganizationalUnit, Position)
from os2datascanner.projects.admin.core.models import Client


class RoleTest(TestCase):

    def setUp(self) -> None:
        translation.activate('en')

    # Generalized version found in core application
    def test_choices(self):
        """The choices method returns the expected format."""
        expected = [
            ('employee', 'employee'),
            ('manager', 'manager'),
            ('dpo', 'data protection officer')
        ]
        self.assertEqual(expected, Role.choices)


@pytest.fixture(autouse=True)
def the_empire():
    empire_cl = Client.objects.create(name="The Galactic Empire")
    Organization.objects.create(name="The Galactic Empire", client=empire_cl)


@pytest.fixture
def first_death_star():
    empire_org = Organization.objects.get(name="The Galactic Empire")

    # Orson Krennic is the Director of the Death Star.
    orson = Account.objects.create(
        username="ock",
        first_name="Orson",
        last_name="Krennic",
        organization=empire_org)
    death_star = OrganizationalUnit.objects.create(name="Death Star", organization=empire_org)
    Position.objects.create(account=orson, unit=death_star, role=Role.MANAGER)

    # He is employed in the Imperial Administration Unit
    empire_admin = OrganizationalUnit.objects.create(
        name="Imperial Administration", organization=empire_org)
    Position.objects.create(account=orson, unit=empire_admin, role=Role.EMPLOYEE)

    # He is also the president and DPO of his home planet chess club
    lexrul_chess_club = OrganizationalUnit.objects.create(
        name="Lexrul Chess Club", organization=empire_org)
    Position.objects.create(account=orson, unit=lexrul_chess_club, role=Role.MANAGER)
    Position.objects.create(account=orson, unit=lexrul_chess_club, role=Role.DPO)

    # He also volunteers at the local library
    lexrul_library = OrganizationalUnit.objects.create(
        name="Lexrul Library", organization=empire_org)
    Position.objects.create(account=orson, unit=lexrul_library, role=Role.EMPLOYEE)

    # He is also the DPO of his personal tax spreadsheet
    orson_spreadsheet = OrganizationalUnit.objects.create(
        name="Orson's Tax Spreadsheet", organization=empire_org)
    Position.objects.create(account=orson, unit=orson_spreadsheet, role=Role.DPO)

    # Return Orson's account, managed units, DPO'd units and employed units
    return (
        orson, {
            "managed_units": (death_star, lexrul_chess_club),
            "dpod_units": (lexrul_chess_club, orson_spreadsheet),
            "employed_units": (empire_admin, lexrul_library)
            })


@pytest.fixture
def second_death_star():
    org = Organization.objects.get(name="The Galactic Empire")

    death_star = OrganizationalUnit.objects.create(
        name="Second Death Star", organization=org)

    sidious = Account.objects.create(
        username="sidious",
        first_name="Sheev",
        last_name="Palpatine",
        organization=org)
    Position.objects.create(account=sidious, unit=death_star, role=Role.MANAGER)
    Position.objects.create(account=sidious, unit=death_star, role=Role.DPO)

    vader = Account.objects.create(
        username="vader",
        first_name="Anakin",
        last_name="Skywalker",
        organization=org)
    Position.objects.create(account=vader, unit=death_star, role=Role.MANAGER)
    Position.objects.create(account=vader, unit=death_star, role=Role.DPO)

    jerjerrod = Account.objects.create(
        username="tje",
        first_name="Tiian",
        last_name="Jerjerrod",
        organization=org)
    Position.objects.create(account=jerjerrod, unit=death_star, role=Role.MANAGER)
    Position.objects.create(account=jerjerrod, unit=death_star, role=Role.EMPLOYEE)

    bevelyn = Account.objects.create(
        username="bev",
        first_name="Bevelyn",
        organization=org)
    Position.objects.create(account=bevelyn, unit=death_star, role=Role.EMPLOYEE)

    dent = Account.objects.create(username="dent", first_name="Dent", organization=org)
    Position.objects.create(account=dent, unit=death_star, role=Role.EMPLOYEE)

    endicott = Account.objects.create(
        username="endicott",
        first_name="Endicott",
        organization=org)
    Position.objects.create(account=endicott, unit=death_star, role=Role.EMPLOYEE)

    # Return the OU, managers, dpos, and employees
    return (death_star,
            (sidious, vader, jerjerrod),
            (sidious, vader),
            (jerjerrod, bevelyn, dent, endicott))


@pytest.fixture
def solo_infiltration(first_death_star):
    org = Organization.objects.get(name="The Galactic Empire")

    # Meet Han and John Soldierman, the supertrooper
    supertrooper = Account.objects.create(
        username="supertrooper",
        first_name="John",
        last_name="Soldierman",
        organization=org)
    hansolo = Account.objects.create(
        username="kessel_master",
        first_name="Han",
        last_name="Solo",
        organization=org)
    unit = OrganizationalUnit.objects.get(name="Death Star")

    # John Soldierman does it all!
    Position.objects.create(account=supertrooper, unit=unit, role=Role.EMPLOYEE)
    Position.objects.create(account=supertrooper, unit=unit, role=Role.MANAGER)
    Position.objects.create(account=supertrooper, unit=unit, role=Role.DPO)

    return (hansolo, supertrooper, unit)


@pytest.mark.django_db
class TestPositions:

    @pytest.mark.parametrize('method,key',
                             [('get_managed_units',
                               'managed_units'),
                              ('get_dpo_units',
                               'dpod_units'),
                                 ('get_employed_units',
                                  'employed_units')])
    def test_account_get_managed_units(self, first_death_star, method, key):
        # Arrange
        orson, expected = first_death_star

        # We expect the get_managed_units method to return both units Orson manages.
        expected_units = expected[key]

        # Act
        units = getattr(orson, method)()

        # Assert
        assert len(units) == len(expected_units)
        assert all(unit in expected_units for unit in units)

    def test_organizational_unit_get_managers(self, second_death_star):
        # Arrange
        death_star, expected_managers, _, _ = second_death_star

        # Act
        managers = death_star.get_managers()

        # Assert
        assert len(managers) == len(expected_managers)
        assert all(acc in expected_managers for acc in managers)

    def test_organizational_unit_get_dpos(self, second_death_star):
        # Arrange
        death_star, _, expected_dpos, _ = second_death_star

        # Act
        dpos = death_star.get_dpos()

        # Assert
        assert len(dpos) == len(expected_dpos)
        assert all(acc in expected_dpos for acc in dpos)

    def test_organizational_unit_get_employees(self, second_death_star):
        # Arrange
        death_star, e_, _, expected_employees = second_death_star

        # Act
        employees = death_star.get_employees()

        # Assert
        assert len(employees) == len(expected_employees)
        assert all(acc in expected_employees for acc in employees)

    @pytest.mark.parametrize('position_manager,role',
                             [(Position.employees,
                               Role.EMPLOYEE),
                              (Position.managers,
                               Role.MANAGER),
                                 (Position.dpos,
                                  Role.DPO)])
    def test_position_custom_manager_queries(self, position_manager, role):
        # Arrange
        expected_qs = Position.objects.filter(role=role)

        # Act
        qs = position_manager.all()

        # Assert
        assert qs.count() == expected_qs.count()
        assert all(pos in expected_qs for pos in qs)

    @pytest.mark.parametrize('position_manager,role',
                             [(Position.employees,
                               Role.EMPLOYEE),
                              (Position.managers,
                               Role.MANAGER),
                                 (Position.dpos,
                                  Role.DPO)])
    def test_position_custom_manager_create(self, solo_infiltration, position_manager, role):
        # Arrange
        hansolo, _, unit = solo_infiltration

        # Act
        position = position_manager.create(account=hansolo, unit=unit)

        # Assert
        assert position.role == role

    @pytest.mark.parametrize('position_manager,role',
                             [(Position.employees,
                               Role.EMPLOYEE),
                              (Position.managers,
                               Role.MANAGER),
                                 (Position.dpos,
                                  Role.DPO)])
    def test_position_custom_manager_update(self, solo_infiltration, position_manager, role):
        # Arrange
        hansolo, supertrooper, unit = solo_infiltration

        # Act
        position_manager.filter(account=supertrooper, unit=unit).update(account=hansolo)

        # Assert
        assert supertrooper.positions.count() == 2
        assert hansolo.positions.first().role == role

    @pytest.mark.parametrize('position_manager,role',
                             [(Position.employees,
                               Role.EMPLOYEE),
                              (Position.managers,
                               Role.MANAGER),
                                 (Position.dpos,
                                  Role.DPO)])
    def test_position_custom_manager_delete(self, solo_infiltration, position_manager, role):
        # Arrange
        _, supertrooper, unit = solo_infiltration

        # Act
        position_manager.filter(account=supertrooper, unit=unit).delete()

        # Assert
        assert supertrooper.positions.count() == 2
        assert role not in supertrooper.positions.values_list("role")
