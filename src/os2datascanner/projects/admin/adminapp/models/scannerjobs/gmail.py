import json

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import pgettext_lazy

from django.utils.translation import gettext_lazy as _
from .scanner import Scanner
from os2datascanner.engine2.model.gmail import GmailSource
from ....organizations.models.aliases import AliasType


class GmailScanner(Scanner):

    def validate_filetype_json(upload_file):
        extension = upload_file.name.split('.')[-1]
        if extension not in ['json']:
            raise ValidationError(
                'Forkert filformat! Upload venligst i json'
            )

    def validate_filetype_csv(upload_file):
        extension = upload_file.name.split('.')[-1]
        if extension not in ['csv']:
            raise ValidationError(
                'Forkert filformat! Upload venligst i csv \n'
                'csv fil hentes af admin fra: https://admin.google.com/ac/users'
            )

    google_api_grant = models.ForeignKey("grants.GoogleApiGrant",
                                         on_delete=models.SET_NULL,
                                         null=True)

    @staticmethod
    def get_type():
        return 'gmail'

    def generate_sources(self):
        yield from (source for _, source in self.generate_sources_with_accounts())

    def generate_sources_with_accounts(self):
        google_api_grant = json.loads(self.google_api_grant.service_account)
        for account in self.compute_covered_accounts():
            for alias in account.aliases.filter(_alias_type=AliasType.EMAIL):
                yield (account, GmailSource(
                        google_api_grant=google_api_grant,
                        user_email_gmail=alias.value
                ))

    object_name = pgettext_lazy("unit of scan", "email message")
    object_name_plural = pgettext_lazy("unit of scan", "email messages")

    class Meta:
        verbose_name = _("Gmail scanner")
