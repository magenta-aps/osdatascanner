from django.db import models
from django.conf import settings

from os2datascanner.projects.utils import aes


class Grant(models.Model):
    """A Grant represents an entitlement to use an external API, issued to this
    OS2datascanner instance by an external gatekeeper.

    Grants exist to allow a separation between the roles of the organisational
    administrator, who can delegate functions to OS2datascanner, and the
    OS2datascanner administrator, who does not necessarily have that power."""

    organization = models.ForeignKey(
            'organizations.Organization',
            related_name="grants",
            on_delete=models.CASCADE)

    def validate(self):
        """Checks that this Grant is still valid, perhaps by using it to
        authenticate against the external API."""
        raise NotImplementedError("Grant.validate")

    class Meta:
        abstract = True


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
