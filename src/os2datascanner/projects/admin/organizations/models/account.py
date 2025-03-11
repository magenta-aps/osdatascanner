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
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector
from os2datascanner.core_organizational_structure.models import Account as Core_Account
from os2datascanner.core_organizational_structure.models import \
    AccountSerializer as Core_AccountSerializer
from os2datascanner.projects.admin.import_services.models import Imported

from .broadcasted_mixin import Broadcasted


@Broadcasted.register
class Account(Core_Account, Imported):
    """ Core logic lives in the core_organizational_structure app.
        Additional specific logic can be implemented here. """

    def get_remediator_scanners(self):
        """Returns a list of dicts of all scanners, which the user is
        specifically assigned remediator for. Each dict contains the name and
        the primary key of the scanner."""

        # Avoid circular import
        from .aliases import AliasType
        from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import Scanner

        scanner_pks = list(self.aliases.filter(_alias_type=AliasType.REMEDIATOR)
                                       .values_list('_value', flat=True))
        scanners = list(Scanner.objects.filter(pk__in=scanner_pks).values('name', 'pk'))
        print([scanner['pk'] for scanner in scanners])
        # Don't forget about deleted scanners!
        for pk in scanner_pks:
            if int(pk) not in [int(scanner['pk']) for scanner in scanners]:
                scanners.append({'name': _(f'Deleted scanner {pk}'), 'pk': pk})
        return scanners

    class Meta(Core_Account.Meta):
        indexes = [
            GinIndex(
                SearchVector(
                    'username',
                    'first_name',
                    'last_name',
                    config='english'),
                name='full_name_search')]
        permissions = [
            ("change_permissions_account",
             _("Can grant and take away permissions to and from users in the report module")),
        ]


class AccountSerializer(Core_AccountSerializer):
    from ..models.organization import Organization
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=True,
        allow_null=False,
        pk_field=UUIDField(format='hex_verbose')
    )
    manager = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(),
        required=False,
        allow_null=True,
        pk_field=UUIDField(format='hex_verbose')
    )

    class Meta(Core_AccountSerializer.Meta):
        model = Account


Account.serializer_class = AccountSerializer
