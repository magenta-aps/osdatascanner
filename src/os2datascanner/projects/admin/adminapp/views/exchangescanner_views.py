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
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.http import HttpResponseRedirect
from os2datascanner.projects.admin.core.models import Feature

from .scanner_views import *
from ..aescipher import decrypt
from ..models.scannerjobs.exchangescanner_model import ExchangeScanner
from ...core.models import Feature, Client
from ...organizations.models import OrganizationalUnit

from rest_framework.generics import ListAPIView
from ..serializers import OrganizationalUnitSerializer


class OrganizationalUnitListing(ListAPIView):
    serializer_class = OrganizationalUnitSerializer

    def get_queryset(self):
        organization_id = self.request.query_params.get('organization_id', None)
        if organization_id:
            queryList = OrganizationalUnit.objects.filter(
                    organization=organization_id)
            # Important in future https://stackoverflow.com/questions/22367711/construct-hierarchy-tree-from-flat-list-with-parent-field
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
        org_units = OrganizationalUnit.objects.all()
        client = Client.objects.none()
        user = self.request.user
        if self.request.user.is_superuser:
            # if you are superuser you are allowed to view all org_units
            # across customers. Also if org_unit featureflags are disabled.
            context['org_units'] = org_units
        elif hasattr(user, 'administrator_for'):
            # if I am administrator for a client I can view org_units
            # for that client.
            client = user.administrator_for.client
            org_units = org_units.filter(
                organization__in=client.organizations.all()
            )
            context['org_units'] = org_units
        else:
            context['org_units'] = OrganizationalUnit.objects.none()

        # Needed to upheld feature flags.
        context['FEATURES'] = Feature.__members__
        context['client'] = client
        return context


class ExchangeScannerCreate(ExchangeScannerBase, ScannerCreate):
    """Create a exchange scanner view."""

    model = ExchangeScanner
    fields = ['name', 'url', 'schedule', 'exclusion_rules', 'do_ocr',
              'do_last_modified_check', 'rules', 'userlist',
              'service_endpoint', 'organization', 'org_unit']
    type = 'exchange'

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/exchangescanners/%s/created/' % self.object.pk

    def get_form(self, form_class=None):
        """Adds special field password."""
        if form_class is None:
            form_class = self.get_form_class()

        form = super().get_form(form_class)

        if self.request.method == 'POST':
            form = validate_userlist_or_org_units(form)
        
        return initialize_form(form)


class ExchangeScannerCopy(ExchangeScannerBase, ScannerCopy):
    """Create a new copy of an existing ExchangeScanner"""


    model = ExchangeScanner
    fields = ['name', 'url', 'schedule', 'exclusion_rules', 'do_ocr',
              'do_last_modified_check', 'rules', 'userlist',
              'service_endpoint', 'organization', 'org_unit']
    type = 'exchange'

    def get_form(self, form_class=None):
        """Adds special field password."""
        # This doesn't copy over it's values, as credentials shouldn't
        # be copyable
        if form_class is None:
            form_class = self.get_form_class()

        form = super().get_form(form_class)
        if self.request.method == 'POST':
            form = validate_userlist_or_org_units(form)

        return initialize_form(form)

    def get_initial(self):
        initial = super(ExchangeScannerCopy, self).get_initial()
        initial["userlist"] = self.get_scanner_object().userlist
        return initial


class ExchangeScannerUpdate(ExchangeScannerBase, ScannerUpdate):
    """Update a scanner view."""

    model = ExchangeScanner
    fields = ['name', 'url', 'schedule', 'exclusion_rules', 'do_ocr',
              'do_last_modified_check', 'rules', 'userlist',
              'service_endpoint', 'organization', 'org_unit']
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
        if authentication.ciphertext:
            password = decrypt(bytes(authentication.iv),
                               bytes(authentication.ciphertext))
            form.fields['password'].initial = password

        #checks if either org_unit or userlist is selected 
        if self.request.method == 'POST':
            form = validate_userlist_or_org_units(form)

        return form


class ExchangeScannerDelete(ScannerDelete):
    """Delete a scanner view."""
    model = ExchangeScanner
    fields = []
    success_url = '/exchangescanners/'


class ExchangeScannerAskRun(ScannerAskRun):
    """Prompt for starting exchange scan, validate first."""

    model = ExchangeScanner

    def get_context_data(self, **kwargs):
        """Check that user is allowed to run this scanner."""
        context = super().get_context_data(**kwargs)
        context['ok'] = True
        return context


class ExchangeScannerRun(ScannerRun):
    """View that handles starting of a exchange scanner run."""

    model = ExchangeScanner

def validate_userlist_or_org_units(form):
    form.is_valid()
    if not form.cleaned_data['userlist'] and not form.cleaned_data['org_unit']:
        error = _("Either a user list or an organisational unit is required")
        form.add_error('org_unit', error)
        form.add_error('userlist', error)
    return form

def initialize_form(form):
    """Initializes the form fields for username and password
    as they are not part of the exchange scanner model."""

    form.fields['url'].widget.attrs['placeholder'] = _('e.g. @example.com')
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
