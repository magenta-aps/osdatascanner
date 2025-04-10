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

from django import forms

from os2datascanner.projects.grants.views.smb_views import SMBGrantScannerForm
from .scanner_views import (
    ScannerBase,
    ScannerDelete,
    ScannerRemove,
    ScannerAskRun,
    ScannerRun,
    ScannerUpdate,
    ScannerCopy,
    ScannerCreate,
    ScannerList)
from .utils.grant_mixin import GrantMixin
from ..models.scannerjobs.filescanner import FileScanner
from django.utils.translation import gettext_lazy as _


class FileScannerList(ScannerList):
    """Displays list of file scanners."""

    model = FileScanner
    type = 'file'


file_scanner_fields = [
    'unc',
    'alias',
    'skip_super_hidden',
    'unc_is_home_root',
    'smb_grant'
]


class FileScannerCreate(GrantMixin, ScannerCreate):
    """Create a file scanner view."""

    model = FileScanner
    type = 'file'
    fields = ScannerBase.fields + file_scanner_fields

    def get_grant_form_classes(self):
        return {
            "smb_grant": SMBGrantScannerForm,
        }

    def get_form(self, form_class=None):
        """Adds special field password."""
        form = super().get_form(form_class)
        return initialize_form(form)

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/filescanners/%s/created/' % self.object.pk


class FileScannerUpdate(GrantMixin, ScannerUpdate):
    """Update a scanner view."""

    model = FileScanner
    type = 'file'
    fields = ScannerBase.fields + file_scanner_fields

    def get_grant_form_classes(self):
        return {
            "smb_grant": SMBGrantScannerForm,
        }

    def get_form(self, form_class=None):
        """Adds special field password."""
        form = super().get_form(form_class)
        return initialize_form(form)

    def get_success_url(self):
        """The URL to redirect to after successful updating.

        Will redirect the user to the validate view if the form was submitted
        with the 'save_and_validate' button.
        """
        if 'save_and_validate' in self.request.POST:
            return 'validate/'
        else:
            return '/filescanners/%s/saved/' % self.object.pk


class FileScannerRemove(ScannerRemove):
    """Remove a scanner view."""
    model = FileScanner
    success_url = '/filescanners/'


class FileScannerDelete(ScannerDelete):
    """Delete a scanner view."""
    model = FileScanner
    success_url = '/filescanners/'


class FileScannerCopy(GrantMixin, ScannerCopy):
    """Create a new copy of an existing FileScanner"""
    model = FileScanner
    type = 'file'
    fields = ScannerBase.fields + file_scanner_fields

    def get_grant_form_classes(self):
        return {
            "smb_grant": SMBGrantScannerForm,
        }

    def get_form(self, form_class=None):
        """Adds special field password."""
        # This doesn't copy over it's values, as credentials shouldn't
        # be copyable
        if form_class is None:
            form_class = self.get_form_class()

        form = super().get_form(form_class)
        return initialize_form(form)


class FileScannerAskRun(ScannerAskRun):
    """Prompt for starting file scan, validate first."""

    model = FileScanner
    run_url_name = "filescanner_run"


class FileScannerRun(ScannerRun):
    """View that handles starting of a file scanner run."""

    model = FileScanner


def initialize_form(form):
    """Initializes the form fields for username and password
    as they are not part of the file scanner model."""

    form.fields['unc'].widget.attrs['placeholder'] = _('e.g. //network-domain/top-folder')
    form.fields['alias'] = forms.CharField(max_length=64, required=False, label=_('Drive letter'))

    return form
