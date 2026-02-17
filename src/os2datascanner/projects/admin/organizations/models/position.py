# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from rest_framework import serializers
from rest_framework.fields import UUIDField

from os2datascanner.projects.admin.import_services.models import Imported
from os2datascanner.core_organizational_structure.models import Position as Core_Position
from os2datascanner.core_organizational_structure.models import \
    PositionSerializer as Core_PositionSerializer
from .broadcasted_mixin import Broadcasted


@Broadcasted.register
class Position(Core_Position, Imported):
    """ Core logic lives in the core_organizational_structure app.
        Additional specific logic can be implemented here. """


class PositionSerializer(Core_PositionSerializer):
    from ..models.account import Account
    from ..models.organizational_unit import OrganizationalUnit

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


Position.serializer_class = PositionSerializer
