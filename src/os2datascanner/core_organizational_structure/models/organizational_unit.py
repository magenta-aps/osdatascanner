# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _

from treebeard.al_tree import AL_Node, AL_NodeManager

from ..serializer import BaseSerializer
from .position import Role


class OrganizationalUnitQuerySet(models.QuerySet):
    def get_descendants(self):
        """Repeatedly finds all nodes whose parent is in the queryset, and
        adds them to the queryset, until no new nodes are found."""
        found_pks = set(self.values_list("pk", flat=True))
        new_pks = found_pks

        while new_pks:
            new_pks = set(
                self.model.objects.filter(parent__in=new_pks).values_list("pk", flat=True)
            ) - found_pks
            found_pks |= new_pks

        return self.model.objects.filter(pk__in=found_pks)


class OrganizationalUnitManager(AL_NodeManager.from_queryset(OrganizationalUnitQuerySet)):
    pass


class OrganizationalUnit(AL_Node):
    """Represents a fragment of an organizational hierarchy.

    An OrganizationalUnit typically represents a department or a product team.
    The hierarchy is built through the parent reference, and represents the
    organizational structure of a given organization.
    """

    serializer_class = None

    objects = OrganizationalUnitManager()

    node_order_by = ['name']

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name=_('UUID'),
    )

    name = models.CharField(
        max_length=256,
        verbose_name=_('name'),
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('parent unit'),
    )

    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    hidden = models.BooleanField(
        default=False,
        verbose_name=_('hidden'),
    )

    def get_employees(self):
        positions = self.positions.filter(role=Role.EMPLOYEE)
        return self.account_set.filter(positions__in=positions)

    def get_managers(self):
        positions = self.positions.filter(role=Role.MANAGER)
        return self.account_set.filter(positions__in=positions)

    def get_dpos(self):
        positions = self.positions.filter(role=Role.DPO)
        return self.account_set.filter(positions__in=positions)

    class Meta:
        abstract = True
        verbose_name = _('organizational unit')
        verbose_name_plural = _('organizational units')

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name} ({self.uuid})>"


class OrganizationalUnitSerializer(BaseSerializer):
    class Meta:
        fields = ["pk", "name", "parent", "organization", "hidden"]
