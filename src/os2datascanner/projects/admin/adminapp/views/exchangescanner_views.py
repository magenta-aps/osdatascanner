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

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.views import View
from rest_framework.generics import ListAPIView
import re

from os2datascanner.projects.admin.utilities import UserWrapper
from .scanner_views import (
    ScannerDelete,
    ScannerRemove,
    ScannerAskRun,
    ScannerRun,
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


class ExchangeScannerCreate(ExchangeScannerBase, ScannerCreate):
    """Create a exchange scanner view."""

    model = ExchangeScanner
    fields = ['name', 'mail_domain', 'schedule', 'exclusion_rule', 'do_ocr',
              'do_last_modified_check', 'rule', 'userlist', 'only_notify_superadmin',
              'service_endpoint', 'organization', 'org_unit', 'keep_false_positives']
    if settings.MSGRAPH_EWS_AUTH:
        fields.append("grant")
    type = 'exchange'

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

        return form


class ExchangeScannerCopy(ExchangeScannerBase, ScannerCopy):
    """Create a new copy of an existing ExchangeScanner"""

    model = ExchangeScanner
    fields = ['name', 'mail_domain', 'schedule', 'exclusion_rule', 'do_ocr',
              'do_last_modified_check', 'rule', 'userlist', 'only_notify_superadmin',
              'service_endpoint', 'organization', 'org_unit', 'keep_false_positives']
    if settings.MSGRAPH_EWS_AUTH:
        fields.append("grant")
    type = 'exchange'

    def get_form(self, form_class=None):
        """Adds special field password."""
        # This doesn't copy over it's values, as credentials shouldn't
        # be copyable
        if form_class is None:
            form_class = self.get_form_class()

        form = super().get_form(form_class)

        form = initialize_form(form)
        if self.request.method == 'POST':
            form.is_valid()
            form = validate_userlist_or_org_units(form)
            form = validate_domain(form)

        return form

    def get_initial(self):
        initial = super(ExchangeScannerCopy, self).get_initial()
        initial["userlist"] = self.get_scanner_object().userlist
        return initial


class ExchangeScannerUpdate(ExchangeScannerBase, ScannerUpdate):
    """Update a scanner view."""

    model = ExchangeScanner
    fields = ['name', 'mail_domain', 'schedule', 'exclusion_rule', 'do_ocr',
              'do_last_modified_check', 'rule', 'userlist', 'only_notify_superadmin',
              'service_endpoint', 'organization', 'org_unit', 'keep_false_positives']
    if settings.MSGRAPH_EWS_AUTH:
        fields.append("grant")
    type = 'exchange'

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

        exchangescanner = self.get_object()
        authentication = exchangescanner.authentication

        if authentication.username:
            form.fields['username'].initial = authentication.username
        if authentication.iv:
            # if there is a set password already, use a dummy to enable the placeholder
            form.fields['password'].initial = "dummy"
        if self.request.method == 'POST':
            form.is_valid()
            form = validate_userlist_or_org_units(form)
            form = validate_domain(form)

        return form


class ExchangeScannerRemove(ScannerRemove):
    """Remove a scanner view."""
    model = ExchangeScanner
    success_url = '/exchangescanners/'


class ExchangeScannerDelete(ScannerDelete):
    """Delete a scanner view."""
    model = ExchangeScanner
    fields = []
    success_url = '/exchangescanners/'


class ExchangeScannerAskRun(ScannerAskRun):
    """Prompt for starting exchange scan, validate first."""

    model = ExchangeScanner
    run_url_name = 'exchangescanner_run'


class ExchangeScannerRun(ScannerRun):
    """View that handles starting of a exchange scanner run."""

    model = ExchangeScanner


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
    form.fields['username'] = forms.CharField(
        max_length=1024,
        required=False,
        label=_('Username')
    )
    form.fields['password'] = forms.CharField(
        max_length=50,
        required=False,
        label=_('Password')
    )

    return form


class ExchangeScannerCleanup(ScannerCleanupStaleAccounts):
    """Prompts the user for confirmation before deleting document reports
    belonging to accounts, which have gone stale for this scanner."""
    model = ExchangeScanner
    type = "exchange"
