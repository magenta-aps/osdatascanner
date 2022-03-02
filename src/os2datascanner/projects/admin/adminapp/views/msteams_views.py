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
from django.views import View
from django.views.generic.base import TemplateView

from ..models.scannerjobs.msteams_model import MSTeamsScanner
from .msgraph_views import make_consent_url
from .views import LoginRequiredMixin
from .scanner_views import (
    ScannerAskRun,
    ScannerCreate,
    ScannerCopy,
    ScannerDelete,
    ScannerList,
    ScannerRun,
    ScannerUpdate,
)


class MSTeamsScannerList(ScannerList):
    """Displays a list of MS Teams scanners."""
    model = MSTeamsScanner
    type = "msgraph-teams"


class MSTeamsScannerCreate(View):
    """Creates a new Microsoft Graph Teams scanner job.

    This view delegates to two other views: one sends the user to Microsoft
    Online to grant permission for the scan, and the other renders the normal
    scanner job creation form when the response comes back."""

    def dispatch(self, request, *args, **kwargs):
        if "tenant" in request.GET:
            handler = _MSTeamsScannerCreate.as_view()
        else:
            handler = _MSTeamsScannerPermissionRequest.as_view()
        return handler(request, *args, **kwargs)


class _MSTeamsScannerCreate(ScannerCreate):
    """Creates a new Microsoft Graph Teams scanner job."""

    model = MSTeamsScanner
    type = "msteams"
    fields = [
        "name",
        "schedule",
        "tenant_id",
        "do_ocr",
        "rules",
        "organization",
    ]

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs), **{"tenant_id": self.request.GET["tenant"]}
        )

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/msgraph-teamsscanners/%s/created/' % self.object.pk


class _MSTeamsScannerPermissionRequest(LoginRequiredMixin, TemplateView):
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


class MSTeamsScannerUpdate(ScannerUpdate):
    """Displays the parameters of an existing Microsoft Teams scanner job via. Graph API."""
    model = MSTeamsScanner
    type = 'msgraph-teamsscanners'
    fields = [
        "name",
        "schedule",
        "tenant_id",
        "do_ocr",
        "rules",
        "organization",
    ]

    def get_success_url(self):
        return '/msgraph-teamsscanners/%s/saved/' % self.object.pk


class MSTeamsScannerDelete(ScannerDelete):
    """Deletes a Microsoft Teams scanner job via. Graph API."""
    model = MSTeamsScanner
    fields = []
    success_url = '/msgraph-teamsscanners/'


class MSTeamsScannerCopy(ScannerCopy):
    """Creates a copy of an existing Microsoft Teams scanner job through
    Graph API."""
    model = MSTeamsScanner
    type = 'msgraph-teams'
    fields = [
        "name",
        "schedule",
        "tenant_id",
        "do_ocr",
        "rules",
        "organization",
    ]


class MSTeamsScannerAskRun(ScannerAskRun):
    """Prompts the user for confirmation before running a
    Microsoft Teams scanner job through the Graph API."""
    model = MSTeamsScanner


class MSTeamsScannerRun(ScannerRun):
    """Runs a Microsoft Teams scanner job, displaying the new scan tag on
    success and error details on failure."""
    model = MSTeamsScanner
