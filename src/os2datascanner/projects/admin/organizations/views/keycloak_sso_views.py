import structlog
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from django.views.generic import CreateView, UpdateView, TemplateView
from django.forms import ModelForm
from django.utils.timezone import now
from os2datascanner.projects.admin.organizations.models import Organization
from os2datascanner.projects.admin.import_services.keycloak_services import (
        create_realm)

from os2datascanner.projects.admin.import_services.models.realm import (IdentityProvider,
                                                                        IdPMappers,
                                                                        Realm,
                                                                        KeycloakClient)
from os2datascanner.projects.admin.core.models.client import Feature

from django.utils.translation import gettext_lazy as _
from rest_framework.reverse import reverse_lazy

logger = structlog.get_logger("import_services")


def handle_idp_mappers(form, idp_mappers):
    # Handle creation/updating/deleting of mappers.
    # This will perform requests even if there is no change, i.e. updates that do nothing,
    # but we'll live with it for now, it's a page that is rarely to be updated.
    for kc_attr, saml_attr in idp_mappers:
        if saml_attr:
            idp_mapper, _ = IdPMappers.objects.update_or_create(
                keycloak_attr=kc_attr, idp=form.instance,
                defaults={
                    "saml_attr": saml_attr,
                })

            idp_mapper.update_or_create_idp_mapper()

        else:
            deleted_instances = form.instance.mappers.filter(keycloak_attr=kc_attr)

            for instance in deleted_instances:
                # Delete from Keycloak
                instance.delete_idp_mapper()

            # Delete from OSdatascanner
            form.instance.mappers.filter(keycloak_attr=kc_attr).delete()


class FetchMetadataUrlMixin:

    def get(self, request, *args, **kwargs):
        self.metadata = kwargs.get("metadata")
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()

        if self.request.method == "POST" and hasattr(self, "metadata"):
            # request.POST is an immutable querydict, copying to circumvent.
            post_copy = self.request.POST.copy()

            # TODO: there might be more options from other metadata providers.

            post_copy["nameid_policy_format"] = self.metadata.get(
                "nameIDPolicyFormat",
                IdentityProvider.NameIDFormatChoices.UNSPECIFIED.value
            )
            post_copy["idp_entity_id"] = self.metadata.get("idpEntityId")
            post_copy["post_binding_response"] = self.metadata.get("postBindingResponse", False)
            post_copy["post_binding_authn_request"] = self.metadata.get("postBindingAuthnRequest",
                                                                        False)
            post_copy["post_binding_logout"] = self.metadata.get("postBindingLogout", False)
            post_copy["single_sign_on_service_url"] = self.metadata.get("singleSignOnServiceUrl")

            kwargs.update({
                'data': post_copy,
            })

        return kwargs


class IdPForm(ModelForm):
    class Meta:
        model = IdentityProvider
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.label_suffix = ""  # Remove colon suffix.
        # Visible because customer will need it for their ADFS configuration
        # Not editable, because it's a Keycloak thing.
        self.fields["entity_id"].disabled = True


class IdPMapperForm(ModelForm):
    class Meta:
        model = IdPMappers
        fields = ["keycloak_attr",
                  "saml_attr"]

    def __init__(self, keycloak_attr, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.label_suffix = ""  # Remove colon suffix.
        # User should never modify this attribute, it's tied to Keycloak user objects.
        self.fields["keycloak_attr"].initial = keycloak_attr
        self.fields["keycloak_attr"].disabled = True
        self.fields["keycloak_attr"].label = _("OSdatascanner user attribute")

        # Well, you could argue that everything but SID is probably ideal to "require"
        # in most cases, but it takes too much custom logic.
        self.fields["saml_attr"].label = _("Claim attribute")
        self.fields["saml_attr"].required = False


class SSOCreateView(LoginRequiredMixin, FetchMetadataUrlMixin, CreateView):
    template_name = "sso/sso_edit.html"
    success_url = '/organizations/'
    model = IdentityProvider
    form_class = IdPForm

    def dispatch(self, request, *args, **kwargs):
        org = self.kwargs["organization"]

        # Yikes.. But basically, if not Keycloak enabled,
        # import service or SSO user creation disallowed.
        if not (settings.KEYCLOAK_ENABLED and
                Feature.IMPORT_SERVICES_MS_GRAPH in org.client.enabled_features or
                Feature.IMPORT_SERVICES_OS2MO in org.client.enabled_features or
                Feature.IMPORT_SERVICES in org.client.enabled_features or
                settings.OIDC_CREATE_USER
                ):
            return HttpResponseRedirect(reverse_lazy("sso-error"))

        realm, created = Realm.objects.get_or_create(
            realm_id=org.slug,
            organization=org,
            defaults={'last_modified': now()},
        )
        if created:
            create_realm(realm.pk)

        self.kwargs['realm'] = realm
        return super().dispatch(request, *args, **kwargs)

    def setup(self, request, *args, **kwargs):
        organization = get_object_or_404(Organization, pk=kwargs['org_id'])
        kwargs['organization'] = organization
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        is_htmx = self.request.headers.get("HX-Request", False) == "true"
        if is_htmx:
            metadata_url = request.POST.get("metadata_url")
            metadata = IdentityProvider(
                metadata_url=metadata_url,
                realm=self.kwargs.get("realm")
            ).read_metadata_url().json()

            # Re-render the form with updated values
            return self.get(request, *args, metadata=metadata)

        else:
            return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.metadata = kwargs.get("metadata")
        return super().get(request, *args, **kwargs)

    def get_initial(self, *args, **kwargs):
        initial_data = super().get_initial()

        initial_data["entity_id"] = (settings.KEYCLOAK_BASE_URL +
                                     f"/auth/realms/{self.kwargs.get('realm')}")
        return initial_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new'] = True
        context["organization"] = self.kwargs["organization"]
        context["realm"] = self.kwargs["realm"]

        context["mappers"] = [IdPMapperForm(keycloak_attr=kc_attr)
                              for kc_attr in IdPMappers.KEYCLOAK_USER_ATTRIBUTES]

        return context

    def form_valid(self, form):
        realm = self.kwargs["realm"]
        form.instance.realm = realm
        org = self.kwargs["organization"]

        # Create a Keycloak client - That's what represents the report module as a "resource".
        keycloak_client, client_created = KeycloakClient.objects.get_or_create(
            realm=realm,
            client_id=settings.OIDC_RP_CLIENT_ID,
            root_url=settings.REPORT_URL
        )

        if client_created:
            logger.info("Creating Keycloak Client")
            keycloak_client.create_keycloak_client()

        # IMPORT_SERVICE is LDAP based import. That requires a different kind of flow, as we
        # utilize Keycloak User Federation.
        if Feature.IMPORT_SERVICES in org.client.enabled_features:
            auth_flow = realm.setup_federated_sso_flow()
        else:
            auth_flow = realm.setup_non_federated_sso_flow()

        # So. Now we have all we need to create a meaningful IdP, pass the instance on:
        form.instance.create_identity_provider(auth_flow=auth_flow)

        # Set default IdP to use.
        realm.set_default_idp(idp=form.instance)

        #  Handle IdPMappers (claims)
        # This bit is bound hard to correct order of attributes in the form
        saml_attrs = self.request.POST.getlist('saml_attr')
        idp_mappers = zip(IdPMappers.KEYCLOAK_USER_ATTRIBUTES, saml_attrs)

        # .. but We have to save the form first, because IdP mappers depend on the IdP being saved
        form_valid = super().form_valid(form)
        handle_idp_mappers(form, idp_mappers)

        return form_valid


class SSOUpdateView(LoginRequiredMixin, FetchMetadataUrlMixin, UpdateView):
    template_name = "sso/sso_edit.html"
    success_url = '/organizations/'
    model = IdentityProvider
    form_class = IdPForm

    def dispatch(self, request, *args, **kwargs):
        org = get_object_or_404(Organization, pk=kwargs['org_id'])

        # Yikes.. But basically, if not Keycloak enabled,
        # import service or SSO user creation disallowed.
        if not (settings.KEYCLOAK_ENABLED and
                Feature.IMPORT_SERVICES_MS_GRAPH in org.client.enabled_features or
                Feature.IMPORT_SERVICES_OS2MO in org.client.enabled_features or
                Feature.IMPORT_SERVICES in org.client.enabled_features or
                settings.OIDC_CREATE_USER
                ):
            return HttpResponseRedirect(reverse_lazy("sso-error"))

        return super().dispatch(request, *args, **kwargs)

    def setup(self, request, *args, **kwargs):
        organization = get_object_or_404(Organization, pk=kwargs['org_id'])
        kwargs['organization'] = organization
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):

        return IdentityProvider.objects.prefetch_related("mappers").get(
            realm__organization_id=self.kwargs["org_id"])

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        is_htmx = self.request.headers.get("HX-Request", False) == "true"

        if is_htmx:
            # Process the metadata_url value
            self.object.metadata_url = request.POST.get("metadata_url")

            metadata = self.object.read_metadata_url().json()

            # Re-render the form with updated values
            return self.get(request, *args, metadata=metadata)

        else:
            return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.kwargs["organization"]
        context["realm"] = self.get_object().realm

        mappers = []

        for kc_attr in IdPMappers.KEYCLOAK_USER_ATTRIBUTES:
            if existing_mapper := self.object.mappers.filter(keycloak_attr=kc_attr).first():

                mappers.append(IdPMapperForm(instance=existing_mapper, keycloak_attr=kc_attr,
                                             auto_id=f"{kc_attr}_%s"))
            else:
                mappers.append(IdPMapperForm(keycloak_attr=kc_attr, auto_id=f"{kc_attr}_%s"))

        context["mappers"] = mappers

        return context

    def form_valid(self, form):
        # Means that the Identity Provider form has changed - not including mappers-
        if form.has_changed():
            if auth_flow := form.instance.realm.authentication_flows.first():
                form.instance.update_identity_provider(auth_flow)

        # This bit is bound hard to correct order of attributes in the form
        saml_attrs = self.request.POST.getlist('saml_attr')
        idp_mappers = zip(IdPMappers.KEYCLOAK_USER_ATTRIBUTES, saml_attrs)

        handle_idp_mappers(form, idp_mappers)

        return super().form_valid(form)


class SSOErrorView(LoginRequiredMixin, TemplateView):
    """
        You'll end here if you're trying to reach the create or update view
        without meaningful system configuration.
    """
    template_name = "sso/sso_error.html"
