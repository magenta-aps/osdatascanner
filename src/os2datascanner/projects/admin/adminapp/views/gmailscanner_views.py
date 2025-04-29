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
# OS2datascanner is developed by Magenta in collaboration with the OS2 public
# sector open source network <https://os2.eu/>.
#
from os2datascanner.projects.admin.adminapp.views.utils.grant_mixin import GrantMixin
from os2datascanner.projects.grants.views.googleapi_views import GoogleApiScannerForm
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
    'org_unit',
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
