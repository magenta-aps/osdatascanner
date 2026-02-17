# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import structlog
from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator
from django.utils.translation import pgettext_lazy
from django.utils.translation import gettext_lazy as _

from os2datascanner.engine2.model.dropbox import DropboxSource
from .scanner import Scanner

# Get an instance of a logger
logger = structlog.get_logger("adminapp")


class DropboxScanner(Scanner):
    """File scanner for scanning network drives and folders"""

    token = models.CharField(
        max_length=64,
        verbose_name='Token',
        null=True,
        validators=[MinLengthValidator(64)])

    def __str__(self):
        """Return the URL for the scanner."""
        return self.url

    @staticmethod
    def get_type():
        return 'dropbox'

    def make_engine2_source(self):
        return DropboxSource(
            self.token)

    @staticmethod
    def enabled():
        return settings.ENABLE_DROPBOXSCAN

    object_name = pgettext_lazy("unit of scan", "file")
    object_name_plural = pgettext_lazy("unit of scan", "files")

    class Meta:
        verbose_name = _("Dropbox scanner")
