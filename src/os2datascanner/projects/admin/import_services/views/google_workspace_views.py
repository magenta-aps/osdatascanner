from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.utils import timezone

from ...organizations.models import Organization
from ..models.google_workspace_configuration import GoogleWorkspaceConfig
from ...utilities import UserWrapper


class GoogleWorkspaceEditForm(forms.ModelForm):
    required_css_class = 'required-form'

    def __init__(self, *args, **kwargs):
        super(GoogleWorkspaceEditForm, self).__init__(*args, **kwargs)
        # organization field is pre-filled and readonly
        if 'organization' in self.fields:
            self.fields['organization'].disabled = True

    class Meta:
        model = GoogleWorkspaceConfig
        # show organization, grant and email.
        fields = [
            'organization',
            'grant',
            'delegated_admin_email',
        ]


class GoogleWorkspaceAddView(LoginRequiredMixin, CreateView):

    model = GoogleWorkspaceConfig
    form_class = GoogleWorkspaceEditForm
    template_name = "import_services/googleworkspace_edit.html"
    success_url = reverse_lazy('organization-list')

    def setup(self, request, *args, **kwargs):
        # set initial organization based on URL org_id
        org = get_object_or_404(Organization, uuid=kwargs['org_id'])
        self.initial = {"organization": org}
        kwargs["organization"] = org
        return super().setup(request, *args, **kwargs)

    def get_form(self):
        form = super().get_form()

        user = self.request.user
        org_q = UserWrapper(user).make_org_Q("pk")
        orgs = Organization.objects.filter(org_q)

        form.fields["organization"].queryset = orgs
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = True
        context['organization'] = self.kwargs.get('organization')
        return context

    def form_valid(self, form):
        form.instance.organization = get_object_or_404(
            Organization, uuid=self.kwargs['org_id']
        )
        if not form.instance.last_modified:
            form.instance.last_modified = timezone.now()
        return super().form_valid(form)


class GoogleWorkspaceUpdateView(LoginRequiredMixin, UpdateView):
    model = GoogleWorkspaceConfig
    form_class = GoogleWorkspaceEditForm
    template_name = "import_services/googleworkspace_edit.html"
    success_url = reverse_lazy("organization-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = False
        context['organization'] = self.object.organization
        return context

    def form_valid(self, form):
        return super().form_valid(form)


@method_decorator(csrf_exempt, name="dispatch")
class GoogleWorkspaceImportView(View):
    def post(self, request, pk):
        config = get_object_or_404(GoogleWorkspaceConfig, pk=pk)

        # Ensure required credentials are configured
        if not config.delegated_admin_email:
            messages.error(request, "Missing delegated admin email or service account email.")
            return redirect(request.META.get('HTTP_REFERER', reverse_lazy('organization-list')))

        try:
            # Create and start the import job
            config.start_import()
            messages.success(request, "Google Workspace import job created")
        except Exception as e:
            print(f"[ERROR] Failed to create import job: {e}")
            messages.error(request, f"Failed to create import job: {e}")

        return redirect(request.META.get('HTTP_REFERER', reverse_lazy('organization-list')))
