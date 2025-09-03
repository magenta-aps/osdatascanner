"""
Views for adding and updating configurations for Microsoft Graph
for importing organizations.
"""
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView

from os2datascanner.projects.grants.models.graphgrant import GraphGrant
from os2datascanner.projects.admin.organizations.views import MSGraphGrantRequestView
from os2datascanner.projects.admin.organizations.models import Organization
from ..models.msgraph_configuration import MSGraphConfiguration
from os2datascanner.projects.admin.import_services.utils import start_msgraph_import


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
            'hide_units_on_import'
        ]


class MSGraphAddView(View):
    """
    View for adding a configuration for Microsoft Graph to import an organization.
    Works as a dispatcher depending on whether or not the user is logged into
    Microsoft Online.
    """
    model = MSGraphConfiguration
    type = "msgraph-add"

    def dispatch(self, request, *args, **kwargs):
        org = get_object_or_404(Organization, pk=kwargs['org_id'])
        if GraphGrant.objects.filter(organization=org).exists():
            handler = _MSGraphAddView.as_view()
        else:
            handler = MSGraphGrantRequestView.as_view(
                    redirect_token="add-msgraph",
                    redirect_kwargs=dict(org_id=str(kwargs["org_id"])))
        return handler(request, *args, **kwargs)


class _MSGraphAddView(LoginRequiredMixin, CreateView):
    """
    View for adding a configuration for importing organizations through
    Microsoft Graph by using a Tenant ID.
    """
    template_name = 'import_services/msgraph_edit.html'
    success_url = reverse_lazy('organization-list')
    form_class = MSGraphEditForm

    def setup(self, request, *args, **kwargs):
        org = get_object_or_404(Organization, pk=kwargs['org_id'])
        grant = GraphGrant.objects.filter(organization=org).first()
        self.initial = {
            "organization": org,
            "grant": grant,
        }
        kwargs["organization"] = org
        kwargs["grant"] = grant
        return super().setup(request, *args, **kwargs)

    def get_form_kwargs(self):
        org = get_object_or_404(Organization, pk=self.kwargs['org_id'])
        return (super().get_form_kwargs() or {}) | {
            "grants": GraphGrant.objects.filter(organization=org)
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = True
        context["grant"] = self.kwargs["grant"]
        context["organization"] = self.kwargs["organization"]
        return context

    def form_valid(self, form):
        form.instance.created = now()
        form.instance.last_modified = now()
        form.instance.grant = self.kwargs["grant"]
        form.instance.organization = self.kwargs['organization']
        result = super().form_valid(form)
        return result


class MSGraphUpdateView(LoginRequiredMixin, UpdateView):
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


class MSGraphImportView(LoginRequiredMixin, DetailView):
    """
    View for creating background import jobs with MS Graph.
    """

    model = MSGraphConfiguration

    def __init__(self):
        self.object = None

    def get(self, request, *args, **kwargs):
        """
        Initiates importation of an organization through MS Graph.
        """
        start_msgraph_import(self.get_object())

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
