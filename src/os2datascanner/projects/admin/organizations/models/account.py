# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from rest_framework import serializers
from rest_framework.fields import UUIDField
from django.db import models
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

    distinguished_name = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('imported LDAP distinguished name'),
    )

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
                scanners.append({
                    'name': _('Deleted scanner {pk}').format(pk=pk),
                    'pk': pk
                })
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
