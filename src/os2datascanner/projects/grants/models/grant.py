from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from os2datascanner.projects.utils import aes


class Grant(models.Model):
    """A Grant represents an entitlement to use an external API, issued to this
    OS2datascanner instance by an external gatekeeper.

    Grants exist to allow a separation between the roles of the organisational
    administrator, who can delegate functions to OS2datascanner, and the
    OS2datascanner administrator, who does not necessarily have that power."""

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name=_('UUID'),
    )

    organization = models.ForeignKey(
            'organizations.Organization',
            related_name="%(class)s",
            related_query_name="%(class)ss",
            on_delete=models.CASCADE,
            verbose_name=_("Organization")
    )

    last_updated = models.DateTimeField(auto_now=True, verbose_name=_("last updated"), null=True)

    def validate(self):
        """Checks that this Grant is still valid, perhaps by using it to
        authenticate against the external API."""
        raise NotImplementedError("Grant.validate")

    @property
    def class_name(self):
        """ Returns class name"""
        return self.__class__.__name__

    @property
    def verbose_name(self):
        """Returns the verbose name of the Grant."""
        return NotImplementedError("Grant.verbose_name")

    @property
    def expiry(self):
        """ If implemented by a subclass, used to return the expiry date for grant."""
        return _("Not known")

    class Meta:
        abstract = False


def wrap_encrypted_field(field_name: str):
    """Returns a property object that transparently manages an encrypted field:
    trying to read from it will decrypt the value, and trying to assign to it
    will first encrypt the value."""

    def _get(self) -> str:
        iv, ciphertext = [bytes.fromhex(c) for c in getattr(self, field_name)]
        return aes.decrypt(iv, ciphertext, settings.DECRYPTION_HEX)

    def _set(self, secret: str):
        iv, ciphertext = tuple(
                c.hex() for c in aes.encrypt(secret, settings.DECRYPTION_HEX))
        setattr(self, field_name, [iv, ciphertext])

    return property(_get, _set)


class UsernamePasswordGrant(Grant):
    """A UsernamePasswordGrant represents a traditional service account, with a
    username and password."""
    __match_args__ = ("username", "password",)

    username = models.TextField(verbose_name=_("username"))
    _password = models.JSONField(verbose_name=_("password (encrypted)"))
    password = wrap_encrypted_field("_password")

    def clean(self):
        super().clean()
        # Since we're using multi table inheritance, it is not possible to use database level
        # constraints on f.e. username+organization (they reside in different tables).
        if self.username:
            if self.objects.filter(username=self.username,
                                   organization=self.organization,
                                   ).exclude(pk=self.pk).exists():
                raise ValidationError(_("A grant using this username already exists."))

    class Meta:
        abstract = True
