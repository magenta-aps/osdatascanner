from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView

from os2datascanner.projects.admin.import_services.keycloak_services import (
    request_create_component, create_realm, request_update_component)
from os2datascanner.projects.admin.organizations.models import Organization
from os2datascanner.projects.admin.import_services.models import LDAPConfig, Realm
from os2datascanner.projects.admin.import_services.utils import start_ldap_import
from os2datascanner.projects.admin.import_services.models.ldap_configuration import \
    LDAPUsernameAttributeMapper, LDAPSIDMapper, LDAPFirstNameAttributeMapper, LDAPGroupFilterMapper
from os2datascanner.projects.grants.admin import AutoEncryptedField, choose_field_value
from os2datascanner.projects.admin.import_services.views.keycloak_api_views import (
    verify_authentication, verify_connection)


class LDAPEditForm(forms.ModelForm):
    """TODO:"""
    required_css_class = 'required-form'

    class Meta:
        model = LDAPConfig
        fields = [  # Specify default order of form fields:
            'connection_protocol',
            'connection_url',
            'bind_dn',
            '_ldap_password',
            'vendor',
            'import_into',
            'group_filter',
            'import_managers',
            'username_attribute',
            'rdn_attribute',
            'uuid_attribute',
            'object_sid_attribute',
            'firstname_attribute',
            'users_dn',
            'search_scope',
            'custom_user_filter',
            'user_obj_classes',
        ]
        widgets = {
            'bind_dn': forms.TextInput(),
            'users_dn': forms.TextInput(),
            'user_obj_classes': forms.TextInput(),
            'custom_user_filter': forms.TextInput(),
        }

    _ldap_password = AutoEncryptedField(required=False)

    def clean__ldap_password(self):
        return choose_field_value(
              self.cleaned_data["_ldap_password"],
              self.instance._ldap_password)

    @staticmethod
    def connection_fields():
        fields = [
            'bind_dn',
            '_ldap_password',
        ]
        return fields

    @staticmethod
    def general_fields():
        fields = [
            'vendor',
            'import_into',
            'group_filter',
            'import_managers',
        ]
        return fields

    @staticmethod
    def user_location_fields():
        fields = [
            'users_dn',
            'search_scope',
            'user_obj_classes',
            'custom_user_filter'
        ]
        return fields

    @staticmethod
    def user_attribute_fields():
        fields = [
            'username_attribute',
            'rdn_attribute',
            'uuid_attribute',
            'object_sid_attribute',
            'firstname_attribute',
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
                'firstname_attribute': "givenName"
            },
        }
        return context

    def form_valid(self, form):
        # TODO: ensure all proper checks are in place either here or elsewhere
        form.instance.created = now()
        form.instance.last_modified = now()
        form.instance.organization = self.kwargs['organization']
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
    request_create_component(realm, payload)
    # TODO: consider moving request elsewhere,
    # else add error-handling!

    # Create SID mapper - if one is set.
    if config_instance.object_sid_attribute:
        sid_attr_mapper = LDAPSIDMapper(ldap_attr=config_instance.object_sid_attribute)
        config_instance.update_or_create_mapper(sid_attr_mapper)

    # Create first name mapper - if one is set.
    if config_instance.firstname_attribute:
        firstname_attr_mapper = LDAPFirstNameAttributeMapper(
            ldap_attr=config_instance.firstname_attribute
        )
        config_instance.update_or_create_mapper(firstname_attr_mapper)

    # Create group filter mapper - if one is set.
    if config_instance.import_into == "group":
        group_filter_mapper = LDAPGroupFilterMapper(config_instance.users_dn,
                                                    config_instance.group_filter)
        config_instance.update_or_create_mapper(group_filter_mapper)


def _keycloak_update(config_instance):
    pk = config_instance.pk
    realm = Realm.objects.get(organization_id=pk)
    payload = config_instance.get_payload_dict()
    args = [payload, pk]

    # Update general fields (those on the user federation)
    request_update_component(realm, *args)

    # Update username attribute mapper. This is created behind the scenes by Keycloak on creation.
    config_instance.update_or_create_mapper(
        LDAPUsernameAttributeMapper(ldap_attr=config_instance.username_attribute)
    )

    # Update or create SID mapper - if one is set.
    if config_instance.object_sid_attribute:
        sid_attr_mapper = LDAPSIDMapper(ldap_attr=config_instance.object_sid_attribute)
        config_instance.update_or_create_mapper(sid_attr_mapper)

    # Update or create first name mapper - if one is set.
    if config_instance.firstname_attribute:
        firstname_attr_mapper = LDAPFirstNameAttributeMapper(
            ldap_attr=config_instance.firstname_attribute
        )
        config_instance.update_or_create_mapper(firstname_attr_mapper)

    # Update or create group filter mapper - if one is set.
    if config_instance.import_into == "group":
        group_filter_mapper = LDAPGroupFilterMapper(config_instance.users_dn,
                                                    config_instance.group_filter)
        config_instance.update_or_create_mapper(group_filter_mapper)

    # If there exists a memberOf mapper, it should be removed
    config_instance.delete_mapper("memberOf")


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


class LDAPTestConnectionView(LoginRequiredMixin, TemplateView):
    template_name = 'import_services/ldap_edit.html'

    def post(self, request, *args, **kwargs):
        is_htmx = self.request.headers.get("HX-Request", False) == "true"

        if is_htmx:
            context = self.get_context_data(**kwargs)
            htmx_trigger = self.request.headers.get("HX-Trigger-Name")

            con_url = (
                f"{self.request.POST.get('connection_protocol')}"
                f"{self.request.POST.get('connection_url')}")
            req = HttpRequest()
            req.method = "POST"
            req.POST["url"] = con_url

            if htmx_trigger == "button-connection":
                con_resp = verify_connection(req)
                context["connection_established"] = True if con_resp.status_code == 200 else False

            if htmx_trigger == "button-auth":
                exisiting_ldap_password = None

                if ldap_conf_pk := request.POST.get("ldap_config"):
                    ldap_conf = LDAPConfig.objects.get(pk=ldap_conf_pk)
                    exisiting_ldap_password = ldap_conf.ldap_password

                ldap_password = self.request.POST.get("_ldap_password")
                req.POST["bind_dn"] = self.request.POST.get("bind_dn")
                req.POST["bind_credential"] = ldap_password or exisiting_ldap_password
                auth_resp = verify_authentication(req)
                context["auth_established"] = True if auth_resp.status_code == 200 else False

            return self.render_to_response(context)
