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
import structlog
import traceback

from rest_framework import serializers
from rest_framework.fields import UUIDField
from django.db import models, transaction, IntegrityError
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from functools import reduce

from os2datascanner.core_organizational_structure.models import Alias as Core_Alias
from os2datascanner.core_organizational_structure.models import \
    AliasSerializer as Core_AliasSerializer
from os2datascanner.core_organizational_structure.models.aliases import AliasType, \
    validate_regex_SID  # noqa

from ..seralizer import BaseBulkSerializer

logger = structlog.get_logger(__name__)


class AliasQuerySet(models.query.QuerySet):
    def associated_report_keys(self):
        return reduce(
            lambda results, it: results | it,
            (set(al.match_relation.values_list('pk', flat=True).iterator())
                for al in self),
            set())

    def delete(self):
        # Avoid circular import
        from os2datascanner.projects.report.reportapp.management.commands.result_collector import \
            create_aliases
        from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport

        associated_report_keys = set(self.associated_report_keys())

        with transaction.atomic():
            rv = super().delete()
            for dr in DocumentReport.objects.filter(
                    pk__in=associated_report_keys,
                    raw_metadata__isnull=False).iterator():
                create_aliases(dr)
            return rv

    def update(self, **kwargs):
        if 'account_id' in kwargs:
            if self.exclude(user__account__uuid=kwargs['account_id']).exists():
                raise IntegrityError(
                    "Attempted to update the account of aliases with the "
                    "Alias.objects.update method, but some aliases are related "
                    "to another user than related to the account with id "
                    f"'{kwargs.get('account_id')}'. Aliases must be related "
                    "to users and accounts, which are also related.")

        if 'user_id' in kwargs:
            if self.exclude(account__user__pk=kwargs['user_id']).exists():
                raise IntegrityError(
                    "Attempted to update the user of aliases with the "
                    "Alias.objects.update method, but some aliases are related "
                    "to another account than related to the user with id "
                    f"'{kwargs.get('user_id')}'. Aliases must be related to "
                    "users and accounts, which are also related.")

        if 'account' in kwargs:
            if self.exclude(user__account=kwargs['account']).exists():
                raise IntegrityError(
                    "Attempted to update the account of aliases with the "
                    "Alias.objects.update method, but some aliases are related "
                    "to another user than related to the account with id "
                    f"'{kwargs.get('account')}'. Aliases must be related "
                    "to users and accounts, which are also related.")

        if 'user' in kwargs.keys():
            if self.exclude(account__user=kwargs['user']).exists():
                raise IntegrityError(
                    "Attempted to update the user of aliases with the "
                    "Alias.objects.update method, but some aliases are related "
                    "to another account than related to the user with id "
                    f"'{kwargs.get('user')}'. Aliases must be related to "
                    "users and accounts, which are also related.")

        return super().update(**kwargs)


class AliasManager(models.Manager):
    def get_queryset(self):
        return AliasQuerySet(self.model, using=self._db, hints=self._hints)

    def create(self, **kwargs):
        user = kwargs.get('user')
        account = kwargs.get('account')
        if account and user == account.user:
            return super().create(**kwargs)
        else:
            raise IntegrityError(
                "Attempted to create an alias with the Alias.create method "
                f"related to the user '{user}' and the account '{account}'. "
                "Aliases must be related to a user and account, which are also "
                f"related.")

    def bulk_create(self, objs, ignore_conflicts: bool = False, **kwargs):
        from os2datascanner.projects.report.reportapp.utils import create_alias_and_match_relations
        allowed_objs = []
        for alias in objs:
            if alias.account == alias.user.account:
                allowed_objs.append(alias)
            elif not ignore_conflicts:
                raise IntegrityError(
                    "An alias sent to the bulk_create-method is "
                    f"related to the account {alias.account} and the user "
                    f"{alias.user}! Aliases must be related to accounts and "
                    "users, which are also related! No aliases were created.")
            else:
                logger.warning(
                    "An alias sent to the bulk_create-method is "
                    f"related to the account {alias.account} and the user "
                    f"{alias.user}! Aliases must be related to accounts and "
                    "users, which are also related! The alias was not created.")
                traceback.print_stack()

        # Sort out alias relations, based on created objects.
        # Note, that this is intentionally placed AFTER we've iterated once above
        # and created the objects. If it isn't we risk creating f.e. remediator aliases that
        # will stick, even if the next object is the correct owner.
        created_objects = super().bulk_create(
            allowed_objs, ignore_conflicts=ignore_conflicts, **kwargs
        )
        for created_alias in created_objects:
            create_alias_and_match_relations(created_alias)

        # It's kind of unfortunate - but since we, of course, create Account objects before
        # aliases, newly created accounts can't get their (if any) existing reports categorized
        # through AccountOutlookSetting bulk_create, because their alias-match relation simply
        # isn't established yet. Do something about that here...
        from .account_outlook_setting import AccountOutlookSetting
        from os2datascanner.core_organizational_structure.models import OutlookCategorizeChoices

        # Find the AccountOutlookSetting corresponding to alias.account & filter by org setting.
        outl_settings = (
            AccountOutlookSetting.objects.filter(
                account__in=[obj.account for obj in created_objects]).filter(
                account__organization__outlook_categorize_email_permission=OutlookCategorizeChoices.ORG_LEVEL)  # noqa: E501, can't make line shorter.

        )
        # That should mean we're good to categorize existing - categories should've been created.
        outl_settings.categorize_existing()

        return created_objects


class Alias(Core_Alias):
    """ Core logic lives in the core_organizational_structure app. """
    objects = AliasManager()
    serializer_class = None
    user = models.ForeignKey(User, null=False, verbose_name=_('user'),
                             on_delete=models.CASCADE, related_name="aliases")

    # TODO: In the future, we want to use "account" instead of django's User objects.
    # However, for now, we don't - hence this field is nullable.
    account = models.ForeignKey(
        'Account',
        on_delete=models.CASCADE,
        related_name='aliases',
        verbose_name=_('account'),
        blank=True,
        null=True
    )

    def delete(self, *args, **kwargs):
        # Defer to the QuerySet -- it cleans up in an optimised way
        return self._meta.model.objects.filter(pk=self.pk).delete()

    @property
    def key(self):
        return self.value

    def __str__(self):
        format_string = ('Alias ({type}) {value}')
        return format_string.format(
            type=self.alias_type.label,
            value=self.value,
        )

    def save(self, *args, prevent_mismatch: bool = True, **kwargs):
        if not prevent_mismatch:
            # This is only for testing purposes!
            super().save(*args, **kwargs)
        elif self.account and self.user == self.account.user:
            super().save(*args, **kwargs)
        else:
            raise IntegrityError(
                "Attempted to create an alias with the Alias.create method "
                f"related to the user '{self.user}' and the account '{self.account}'. "
                "Aliases must be related to a user and account, which are also "
                f"related.")


class AliasBulkSerializer(BaseBulkSerializer):
    class Meta:
        model = Alias

    @transaction.atomic
    def create(self, validated_data):
        aliases = [Alias(**alias_attrs) for alias_attrs in validated_data]
        for alias in aliases:
            # TODO: Fishy; correct when User/Acc merged.
            user_obj = User.objects.get(username=alias.account.username)
            alias.user = user_obj

        return Alias.objects.bulk_create(aliases)


class AliasSerializer(Core_AliasSerializer):
    pk = serializers.UUIDField(read_only=False)
    from ..models.account import Account
    account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(),
        required=True,
        allow_null=False,
        # This will properly serialize uuid.UUID to str:
        pk_field=UUIDField(format='hex_verbose'))

    class Meta(Core_AliasSerializer.Meta):
        model = Alias
        list_serializer_class = AliasBulkSerializer


Alias.serializer_class = AliasSerializer
