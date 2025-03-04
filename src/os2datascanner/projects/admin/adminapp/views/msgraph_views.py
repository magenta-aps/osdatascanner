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

from django.forms import ModelChoiceField
from django.views import View
from django.urls import reverse_lazy

from os2datascanner.projects.grants.models.graphgrant import GraphGrant
from os2datascanner.projects.grants.views import MSGraphGrantRequestView
from os2datascanner.projects.admin.utilities import UserWrapper
from ..models.scannerjobs.msgraph import MSGraphMailScanner
from ..models.scannerjobs.msgraph import MSGraphFileScanner
from ..models.scannerjobs.msgraph import MSGraphCalendarScanner
from ..models.scannerjobs.msgraph import MSGraphTeamsFileScanner
from .scanner_views import (
        ScannerRun, ScannerList, ScannerAskRun, ScannerCreate, ScannerDelete,
        ScannerUpdate, ScannerCopy, ScannerCleanupStaleAccounts, ScannerRemove)


class MSGraphMailScannerList(ScannerList):
    """Displays the list of all Microsoft Graph mail scanner jobs."""
    model = MSGraphMailScanner
    type = 'msgraph-mail'


class MSGraphMailScannerCreate(View):
    """Creates a new Microsoft Graph mail scanner job.

    This view delegates to two other views: one sends the user to Microsoft
    Online to grant permission for the scan, and the other renders the normal
    scanner job creation form when the response comes back."""

    def dispatch(self, request, *args, **kwargs):
        user = UserWrapper(request.user)
        if GraphGrant.objects.filter(user.make_org_Q()).exists():
            handler = _MSGraphMailScannerCreate.as_view()
        else:
            handler = MSGraphGrantRequestView.as_view(
                    redirect_token="msgraphmailscanner_add")
        return handler(request, *args, **kwargs)


def patch_form(view, form):
    user = UserWrapper(view.request.user)

    grant_qs = GraphGrant.objects.filter(user.make_org_Q())
    form.fields['grant'] = ModelChoiceField(grant_qs, empty_label=None)

    return form


class _MSGraphMailScannerCreate(ScannerCreate):
    """Creates a new Microsoft Graph mail scanner job."""
    model = MSGraphMailScanner
    type = 'msgraph-mail'
    fields = [
        'name',
        'schedule',
        'grant',
        'only_notify_superadmin',
        'do_ocr',
        'org_unit',
        'exclusion_rule',
        'do_last_modified_check',
        'keep_false_positives',
        'scan_deleted_items_folder',
        'scan_syncissues_folder',
        'scan_attachments',
        'rule',
        'organization',
        'contacts'
     ]

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/msgraphmailscanners/%s/created/' % self.object.pk


class MSGraphMailScannerUpdate(ScannerUpdate):
    """Displays the parameters of an existing Microsoft Graph mail scanner job
    for modification."""
    model = MSGraphMailScanner
    type = 'msgraph-mailscanners'
    fields = [
        'name',
        'schedule',
        'grant',
        'only_notify_superadmin',
        'do_ocr',
        'org_unit',
        'exclusion_rule',
        'do_last_modified_check',
        'keep_false_positives',
        'scan_deleted_items_folder',
        'scan_syncissues_folder',
        'scan_attachments',
        'rule',
        'organization',
        'contacts'
     ]

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        return '/msgraphmailscanners/%s/saved/' % self.object.pk


class MSGraphMailScannerRemove(ScannerRemove):
    """Remove a scanner view."""
    model = MSGraphMailScanner
    success_url = reverse_lazy("msgraphmailscanners")


class MSGraphMailScannerDelete(ScannerDelete):
    """Deletes a Microsoft Graph mail scanner job."""
    model = MSGraphMailScanner
    fields = []
    success_url = reverse_lazy("msgraphmailscanners")


class MSGraphMailScannerCopy(ScannerCopy):
    """Creates a copy of an existing Microsoft Graph mail scanner job."""
    model = MSGraphMailScanner
    type = 'msgraph-mail'
    fields = [
        'name',
        'schedule',
        'grant',
        'only_notify_superadmin',
        'do_ocr',
        'org_unit',
        'exclusion_rule',
        'do_last_modified_check',
        'keep_false_positives',
        'scan_deleted_items_folder',
        'scan_syncissues_folder',
        'scan_attachments',
        'rule',
        'organization',
        'contacts'
     ]


class MSGraphMailScannerAskRun(ScannerAskRun):
    """Prompts the user for confirmation before running a Microsoft Graph mail
    scanner job."""
    model = MSGraphMailScanner
    run_url_name = "msgraphmailscanner_run"


class MSGraphMailScannerRun(ScannerRun):
    """Runs a Microsoft Graph mail scanner job, displaying the new scan tag on
    success and error details on failure."""
    model = MSGraphMailScanner


class MSGraphMailScannerCleanup(ScannerCleanupStaleAccounts):
    """Prompts the user for confirmation before deleting document reports
    belonging to accounts, which have gone stale for this scanner."""
    model = MSGraphMailScanner
    type = "msgraph-mail"


class MSGraphFileScannerList(ScannerList):
    """Displays the list of all Microsoft Graph file scanner jobs."""
    model = MSGraphFileScanner
    type = 'msgraph-file'


class MSGraphFileScannerCreate(View):
    """Creates a new Microsoft Graph file scanner job. (See MSGraphMailCreate
    for more details.)"""

    def dispatch(self, request, *args, **kwargs):
        user = UserWrapper(request.user)
        if GraphGrant.objects.filter(user.make_org_Q()).exists():
            handler = _MSGraphFileScannerCreate.as_view()
        else:
            handler = MSGraphGrantRequestView.as_view(
                    redirect_token="msgraphfilescanner_add")
        return handler(request, *args, **kwargs)


class _MSGraphFileScannerCreate(ScannerCreate):
    """Creates a new Microsoft Graph file scanner job."""
    model = MSGraphFileScanner
    type = 'msgraph-file'
    fields = ['name', 'schedule', 'grant',
              'org_unit', 'exclusion_rule', 'only_notify_superadmin',
              'scan_site_drives', 'scan_user_drives', 'do_ocr',
              'do_last_modified_check', 'rule', 'organization', 'keep_false_positives',
              'contacts']

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/msgraphfilescanners/%s/created/' % self.object.pk


class MSGraphFileScannerUpdate(ScannerUpdate):
    """Displays the parameters of an existing Microsoft Graph file scanner job
    for modification."""
    model = MSGraphFileScanner
    type = 'msgraph-filescanners'
    fields = ['name', 'schedule', 'grant', 'org_unit',
              'scan_site_drives', 'scan_user_drives',
              'do_ocr', 'only_notify_superadmin', 'exclusion_rule',
              'do_last_modified_check', 'rule', 'organization', 'keep_false_positives',
              'contacts']

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        return '/msgraphfilescanners/%s/saved/' % self.object.pk


class MSGraphFileScannerRemove(ScannerRemove):
    """Remove a scanner view."""
    model = MSGraphFileScanner
    success_url = reverse_lazy("msgraphfilescanners")


class MSGraphFileScannerDelete(ScannerDelete):
    """Deletes a Microsoft Graph file scanner job."""
    model = MSGraphFileScanner
    fields = []
    success_url = reverse_lazy("msgraphfilescanners")


class MSGraphFileScannerCopy(ScannerCopy):
    """Creates a copy of an existing Microsoft Graph mail scanner job."""
    model = MSGraphFileScanner
    type = 'msgraph-file'
    fields = ['name', 'schedule', 'grant',
              'org_unit', 'exclusion_rule', 'only_notify_superadmin',
              'scan_site_drives', 'scan_user_drives', 'do_ocr',
              'do_last_modified_check', 'rule', 'organization', 'keep_false_positives',
              'contacts']


class MSGraphFileScannerAskRun(ScannerAskRun):
    """Prompts the user for confirmation before running a Microsoft Graph file
    scanner job."""
    model = MSGraphFileScanner
    run_url_name = "msgraphfilescanner_run"


class MSGraphFileScannerRun(ScannerRun):
    """Runs a Microsoft Graph file scanner job, displaying the new scan tag on
    success and error details on failure."""
    model = MSGraphFileScanner


class MSGraphFileScannerCleanup(ScannerCleanupStaleAccounts):
    """Prompts the user for confirmation before deleting document reports
    belonging to accounts, which have gone stale for this scanner."""
    model = MSGraphFileScanner
    type = "msgraph-file"


class MSGraphCalendarScannerList(ScannerList):
    """"""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'


class MSGraphCalendarScannerCreate(View):
    """"""
    type = 'msgraph-calendar'

    def dispatch(self, request, *args, **kwargs):
        user = UserWrapper(request.user)
        if GraphGrant.objects.filter(user.make_org_Q()).exists():
            handler = _MSGraphCalendarScannerCreate.as_view()
        else:
            handler = MSGraphGrantRequestView.as_view(
                    redirect_token="msgraphcalendarscanner_add")
        return handler(request, *args, **kwargs)


class _MSGraphCalendarScannerCreate(ScannerCreate):
    """Creates a new Microsoft Graph calendar scanner job."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'
    fields = ['name', 'schedule', 'grant', 'only_notify_superadmin',
              'do_ocr', 'org_unit', 'exclusion_rule',
              'do_last_modified_check', 'rule', 'organization', 'keep_false_positives',
              'contacts']

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/msgraphcalendarscanners/%s/created' % self.object.pk


class MSGraphCalendarScannerUpdate(ScannerUpdate):
    """Displays the parameters of an existing Microsoft Graph mail scanner job
    for modification."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendarscanners'
    fields = ['name', 'schedule', 'grant', 'only_notify_superadmin',
              'do_ocr', 'org_unit', 'exclusion_rule',
              'do_last_modified_check', 'rule', 'organization', 'keep_false_positives',
              'contacts']

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        return '/msgraphcalendarscanners/%s/saved/' % self.object.pk


class MSGraphCalendarScannerRemove(ScannerRemove):
    """Remove a scanner view."""
    model = MSGraphCalendarScanner
    success_url = reverse_lazy("msgraphcalendarscanners")


class MSGraphCalendarScannerDelete(ScannerDelete):
    """Deletes a Microsoft Graph calendar scanner job."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'
    fields = []
    success_url = reverse_lazy("msgraphcalendarscanners")


class MSGraphCalendarScannerCopy(ScannerCopy):
    """Creates a copy of an existing Microsoft Graph calendar scanner job."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'
    fields = ['name', 'schedule', 'grant', 'only_notify_superadmin',
              'do_ocr', 'org_unit', 'exclusion_rule',
              'do_last_modified_check', 'rule', 'organization', 'keep_false_positives',
              'contacts']


class MSGraphCalendarScannerAskRun(ScannerAskRun):
    """Prompts the user for confirmation before running a Microsoft Graph
    calendar scanner job."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'
    run_url_name = "msgraphcalendarscanner_run"


class MSGraphCalendarScannerRun(ScannerRun):
    """Runs a Microsoft Graph calendar scanner job, displaying the new scan tag on
    success and error details on failure."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'


class MSGraphCalendarScannerCleanup(ScannerCleanupStaleAccounts):
    """Prompts the user for confirmation before deleting document reports
    belonging to accounts, which have gone stale for this scanner."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'


class MSGraphTeamsFileScannerList(ScannerList):
    """Displays the list of all Microsoft Graph file scanner jobs."""
    model = MSGraphTeamsFileScanner
    type = 'msgraph-teams-file'


class MSGraphTeamsFileScannerCreate(View):
    """Creates a new Microsoft Graph Teams file scanner job. (See MSGraphMailCreate
    for more details.)"""

    def dispatch(self, request, *args, **kwargs):
        user = UserWrapper(request.user)
        if GraphGrant.objects.filter(user.make_org_Q()).exists():
            handler = _MSGraphTeamsFileScannerCreate.as_view()
        else:
            handler = MSGraphGrantRequestView.as_view(
                    redirect_token="msgraphteamsfilescanner_add")
        return handler(request, *args, **kwargs)


class _MSGraphTeamsFileScannerCreate(ScannerCreate):
    """Creates a new Microsoft Graph file scanner job."""
    model = MSGraphTeamsFileScanner
    type = 'msgraph-teams-file'
    fields = ['name', 'schedule', 'grant',
              'exclusion_rule', 'only_notify_superadmin',
              'do_ocr', 'do_last_modified_check', 'rule',
              'organization', 'keep_false_positives']

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/msgraphteamsfilescanners/%s/created/' % self.object.pk


class MSGraphTeamsFileScannerUpdate(ScannerUpdate):
    """Displays the parameters of an existing Microsoft Graph file scanner job
    for modification."""
    model = MSGraphTeamsFileScanner
    type = 'msgraph-teams-filescanners'
    fields = ['name', 'schedule', 'grant',
              'do_ocr', 'only_notify_superadmin', 'exclusion_rule',
              'do_last_modified_check', 'rule', 'organization', 'keep_false_positives',
              'contacts']

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        return '/msgraphteamsfilescanners/%s/saved/' % self.object.pk


class MSGraphTeamsFileScannerRemove(ScannerRemove):
    """Remove a scanner view."""
    model = MSGraphTeamsFileScanner
    success_url = reverse_lazy("msgraphteamsfilescanners")


class MSGraphTeamsFileScannerDelete(ScannerDelete):
    """Deletes a Microsoft Graph file scanner job."""
    model = MSGraphTeamsFileScanner
    fields = []
    success_url = reverse_lazy("msgraphteamsfilescanners")


class MSGraphTeamsFileScannerCopy(ScannerCopy):
    """Creates a copy of an existing Microsoft Graph mail scanner job."""
    model = MSGraphTeamsFileScanner
    type = 'msgraph-teams-file'
    fields = ['name', 'schedule', 'grant',
              'exclusion_rule', 'only_notify_superadmin',
              'do_ocr', 'do_last_modified_check', 'rule',
              'organization', 'keep_false_positives', 'contacts']


class MSGraphTeamsFileScannerAskRun(ScannerAskRun):
    """Prompts the user for confirmation before running a Microsoft Graph file
    scanner job."""
    model = MSGraphTeamsFileScanner
    run_url_name = "msgraphteamsfilescanner_run"


class MSGraphTeamsFileScannerRun(ScannerRun):
    """Runs a Microsoft Graph file scanner job, displaying the new scan tag on
    success and error details on failure."""
    model = MSGraphTeamsFileScanner
