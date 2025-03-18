from django.db import models
from django.utils.translation import gettext_lazy as _
from .grant import Grant, wrap_encrypted_field


class GoogleApiGrant(Grant):
    """"
    A GoogleApiGrant represents credentials for a service account with
    authorization to access the Google API.
    """

    __match_args__ = ("service_account", "account_name")

    _service_account = models.JSONField(verbose_name=_("Service account json"),
                                        null=True)

    service_account = wrap_encrypted_field("_service_account")

    account_name = models.CharField(verbose_name=_("Service Account Name"), max_length=256)

    class Meta:
        verbose_name = _("Google Api Grant")
        constraints = [
            models.UniqueConstraint(
                    fields=["organization", "account_name"],
                    name="avoid_duplicate_grants")
        ]

    def __str__(self):
        return self.account_name

    @property
    def verbose_name(self):
        return self._meta.verbose_name
