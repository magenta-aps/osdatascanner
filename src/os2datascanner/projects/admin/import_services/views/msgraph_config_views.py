# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""
Views for adding and updating configurations for Microsoft Graph
for importing organizations.
"""
from typing import override

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from os2datascanner.projects.grants.models.graphgrant import GraphGrant
from os2datascanner.projects.admin.adminapp.views.views import OrgRestrictedMixin
from os2datascanner.projects.admin.organizations.views import MSGraphGrantRequestView
from os2datascanner.projects.admin.organizations.utils import get_user_org_or_404
from os2datascanner.projects.admin.organizations.views.mixins import UserOrgFromURLMixin
from ..models.msgraph_configuration import MSGraphConfiguration


class MSGraphEditForm(forms.ModelForm):
    required_css_class = 'required-form'

    def __init__(self, *args, grants, **kwargs):
        super(MSGraphEditForm, self).__init__(*args, **kwargs)
        self.fields['organization'].disabled = True
        self.fields['grant'] = forms.ModelChoiceField(
                queryset=grants, empty_label=None)

    class Meta:
        model = MSGraphConfiguration
        fields = [
            'organization',
            'grant',
            'hide_units_on_import',
            'exclude_guests',
        ]


class MSGraphAddView(LoginRequiredMixin, View):
    """
    View for adding a configuration for Microsoft Graph to import an organization.
    Dispatches to the configuration form if the organization has a GraphGrant,
    and to the Microsoft Online consent flow otherwise.
    """

    @override
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        org = get_user_org_or_404(request.user, kwargs["org_id"])
        if GraphGrant.objects.filter(organization=org).exists():
            handler = _MSGraphAddView.as_view()
        else:
            handler = MSGraphGrantRequestView.as_view(
                    redirect_token="add-msgraph",
                    redirect_kwargs=dict(org_id=str(org.pk)))
        return handler(request, *args, **kwargs)


class _MSGraphAddView(LoginRequiredMixin, UserOrgFromURLMixin, CreateView):
    """
    View for adding a configuration for importing organizations through
    Microsoft Graph by using a Tenant ID.
    """
    template_name = 'import_services/msgraph_edit.html'
    success_url = reverse_lazy('organization-list')
    form_class = MSGraphEditForm

    def get_grants(self):
        return GraphGrant.objects.filter(organization=self.kwargs["organization"])

    @override
    def get_initial(self):
        return super().get_initial() | {
            "organization": self.kwargs["organization"],
            "grant": self.get_grants().first(),
        }

    @override
    def get_form_kwargs(self):
        return (super().get_form_kwargs() or {}) | {"grants": self.get_grants()}

    @override
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = True
        context["grant"] = self.get_grants().first()
        context["organization"] = self.kwargs["organization"]
        return context

    @override
    def form_valid(self, form):
        form.instance.created = now()
        form.instance.last_modified = now()
        form.instance.grant = self.get_grants().first()
        form.instance.organization = self.kwargs['organization']
        result = super().form_valid(form)
        return result


class MSGraphUpdateView(OrgRestrictedMixin, UpdateView):
    """
    Page where the user can edit the configuration for Microsoft Graph
    for importing organizations.
    """

    model = MSGraphConfiguration
    template_name = 'import_services/msgraph_edit.html'
    success_url = reverse_lazy('organization-list')
    form_class = MSGraphEditForm

    def setup(self, request, *args, **kwargs):
        return super().setup(request, *args, **kwargs)

    def get_form_kwargs(self):
        return (super().get_form_kwargs() or {}) | {
            "grants": GraphGrant.objects.filter(
                    organization=self.object.organization)
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = False
        context['grant'] = self.object.grant
        context['organization'] = self.object.organization
        return context

    def form_valid(self, form):
        form.instance.last_modified = now()
        form.instance.grant = form.cleaned_data["grant"]
        form.instance.organization = form.cleaned_data['organization']
        return super().form_valid(form)


class MSGraphImportView(OrgRestrictedMixin, SingleObjectMixin, View):
    """
    View for creating background import jobs with MS Graph.
    """

    model = MSGraphConfiguration

    def post(self, request, *args, **kwargs):
        """
        Initiates importation of an organization through MS Graph.
        """
        self.get_object().start_import()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
