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

from uuid import uuid4

from email_validator import validate_email

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..serializer import BaseSerializer

# Instance of regex validator, using regex to validate a SID
validate_regex_SID = RegexValidator(regex=r'^S-1-\d+(-\d+){0,15}$')


def validate_aliastype_value(kind, value):
    match kind:
        case AliasType.SID:
            validate_regex_SID(value)
        case AliasType.EMAIL | AliasType.USER_PRINCIPAL_NAME:
            # Don't check mail deliverability; we don't care about that
            # (email addresses might be disabled, and UPNs aren't necessarily
            # email addresses anyway)
            try:
                validate_email(value, check_deliverability=False)
            except Exception as e:
                raise ValidationError(e)
        case AliasType.REMEDIATOR:
            if not isinstance(value, int):
                raise ValidationError("Value must be an integer!")
        case _:
            # Don't validate anything else
            pass


class AliasType(models.TextChoices):
    """Enumeration of Alias types and their respective validators."""
    # A traditional Microsoft unique account ID
    # for example, S-1-5-21-147742093-2662784958-47748248-1000
    SID = 'SID', _('SID')

    # An email address
    # for example, alec@website.example
    EMAIL = 'email', _('email')

    # A scanner ID for which a user should be shown all unassociated results,
    # or 0 to give this access to all scanners
    # for example, 7
    REMEDIATOR = 'remediator', _('remediator')

    # A modern Microsoft unique account ID; looks like an email address, but
    # cannot necessarily receive email
    # for example, alec@example.onmicrosoft.com
    #           or alec@website.example
    USER_PRINCIPAL_NAME = 'upn', _('user principal name')

    # A web domain for which a user should be shown all matches (with
    # unfortunate naming)
    # for example, magenta.dk
    GENERIC = 'generic', _('generic')


class Alias(models.Model):
    """Represent an alias of a given type for a given Account.

    An Alias is a connection between a labelled item of identifying information
    and an Account. Aliases are broadcasted to the OS2datascanner Report module
    and used to assign matches to relevant user accounts.

    An Account may have several Aliases of the same type.
    """
    serializer_class = None

    uuid = models.UUIDField(
        default=uuid4,
        primary_key=True,
        editable=False,
        verbose_name=_('alias ID'),
    )
    account = models.ForeignKey(
        'Account',
        on_delete=models.CASCADE,
        related_name='aliases',
        verbose_name=_('account'),
    )
    _alias_type = models.CharField(
        max_length=32,
        db_column='alias_type',
        db_index=True,
        choices=AliasType.choices,
        verbose_name=_('alias type'),
    )
    _value = models.CharField(
        max_length=256,
        verbose_name=_('value')
    )
    shared = models.BooleanField(verbose_name=_('shared'), default=False, help_text=_(
        'The results related to the user through this alias is shared with other users. '
        'Matches associated through this alias will not be taken into account in '
        'user statistics.'), )

    @property
    def alias_type(self):
        return AliasType(self._alias_type)

    @alias_type.setter
    def alias_type(self, enum):
        self._alias_type = enum.value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        validate_aliastype_value(self.alias_type, val)
        self._value = val

    class Meta:
        abstract = True
        verbose_name = _('alias')
        verbose_name_plural = _('aliases')

        constraints = [
            # Disallow duplicated aliases for account.
            models.UniqueConstraint(fields=['account', '_alias_type', '_value'],
                                    name='%(app_label)s_alias_account_unique_constraint')
        ]

    def __str__(self):
        format_string = _('Alias ({type}) for {account_user}: {value}')
        return format_string.format(
            type=self.alias_type.label,
            account_user=self.account.username,
            value=self.value,
        )

    def __repr__(self):
        f_str = "<{cls}: {value} ({type}) for {account} (Account) - {uuid}>"
        return f_str.format(
            cls=self.__class__.__name__,
            account=self.account_id,
            type=self.alias_type.value,
            value=self.value,
            uuid=self.uuid,
        )


class AliasSerializer(BaseSerializer):
    class Meta:
        fields = ["pk", "account", "_value", "_alias_type", "shared"]
