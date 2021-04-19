from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from os2datascanner.projects.admin.import_services.keycloak_services import add_or_update_ldap_conf
from os2datascanner.projects.admin.organizations.models import Organization

from .models import LDAPConfig


class LDAPEditForm(forms.ModelForm):
    """TODO:"""
    required_css_class = 'required-form'

    class Meta:
        model = LDAPConfig
        fields = [  # Specify default order of form fields:
            'vendor',
            'import_users',
            'edit_mode',
            'username_attribute',
            'rdn_attribute',
            'uuid_attribute',
            'user_obj_classes',
            'users_dn',
            'search_scope',
            'connection_url',
            'bind_dn',
        ]

    ldap_password = forms.CharField(
        widget=forms.PasswordInput(),
        help_text="",  # TODO: add text
        # TODO: add translated label
    )


class LDAPEditView(LoginRequiredMixin, CreateView):
    model = LDAPConfig
    template_name = 'import_services/ldap_add.html'
    success_url = reverse_lazy('organization-list')
    form_class = LDAPEditForm

    def setup(self, request, *args, **kwargs):
        # TODO: consider most sensible way to handle invalid/misisng uuid:
        organization = Organization.objects.get(pk=kwargs['org_id'])
        request.ds_organization = organization
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = True  # TODO: change to actual check
        context['organization'] = self.request.ds_organization.name
        return context

    def form_valid(self, form):
        # TODO: ensure all proper checks are in place either here or elsewhere
        form.instance.organization_id = self.kwargs['org_id']
        form.instance.ldap_credential = form.cleaned_data['ldap_password']
        payload = form.instance.get_payload_dict()
        print(f"\nPayload:\n{payload}")
        realm = self.request.ds_organization.slug
        add_or_update_ldap_conf(realm, payload)
        return super().form_valid(form)
