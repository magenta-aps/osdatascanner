import os
import json
from csv import DictReader

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import pgettext_lazy

from django.utils.translation import gettext_lazy as _
from .scanner import Scanner
from ...utils import upload_path_gdrive_users
from os2datascanner.engine2.model.googledrive import GoogleDriveSource


class GoogleDriveScanner(Scanner):

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

    user_emails = models.FileField(upload_to=upload_path_gdrive_users,
                                   null=False,
                                   validators=[validate_filetype_csv])

    @staticmethod
    def get_type():
        return 'googledrive'

    def generate_sources(self):
        google_api_grant = json.loads(self.google_api_grant.service_account)
        with open(os.path.join(settings.MEDIA_ROOT, self.user_emails.name), 'r') as usrem:
            csv_dict_reader = DictReader(usrem)
            for row in csv_dict_reader:
                user_email = row['Email Address [Required]']
                yield GoogleDriveSource(google_api_grant=google_api_grant,
                                        user_email=user_email)

    object_name = pgettext_lazy("unit of scan", "file")
    object_name_plural = pgettext_lazy("unit of scan", "files")

    class Meta:
        verbose_name = _("Google Drive scanner")
