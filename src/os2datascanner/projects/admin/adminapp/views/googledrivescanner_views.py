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
from ..models.scannerjobs.googledrivescanner_model import GoogleDriveScanner
from .scanner_views import *


class GoogleDriveScannerList(ScannerList):
    """Displays a list of file scanners."""
    model = GoogleDriveScanner
    type = 'googledrive'


class GoogleDriveScannerCreate(ScannerCreate):
    """Create a file scanner view"""

    model = GoogleDriveScanner
    fields = [
        'name',
        'schedule',
        'service_account_file',
        'user_emails',
        'exclusion_rules',
        'do_ocr',
        'do_last_modified_check',
        'rules',
        'ldap_organization'
    ]

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/googledrivescanners/%s/created/' % self.object.pk


class GoogleDriveScannerUpdate(ScannerUpdate):
    """Update a scanner view."""

    model = GoogleDriveScanner
    fields = [
        'name',
        'schedule',
        'service_account_file',
        'user_emails',
        'exclusion_rules',
        'do_ocr',
        'do_last_modified_check',
        'rules',
    ]

    def get_success_url(self):
        """The URL to redirect to after successful updating.

        Will redirect the user to the validate view if the form was submitted
        with the 'save_and_validate' button.
        """
        if 'save_and_validate' in self.request.POST:
            return 'validate/'
        else:
            return '/googledrivescanners/%s/saved/' % self.object.pk


class GoogleDriveScannerDelete(ScannerDelete):
    """Delete a scanner view."""
    model = GoogleDriveScanner
    fields = []
    success_url = '/googledrivescanners/'


class GoogleDriveScannerAskRun(ScannerAskRun):
    """Prompt for starting google drive scan, validate first."""
    model = GoogleDriveScanner


class GoogleDriveScannerRun(ScannerRun):
    """View that handles starting of a scanner run."""
    model = GoogleDriveScanner
