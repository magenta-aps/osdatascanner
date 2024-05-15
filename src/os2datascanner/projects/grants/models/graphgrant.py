from uuid import uuid4
from django.db import models

from os2datascanner.engine2.model.msgraph.utilities import make_token
from os2datascanner.projects.utils import aes
from .grant import Grant

from django.conf import settings


class GraphGrant(Grant):
    """A GraphGrant represents an entitlement to use the Microsoft Graph API
    to explore the resources associated with a particular tenant.

    (Note that the specific permissions associated with this entitlement are
    not specified here, but in the OS2datascanner application registration in
    Microsoft's portal.)"""
    app_id = models.UUIDField(
            default=uuid4, editable=False, verbose_name="app ID")

    tenant_id = models.UUIDField(
            default=uuid4, editable=False, verbose_name="tenant ID")

    _client_secret = models.JSONField(verbose_name="client secret")

    @classmethod
    def encrypt_secret(cls, secret: str) -> (str, str):
        return tuple(
                c.hex() for c in aes.encrypt(secret, settings.DECRYPTION_HEX))

    @property
    def client_secret(self) -> str:
        iv, ciphertext = [bytes.fromhex(c) for c in self._client_secret]
        return aes.decrypt(iv, ciphertext, settings.DECRYPTION_HEX)

    @client_secret.setter
    def client_secret(self, secret: str):
        self._client_secret = self.encrypt_secret(secret)

    def make_token(self):
        return make_token(
                self.app_id,
                str(self.tenant_id),
                self.client_secret)

    def validate(self):
        return self.make_token() is not None

    def __str__(self):
        return f"Microsoft Graph access to tenant {self.tenant_id}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                    fields=["organization", "tenant_id"],
                    name="avoid_multiple_overlapping_grants")
        ]
