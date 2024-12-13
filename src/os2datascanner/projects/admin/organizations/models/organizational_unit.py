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
