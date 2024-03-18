from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView

from os2datascanner.projects.admin.import_services.keycloak_services import \
    add_ldap_conf, create_realm, request_update_component, \
    get_token_first, create_member_of_attribute_mapper, create_sid_attribute_mapper
from os2datascanner.projects.admin.organizations.models import Organization
from os2datascanner.projects.admin.import_services.models import LDAPConfig, Realm
from os2datascanner.projects.admin.import_services.utils import start_ldap_import


class LDAPEditForm(forms.ModelForm):
    """TODO:"""
    required_css_class = 'required-form'

    class Meta:
        model = LDAPConfig
        fields = [  # Specify default order of form fields:
            'connection_protocol',
            'connection_url',
            'bind_dn',
            'ldap_password',
            'vendor',
            'import_into',
            'username_attribute',
            'rdn_attribute',
            'uuid_attribute',
            'object_sid_attribute',
            'users_dn',
            'search_scope',
            'user_obj_classes',
        ]
        widgets = {
            'bind_dn': forms.TextInput(),
            'users_dn': forms.TextInput(),
            'user_obj_classes': forms.TextInput(),
        }

    ldap_password = forms.CharField(
        widget=forms.PasswordInput(),
        help_text="",  # TODO: add text
        # TODO: add translated label
    )

    @staticmethod
    def connection_fields():
        fields = [
            'bind_dn',
            'ldap_password',
        ]
        return fields

    @staticmethod
    def general_fields():
        fields = [
            'vendor',
            'import_into',
        ]
        return fields

    @staticmethod
    def user_location_fields():
        fields = [
            'users_dn',
            'search_scope',
            'user_obj_classes',
        ]
        return fields

    @staticmethod
    def user_attribute_fields():
        fields = [
            'username_attribute',
            'rdn_attribute',
            'uuid_attribute',
            'object_sid_attribute'
        ]
        return fields


class LDAPAddView(LoginRequiredMixin, CreateView):
    model = LDAPConfig
    template_name = 'import_services/ldap_edit.html'
    success_url = reverse_lazy('organization-list')
    form_class = LDAPEditForm

    def setup(self, request, *args, **kwargs):
        organization = get_object_or_404(Organization, pk=kwargs['org_id'])
        kwargs['organization'] = organization
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = True
        context['organization'] = self.kwargs['organization']
        context['auto_fill_data'] = {
            'ad': {
                'username_attribute': "sAMAccountName",
                'rdn_attribute': "cn",
                'uuid_attribute': "objectGUID",
                'user_obj_classes': "person, organizationalPerson, user",
            },
            'other': {
                'username_attribute': "uid",
                'rdn_attribute': "uid",
                'uuid_attribute': "entryUUID",
                'user_obj_classes': "inetOrgPerson, organizationalPerson",
                'object_sid_attribute': "objectSid",
            },
        }
        return context

    def form_valid(self, form):
        # TODO: ensure all proper checks are in place either here or elsewhere
        form.instance.created = now()
        form.instance.last_modified = now()
        form.instance.organization = self.kwargs['organization']
        form.instance.ldap_credential = form.cleaned_data['ldap_password']
        # NB! Must call super here to ensure instance has a pk
        result = super().form_valid(form)
        _keycloak_creation(form.instance)
        return result


# TODO: consider handling this in a queue
# TODO: add proper error-handling
def _keycloak_creation(config_instance):
    organization = config_instance.organization
    # TODO: ensure Realm existence upon activating feature! And on Org creation
    # (if feature is active)
    realm, created = Realm.objects.get_or_create(
        realm_id=organization.slug,
        organization=organization,
        defaults={'last_modified': now()},
    )
    # TODO: Realm creation should be moved elsewhere, but if not, token
    #  should only be retrieved once in a separate call, and the direct
    #  keycloak services should be called, not the two utility functions.
    if created:
        create_realm(realm.pk)
    payload = config_instance.get_payload_dict()
    add_ldap_conf(realm.pk, payload)
    # TODO: consider moving request elsewhere,
    # else add error-handling!
    # Create a memberOf attribute mapper on the LDAP user federation in Keycloak upon creation
    get_token_first(create_member_of_attribute_mapper, realm.pk, payload["id"])
    res = get_token_first(create_sid_attribute_mapper, realm.pk,
                          payload["id"], config_instance)
    if res.ok:
        # Keycloak returns an empty body upon creation, so we'll fish the id from headers.
        loc = res.headers.get("Location")
        mapper_uuid = loc.split("/")[-1]  # The UUID of the mapper should be the last thing.
        config_instance.object_sid_mapper_uuid = mapper_uuid
        config_instance.save()


def _keycloak_update(config_instance):
    pk = config_instance.pk
    realm = Realm.objects.get(organization_id=pk)
    payload = config_instance.get_payload_dict()
    args = [payload, pk]
    get_token_first(request_update_component, realm.pk, *args)
    # Do the same for SID mapper - if one is set.
    if config_instance.object_sid_mapper_uuid:
        mapper_payload = config_instance.get_mapper_payload_dict()
        mapper_args = [mapper_payload, config_instance.object_sid_mapper_uuid]
        get_token_first(request_update_component, realm.pk, *mapper_args)

    # In case we're doing "Update" but don't have an existing objectSid mapper
    if not config_instance.object_sid_mapper_uuid and config_instance.object_sid_attribute:
        res = get_token_first(create_sid_attribute_mapper, realm.pk,
                              payload["id"], config_instance)
        if res.ok:
            # Keycloak returns an empty body upon creation, so we'll fish the id from headers.
            loc = res.headers.get("Location")
            mapper_uuid = loc.split("/")[-1]  # The UUID of the mapper should be the last thing.
            config_instance.object_sid_mapper_uuid = mapper_uuid
            config_instance.save()


class LDAPUpdateView(LoginRequiredMixin, UpdateView):

    model = LDAPConfig
    template_name = 'import_services/ldap_edit.html'
    success_url = reverse_lazy('organization-list')
    form_class = LDAPEditForm

    def setup(self, request, *args, **kwargs):
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = False
        context['organization'] = self.object.organization
        return context

    def form_valid(self, form):
        form.instance.ldap_credential = form.cleaned_data['ldap_password']
        _keycloak_update(form.instance)
        return super().form_valid(form)


class LDAPImportView(LoginRequiredMixin, DetailView):
    """Base class for view that handles starting of a scanner run."""

    model = LDAPConfig

    def __init__(self):
        self.object = None

    def get(self, request, *args, **kwargs):
        """
        Handle a get request to the LDAPImportView.
        """
        start_ldap_import(self.get_object())

        # redirect back to organizations
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
