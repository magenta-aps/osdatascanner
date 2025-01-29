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
# OS2Webscanner was developed by Magenta in collaboration with OS2 the
# Danish community of open source municipalities (http://www.os2web.dk/).
#
# The code is currently governed by OS2 the Danish community of open
# source municipalities ( http://www.os2web.dk/ )

import structlog
from django.db import models
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django.core.exceptions import ValidationError

from os2datascanner.engine2.model.smbc import SMBCSource
from os2datascanner.projects.grants.models import SMBGrant
from .scanner import Scanner

# Get an instance of a logger
logger = structlog.get_logger("adminapp")


class FileScanner(Scanner):
    """File scanner for scanning network drives and folders"""
    supports_rule_preexec = True

    unc = models.CharField(max_length=2048, blank=False, verbose_name='UNC')
    alias = models.CharField(
        max_length=64,
        verbose_name=_("drive letter"),
        null=True)
    skip_super_hidden = models.BooleanField(
        verbose_name=_("skip super-hidden files"),
        help_text=_("do not scan files with the HIDDEN and SYSTEM bits"
                    " set, or files with the HIDDEN bit set whose name"
                    " starts with a tilde"),
        default=False)
    unc_is_home_root = models.BooleanField(
        verbose_name=_("UNC is home root"),
        help_text=_("all folders under the given UNC are user home folders;"
                    " their owners have responsibility for everything they"
                    " contain regardless of other filesystem metadata"),
        default=False)

    smb_grant = models.ForeignKey(SMBGrant, null=True, on_delete=models.SET_NULL)

    @property
    def root_url(self):
        """Return the root url of the domain."""
        url = self.unc.replace('*.', '')
        return url

    def __str__(self):
        """Return the URL for the scanner."""
        return self.unc

    @staticmethod
    def get_type():
        return 'file'

    def generate_sources(self):
        yield SMBCSource(
                self.unc,
                user=self.authentication.username,
                password=self.authentication.get_password(),
                domain=self.authentication.domain,
                driveletter=self.alias,
                skip_super_hidden=self.skip_super_hidden,
                unc_is_home_root=self.unc_is_home_root)

    def clean(self):
        # Backslashes (\) are an escaped character and therefore '\\\\' = '\\'
        if not self.unc.startswith(('//', '\\\\')) or any(x in self.unc for x in ['\\\\\\', '///']):
            error = _("UNC must follow the UNC format")
            raise ValidationError({"unc": error})

    object_name = pgettext_lazy("unit of scan", "file")
    object_name_plural = pgettext_lazy("unit of scan", "files")

    class Meta:
        verbose_name = _("Filescanner")
