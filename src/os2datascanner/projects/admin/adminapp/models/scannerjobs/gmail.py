import os
import json
from csv import DictReader

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import pgettext_lazy

from django.utils.translation import gettext_lazy as _
from .scanner import Scanner
from os2datascanner.engine2.model.gmail import GmailSource
from ...utils import upload_path_gmail_users


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

    scan_attachments = models.BooleanField(
        default=True,
        verbose_name=_('Scan attachments'),
        help_text=_("Scan attached files"),
    )

    user_emails_gmail = models.FileField(upload_to=upload_path_gmail_users,
                                         null=True,
                                         blank=True,
                                         validators=[validate_filetype_csv])

    @staticmethod
    def get_type():
        return 'gmail'

# This will need to change once we know how the accounts and orgs are imported
    def generate_sources(self):
        service_account = json.loads(self.google_api_grant.service_account)
        if self.user_emails_gmail:
            with open(os.path.join(settings.MEDIA_ROOT, self.user_emails_gmail.name), 'r') as usrem:
                csv_dict_reader = DictReader(usrem)
                for row in csv_dict_reader:
                    user_email = row['Email Address [Required]']
                    yield GmailSource(
                            google_api_grant=service_account,
                            user_email_gmail=user_email
                    )
        else:
            yield from (source for _, source in self.generate_sources_with_accounts())

    def generate_sources_with_accounts(self):
        service_account = json.loads(self.google_api_grant.service_account)
        for account in self.compute_covered_accounts():
            yield (account, GmailSource(
                    google_api_grant=service_account,
                    user_email_gmail=account.email
            ))

    object_name = pgettext_lazy("unit of scan", "email message")
    object_name_plural = pgettext_lazy("unit of scan", "email messages")

    class Meta:
        verbose_name = _("Gmail scanner")
