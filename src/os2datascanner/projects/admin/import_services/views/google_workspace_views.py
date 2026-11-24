# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from typing import override

import structlog
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views import View
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone

from os2datascanner.projects.grants.models import GoogleApiGrant
from ...adminapp.views.views import OrgRestrictedMixin
from ...organizations.views.mixins import UserOrgFromURLMixin
from ..models.google_workspace_configuration import GoogleWorkspaceConfig

logger = structlog.get_logger("import_services")


class GoogleWorkspaceEditForm(forms.ModelForm):
    required_css_class = 'required-form'

    def __init__(self, *args, grants, **kwargs):
        super(GoogleWorkspaceEditForm, self).__init__(*args, **kwargs)
        # organization field is pre-filled and readonly
        if 'organization' in self.fields:
            self.fields['organization'].disabled = True
        self.fields['grant'].queryset = grants

    class Meta:
        model = GoogleWorkspaceConfig
        # show organization, grant and email.
        fields = [
            'organization',
            'grant',
            'delegated_admin_email',
        ]


class GoogleWorkspaceAddView(LoginRequiredMixin, UserOrgFromURLMixin, CreateView):

    model = GoogleWorkspaceConfig
    form_class = GoogleWorkspaceEditForm
    template_name = "import_services/googleworkspace_edit.html"
    success_url = reverse_lazy('organization-list')

    @override
    def get_initial(self):
        return super().get_initial() | {"organization": self.kwargs["organization"]}

    @override
    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            "grants": GoogleApiGrant.objects.filter(organization=self.kwargs["organization"])
        }

    @override
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = True
        context['organization'] = self.kwargs.get('organization')
        return context

    @override
    def form_valid(self, form):
        form.instance.organization = self.kwargs["organization"]
        if not form.instance.last_modified:
            form.instance.last_modified = timezone.now()
        return super().form_valid(form)


class GoogleWorkspaceUpdateView(OrgRestrictedMixin, UpdateView):
    model = GoogleWorkspaceConfig
    form_class = GoogleWorkspaceEditForm
    template_name = "import_services/googleworkspace_edit.html"
    success_url = reverse_lazy("organization-list")

    @override
    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            "grants": GoogleApiGrant.objects.filter(organization=self.object.organization)
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = False
        context['organization'] = self.object.organization
        return context


class GoogleWorkspaceImportView(OrgRestrictedMixin, SingleObjectMixin, View):
    model = GoogleWorkspaceConfig

    def post(self, request, *args, **kwargs):
        config = self.get_object()

        # Ensure required credentials are configured
        if not config.delegated_admin_email:
            messages.error(request, "Missing delegated admin email or service account email.")
            return redirect(request.META.get('HTTP_REFERER', reverse_lazy('organization-list')))

        try:
            # Create and start the import job
            config.start_import()
            messages.success(request, "Google Workspace import job created")
        except Exception as e:
            logger.exception("Failed to create import job", config=config.pk)
            messages.error(request, f"Failed to create import job: {e}")

        return redirect(request.META.get('HTTP_REFERER', reverse_lazy('organization-list')))
