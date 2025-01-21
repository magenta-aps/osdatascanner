# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
from enum import Enum

import requests
import json
import structlog
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .exported_mixin import Exported
from ..keycloak_services import refresh_token, request_access_token

logger = structlog.get_logger("import_services")


class Realm(Exported, models.Model):
    realm_id = models.SlugField(
        allow_unicode=True,
        primary_key=True,
        verbose_name=_('realm id'),
    )
    organization = models.OneToOneField(
        'organizations.Organization',
        on_delete=models.PROTECT,  # TODO: 43163
        verbose_name=_('organization'),
        related_name='realm'
    )

    class Meta:
        verbose_name = _('Keycloak realm')
        verbose_name_plural = _('Keycloak realms')

    FEDERATED_LOGIN_FLOW_EXECUTIONS = ["idp-detect-existing-broker-user", "idp-auto-link"]
    NON_FEDERATED_LOGIN_FLOW_EXECUTIONS = ["idp-create-user-if-unique", "idp-auto-link"]

    def __str__(self):
        return self.realm_id

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.realm_id}>"

    def setup_federated_sso_flow(self, token=None):
        # 1. Create an authentication flow
        auth_flow, auth_flow_created = AuthenticationFlow.objects.get_or_create(
            realm=self,
            flow_name="LDAP-FEDERATED-LOGIN-FLOW")

        if auth_flow_created:
            auth_flow.create_LDAP_auth_flow(token=token)

        # 2. Create needed flow executions
            for execution in self.FEDERATED_LOGIN_FLOW_EXECUTIONS:
                self.create_flow_execution(
                    auth_flow, execution,
                    FlowExecution.Requirement.REQUIRED, token=token)

        # Return the thing you just made, woah.
        return auth_flow

    def setup_non_federated_sso_flow(self, token=None):
        # 1. Create an authentication flow
        auth_flow, auth_flow_created = AuthenticationFlow.objects.get_or_create(
            realm=self,
            flow_name="NON-FEDERATED-LOGIN-FLOW")

        if auth_flow_created:
            auth_flow.create_LDAP_auth_flow(token=token)

        # 2. Create needed flow executions
            for execution in self.NON_FEDERATED_LOGIN_FLOW_EXECUTIONS:
                self.create_flow_execution(
                    auth_flow, execution,
                    FlowExecution.Requirement.ALTERNATIVE, token=token
                )

        # Return the thing you just made, woah.
        return auth_flow

    def create_flow_execution(self, auth_flow, execution, requirement, token=None):
        flow_exec, created = FlowExecution.objects.get_or_create(
            realm=self, flow=auth_flow, provider=execution
        )

        if created:
            # Create the execution
            flow_exec.create_authentication_flow_execution(token=token)
            # Get its ID, because we're going to need it ...
            flow_exec_id = flow_exec.get_authentication_flow_execution_id()
            flow_exec.exec_flow_id = flow_exec_id
            flow_exec.save()
            # ... because you have to set requirement in a separate call ... why...
            flow_exec.set_authentication_flow_execution_requirement(
                requirement=requirement, token=token
            )

        else:
            # Todo: probably look to check it's there to make it idempotent.
            logger.warning("Didn't create any new flow execution")

    @refresh_token
    def set_default_idp(self, idp, token=None):
        # We don't want the Keycloak login screen when using SSO, it doesn't make sense for our
        # single-tenant on-prem customers. This can be circumvented by altering the "browser"
        # authentication flow, setting a default identity provider.
        # (which we should have created by the time we run this function)

        headers = {
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json;charset=utf-8',
        }

        # We need the ID of this particular execution first.
        flow_name = "browser"  # A Keycloak Built-in flow.
        idp_redirector = "identity-provider-redirector"
        idp_redirector_exec_id = None

        url_get_id = (settings.KEYCLOAK_BASE_URL +
                      f"/auth/admin/realms/{self}"
                      f"/authentication/flows/{flow_name}/executions")

        response = requests.get(url_get_id, headers=headers)

        # TODO: probably need some error handling / in case it isn't found.
        for execution in response.json():
            # Why tf. is it a "providerId" in this context Keycloak...
            if execution.get("providerId", "") == idp_redirector:
                idp_redirector_exec_id = execution["id"]

        if idp_redirector_exec_id:
            url = (settings.KEYCLOAK_BASE_URL +
                   f"/auth/admin/realms/{self}/authentication"
                   f"/executions/{idp_redirector_exec_id}/config")

            body = {
                "alias": "sso",  # This is just an alias for the execution itself.
                "config":
                    {
                        "defaultProvider": idp.alias  # This bit is what matters.
                    }
            }

            return requests.post(url, headers=headers, data=json.dumps(body))

        else:
            logger.warning("Something went wrong trying to set default IdP..")


class KeycloakClient(models.Model):
    # Prefixed Keycloak because OSdatascanner has a "Client" already.

    realm = models.ForeignKey(Realm,
                              on_delete=models.CASCADE,
                              related_name='clients', editable=False)

    # Is just here for good measure / future - currently there'd be no reason for changing.
    protocol = models.CharField(editable=False, max_length=255, default="openid-connect")

    client_id = models.CharField(max_length=255)

    root_url = models.CharField(max_length=255)

    redirect_uri = models.CharField(max_length=255, default="*")

    @refresh_token
    def create_keycloak_client(self, token=None):
        # Root url = Hostname
        # Valid redirect /* (anything appended to hostname)
        # Rest are default settings
        headers = {
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json;charset=utf-8',
        }
        url = (settings.KEYCLOAK_BASE_URL + f"/auth/admin/realms/{self.realm}/clients")

        body = {
            "protocol": self.protocol,
            "clientId": self.client_id,
            # TODO: Be careful here.. If rootUrl has a trailing /, you can't have one
            # in your redirect
            "rootUrl": self.root_url,
            "redirectUris": [self.redirect_uri],
        }

        return requests.post(url, headers=headers, data=json.dumps(body))


class IdentityProvider(models.Model):
    realm = models.ForeignKey(Realm,
                              on_delete=models.CASCADE,
                              related_name='providers', editable=False)

    # We're dependent on knowing these values and there's no value in the user changing them.
    # If one day we want multiple IdP's in one realm, we can reconsider editable.
    provider_id = models.CharField(default="saml", max_length=255, editable=False)
    alias = models.CharField(default="SAML-SSO", max_length=255, editable=False)

    metadata_url = models.CharField(max_length=510, blank=True, null=True,
                                    verbose_name=_("metadata url"),
                                    help_text=_("should be a reachable url providing federation "
                                                "metadata in xml format "))
    entity_id = models.CharField(max_length=255,
                                 verbose_name=_("service provider entity id"),
                                 help_text=_("entity id of the service provider"))

    idp_entity_id = models.CharField(max_length=255,
                                     verbose_name=_("identity provider entity id"),
                                     help_text=_("entity id of the identity provider"))

    single_sign_on_service_url = models.CharField(
        max_length=255,
        verbose_name=_("Single Sign-On service url"),
        help_text=_(
            "The url that must be used to send authentication requests (SAML AuthnRequest).")
    )

    # Todo: I'm not actually sure if we need this in any case?
    single_logout_service_url = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name=_("Single logout service url"),
        help_text=_("The url that must be used to send logout requests.")
    )

    class NameIDFormatChoices(models.TextChoices):
        UNSPECIFIED = "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified", "Unspecified"
        PERSISTENT = "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent", "Persistent"
        TRANSIENT = "urn:oasis:names:tc:SAML:2.0:nameid-format:transient", "Transient"
        EMAIL = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress", "Email"

    nameid_policy_format = models.CharField(
        choices=NameIDFormatChoices.choices,
        default=NameIDFormatChoices.UNSPECIFIED,
        max_length=255,
        verbose_name=_("nameid policy format"),
        help_text=_("Specifies the URI reference corresponding to a name identifier format.")
    )

    class PrincipalAttrTypeChoices(models.TextChoices):
        SUBJECT = "SUBJECT", "Subject NameID"
        ATTR_NAME = "ATTRIBUTE", "Attribute Name"
        ATTR_FRIENDLY = "FRIENDLY_ATTRIBUTE", "Attribute Friendly Name"

    principal_type = models.CharField(
        max_length=255, choices=PrincipalAttrTypeChoices.choices,
        default=PrincipalAttrTypeChoices.SUBJECT,
        verbose_name=_("principal type"),
        help_text=_("Way to identify and track external users from the assertion."
                    " Default is using Subject NameID, "
                    "alternatively you can set up identifying attribute.")
    )

    # TODO: Only meaningful if attr name og attr friendly is chosen
    principal_attr = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name=_("principal attribute"),
        help_text=_("Name or Friendly Name of the attribute used to identify external users. "
                    "Only relevant if principal type is set to an 'Attribute' option. ")
    )

    # I _think_ False is sensible here - AFAIK, we generally only need REDIRECT binding.
    post_binding_response = models.BooleanField(
        default=False,
        verbose_name=_("HTTP-POST binding response"),
        help_text=_("Indicates whether to respond to requests using HTTP-POST binding. "
                    "If off, HTTP-REDIRECT binding will be used.")
    )

    post_binding_authn_request = models.BooleanField(
        default=False,
        verbose_name=_("HTTP-POST binding for AuthnRequest"),
        help_text=_("Indicates whether the AuthnRequest must be sent using HTTP-POST binding."
                    " If off, HTTP-REDIRECT binding will be used.")
    )

    post_binding_logout = models.BooleanField(
        default=False,
        verbose_name=_("HTTP-POST binding logout"),
        help_text=_("Indicates whether to respond to requests using HTTP-POST binding."
                    " If off, HTTP-REDIRECT binding will be used.")
    )

    # Signage
    authn_requests_signed = models.BooleanField(
        default=False,
        verbose_name=_("AuthnRequests signed"),
        help_text=_("Indicates whether the identity provider expects a signed AuthnRequest.")
    )
    assertions_signed = models.BooleanField(
        default=False,
        verbose_name=_("Assertions signed"),
        help_text=_("Indicates whether this service provider expects a signed Assertion.")
    )

    # When SAML does it's thing, it generally needs to be very time accurate
    # this setting allows _some_ difference, in seconds.
    allowed_clock_skew = models.FloatField(
        default=0,
        verbose_name=_("allowed clock skew"),
        help_text=_("Clock skew in seconds that is "
                    "tolerated when validating identity provider tokens. ")
    )

    def request_body(self, auth_flow) -> dict:
        # SAML SETTINGS
        body = {
            "alias": self.alias,
            "config": {
                "guiOrder": "",
                "entityId": self.entity_id,
                "idpEntityId": self.idp_entity_id,
                "singleSignOnServiceUrl": self.single_sign_on_service_url,
                "singleLogoutServiceUrl": self.single_logout_service_url or "",
                "attributeConsumingServiceName": "",
                "backchannelSupported": "false",
                "nameIDPolicyFormat": self.nameid_policy_format,
                "principalType": self.principal_type,
                "postBindingResponse": self.post_binding_response,
                "postBindingAuthnRequest": self.post_binding_authn_request,
                "postBindingLogout": self.post_binding_logout,
                "wantAuthnRequestsSigned": self.authn_requests_signed,
                "wantAssertionsSigned": self.assertions_signed,
                "wantAssertionsEncrypted": "false",
                "forceAuthn": "false",
                "validateSignature": "false",
                "signSpMetadata": "false",
                "loginHint": "false",
                "allowedClockSkew": self.allowed_clock_skew,
                "attributeConsumingServiceIndex": 0,
                "principalAttribute": self.principal_attr or "",
                # 'force' to always update the user during every login with this identity provider.
                "syncMode": "FORCE",
            },
            "displayName": "",
            "providerId": self.provider_id,
            # ADVANCED SETTING
            # First login flow: Must be set to the Authentication flow we customized.
            "firstBrokerLoginFlowAlias": auth_flow.flow_name,
        }
        return body

    @refresh_token
    def create_identity_provider(self, auth_flow, token=None):
        headers = {
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json;charset=utf-8',
        }
        url = (settings.KEYCLOAK_BASE_URL + f"/auth/admin/realms/{self.realm}"
               f"/identity-provider/instances")

        body = self.request_body(auth_flow)

        return requests.post(url, headers=headers, data=json.dumps(body))

    @refresh_token
    def update_identity_provider(self, auth_flow, token=None):
        headers = {
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json;charset=utf-8',
        }
        url = (settings.KEYCLOAK_BASE_URL + f"/auth/admin/realms/{self.realm}"
               f"/identity-provider/instances/{self.alias}")

        body = self.request_body(auth_flow)

        return requests.put(url, headers=headers, data=json.dumps(body))

    @refresh_token
    def read_metadata_url(self, token=None):
        headers = {
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json;charset=utf-8',
        }
        url = (settings.KEYCLOAK_BASE_URL + f"/auth/admin/realms"
               f"/{self.realm}/identity-provider/import-config")

        body = {
            "providerId": self.provider_id,
            "fromUrl": self.metadata_url}

        return requests.post(url, headers=headers, data=json.dumps(body))


class IdPMappers(models.Model):

    # Use email, lastName, and firstName to map to those predefined user properties.
    KEYCLOAK_USER_ATTRIBUTES = ["username", "firstName", "lastName", "email", "objectSid"]

    idp = models.ForeignKey(IdentityProvider, related_name='mappers', on_delete=models.CASCADE)

    saml_attr = models.CharField(max_length=255,)
    keycloak_attr = models.CharField(max_length=255)

    @refresh_token
    def get_idp_mappers(self, token=None):
        headers = {
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json;charset=utf-8',
        }

        url = (settings.KEYCLOAK_BASE_URL +
               f"/auth/admin/realms/{self.idp.realm}/identity-provider/instances/SAML-SSO/mappers")

        return requests.get(url, headers=headers)

    @refresh_token
    def update_or_create_idp_mapper(self, token=None):
        headers = {
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json;charset=utf-8',
        }
        body = {
            "name": self.keycloak_attr,
            "config": {
                "syncMode": "INHERIT",  # Inherit, Import, Legacy, Force, Idk..
                "attribute.name": self.saml_attr,
                "template": "${ALIAS}.${NAMEID}",
                # TODO: could be configurable, there's also ATTRIBUTE_FORMAT_URI & .._UNSPECIFIED
                # .. but basic is the default and should be ok for our use cases
                "attribute.name.format": "ATTRIBUTE_FORMAT_BASIC",
                "user.attribute": self.keycloak_attr
            },
            "identityProviderMapper": "saml-user-attribute-idp-mapper",
            "identityProviderAlias": self.idp.alias
        }

        url = (settings.KEYCLOAK_BASE_URL +
               f"/auth/admin/realms/{self.idp.realm}"
               f"/identity-provider/instances/{self.idp.alias}/mappers")

        existing_idp_mappers = self.get_idp_mappers(token=token).json()

        name_to_id = {d["name"]: d["id"] for d in existing_idp_mappers}
        mapper_id = name_to_id.get(self.keycloak_attr)

        if mapper_id:
            logger.info("Existing IdP mapper, issuing update.", keycloak_attr=self.keycloak_attr)

            # Adding id to request body
            body["id"] = mapper_id

            return requests.put(url + f"/{mapper_id}", headers=headers, data=json.dumps(body))

        else:
            logger.info("No existing IdP mapper, creating one.", keycloak_attr=self.keycloak_attr)
            return requests.post(url, headers=headers, data=json.dumps(body))

    @refresh_token
    def delete_idp_mapper(self, token=None):
        headers = {
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json;charset=utf-8',
        }

        existing_idp_mappers = self.get_idp_mappers(token=token).json()

        name_to_id = {d["name"]: d["id"] for d in existing_idp_mappers}
        mapper_id = name_to_id.get(self.keycloak_attr)

        url = (settings.KEYCLOAK_BASE_URL +
               f"/auth/admin/realms/{self.idp.realm}"
               f"/identity-provider/instances/{self.idp.alias}/mappers/{mapper_id}")

        if mapper_id:
            logger.info("Deleting IdP mapper.", keycloak_attr=self.keycloak_attr)
            return requests.delete(url, headers=headers)

        else:
            logger.info("There was mo existing IdP mapper in Keycloak.",
                        keycloak_attr=self.keycloak_attr)


class AuthenticationFlow(models.Model):
    realm = models.ForeignKey(Realm,
                              on_delete=models.CASCADE,
                              related_name='authentication_flows',
                              editable=False)

    flow_name = models.CharField(max_length=255, unique=True)

    @refresh_token
    def create_LDAP_auth_flow(self, token=None):
        url = (settings.KEYCLOAK_BASE_URL +
               f'/auth/admin/realms/{self.realm}/authentication/flows')
        headers = {
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json;charset=utf-8',
        }

        body = {
            "alias": self.flow_name,
            "description": "",
            "providerId": "basic-flow",
            "builtIn": False,
            "topLevel": True
        }

        return requests.post(url, headers=headers, data=json.dumps(body))


class FlowExecution(models.Model):
    # Todo: realm might be redundant here, cause of the fk to AuthFlow, which already knows
    realm = models.ForeignKey(Realm,
                              on_delete=models.CASCADE,
                              related_name='flow_executions')

    flow = models.ForeignKey(AuthenticationFlow,
                             on_delete=models.CASCADE,
                             related_name='flow_executions')

    # This is a bad name, but it is what it is - that's what it's called in the API call.
    # It represents the different "built in" execution flows.
    provider = models.CharField(max_length=255)

    exec_flow_id = models.CharField(max_length=255, null=True, blank=True, editable=False)

    class Requirement(Enum):
        # Alternative means:
        # Only a single element must successfully execute for the flow to evaluate as successful.
        # Because the Required flow elements are sufficient to mark a flow as successful,
        # any Alternative flow element within a flow containing
        # Required flow elements will not execute
        REQUIRED = "REQUIRED"
        ALTERNATIVE = "ALTERNATIVE"
        DISABLED = "DISABLED"

    @refresh_token
    def create_authentication_flow_execution(self, token=None):
        headers = {
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json;charset=utf-8',
        }

        url = (settings.KEYCLOAK_BASE_URL +
               f"/auth/admin/realms/{self.flow.realm}"
               f"/authentication/flows/{self.flow.flow_name}/executions/execution")

        body = {"provider": self.provider}

        return requests.post(url, headers=headers, data=json.dumps(body))

    def get_authentication_flow_execution_id(self) -> str:
        # Not returning a request response here, so can't use refresh_token.
        token = request_access_token()
        headers = {
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json;charset=utf-8',
        }
        url = (settings.KEYCLOAK_BASE_URL +
               f"/auth/admin/realms/{self.flow.realm}"
               f"/authentication/flows/{self.flow.flow_name}/executions")

        response = requests.get(url, headers=headers)

        # TODO: probably need some error handling / in case it isn't found.
        for execution in response.json():
            # Why tf. is it a "providerId" in this context Keycloak...
            if execution.get("providerId", "") == self.provider:
                return execution["id"]

    @refresh_token
    def set_authentication_flow_execution_requirement(self, requirement: Requirement, token=None):

        headers = {
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json;charset=utf-8',
        }

        url = (settings.KEYCLOAK_BASE_URL +
               f"/auth/admin/realms/{self.flow.realm}"
               f"/authentication/flows/{self.flow.flow_name}/executions")

        body = {
            "id": self.exec_flow_id,
            "providerId": self.provider,
            "requirement": requirement.value,
            "requirementChoices": ["REQUIRED", "ALTERNATIVE", "DISABLED"]
        }

        return requests.put(url, headers=headers, data=json.dumps(body))
