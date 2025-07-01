import json

from django.db import models
from django.conf import settings
from django.utils.translation import pgettext_lazy

from django.utils.translation import gettext_lazy as _
from .scanner import Scanner
from os2datascanner.engine2.model.googleshareddrive import GoogleSharedDrivesSource


class GoogleSharedDriveScanner(Scanner):

    @staticmethod
    def enabled():
        return settings.ENABLE_GOOGLESHAREDDRIVESCAN

    google_api_grant = models.ForeignKey("grants.GoogleApiGrant",
                                         on_delete=models.SET_NULL,
                                         null=True)

    google_admin_account = models.TextField(
        blank=False,
        verbose_name=_("Google Workspace Admin Email"),
        help_text=_(
            "In order to scan shared drives an admin"
            "account for the scanned workspace is required."
            )
    )

    @staticmethod
    def get_type():
        return 'googleshareddrive'

    def generate_sources(self):
        google_api_grant = json.loads(self.google_api_grant.service_account)
        yield GoogleSharedDrivesSource(
            google_api_grant=google_api_grant,
            google_admin_account=self.google_admin_account
        )

    object_name = pgettext_lazy("unit of scan", "file")
    object_name_plural = pgettext_lazy("unit of scan", "files")

    class Meta:
        verbose_name = _("Google Shared Drive scanner")
