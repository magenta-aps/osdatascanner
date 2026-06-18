# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _

from .utilities import ModelChoiceFlag


class Scan(ModelChoiceFlag):
    """Enumeration of available scan types"""
    # Ints are given explicitly to allow reorganization without database issues
    WEBSCAN = (1 << 0, _('web scan'))
    FILESCAN = (1 << 1, _('file scan'))
    EXCHANGESCAN = (1 << 2, _('Exchange scan'))
    SBSYSSCAN = (1 << 3, _('SBSYS scan'))
    DROPBOXSCAN = (1 << 4, _('Dropbox scan'))
    MSGRAPH_MAILSCAN = (1 << 5, _('Microsoft Graph - mail scan'))
    MSGRAPH_FILESCAN = (1 << 6, _('Microsoft Graph - file scan'))
    GOOGLE_DRIVESCAN = (1 << 7, _('Google - drive scan'))
    GOOGLE_MAILSCAN = (1 << 8, _('Google - mail scan'))
    MSGRAPH_TEAMS_FILESCAN = (1 << 9, _('Microsoft Graph - Teams file scan'))
    # NB! Int value must not exceed 2,147,483,647 (limited by the db field)
    # Thus a maximum of 31 scan types in one Flag class


class ImportSource(models.TextChoices):
    """The single identity-management source a Client imports organizational data from."""
    NONE = "none", _("No import")
    LDAP = "ldap", _("LDAP")
    MS_GRAPH = "msgraph", _("Microsoft Graph")
    OS2MO = "os2mo", _("OS2mo")
    GOOGLE_WORKSPACE = "google", _("Google Workspace")


class Client(models.Model):
    """Stores data for a specific client.

    A Client is identified by a uuid and further stores a human readable name,
    contact information (email and phone number), the import source for
    organizational data, and enabled scan types.

    In a multi-tenant system, any Client should only be able to access and
    manage resources owned by that Client.
    """

    uuid = models.UUIDField(
        default=uuid4,
        primary_key=True,
        editable=False,
        verbose_name=_('client ID'),
    )
    name = models.CharField(
        max_length=256,
        unique=True,
        verbose_name=_('name'),
    )
    contact_email = models.CharField(
        max_length=256,
        verbose_name=_('e-mail'),
    )
    contact_phone = models.CharField(
        max_length=32,
        verbose_name=_('phone number'),
    )

    import_source = models.CharField(
        max_length=16,
        choices=ImportSource.choices,
        default=ImportSource.NONE,
        verbose_name=_('import source'),
    )

    scans = models.PositiveIntegerField(
        default=0,
        validators=[Scan.validator],
        verbose_name=_('activated scan types'),
    )

    explorer_delta_queue = models.TextField(
        default="os2ds_scan_specs",
    )
    explorer_full_queue = models.TextField(
        default="os2ds_scan_specs",
    )
    conversion_delta_queue = models.TextField(
        default="os2ds_conversions"
    )
    conversion_full_queue = models.TextField(
        default="os2ds_conversions"
    )

    @property
    def activated_scan_types(self):
        return Scan(self.scans)

    @activated_scan_types.setter
    def activated_scan_types(self, flag_enum):
        self.scans = flag_enum.value

    class Meta:
        verbose_name = _('client')
        verbose_name_plural = _('clients')

    def __str__(self):
        """Return the name of the client"""
        return self.name

    def __repr__(self):
        """Return the id and name of the client"""
        return f"<{self.__class__.__name__}: {self.name} ({self.uuid})>"
