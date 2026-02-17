# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.db import models, IntegrityError

from os2datascanner.core_organizational_structure.models import Alias as Core_Alias
from os2datascanner.core_organizational_structure.models import \
    AliasSerializer as Core_AliasSerializer
from os2datascanner.core_organizational_structure.models.aliases import AliasType  # noqa
from os2datascanner.projects.admin.import_services.models import Imported
from .broadcasted_mixin import Broadcasted


class AliasManager(models.Manager):
    def create(self, **kwargs):
        # If the account is being designated as a universal remediator ...
        if kwargs.get('_alias_type') == AliasType.REMEDIATOR and kwargs.get('_value') == 0:
            # ... delete all other remediator aliases for the account.
            Alias.objects.filter(
                account=kwargs.get('account'),
                _alias_type=AliasType.REMEDIATOR).delete()
            return super().create(**kwargs)
        # If the account is being designated as a remediator of a specific job ...
        elif kwargs.get('_alias_type') == AliasType.REMEDIATOR and kwargs.get('_value') != 0:
            # ... raise an exception if the account is already a universal remediator.
            account = kwargs.get('account')
            if Alias.objects.filter(
                    account=account,
                    _alias_type=AliasType.REMEDIATOR,
                    _value=0).exists():
                raise IntegrityError(
                    f"The account '{account}' is a universal remediator. "
                    "Assigning the account as a remediator for a specific "
                    "scannerjob is not allowed!")
            else:
                return super().create(**kwargs)
        else:
            return super().create(**kwargs)


@Broadcasted.register
class Alias(Core_Alias, Imported):
    """ Core logic lives in the core_organizational_structure app.
        Additional specific logic can be implemented here. """
    objects = AliasManager()


class AliasSerializer(Core_AliasSerializer):
    from rest_framework import serializers
    from rest_framework.fields import UUIDField
    from ..models.account import Account
    account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(),
        required=True,
        allow_null=False,
        # This will properly serialize uuid.UUID to str:
        pk_field=UUIDField(format='hex_verbose'))

    class Meta(Core_AliasSerializer.Meta):
        model = Alias


Alias.serializer_class = AliasSerializer
