# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2datascanner is developed by Magenta in collaboration with the OS2 public
# sector open source network <https://os2.eu/>.
#
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
