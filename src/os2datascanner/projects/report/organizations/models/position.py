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
from os2datascanner.core_organizational_structure.models import Position as Core_Position
from os2datascanner.core_organizational_structure.models import \
    PositionSerializer as Core_PositionSerializer
from os2datascanner.core_organizational_structure.serializer import BaseBulkSerializer


class Position(Core_Position):
    """ Core logic lives in the core_organizational_structure app.
      Additional logic can be implemented here, but currently, none needed, hence we pass. """
    serializer_class = None


class PositionBulkSerializer(BaseBulkSerializer):
    """ Bulk create & update logic lives in BaseBulkSerializer """
    class Meta:
        model = Position


class PositionSerializer(Core_PositionSerializer):
    from ..models.account import Account
    from ..models.organizational_unit import OrganizationalUnit
    pk = serializers.IntegerField(read_only=False)
    account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(),
        required=True,
        allow_null=False,
        # This will properly serialize uuid.UUID to str:
        pk_field=UUIDField(format='hex_verbose'))

    unit = serializers.PrimaryKeyRelatedField(
        queryset=OrganizationalUnit.objects.all(),
        required=True,
        allow_null=False,
        # This will properly serialize uuid.UUID to str:
        pk_field=UUIDField(format='hex_verbose'))

    class Meta(Core_PositionSerializer.Meta):
        model = Position
        list_serializer_class = PositionBulkSerializer


Position.serializer_class = PositionSerializer
