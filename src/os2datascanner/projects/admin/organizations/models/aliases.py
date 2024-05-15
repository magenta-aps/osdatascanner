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
