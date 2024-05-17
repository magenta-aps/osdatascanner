import pytest

from django.test import TestCase
from django.utils import translation

from os2datascanner.core_organizational_structure.models.position import Role
from os2datascanner.projects.admin.organizations.models import (
    OrganizationalUnit, Position)


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


@pytest.fixture
def oluf_positions(
        oluf,
        bingoklubben,
        nørre_snede_if,
        kok_sokker,
        dansk_kartoffelavlerforening,
        familien_sand):
    Position.objects.create(account=oluf, unit=bingoklubben, role=Role.DPO)
    Position.objects.create(account=oluf, unit=nørre_snede_if, role=Role.MANAGER)
    Position.objects.create(account=oluf, unit=kok_sokker, role=Role.DPO)
    Position.objects.create(account=oluf, unit=dansk_kartoffelavlerforening, role=Role.MANAGER)
    return (oluf,
            {"managed_units": [nørre_snede_if, dansk_kartoffelavlerforening],
             "dpod_units": [bingoklubben, kok_sokker],
             "employed_units": [familien_sand]})


@pytest.fixture
def the_julekalender(test_org, oluf, gertrud, benny, fritz, günther, hansi):
    ou = OrganizationalUnit.objects.create(name="Julekalender", organization=test_org)
    Position.objects.create(account=oluf, unit=ou, role=Role.DPO)
    Position.objects.create(account=gertrud, unit=ou, role=Role.EMPLOYEE)
    Position.objects.create(account=benny, unit=ou, role=Role.MANAGER)
    Position.objects.create(account=fritz, unit=ou, role=Role.EMPLOYEE)
    Position.objects.create(account=günther, unit=ou, role=Role.MANAGER)
    Position.objects.create(account=hansi, unit=ou, role=Role.DPO)
    return (
        ou, {
            "managers": [
                benny, günther], "dpos": [
                oluf, hansi], "employees": [
                    gertrud, fritz]})


@pytest.mark.django_db
class TestPositions:

    @pytest.mark.parametrize('method,key',
                             [('get_managed_units',
                               'managed_units'),
                              ('get_dpo_units',
                               'dpod_units'),
                              ('get_employed_units',
                               'employed_units')])
    def test_account_get_units(self, oluf_positions, method, key):
        # Arrange
        oluf, expected = oluf_positions

        # We expect the method to return the units defined in the expected dict
        expected_units = expected[key]

        # Act
        units = getattr(oluf, method)()

        # Assert
        assert len(units) == len(expected_units)
        assert all(unit in expected_units for unit in units)

    @pytest.mark.parametrize('method,key', [
        ('get_managers', 'managers'),
        ('get_dpos', 'dpos'),
        ('get_employees', 'employees')
    ])
    def test_organizational_unit_get_positions(self, the_julekalender, method, key):
        # Arrange
        ou, expected = the_julekalender

        # We expect the method to return the positions defined in the expected dict
        expected_accounts = expected[key]

        # Act
        accounts = getattr(ou, method)()

        # Assert
        assert len(accounts) == len(expected_accounts)
        assert all(acc in expected_accounts for acc in accounts)

    @pytest.mark.parametrize('position_manager,role',
                             [(Position.employees,
                               Role.EMPLOYEE),
                              (Position.managers,
                               Role.MANAGER),
                                 (Position.dpos,
                                  Role.DPO)])
    def test_position_custom_manager_queries(self, the_julekalender, position_manager, role):
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
    def test_position_custom_manager_create(self, the_julekalender, oluf, position_manager, role):
        # Arrange
        unit, _ = the_julekalender

        # Act
        position, _ = position_manager.get_or_create(account=oluf, unit=unit)

        # Assert
        assert position.role == role

    @pytest.mark.parametrize('position_manager,role',
                             [(Position.employees,
                               Role.EMPLOYEE),
                              (Position.managers,
                               Role.MANAGER),
                                 (Position.dpos,
                                  Role.DPO)])
    def test_position_custom_manager_update(
            self,
            fritz_boss,
            gammel_nok,
            nisserne,
            position_manager,
            role):
        # Act
        position_manager.filter(account=fritz_boss, unit=nisserne).update(account=gammel_nok)

        # Assert
        assert fritz_boss.positions.count() == 2
        assert gammel_nok.positions.first().role == role

    @pytest.mark.parametrize('position_manager,role',
                             [(Position.employees,
                               Role.EMPLOYEE),
                              (Position.managers,
                               Role.MANAGER),
                                 (Position.dpos,
                                  Role.DPO)])
    def test_position_custom_manager_delete(self, fritz_boss, nisserne, position_manager, role):
        # Act
        position_manager.filter(account=fritz_boss, unit=nisserne).delete()

        # Assert
        assert fritz_boss.positions.count() == 2
        assert role not in fritz_boss.positions.values_list("role")
