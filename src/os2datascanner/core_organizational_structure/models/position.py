# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from abc import ABC

from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import TreeForeignKey
from ..serializer import BaseSerializer


class Role(models.TextChoices):
    """Enumeration of distinguished positions in organizations

    Members are defined by a (value, label) tuple to support translation of
    choice labels.
    """
    EMPLOYEE = 'employee', _('employee')
    MANAGER = 'manager', _('manager')
    DPO = 'dpo', _('data protection officer')


class RolePositionQuerySet(ABC, models.QuerySet):
    """Abstract parent class for querysets of positions with a certain role."""

    def create(self, *args, **kwargs):
        kwargs["role"] = self._role
        return super().create(*args, **kwargs)

    def update(self, *args, **kwargs):
        if "role" in kwargs:
            kwargs["role"] = self._role
        return super().update(*args, **kwargs)


class EmployeePositionQuerySet(RolePositionQuerySet):
    _role = Role.EMPLOYEE


class ManagerPositionQuerySet(RolePositionQuerySet):
    _role = Role.MANAGER


class DPOPositionQuerySet(RolePositionQuerySet):
    _role = Role.DPO


class RolePositionManager(ABC, models.Manager):
    """Abstract parent class for defining managers specific for querying
    positions with a certain role."""

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=self._role)


class EmployeePositionManager(RolePositionManager):
    _queryset_class = EmployeePositionQuerySet
    _role = Role.EMPLOYEE


class ManagerPositionManager(RolePositionManager):
    _queryset_class = ManagerPositionQuerySet
    _role = Role.MANAGER


class DPOPositionManager(RolePositionManager):
    _queryset_class = DPOPositionQuerySet
    _role = Role.DPO


class Position(models.Model):
    serializer_class = None

    # When defining custom managers, the default manager is excluded by default.
    objects = models.Manager()

    employees = EmployeePositionManager()
    managers = ManagerPositionManager()
    dpos = DPOPositionManager()

    account = models.ForeignKey(
        'Account',
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name=_('account'),
    )
    unit = TreeForeignKey(
        'OrganizationalUnit',
        on_delete=models.CASCADE,
        verbose_name=_('organizational unit'),
        related_name='positions',
    )
    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        null=False,
        blank=False,
        default=Role.EMPLOYEE.value,
        db_index=True,
    )

    class Meta:
        abstract = True
        verbose_name = _('position')
        verbose_name_plural = _('positions')

        # Do not allow duplicate positions.
        constraints = [
            models.UniqueConstraint(fields=['account', 'unit', 'role'],
                                    name='%(app_label)s_position_unique_constraint')
        ]

    def __str__(self):
        format_str = _("{cls}: {account} ({role}) at {unit}")
        cls = _(self.__class__.__name__.lower()).capitalize()
        account = self.account
        role = Role(self.role).label
        unit = self.unit.name
        return format_str.format(account=account, role=role, unit=unit, cls=cls)

    def __repr__(self):
        cls = self.__class__.__name__
        account = self.account
        role = self.role
        unit = self.unit
        return f"<{cls}: {account} (account) is {role} at {unit} (unit)>"


class PositionSerializer(BaseSerializer):
    class Meta:
        fields = ["pk", "account", "unit", "role"]
