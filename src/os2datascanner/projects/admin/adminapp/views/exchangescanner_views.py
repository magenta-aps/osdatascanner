# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.views import View
from rest_framework.generics import ListAPIView
import re

from os2datascanner.projects.grants.views.ews_views import EWSGrantScannerForm
from os2datascanner.projects.grants.views.msgraph_views import MSGraphGrantScannerForm
from os2datascanner.projects.admin.utilities import UserWrapper
from .utils.grant_mixin import GrantMixin

from .scanner_views import (
    ScannerBase,
    ScannerUpdate,
    ScannerCopy,
    ScannerCreate,
    ScannerList,
    ScannerCleanupStaleAccounts)
from ..serializers import OrganizationalUnitSerializer
from ..models.scannerjobs.exchangescanner import (
        ExchangeScanner, get_users_from_file)
from ...core.models import Feature
from ...organizations.models import OrganizationalUnit


class OrganizationalUnitListing(ListAPIView):
    serializer_class = OrganizationalUnitSerializer

    def get_queryset(self):
        organization_id = self.request.query_params.get('organizationId', None)

        if organization_id:
            # Filter by organization and exclude hidden units
            queryList = OrganizationalUnit.objects.filter(
                organization=organization_id,
                hidden=False
            )
        else:
            queryList = []

        return queryList


class ExchangeScannerList(ScannerList):
    """Displays list of exchange scanners."""

    model = ExchangeScanner
    type = 'exchange'

    def get_queryset(self):
        return super().get_queryset()


exchange_scanner_fields = [
    'mail_domain',
    'userlist',
    'service_endpoint',
    'ews_grant',
    'org_unit',
    'scan_subject',
]


class ExchangeScannerBase(View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = UserWrapper(self.request.user)
        context["org_units"] = (
                OrganizationalUnit.objects.filter(user.make_org_Q()))

        # Needed to upheld feature flags.
        context['FEATURES'] = Feature.__members__
        context['client'] = user.get_client()
        return context


class ExchangeScannerCreate(ExchangeScannerBase, GrantMixin, ScannerCreate):
    """Create an Exchange scanner view."""

    model = ExchangeScanner
    fields = ScannerBase.fields + exchange_scanner_fields

    if settings.MSGRAPH_EWS_AUTH:
        fields.append("graph_grant")
    type = 'exchange'

    def get_grant_form_classes(self):
        if settings.MSGRAPH_EWS_AUTH:
            return {
                "ews_grant": EWSGrantScannerForm,
                "graph_grant": MSGraphGrantScannerForm
            }

        return {"ews_grant": EWSGrantScannerForm}

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/exchangescanners/%s/created/' % self.object.pk

    def get_form(self, form_class=None):
        """Adds special field password."""
        if form_class is None:
            form_class = self.get_form_class()

        form = super().get_form(form_class)

        form = initialize_form(form)
        if self.request.method == 'POST':
            form.is_valid()
            form = validate_userlist_or_org_units(form)
            form = validate_domain(form)
            form = validate_grant_selected(form)

        return form


class ExchangeScannerCopy(ExchangeScannerBase, GrantMixin, ScannerCopy):
    """Create a new copy of an existing ExchangeScanner"""

    model = ExchangeScanner
    fields = ScannerBase.fields + exchange_scanner_fields

    def get_grant_form_classes(self):
        if settings.MSGRAPH_EWS_AUTH:
            return {
                "ews_grant": EWSGrantScannerForm,
                "graph_grant": MSGraphGrantScannerForm
            }

        return {"ews_grant": EWSGrantScannerForm}

    if settings.MSGRAPH_EWS_AUTH:
        fields.append("graph_grant")
    type = 'exchange'

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        form = super().get_form(form_class)

        form = initialize_form(form)
        if self.request.method == 'POST':
            form.is_valid()
            form = validate_userlist_or_org_units(form)
            form = validate_domain(form)
            form = validate_grant_selected(form)

        return form

    def get_initial(self):
        initial = super(ExchangeScannerCopy, self).get_initial()
        initial["userlist"] = self.get_scanner_object().userlist
        return initial


class ExchangeScannerUpdate(ExchangeScannerBase, GrantMixin, ScannerUpdate):
    """Update a scanner view."""

    model = ExchangeScanner
    fields = ScannerBase.fields + exchange_scanner_fields

    if settings.MSGRAPH_EWS_AUTH:
        fields.append("graph_grant")
    type = 'exchange'

    def get_grant_form_classes(self):
        if settings.MSGRAPH_EWS_AUTH:
            return {
                "ews_grant": EWSGrantScannerForm,
                "graph_grant": MSGraphGrantScannerForm
            }

        return {"ews_grant": EWSGrantScannerForm}

    def get_success_url(self):
        """The URL to redirect to after successful updating.

        Will redirect the user to the validate view if the form was submitted
        with the 'save_and_validate' button.
        """
        if 'save_and_validate' in self.request.POST:
            return 'validate/'
        else:
            return '/exchangescanners/%s/saved/' % self.object.pk

    def get_form(self, form_class=None):
        """Adds special field password and decrypts password."""
        if form_class is None:
            form_class = self.get_form_class()

        form = super().get_form(form_class)
        form = initialize_form(form)

        if self.request.method == 'POST':
            form.is_valid()
            form = validate_userlist_or_org_units(form)
            form = validate_domain(form)
            form = validate_grant_selected(form)

        return form


def validate_userlist_or_org_units(form):  # noqa CCR001
    """Validates whether the form has either a userlist or organizational units.
    Also checks that the formatting of the userlist is valid.
    NB : must be called after initialize form. """
    if not form.cleaned_data['userlist'] and not form.cleaned_data['org_unit']:
        form.add_error('org_unit', _("No organizational units has been selected"))
        form.add_error('userlist', _("No userlist has been selected"))
    if userlist := form.cleaned_data.get('userlist'):
        userlist_errors = set()

        users = []
        try:
            users = get_users_from_file(userlist)
        except ValueError:
            userlist_errors.add((
                "userlist",
                _("The uploaded file does not appear to be a text file")))

        for user in users:
            if "@" in user:
                userlist_errors.add((
                    'userlist',
                    _("The userlist should only include the usernames of the "
                      "users, not the domain!")))
            if any(c in user for c in (",", " ")):
                userlist_errors.add((
                    'userlist',
                    _("Usernames in the userlist should be separated by "
                      "newlines, not commas or whitespace!")))
        for error in userlist_errors:
            form.add_error(*error)

    return form


def validate_grant_selected(form):
    ews_grant = form.cleaned_data.get('ews_grant')
    graph_grant = form.cleaned_data.get('graph_grant')

    if not ews_grant and not graph_grant:
        form.add_error(
            None,
            _("You must select either an EWS or a Graph grant!"))

    return form


def validate_domain(form):
    """Validates whether the mail_domain starts with '@'. """

    mail_domain = form.cleaned_data.get('mail_domain', '')
    pattern = r'^@[^@]+'

    match = re.match(pattern, mail_domain)

    if mail_domain and not match:
        form.add_error(
            'mail_domain',
            _("The domain is invalid"))

    return form


def initialize_form(form):
    """Initializes the form fields for username and password
    as they are not part of the exchange scanner model."""

    form.fields['mail_domain'].widget.attrs['placeholder'] = _('e.g. @example.com')

    return form


class ExchangeScannerCleanup(ScannerCleanupStaleAccounts):
    """Prompts the user for confirmation before deleting document reports
    belonging to accounts, which have gone stale for this scanner."""
    model = ExchangeScanner
    type = "exchange"
