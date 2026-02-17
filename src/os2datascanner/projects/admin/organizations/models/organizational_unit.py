# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from rest_framework import serializers
from rest_framework.fields import UUIDField

from django.utils.translation import gettext_lazy as _

from os2datascanner.projects.admin.import_services.models import Imported
from os2datascanner.core_organizational_structure.models import \
    OrganizationalUnit as Core_OrganizationalUnit
from os2datascanner.core_organizational_structure.models import \
    OrganizationalUnitSerializer as Core_OrganizationalUnitSerializer
from .broadcasted_mixin import Broadcasted


@Broadcasted.register
class OrganizationalUnit(Core_OrganizationalUnit, Imported):
    """ Core logic lives in the core_organizational_structure app.
        Additional specific logic can be implemented here. """

    @property
    def members_associated(self):
        return self.get_employees().count()

    def get_root(self):
        if self.parent is None:
            return self
        else:
            return self.parent.get_root()

    class Meta(Core_OrganizationalUnit.Meta):
        permissions = [("change_visibility_organizationalunit",
                        _("Can change visibility of organizational units"))]


class OrganizationalUnitSerializer(Core_OrganizationalUnitSerializer):
    from ..models.organization import Organization

    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=True,
        allow_null=False,
        # This will properly serialize uuid.UUID to str:
        pk_field=UUIDField(format='hex_verbose'))

    parent = serializers.PrimaryKeyRelatedField(
        queryset=OrganizationalUnit.objects.all(),
        required=False,
        allow_null=True,
        # This will properly serialize uuid.UUID to str:
        pk_field=UUIDField(format='hex_verbose'))

    class Meta(Core_OrganizationalUnitSerializer.Meta):
        model = OrganizationalUnit


OrganizationalUnit.serializer_class = OrganizationalUnitSerializer
