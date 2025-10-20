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

import requests
from django.forms import ModelChoiceField
from django.views import View
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from rest_framework.generics import ListAPIView

from os2datascanner.engine2.model.msgraph.utilities import MSGraphSource
from os2datascanner.projects.grants.models.graphgrant import GraphGrant
from os2datascanner.projects.admin.organizations.views import MSGraphGrantRequestView
from os2datascanner.projects.admin.organizations.views import MSGraphGrantScannerForm
from os2datascanner.projects.admin.utilities import UserWrapper
from .utils.grant_mixin import GrantMixin
from ..models.scannerjobs.msgraph import MSGraphMailScanner
from ..models.scannerjobs.msgraph import MSGraphFileScanner
from ..models.scannerjobs.msgraph import MSGraphCalendarScanner
from ..models.scannerjobs.msgraph import MSGraphTeamsFileScanner
from ..models.scannerjobs.msgraph import MSGraphSharepointScanner
from ..models.MSGraphSharePointSite import MSGraphSharePointSite
from ..serializers import SharePointSiteSerializer
from .scanner_views import (
    ScannerBase,
    ScannerList,
    ScannerCreate,
    ScannerUpdate,
    ScannerCopy,
    ScannerCleanupStaleAccounts)


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
    form.fields['graph_grant'] = ModelChoiceField(grant_qs, empty_label=None)

    return form


msgraph_mail_scanner_fields = [
    'graph_grant',
    'org_units',
    'scan_entire_org',
    'scan_deleted_items_folder',
    'scan_syncissues_folder',
    'scan_attachments',
    'scan_subject',
]


class _MSGraphMailScannerCreate(GrantMixin, ScannerCreate):
    """Creates a new Microsoft Graph mail scanner job."""
    model = MSGraphMailScanner
    type = 'msgraph-mail'
    fields = ScannerBase.fields + msgraph_mail_scanner_fields

    def get_grant_form_classes(self):
        return {"graph_grant": MSGraphGrantScannerForm}

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/msgraphmailscanners/%s/created/' % self.object.pk


class MSGraphMailScannerUpdate(GrantMixin, ScannerUpdate):
    """Displays the parameters of an existing Microsoft Graph mail scanner job
    for modification."""
    model = MSGraphMailScanner
    type = 'msgraph-mailscanners'
    fields = ScannerBase.fields + msgraph_mail_scanner_fields

    def get_grant_form_classes(self):
        return {"graph_grant": MSGraphGrantScannerForm}

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        return '/msgraphmailscanners/%s/saved/' % self.object.pk


class MSGraphMailScannerCopy(GrantMixin, ScannerCopy):
    """Creates a copy of an existing Microsoft Graph mail scanner job."""
    model = MSGraphMailScanner
    type = 'msgraph-mail'
    fields = ScannerBase.fields + msgraph_mail_scanner_fields

    def get_grant_form_classes(self):
        return {"graph_grant": MSGraphGrantScannerForm}


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


msgraph_file_scanner_fields = [
    'graph_grant',
    'org_units',
    'scan_entire_org',
    'scan_site_drives',
    'scan_user_drives',
]


class _MSGraphFileScannerCreate(GrantMixin, ScannerCreate):
    """Creates a new Microsoft Graph file scanner job."""
    model = MSGraphFileScanner
    type = 'msgraph-file'
    fields = ScannerBase.fields + msgraph_file_scanner_fields

    def get_grant_form_classes(self):
        return {"graph_grant": MSGraphGrantScannerForm}

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/msgraphfilescanners/%s/created/' % self.object.pk


class MSGraphFileScannerUpdate(GrantMixin, ScannerUpdate):
    """Displays the parameters of an existing Microsoft Graph file scanner job
    for modification."""
    model = MSGraphFileScanner
    type = 'msgraph-filescanners'
    fields = ScannerBase.fields + msgraph_file_scanner_fields

    def get_grant_form_classes(self):
        return {"graph_grant": MSGraphGrantScannerForm}

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        return '/msgraphfilescanners/%s/saved/' % self.object.pk


class MSGraphFileScannerCopy(GrantMixin, ScannerCopy):
    """Creates a copy of an existing Microsoft Graph mail scanner job."""
    model = MSGraphFileScanner
    type = 'msgraph-file'
    fields = ScannerBase.fields + msgraph_file_scanner_fields

    def get_grant_form_classes(self):
        return {"graph_grant": MSGraphGrantScannerForm}


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


msgraph_calendar_scanner_fields = [
    'graph_grant',
    'org_units',
    'scan_entire_org',
]


class _MSGraphCalendarScannerCreate(GrantMixin, ScannerCreate):
    """Creates a new Microsoft Graph calendar scanner job."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'
    fields = ScannerBase.fields + msgraph_calendar_scanner_fields

    def get_grant_form_classes(self):
        return {"graph_grant": MSGraphGrantScannerForm}

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/msgraphcalendarscanners/%s/created' % self.object.pk


class MSGraphCalendarScannerUpdate(GrantMixin, ScannerUpdate):
    """Displays the parameters of an existing Microsoft Graph mail scanner job
    for modification."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendarscanners'
    fields = ScannerBase.fields + msgraph_calendar_scanner_fields

    def get_grant_form_classes(self):
        return {"graph_grant": MSGraphGrantScannerForm}

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        return '/msgraphcalendarscanners/%s/saved/' % self.object.pk


class MSGraphCalendarScannerCopy(GrantMixin, ScannerCopy):
    """Creates a copy of an existing Microsoft Graph calendar scanner job."""
    model = MSGraphCalendarScanner
    type = 'msgraph-calendar'
    fields = ScannerBase.fields + msgraph_calendar_scanner_fields

    def get_grant_form_classes(self):
        return {"graph_grant": MSGraphGrantScannerForm}


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


msgraph_teams_scanner_fields = [
    'graph_grant',
]


class _MSGraphTeamsFileScannerCreate(GrantMixin, ScannerCreate):
    """Creates a new Microsoft Graph file scanner job."""
    model = MSGraphTeamsFileScanner
    type = 'msgraph-teams-file'
    fields = ScannerBase.fields + msgraph_teams_scanner_fields

    def get_grant_form_classes(self):
        return {"graph_grant": MSGraphGrantScannerForm}

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/msgraphteamsfilescanners/%s/created/' % self.object.pk


class MSGraphTeamsFileScannerUpdate(GrantMixin, ScannerUpdate):
    """Displays the parameters of an existing Microsoft Graph file scanner job
    for modification."""
    model = MSGraphTeamsFileScanner
    type = 'msgraph-teams-filescanners'
    fields = ScannerBase.fields + msgraph_teams_scanner_fields

    def get_grant_form_classes(self):
        return {"graph_grant": MSGraphGrantScannerForm}

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def get_success_url(self):
        return '/msgraphteamsfilescanners/%s/saved/' % self.object.pk


class MSGraphTeamsFileScannerCopy(GrantMixin, ScannerCopy):
    """Creates a copy of an existing Microsoft Graph mail scanner job."""
    model = MSGraphTeamsFileScanner
    type = 'msgraph-teams-file'
    fields = ScannerBase.fields + msgraph_teams_scanner_fields

    def get_grant_form_classes(self):
        return {"graph_grant": MSGraphGrantScannerForm}


class MSGraphSharepointList(ScannerList):
    model = MSGraphSharepointScanner
    type = 'msgraphsharepoint'


msgraph_sharepoint_scanner_fields = [
     "graph_grant",
     "scan_drives",
     "scan_lists",
     "sharepoint_sites",
     "scan_descriptions",
 ]


class MSGraphSharepointScannerCreate(View):
    def dispatch(self, request, *args, **kwargs):
        user = UserWrapper(request.user)
        if GraphGrant.objects.filter(user.make_org_Q()).exists():
            handler = _MSGraphSharepointScannerCreate.as_view()
        else:
            handler = MSGraphGrantRequestView.as_view(
                    redirect_token="msgraphsharepointscanner_add")
        return handler(request, *args, **kwargs)


class _MSGraphSharepointScannerCreate(GrantMixin, ScannerCreate):
    model = MSGraphSharepointScanner
    type = 'msgraphsharepoint'
    fields = ScannerBase.fields + msgraph_sharepoint_scanner_fields

    def get_grant_form_classes(self):
        return {"graph_grant": MSGraphGrantScannerForm}

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def form_valid(self, form):
        data = form.cleaned_data
        if data.get("scan_lists") or data.get("scan_drives"):
            pass
        else:
            form.add_error("scan_lists", _("You must choose to scan drives, lists, or both!"))
            form.add_error("scan_drives", '')
            return self.form_invalid(form)
        return super().form_valid(form)


class MSGraphSharepointCopy(GrantMixin, ScannerCopy):
    """Creates a copy of an existing Microsoft Graph mail scanner job."""
    model = MSGraphSharepointScanner
    type = 'msgraphsharepoint'
    fields = ScannerBase.fields + msgraph_sharepoint_scanner_fields

    def get_grant_form_classes(self):
        return {"graph_grant": MSGraphGrantScannerForm}


class MSGraphSharepointScannerUpdate(GrantMixin, ScannerUpdate):
    model = MSGraphSharepointScanner
    type = 'msgraphsharepoint'
    fields = ScannerBase.fields + msgraph_sharepoint_scanner_fields

    def get_grant_form_classes(self):
        return {"graph_grant": MSGraphGrantScannerForm}

    def get_form(self, form_class=None):
        return patch_form(self, super().get_form(form_class))

    def form_valid(self, form):
        data = form.cleaned_data
        if not (data.get("scan_lists") or data.get("scan_drives")):
            form.add_error("scan_lists", _("You must choose to scan drives, lists, or both!"))
            form.add_error("scan_drives", '')
            return self.form_invalid(form)
        return super().form_valid(form)


class SharePointListing(ListAPIView):
    serializer_class = SharePointSiteSerializer

    def get_queryset(self):
        if grant_id := self.request.query_params.get('grantId', None):
            grant = GraphGrant.objects.filter(uuid=grant_id).first()
            if self.request.query_params.get('sync', False):
                self._sync_sites(grant)

            return MSGraphSharePointSite.objects.filter(graph_grant=grant)

        return None

    @staticmethod
    def _sync_sites(grant):
        with (requests.Session() as session):
            gc = MSGraphSource.GraphCaller(grant.make_token, session)
            # We only want their id and name, but we have to include isPersonalSite to
            # filter on that value
            sites = gc.paginated_get(
                "sites/getAllSites?$select=id,name,isPersonalSite&$filter=isPersonalSite ne true")

            sites_list = []
            for site in sites:
                site["id"] = site["id"].split(",")[1]
                # Sites in sharepoint don't always have a name.
                sites_list.append(
                    MSGraphSharePointSite(
                        uuid=site["id"],
                        name=site.get(
                            "name",
                            _("Unnamed Site")),
                        graph_grant=grant,
                        organization=grant.organization,
                        ))

            with transaction.atomic():
                MSGraphSharePointSite.objects.bulk_create(
                    sites_list,
                    update_conflicts=True,
                    unique_fields=["uuid", "organization"],
                    update_fields=["name", "graph_grant", "organization"],
                )

                # Remove any sites for no longer available within the used grant only
                current_sites = [site.uuid for site in sites_list]
                MSGraphSharePointSite.objects.filter(
                    graph_grant=grant).exclude(
                    uuid__in=current_sites).delete()
