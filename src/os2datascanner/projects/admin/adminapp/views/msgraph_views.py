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
from django.conf import settings
from django.views import View
from django.views.generic.base import TemplateView
from urllib.parse import urlencode

from ..models.scannerjobs.msgraph_models import MSGraphMailScanner
from ..models.scannerjobs.msgraph_models import MSGraphFileScanner
from ..models.scannerjobs.msgraph_models import MSGraphCalendarScanner
from ..models.scannerjobs.msgraph_models import MSGraphTeamsScanner
from .views import LoginRequiredMixin
from .scanner_views import (ScannerRun, ScannerList,
                            ScannerAskRun, ScannerCreate, ScannerDelete, ScannerUpdate, ScannerCopy)


def make_consent_url(label):
    if settings.MSGRAPH_APP_ID:
        redirect_uri = settings.SITE_URL + "msgraph-{0}/add/".format(label)
        return ("https://login.microsoftonline.com/common/adminconsent?"
                + urlencode({
                    "client_id": settings.MSGRAPH_APP_ID,
                    "scope": "https://graph.microsoft.com/.default",
                    "response_type": "code",
                    "redirect_uri": redirect_uri
                }))
    else:
        return None


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
        if 'tenant' in request.GET:
            handler = _MSGraphMailCreate.as_view()
        else:
            handler = _MSGraphMailPermissionRequest.as_view()
        return handler(request, *args, **kwargs)


class _MSGraphMailPermissionRequest(LoginRequiredMixin, TemplateView):
    """Sends the user to the Microsoft Online login system in order to permit
    OS2datascanner to access organisational mail accounts through the Graph
    API.

    Note that only Microsoft accounts with organisational administrator
    privileges can grant applications the right to access Graph resources
    without having to go through a specific user account."""
    template_name = "os2datascanner/scanner_oauth_start.html"

    def get_context_data(self, **kwargs):
        return dict(**super().get_context_data(**kwargs), **{
            "service_name": "Microsoft Online",
            "auth_endpoint": make_consent_url("mailscanners"),
            "error": self.request.GET.get("error"),
            "error_description": self.request.GET.get("error_description")
        })


class _MSGraphMailCreate(ScannerCreate):
    """Creates a new Microsoft Graph mail scanner job."""
    model = MSGraphMailScanner
    type = 'msgraph-mail'
    fields = ['name', 'schedule', 'tenant_id', 'do_ocr', 'org_unit',
              'do_last_modified_check', 'rules', 'organization', ]

    def get_context_data(self, **kwargs):
        return dict(**super().get_context_data(**kwargs), **{
            "tenant_id": self.request.GET['tenant']
        })

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/msgraph-mailscanners/%s/created/' % self.object.pk


class MSGraphMailUpdate(ScannerUpdate):
    """Displays the parameters of an existing Microsoft Graph mail scanner job
    for modification."""
    model = MSGraphMailScanner
    type = 'msgraph-mailscanners'
    fields = ['name', 'schedule', 'tenant_id', 'do_ocr', 'org_unit',
              'do_last_modified_check', 'rules', 'organization', ]

    def get_success_url(self):
        return '/msgraph-mailscanners/%s/saved/' % self.object.pk


class MSGraphMailDelete(ScannerDelete):
    """Deletes a Microsoft Graph mail scanner job."""
    model = MSGraphMailScanner
    fields = []
    success_url = '/msgraph-mailscanners/'


class MSGraphMailCopy(ScannerCopy):
    """Creates a copy of an existing Microsoft Graph mail scanner job."""
    model = MSGraphMailScanner
    type = 'msgraph-mail'
    fields = ['name', 'schedule', 'tenant_id', 'do_ocr', 'org_unit',
              'do_last_modified_check', 'rules', 'organization', ]


class MSGraphMailAskRun(ScannerAskRun):
    """Prompts the user for confirmation before running a Microsoft Graph mail
    scanner job."""
    model = MSGraphMailScanner


class MSGraphMailRun(ScannerRun):
    """Runs a Microsoft Graph mail scanner job, displaying the new scan tag on
    success and error details on failure."""
    model = MSGraphMailScanner


class MSGraphFileList(ScannerList):
    """Displays the list of all Microsoft Graph file scanner jobs."""
    model = MSGraphFileScanner
    type = 'msgraph-file'


class MSGraphFileCreate(View):
    """Creates a new Microsoft Graph file scanner job. (See MSGraphMailCreate
    for more details.)"""

    def dispatch(self, request, *args, **kwargs):
        if 'tenant' in request.GET:
            handler = _MSGraphFileCreate.as_view()
        else:
            handler = _MSGraphFilePermissionRequest.as_view()
        return handler(request, *args, **kwargs)


class _MSGraphFilePermissionRequest(TemplateView, LoginRequiredMixin):
    """Sends the user to the Microsoft Online login system in order to permit
    OS2datascanner to access organisational OneDrive and SharePoint drives
    through the Graph API. (See _MSGraphMailPermissionRequest for more
    details.)"""
    template_name = "os2datascanner/scanner_oauth_start.html"

    def get_context_data(self, **kwargs):
        return dict(**super().get_context_data(**kwargs), **{
            "service_name": "Microsoft Online",
            "auth_endpoint": make_consent_url("filescanners"),
            "error": self.request.GET.get("error"),
            "error_description": self.request.GET.get("error_description")
        })


class _MSGraphFileCreate(ScannerCreate):
    """Creates a new Microsoft Graph file scanner job."""
    model = MSGraphFileScanner
    type = 'msgraph-file'
    fields = ['name', 'schedule', 'tenant_id', 'org_unit',
              'scan_site_drives', 'scan_user_drives', 'do_ocr',
              'do_last_modified_check', 'rules', 'organization', ]

    def get_context_data(self, **kwargs):
        return dict(**super().get_context_data(**kwargs), **{
            "tenant_id": self.request.GET['tenant']
        })

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/msgraph-filescanners/%s/created/' % self.object.pk


class MSGraphFileUpdate(ScannerUpdate):
    """Displays the parameters of an existing Microsoft Graph file scanner job
    for modification."""
    model = MSGraphFileScanner
    type = 'msgraph-filescanners'
    fields = ['name', 'schedule', 'tenant_id', 'org_unit',
              'scan_site_drives', 'scan_user_drives', 'do_ocr',
              'do_last_modified_check', 'rules', 'organization', ]

    def get_success_url(self):
        return '/msgraph-filescanners/%s/saved/' % self.object.pk


class MSGraphFileDelete(ScannerDelete):
    """Deletes a Microsoft Graph file scanner job."""
    model = MSGraphFileScanner
    fields = []
    success_url = '/msgraph-filescanners/'


class MSGraphFileCopy(ScannerCopy):
    """Creates a copy of an existing Microsoft Graph mail scanner job."""
    model = MSGraphFileScanner
    type = 'msgraph-file'
    fields = ['name', 'schedule', 'tenant_id', 'org_unit',
              'scan_site_drives', 'scan_user_drives', 'do_ocr',
              'do_last_modified_check', 'rules', 'organization', ]


class MSGraphFileAskRun(ScannerAskRun):
    """Prompts the user for confirmation before running a Microsoft Graph file
    scanner job."""
    model = MSGraphFileScanner


class MSGraphFileRun(ScannerRun):
    """Runs a Microsoft Graph file scanner job, displaying the new scan tag on
    success and error details on failure."""
    model = MSGraphFileScanner


class MSGraphCalendarList(ScannerList):
    """"""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'


class MSGraphCalendarCreate(View):
    """"""
    type = 'msgraph-calendar'

    def dispatch(self, request, *args, **kwargs):
        if 'tenant' in request.GET:
            handler = _MSGraphCalendarCreate.as_view()
        else:
            handler = _MSGraphCalendarPermissionRequest.as_view()
        return handler(request, *args, **kwargs)


class _MSGraphCalendarPermissionRequest(LoginRequiredMixin, TemplateView):
    """"""
    template_name = "os2datascanner/scanner_oauth_start.html"

    def get_context_data(self, **kwargs):
        return dict(**super().get_context_data(**kwargs), **{
            "service_name": "Microsoft Online",
            "auth_endpoint": make_consent_url("calendarscanners"),
            "error": self.request.GET.get("error"),
            "error_description": self.request.GET.get("error_description")
        })


class _MSGraphCalendarCreate(ScannerCreate):
    """Creates a new Microsoft Graph calendar scanner job."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'
    fields = ['name', 'schedule', 'tenant_id', 'do_ocr', 'org_unit',
              'do_last_modified_check', 'rules', 'organization', ]

    def get_context_data(self, **kwargs):
        return dict(**super().get_context_data(**kwargs), **{
            "tenant_id": self.request.GET['tenant']
        })

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/msgraph-calendarscanners/%s/created' % self.object.pk


class MSGraphCalendarUpdate(ScannerUpdate):
    """Displays the parameters of an existing Microsoft Graph mail scanner job
    for modification."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendarscanners'
    fields = ['name', 'schedule', 'tenant_id', 'do_ocr', 'org_unit',
              'do_last_modified_check', 'rules', 'organization', ]

    def get_success_url(self):
        return '/msgraph-calendarscanners/%s/saved/' % self.object.pk


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
    fields = ['name', 'schedule', 'tenant_id', 'do_ocr', 'org_unit',
              'do_last_modified_check', 'rules', 'organization', ]


class MSGraphCalendarAskRun(ScannerAskRun):
    """Prompts the user for confirmation before running a Microsoft Graph
    calendar scanner job."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'


class MSGraphCalendarRun(ScannerRun):
    """Runs a Microsoft Graph calendar scanner job, displaying the new scan tag on
    success and error details on failure."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'


class MSGraphTeamsScannerList(ScannerList):
    """Displays a list of MS Teams scanners."""
    model = MSGraphTeamsScanner
    type = "msgraph-teams"


class MSGraphTeamsScannerCreate(View):
    """Creates a new Microsoft Graph Teams scanner job.

    This view delegates to two other views: one sends the user to Microsoft
    Online to grant permission for the scan, and the other renders the normal
    scanner job creation form when the response comes back."""

    model = MSGraphTeamsScanner
    type = "msgraph-teams"

    def dispatch(self, request, *args, **kwargs):
        if "tenant" in request.GET:
            handler = _MSGraphTeamsScannerCreate.as_view()
        else:
            handler = _MSGraphTeamsScannerPermissionRequest.as_view()
        return handler(request, *args, **kwargs)


class _MSGraphTeamsScannerCreate(ScannerCreate):
    """Creates a new Microsoft Graph Teams scanner job."""

    model = MSGraphTeamsScanner
    type = "msgraph-teams"
    fields = ['name', 'schedule', 'tenant_id', 'do_ocr', 'org_unit',
              'do_last_modified_check', 'rules', 'organization', ]

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs), **{"tenant_id": self.request.GET["tenant"]}
        )

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/msgraph-teamsscanners/%s/created/' % self.object.pk


class _MSGraphTeamsScannerPermissionRequest(LoginRequiredMixin, TemplateView):
    """Sends the user to thet Microsoft Online login system in order to permit
    OS2datascanner to access organisational Teams accounts through the Graph API.

    Note that only Microsoft accounts with organisational administrator
    privileges can grant applications the right to access Graph resources
    without having to go through a specific user account."""

    template_name = "os2datascanner/scanner_oauth_start.html"

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            **{
                "service_name": "Microsoft Online",
                "auth_endpoint": make_consent_url("teamsscanners"),
                "error": self.request.GET.get("error"),
                "error_description": self.request.GET.get("error_description"),
            }
        )


class MSGraphTeamsScannerUpdate(ScannerUpdate):
    """Displays the parameters of an existing Microsoft Teams scanner job via. Graph API."""
    model = MSGraphTeamsScanner
    type = 'msgraph-teamsscanners'
    fields = ['name', 'schedule', 'tenant_id', 'do_ocr', 'org_unit',
              'do_last_modified_check', 'rules', 'organization', ]

    def get_success_url(self):
        if 'save_and_validate' in self.request.POST:
            return 'validate/'
        else:
            return '/msgraph-teamsscanners/%s/saved/' % self.object.pk


class MSGraphTeamsScannerDelete(ScannerDelete):
    """Deletes a Microsoft Teams scanner job via. Graph API."""
    model = MSGraphTeamsScanner
    fields = []
    success_url = '/msgraph-teamsscanners/'


class MSGraphTeamsScannerCopy(ScannerCopy):
    """Creates a copy of an existing Microsoft Teams scanner job through
    Graph API."""
    model = MSGraphTeamsScanner
    type = 'msgraph-teams'
    fields = ['name', 'schedule', 'tenant_id', 'do_ocr', 'org_unit',
              'do_last_modified_check', 'rules', 'organization', ]


class MSGraphTeamsScannerAskRun(ScannerAskRun):
    """Prompts the user for confirmation before running a
    Microsoft Teams scanner job through the Graph API."""

    model = MSGraphTeamsScanner


class MSGraphTeamsScannerRun(ScannerRun):
    """Runs a Microsoft Teams scanner job, displaying the new scan tag on
    success and error details on failure."""

    model = MSGraphTeamsScanner
