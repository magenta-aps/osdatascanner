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
from .scanner_views import (
    ScannerBase,
    ScannerUpdate,
    ScannerCreate,
    ScannerList)
from ..models.scannerjobs.dropboxscanner import DropboxScanner


class DropboxScannerList(ScannerList):
    """Displays list of file scanners."""

    model = DropboxScanner
    type = 'dropbox'


dropbox_scanner_fields = [
    'token',
]


class DropboxScannerCreate(ScannerCreate):
    """Create a file scanner view."""

    model = DropboxScanner
    fields = ScannerBase.fields + dropbox_scanner_fields

    def get_form(self, form_class=None):
        """Adds special field password."""
        if form_class is None:
            form_class = self.get_form_class()

        form = super().get_form(form_class)

        return form

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/dropboxscanners/%s/created/' % self.object.pk


class DropboxScannerUpdate(ScannerUpdate):
    """Update a scanner view."""

    model = DropboxScanner
    fields = ScannerBase.fields + dropbox_scanner_fields

    def get_form(self, form_class=None):
        """Adds special field password and decrypts password."""
        if form_class is None:
            form_class = self.get_form_class()

        form = super().get_form(form_class)

        return form

    def get_success_url(self):
        """The URL to redirect to after successful updating.

        Will redirect the user to the validate view if the form was submitted
        with the 'save_and_validate' button.
        """
        if 'save_and_validate' in self.request.POST:
            return 'validate/'
        else:
            return '/dropboxscanners/%s/saved/' % self.object.pk
