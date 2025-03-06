from uuid import uuid4
from django.db import models
from django.utils.translation import gettext_lazy as _
from os2datascanner.engine2.model.msgraph.utilities import make_token
from .grant import Grant, wrap_encrypted_field


class GraphGrant(Grant):
    """A GraphGrant represents an entitlement to use the Microsoft Graph API
    to explore the resources associated with a particular tenant.

    (Note that the specific permissions associated with this entitlement are
    not specified here, but in the OS2datascanner application registration in
    Microsoft's portal.)"""

    __match_args__ = ("app_id", "tenant_id", "client_secret",)

    app_id = models.UUIDField(
            default=uuid4, editable=True, verbose_name=_("app ID"))

    tenant_id = models.UUIDField(
            default=uuid4, editable=True, verbose_name=_("tenant ID"))

    expiry_date = models.DateField(
        blank=True, null=True, verbose_name=_("expiry date")
    )

    _client_secret = models.JSONField(verbose_name=_("client secret"))
    client_secret = wrap_encrypted_field("_client_secret")

    def make_token(self):
        return make_token(
                self.app_id,
                str(self.tenant_id),
                self.client_secret)

    def validate(self):
        return self.make_token() is not None

    @property
    def verbose_name(self):
        return self._meta.verbose_name

    @property
    def expiry(self):
        return self.expiry_date

    def __str__(self):
        return f"Microsoft Graph access to tenant {self.tenant_id}"

    class Meta:
        verbose_name = "Microsoft Graph"
        constraints = [
            models.UniqueConstraint(
                    fields=["organization", "tenant_id"],
                    name="avoid_multiple_overlapping_grants")
        ]
