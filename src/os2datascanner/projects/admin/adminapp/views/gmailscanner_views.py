# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from os2datascanner.projects.admin.adminapp.views.utils.grant_mixin import GrantMixin
from os2datascanner.projects.admin.organizations.views import GoogleApiScannerForm
from ..models.scannerjobs.gmail import GmailScanner
from .scanner_views import (
    ScannerBase,
    ScannerUpdate,
    ScannerCopy,
    ScannerCreate,
    ScannerList,
    ScannerCleanupStaleAccounts
    )


class GmailScannerList(ScannerList):
    """Displays a list of file scanners."""
    model = GmailScanner
    type = 'gmail'


gmail_scanner_fields = [
    'scan_subject',
    'google_api_grant',
    'org_units',
    'scan_attachments',
    'scan_entire_org',
]


class GmailScannerCreate(GrantMixin, ScannerCreate):
    """Create a scanner view"""

    model = GmailScanner
    fields = ScannerBase.fields + gmail_scanner_fields

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/gmailscanners/%s/created/' % self.object.pk

    def get_grant_form_classes(self):
        return {"google_api_grant": GoogleApiScannerForm}


class GmailScannerUpdate(GrantMixin, ScannerUpdate):
    """Update a scanner view."""

    model = GmailScanner
    fields = ScannerBase.fields + gmail_scanner_fields

    def get_success_url(self):
        """The URL to redirect to after successful updating.

        Will redirect the user to the validate view if the form was submitted
        with the 'save_and_validate' button.
        """
        if 'save_and_validate' in self.request.POST:
            return 'validate/'
        else:
            return '/gmailscanners/%s/saved/' % self.object.pk

    def get_grant_form_classes(self):
        return {"google_api_grant": GoogleApiScannerForm}


class GmailScannerCopy(ScannerCopy):
    """Create a new copy of an existing GmailScanner"""

    model = GmailScanner
    fields = ScannerBase.fields + gmail_scanner_fields

    def get_initial(self):
        initial = super(GmailScannerCopy, self).get_initial()
        return initial


class GmailScannerCleanup(ScannerCleanupStaleAccounts):
    """Cleanup stale accounts for a GmailScanner"""
    model = GmailScanner
    type = "gmail"
