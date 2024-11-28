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
from enum import Enum
from uuid import uuid4

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .position import Role

from functools import cached_property


class AccountPermission(Enum):
    """Enum of the codenames of permissions that can be granted to
    users in the report module by users in the admin module."""
    pass

    @classmethod
    def test_list(cls, lst):
        """It seems like python 3.12 supports using something like

        test = [var in EnumClass for var in lst]

        we should probably switch to that when we can."""
        results = []
        for val in lst:
            try:
                cls(val)
                results.append(True)
            except ValueError:
                results.append(False)
        return results


def validate_list_of_enum_vals(value):
    is_list = isinstance(value, list)
    contained_in_enum = all(AccountPermission.test_list(value))
    if not (is_list and contained_in_enum):
        raise ValidationError(
            "Field must only contain a list of enum-values!",
            code="invalid",
            params={"value": value},
        )


class Account(models.Model):
    """Represents a known entity in an organizational hierarchy.

    An Account may be related to several OrganizationalUnits within the same
    Organization.

    Note that Accounts are data representations of accounts on other systems
    and as such does not give its corresponding entity access to the
    OS2datascanner administration system.
    """

    serializer_class = None

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name=_('UUID'),
    )
    username = models.CharField(
        max_length=256,
        verbose_name=_('username'),
    )
    first_name = models.CharField(
        max_length=256,
        verbose_name=_('first name'),
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        max_length=256,
        verbose_name=_('last name'),
        blank=True,
        null=True,
    )
    email = models.EmailField(
        verbose_name=_('contact email'),
        blank=True,
        null=True,
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='user_accounts',
        verbose_name=_('organization'),
    )
    units = models.ManyToManyField(
        'OrganizationalUnit',
        through='Position',
    )
    manager = models.ForeignKey(
        'account',
        models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_accounts",
    )
    is_universal_dpo = models.BooleanField(
        verbose_name=_('universal dpo status'),
        default=False
    )
    is_superuser = models.BooleanField(
        verbose_name=_('superuser_status'),
        default=False
    )
    permissions = models.JSONField(
        verbose_name="Account permissions",
        default=list,
        validators=[validate_list_of_enum_vals],
        blank=True
    )

    def get_employed_units(self):
        positions = self.positions.filter(role=Role.EMPLOYEE)
        return self.units.filter(positions__in=positions)

    def get_managed_units(self):
        positions = self.positions.filter(role=Role.MANAGER)
        return self.units.filter(positions__in=positions)

    def get_dpo_units(self):
        positions = self.positions.filter(role=Role.DPO)
        return self.units.filter(positions__in=positions)

    class Meta:
        abstract = True
        verbose_name = _('account')
        verbose_name_plural = _('accounts')

        unique_together = ('organization', 'username')

    def __str__(self):
        return self.username

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.username} ({self.uuid})>'

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}" if self.last_name \
            else self.first_name if self.first_name \
            else self.username

    @cached_property
    def initials(self):
        initials = ""
        initials += self.first_name[0].capitalize() if self.first_name else ""
        initials += self.last_name[0].capitalize() if self.last_name else ""
        return initials if initials else None

    @cached_property
    def initials_color(self):
        colors = ['#BA7EBB', '#A161AE', '#B69DC9', '#7E6FA8', '#9D9EC9',
                  '#309D9D', '#60C6C3', '#75CFBE', '#53C193', '#309D82']

        return colors[int(self.pk) % 10]

    @cached_property
    def is_manager(self):
        return self.get_managed_units().exists()

    @cached_property
    def is_dpo(self):
        return self.is_universal_dpo or self.get_dpo_units().exists()

    @cached_property
    def is_remediator(self):
        from .aliases import AliasType  # avoid circular import
        return self.aliases.filter(_alias_type=AliasType.REMEDIATOR).exists()

    @cached_property
    def universal_remediator(self):
        """Returns true if the account is a universal remediator."""

        # Avoid circular import
        from .aliases import AliasType

        return self.aliases.filter(_alias_type=AliasType.REMEDIATOR, _value=0).exists()


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            "pk",
            "username",
            "first_name",
            "last_name",
            "organization",
            "manager",
            "is_superuser",
            "email",
            "is_universal_dpo",
            "permissions"]

    def get_unique_together_validators(self):
        # TODO: Tests implode if the serializers try to uphold unique-together
        # validators. We should have some validation logic in the future.
        return []
