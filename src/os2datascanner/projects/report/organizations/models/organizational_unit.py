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
from mptt.managers import TreeManager
from os2datascanner.core_organizational_structure.models import \
    OrganizationalUnit as Core_OrganizationalUnit
from os2datascanner.core_organizational_structure.models import \
    OrganizationalUnitSerializer as Core_OrganizationalUnitSerializer

from rest_framework import serializers
from rest_framework.fields import UUIDField
from os2datascanner.core_organizational_structure.serializer import (BaseBulkSerializer,
                                                                     SelfRelatingField)
from django.db.models import Count, Q, F


class OrganizationlUnitManager(TreeManager):
    def with_match_counts(self):
        return self.annotate(
            total_ou_matches=Count(
                'positions__account__aliases__reports',
                filter=Q(
                    positions__account__aliases__reports__number_of_matches__gte=1,
                    positions__account__aliases__reports__only_notify_superadmin=False,
                    positions__account__aliases__reports__organization=F('organization'),
                ),
                exclude=Q(positions__account__aliases__shared=True),
                distinct=True),
            handled_ou_matches=Count(
                'positions__account__aliases__reports',
                filter=Q(
                    positions__account__aliases__reports__resolution_status__isnull=False,
                    positions__account__aliases__reports__number_of_matches__gte=1,
                    positions__account__aliases__reports__only_notify_superadmin=False,
                    positions__account__aliases__reports__organization=F('organization'),
                ),
                distinct=True))


class OrganizationalUnit(Core_OrganizationalUnit):
    """ Core logic lives in the core_organizational_structure app.
      Additional logic can be implemented here, but currently, none needed, hence we pass. """
    serializer_class = None

    objects = OrganizationlUnitManager()


class OrganizationalUnitBulkSerializer(BaseBulkSerializer):
    """ Bulk create & update logic lives in BaseBulkSerializer """
    class Meta:
        model = OrganizationalUnit


class OrganizationalUnitSerializer(Core_OrganizationalUnitSerializer):
    pk = serializers.UUIDField(read_only=False)
    lft = serializers.IntegerField(read_only=False)
    rght = serializers.IntegerField(read_only=False)
    tree_id = serializers.IntegerField(read_only=False)
    level = serializers.IntegerField(read_only=False)

    parent = SelfRelatingField(queryset=OrganizationalUnit.objects.all(), many=False,
                               allow_null=True)

    from ..models.organization import Organization
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=True,
        allow_null=False,
        # This will properly serialize uuid.UUID to str:
        pk_field=UUIDField(format='hex_verbose'),
    )

    class Meta(Core_OrganizationalUnitSerializer.Meta):
        model = OrganizationalUnit
        list_serializer_class = OrganizationalUnitBulkSerializer


OrganizationalUnit.serializer_class = OrganizationalUnitSerializer
