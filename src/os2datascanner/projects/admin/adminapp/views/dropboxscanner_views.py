# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

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
