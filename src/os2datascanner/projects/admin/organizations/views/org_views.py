from typing import Any, Dict
from django.contrib.auth.models import User
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from os2datascanner.projects.admin.adminapp.views.views import (
    RestrictedDeleteView,
    RestrictedDetailView,
    RestrictedCreateView,
    RestrictedListView,
    RestrictedUpdateView)
from django.core.exceptions import PermissionDenied

from os2datascanner.projects.admin.core.models import Client, Feature, Administrator
from ..models.organization import Organization

from django import forms

import structlog

logger = structlog.get_logger("admin_organizations")


class OrganizationListView(RestrictedListView):
    model = Organization
    paginate_by = 10  # TODO: reasonable number? Possibly irrelevant?
    context_object_name = 'client_list'

    # filter list based on user
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset(org_path="uuid")
        if user.has_perm('core.view_client'):
            queryset = Client.objects.all()
        elif hasattr(user, 'administrator_for'):
            client_id = user.administrator_for.client_id
            queryset = Client.objects.filter(pk=client_id)
        return queryset.prefetch_related('organizations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['FEATURES'] = Feature.__members__
        return context

    def get_template_names(self):
        is_htmx = self.request.headers.get('HX-Request') == "true"
        return 'organizations/org_table.html' if is_htmx else "organizations/org_list.html"


class AddOrganizationView(PermissionRequiredMixin, RestrictedCreateView):
    model = Organization
    permission_required = 'organizations.add_organization'
    template_name = 'organizations/org_add.html'
    success_url = reverse_lazy('organization-list')
    fields = ['name', 'contact_email', 'contact_phone',
              'email_header_banner', 'email_notification_schedule']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.required_css_class = 'required-form'
        # form.error_css_class = # TODO: add if relevant?
        return form

    def form_valid(self, form):
        client_id = self.kwargs['client_id']
        form.instance.client = Client.objects.get(pk=client_id)
        if Organization.objects.filter(
                slug=Organization.convert_name_to_slug(form.instance.name)).exists():
            form.add_error('name', _('That name is already taken.'))
            return self.form_invalid(form)
        else:
            return super().form_valid(form)

    def get_queryset(self):
        return super().get_queryset(org_path="uuid")

    def dispatch(self, request, *args, **kwargs):
        client_id = self.kwargs['client_id']
        if request.user.has_perm('core.view_client') or \
                Administrator.objects.filter(user=request.user, client=client_id).exists():
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


class UpdateOrganizationView(PermissionRequiredMixin, RestrictedUpdateView):
    model = Organization
    permission_required = 'organizations.change_organization'
    template_name = 'organizations/org_update.html'
    success_url = reverse_lazy('organization-list')
    fields = ['name', 'contact_email', 'contact_phone',
              'leadertab_access', 'dpotab_access', 'show_support_button',
              'support_contact_method', 'support_name', 'support_value',
              'dpo_contact_method', 'dpo_name', 'dpo_value',
              'outlook_categorize_email_permission', 'outlook_delete_email_permission',
              'onedrive_delete_permission', 'email_header_banner', 'email_notification_schedule',
              'synchronization_time']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        outlook_field = form.fields['outlook_categorize_email_permission']
        outlook_field.widget = forms.RadioSelect()
        outlook_field.choices = Organization._meta.get_field(
            'outlook_categorize_email_permission').choices

        form.required_css_class = 'required-form'
        # TODO: Overhaul styling of form: Dropdowns & Helptext
        # form.error_css_class = # TODO: add if relevant?
        return form

    def form_valid(self, form):
        slug = self.kwargs['slug']
        if Organization.objects.filter(
            slug=Organization.convert_name_to_slug(form.instance.name)).exclude(
                slug=slug).exists():
            form.add_error('name', _('That name is already taken.'))
            return self.form_invalid(form)
        else:
            return super().form_valid(form)

    def get_queryset(self):
        return super().get_queryset(org_path="uuid")


class DeleteOrganizationView(PermissionRequiredMixin, RestrictedDeleteView):
    """Delete an organization view."""
    model = Organization
    permission_required = 'organizations.delete_organization'
    success_url = '/organizations/'

    def post(self, request, *args, **kwargs):
        username = request.user.username
        if not User.objects.get(username=username).has_perm("organizations.delete_organization"):
            # Imposter! Keep out!.
            raise PermissionDenied

        # User is OK. Proceed.
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset(org_path="uuid")


class OrganizationDeletionBlocked(RestrictedDetailView):
    """Prompt when user is trying to delete organization with running scannerjob"""
    model = Organization
    fields = []
    template_name = "organizations/org_delete_blocked.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs)
