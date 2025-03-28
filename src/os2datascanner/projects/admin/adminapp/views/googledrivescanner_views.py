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
from ..models.scannerjobs.googledrivescanner import GoogleDriveScanner
from .scanner_views import (
    ScannerDelete,
    ScannerRemove,
    ScannerAskRun,
    ScannerRun,
    ScannerUpdate,
    ScannerCopy,
    ScannerCreate,
    ScannerList)


class GoogleDriveScannerList(ScannerList):
    """Displays a list of file scanners."""
    model = GoogleDriveScanner
    type = 'googledrive'


class GoogleDriveScannerCreate(GrantMixin, ScannerCreate):
    """Create a file scanner view"""

    model = GoogleDriveScanner
    fields = [
        'name',
        'schedule',
        'exclusion_rule',
        'do_ocr',
        'do_last_modified_check',
        'keep_false_positives',
        'only_notify_superadmin',
        'rule',
        'organization',
        'contacts',
        'google_api_grant',
        'org_unit'
    ]

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/googledrivescanners/%s/created/' % self.object.pk

    def get_grant_form_classes(self):
        return {"google_api_grant": GoogleApiScannerForm}


class GoogleDriveScannerUpdate(GrantMixin, ScannerUpdate):
    """Update a scanner view."""

    model = GoogleDriveScanner
    fields = [
        'name',
        'schedule',
        'exclusion_rule',
        'do_ocr',
        'do_last_modified_check',
        'keep_false_positives',
        'only_notify_superadmin',
        'rule',
        'organization',
        'contacts',
        'google_api_grant',
        'org_unit'
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

    def get_grant_form_classes(self):
        return {"google_api_grant": GoogleApiScannerForm}


class GoogleDriveScannerRemove(ScannerRemove):
    """Remove a scanner view."""
    model = GoogleDriveScanner
    success_url = '/googledrivescanners/'


class GoogleDriveScannerDelete(ScannerDelete):
    """Delete a scanner view."""
    model = GoogleDriveScanner
    fields = []
    success_url = '/googledrivescanners/'


class GoogleDriveScannerCopy(ScannerCopy):
    """Create a new copy of an existing Google Drive Scanner"""
    model = GoogleDriveScanner
    fields = [
        'name',
        'schedule',
        'exclusion_rule',
        'do_ocr',
        'do_last_modified_check',
        'keep_false_positives',
        'only_notify_superadmin',
        'rule',
        'organization',
        'contacts',
        'google_api_grant',
        'org_unit'
    ]

    def get_initial(self):
        initial = super(GoogleDriveScannerCopy, self).get_initial()
        initial["user_emails"] = self.get_scanner_object().user_emails
        return initial


class GoogleDriveScannerAskRun(ScannerAskRun):
    """Prompt for starting google drive scan, validate first."""
    model = GoogleDriveScanner
    run_url_name = "googledrivescanner_run"


class GoogleDriveScannerRun(ScannerRun):
    """View that handles starting of a scanner run."""
    model = GoogleDriveScanner
