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


class MSGraphMailList(ScannerList):
    """Displays the list of all Microsoft Graph mail scanner jobs."""
    model = MSGraphMailScanner
    type = 'msgraph-mail'


class MSGraphMailCreate(View):
    """Creates a new Microsoft Graph mail scanner job.

    This view delegates to two other views: one sends the user to Microsoft
    Online to grant permission for the scan, and the other renders the normal
    scanner job creation form when the response comes back."""

    def dispatch(self, request, *args, **kwargs):
        user = UserWrapper(request.user)
        if GraphGrant.objects.filter(user.make_org_Q()).exists():
            handler = _MSGraphMailCreate.as_view()
        else:
            handler = MSGraphGrantRequestView.as_view(
                    redirect_token="msgraphmailscanner_add")
        return handler(request, *args, **kwargs)


def patch_form(view, form):
    user = UserWrapper(view.request.user)

    grant_qs = GraphGrant.objects.filter(user.make_org_Q())
    form.fields['grant'] = ModelChoiceField(grant_qs, empty_label=None)

    return form


class _MSGraphMailCreate(ScannerCreate):
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
     ]

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/msgraph-mailscanners/%s/created/' % self.object.pk


class MSGraphMailUpdate(ScannerUpdate):
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
     ]

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        return '/msgraph-mailscanners/%s/saved/' % self.object.pk


class MSGraphMailRemove(ScannerRemove):
    """Remove a scanner view."""
    model = MSGraphMailScanner
    success_url = '/msgraph-mailscanners/'


class MSGraphMailDelete(ScannerDelete):
    """Deletes a Microsoft Graph mail scanner job."""
    model = MSGraphMailScanner
    fields = []
    success_url = '/msgraph-mailscanners/'


class MSGraphMailCopy(ScannerCopy):
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
     ]


class MSGraphMailAskRun(ScannerAskRun):
    """Prompts the user for confirmation before running a Microsoft Graph mail
    scanner job."""
    model = MSGraphMailScanner
    run_url_name = "msgraphmailscanner_run"


class MSGraphMailRun(ScannerRun):
    """Runs a Microsoft Graph mail scanner job, displaying the new scan tag on
    success and error details on failure."""
    model = MSGraphMailScanner


class MSGraphMailCleanupStaleAccounts(ScannerCleanupStaleAccounts):
    """Prompts the user for confirmation before deleting document reports
    belonging to accounts, which have gone stale for this scanner."""
    model = MSGraphMailScanner
    type = "msgraph-mail"


class MSGraphFileList(ScannerList):
    """Displays the list of all Microsoft Graph file scanner jobs."""
    model = MSGraphFileScanner
    type = 'msgraph-file'


class MSGraphFileCreate(View):
    """Creates a new Microsoft Graph file scanner job. (See MSGraphMailCreate
    for more details.)"""

    def dispatch(self, request, *args, **kwargs):
        user = UserWrapper(request.user)
        if GraphGrant.objects.filter(user.make_org_Q()).exists():
            handler = _MSGraphFileCreate.as_view()
        else:
            handler = MSGraphGrantRequestView.as_view(
                    redirect_token="msgraphfilescanner_add")
        return handler(request, *args, **kwargs)


class _MSGraphFileCreate(ScannerCreate):
    """Creates a new Microsoft Graph file scanner job."""
    model = MSGraphFileScanner
    type = 'msgraph-file'
    fields = ['name', 'schedule', 'grant',
              'org_unit', 'exclusion_rule', 'only_notify_superadmin',
              'scan_site_drives', 'scan_user_drives', 'do_ocr',
              'do_last_modified_check', 'rule', 'organization', 'keep_false_positives']

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/msgraph-filescanners/%s/created/' % self.object.pk


class MSGraphFileUpdate(ScannerUpdate):
    """Displays the parameters of an existing Microsoft Graph file scanner job
    for modification."""
    model = MSGraphFileScanner
    type = 'msgraph-filescanners'
    fields = ['name', 'schedule', 'grant', 'org_unit',
              'scan_site_drives', 'scan_user_drives',
              'do_ocr', 'only_notify_superadmin', 'exclusion_rule',
              'do_last_modified_check', 'rule', 'organization', 'keep_false_positives']

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        return '/msgraph-filescanners/%s/saved/' % self.object.pk


class MSGraphFileRemove(ScannerRemove):
    """Remove a scanner view."""
    model = MSGraphFileScanner
    success_url = '/msgraph-filescanners/'


class MSGraphFileDelete(ScannerDelete):
    """Deletes a Microsoft Graph file scanner job."""
    model = MSGraphFileScanner
    fields = []
    success_url = '/msgraph-filescanners/'


class MSGraphFileCopy(ScannerCopy):
    """Creates a copy of an existing Microsoft Graph mail scanner job."""
    model = MSGraphFileScanner
    type = 'msgraph-file'
    fields = ['name', 'schedule', 'grant',
              'org_unit', 'exclusion_rule', 'only_notify_superadmin',
              'scan_site_drives', 'scan_user_drives', 'do_ocr',
              'do_last_modified_check', 'rule', 'organization', 'keep_false_positives']


class MSGraphFileAskRun(ScannerAskRun):
    """Prompts the user for confirmation before running a Microsoft Graph file
    scanner job."""
    model = MSGraphFileScanner
    run_url_name = "msgraphfilescanner_run"


class MSGraphFileRun(ScannerRun):
    """Runs a Microsoft Graph file scanner job, displaying the new scan tag on
    success and error details on failure."""
    model = MSGraphFileScanner


class MSGraphFileCleanupStaleAccounts(ScannerCleanupStaleAccounts):
    """Prompts the user for confirmation before deleting document reports
    belonging to accounts, which have gone stale for this scanner."""
    model = MSGraphFileScanner
    type = "msgraph-file"


class MSGraphCalendarList(ScannerList):
    """"""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'


class MSGraphCalendarCreate(View):
    """"""
    type = 'msgraph-calendar'

    def dispatch(self, request, *args, **kwargs):
        user = UserWrapper(request.user)
        if GraphGrant.objects.filter(user.make_org_Q()).exists():
            handler = _MSGraphCalendarCreate.as_view()
        else:
            handler = MSGraphGrantRequestView.as_view(
                    redirect_token="msgraphcalendarscanner_add")
        return handler(request, *args, **kwargs)


class _MSGraphCalendarCreate(ScannerCreate):
    """Creates a new Microsoft Graph calendar scanner job."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'
    fields = ['name', 'schedule', 'grant', 'only_notify_superadmin',
              'do_ocr', 'org_unit', 'exclusion_rule',
              'do_last_modified_check', 'rule', 'organization', 'keep_false_positives']

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/msgraph-calendarscanners/%s/created' % self.object.pk


class MSGraphCalendarUpdate(ScannerUpdate):
    """Displays the parameters of an existing Microsoft Graph mail scanner job
    for modification."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendarscanners'
    fields = ['name', 'schedule', 'grant', 'only_notify_superadmin',
              'do_ocr', 'org_unit', 'exclusion_rule',
              'do_last_modified_check', 'rule', 'organization', 'keep_false_positives']

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        return '/msgraph-calendarscanners/%s/saved/' % self.object.pk


class MSGraphCalendarRemove(ScannerRemove):
    """Remove a scanner view."""
    model = MSGraphCalendarScanner
    success_url = '/msgraph-calendarscanners/'


class MSGraphCalendarDelete(ScannerDelete):
    """Deletes a Microsoft Graph calendar scanner job."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'
    fields = []
    success_url = '/msgraph-calendarscanners/'


class MSGraphCalendarCopy(ScannerCopy):
    """Creates a copy of an existing Microsoft Graph calendar scanner job."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'
    fields = ['name', 'schedule', 'grant', 'only_notify_superadmin',
              'do_ocr', 'org_unit', 'exclusion_rule',
              'do_last_modified_check', 'rule', 'organization', 'keep_false_positives']


class MSGraphCalendarAskRun(ScannerAskRun):
    """Prompts the user for confirmation before running a Microsoft Graph
    calendar scanner job."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'
    run_url_name = "msgraphcalendarscanner_run"


class MSGraphCalendarRun(ScannerRun):
    """Runs a Microsoft Graph calendar scanner job, displaying the new scan tag on
    success and error details on failure."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'


class MSGraphTeamsFileList(ScannerList):
    """Displays the list of all Microsoft Graph file scanner jobs."""
    model = MSGraphTeamsFileScanner
    type = 'msgraph-teams-file'


class MSGraphTeamsFileCreate(View):
    """Creates a new Microsoft Graph Teams file scanner job. (See MSGraphMailCreate
    for more details.)"""

    def dispatch(self, request, *args, **kwargs):
        user = UserWrapper(request.user)
        if GraphGrant.objects.filter(user.make_org_Q()).exists():
            handler = _MSGraphTeamsFileCreate.as_view()
        else:
            handler = MSGraphGrantRequestView.as_view(
                    redirect_token="msgraphteamsfilescanner_add")
        return handler(request, *args, **kwargs)


class _MSGraphTeamsFileCreate(ScannerCreate):
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
        return '/msgraph-teams-filescanners/%s/created/' % self.object.pk


class MSGraphTeamsFileUpdate(ScannerUpdate):
    """Displays the parameters of an existing Microsoft Graph file scanner job
    for modification."""
    model = MSGraphTeamsFileScanner
    type = 'msgraph-teams-filescanners'
    fields = ['name', 'schedule', 'grant',
              'do_ocr', 'only_notify_superadmin', 'exclusion_rule',
              'do_last_modified_check', 'rule', 'organization', 'keep_false_positives']

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        return '/msgraph-teams-filescanners/%s/saved/' % self.object.pk


class MSGraphTeamsFileRemove(ScannerRemove):
    """Remove a scanner view."""
    model = MSGraphTeamsFileScanner
    success_url = '/msgraph-teams-filescanners/'


class MSGraphTeamsFileDelete(ScannerDelete):
    """Deletes a Microsoft Graph file scanner job."""
    model = MSGraphTeamsFileScanner
    fields = []
    success_url = '/msgraph-teams-filescanners/'


class MSGraphTeamsFileCopy(ScannerCopy):
    """Creates a copy of an existing Microsoft Graph mail scanner job."""
    model = MSGraphTeamsFileScanner
    type = 'msgraph-teams-file'
    fields = ['name', 'schedule', 'grant',
              'exclusion_rule', 'only_notify_superadmin',
              'do_ocr', 'do_last_modified_check', 'rule',
              'organization', 'keep_false_positives']


class MSGraphTeamsFileAskRun(ScannerAskRun):
    """Prompts the user for confirmation before running a Microsoft Graph file
    scanner job."""
    model = MSGraphTeamsFileScanner
    run_url_name = "msgraphteamsfilescanner_run"


class MSGraphTeamsFileRun(ScannerRun):
    """Runs a Microsoft Graph file scanner job, displaying the new scan tag on
    success and error details on failure."""
    model = MSGraphTeamsFileScanner


class MSGraphCalendarCleanupStaleAccounts(ScannerCleanupStaleAccounts):
    """Prompts the user for confirmation before deleting document reports
    belonging to accounts, which have gone stale for this scanner."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'
