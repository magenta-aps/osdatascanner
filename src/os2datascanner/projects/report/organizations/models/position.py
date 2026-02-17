# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

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
