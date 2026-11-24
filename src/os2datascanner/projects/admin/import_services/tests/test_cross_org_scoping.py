# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import uuid

import pytest
from django.test import Client
from django.urls import reverse
from django.utils.timezone import now

from os2datascanner.projects.grants.models import GraphGrant
from ...organizations.tests.test_grant_cross_org_scoping import make_grant
from ..models import (
    GoogleWorkspaceConfig, GoogleWorkspaceImportJob, LDAPConfig, LDAPImportJob,
    MSGraphConfiguration, MSGraphImportJob, OS2moConfiguration, OS2moImportJob, Realm)


def make_graph_grant(org):
    grant = GraphGrant(
        organization=org, app_id=uuid.uuid4(), tenant_id=uuid.uuid4())
    grant.client_secret = "Mystra's weave"
    grant.save()
    return grant


def make_ldap_config(org):
    Realm.objects.create(realm_id=org.slug, organization=org, last_modified=now())
    return LDAPConfig.objects.create(
        organization=org,
        vendor="other",
        username_attribute="cn",
        rdn_attribute="cn",
        uuid_attribute="uidNumber",
        user_obj_classes="inetOrgPerson, organizationalPerson",
        connection_protocol="ldap://",
        connection_url="candlekeep:389",
        users_dn="ou=Monks,dc=candlekeep,dc=faerun",
        search_scope=2,
        bind_dn="cn=ulraunt,dc=candlekeep,dc=faerun",
        last_modified=now(),
        ldap_password="alaundo")


def make_config(kind, org):
    match kind:
        case "ldap":
            return make_ldap_config(org)
        case "msgraph":
            return MSGraphConfiguration.objects.create(
                organization=org, grant=make_graph_grant(org), last_modified=now())
        case "os2mo":
            return OS2moConfiguration.objects.create(organization=org, last_modified=now())
        case "googleworkspace":
            return GoogleWorkspaceConfig.objects.create(
                organization=org, grant=make_grant("googleapi", org),
                delegated_admin_email="khelben@waterdeep.faerun", last_modified=now())


IMPORT_JOB_MODELS = {
    "ldap": LDAPImportJob,
    "msgraph": MSGraphImportJob,
    "os2mo": OS2moImportJob,
    "googleworkspace": GoogleWorkspaceImportJob,
}


@pytest.fixture
def os2mo_enabled(settings):
    settings.OS2MO_CLIENT_ID = "harper"
    settings.OS2MO_CLIENT_SECRET = "mistletoe"


@pytest.mark.django_db
class TestImportServiceScoping:
    @pytest.mark.parametrize("kind", IMPORT_JOB_MODELS)
    def test_edit_other_client_config_is_404(
            self, client, user_admin, test_org2, kind):
        config = make_config(kind, test_org2)
        client.force_login(user_admin)
        url = reverse(f"edit-{kind}", kwargs={"pk": config.pk})

        assert client.get(url).status_code == 404
        assert client.post(url, {}).status_code == 404

    @pytest.mark.parametrize("kind", IMPORT_JOB_MODELS)
    def test_edit_own_config_is_allowed(
            self, client, user_admin, test_org, kind):
        config = make_config(kind, test_org)
        client.force_login(user_admin)

        response = client.get(reverse(f"edit-{kind}", kwargs={"pk": config.pk}))

        assert response.status_code == 200

    @pytest.mark.parametrize("kind", IMPORT_JOB_MODELS)
    def test_add_for_other_client_org_is_404(
            self, client, user_admin, test_org2, os2mo_enabled, kind):
        if kind == "msgraph":
            make_graph_grant(test_org2)
        client.force_login(user_admin)
        url = reverse(f"add-{kind}", kwargs={"org_id": test_org2.pk})

        assert client.get(url).status_code == 404
        assert client.post(url, {}).status_code == 404

    @pytest.mark.parametrize("kind", IMPORT_JOB_MODELS)
    def test_add_anonymous_redirects_without_org_lookup(
            self, client, os2mo_enabled, kind):
        response = client.get(reverse(f"add-{kind}", kwargs={"org_id": uuid.uuid4()}))

        assert response.status_code == 302
        assert "login" in response.url

    @pytest.mark.parametrize("kind", IMPORT_JOB_MODELS)
    def test_import_other_client_config_is_404(
            self, client, user_admin, test_org2, kind):
        config = make_config(kind, test_org2)
        client.force_login(user_admin)

        response = client.post(reverse(f"import-{kind}", kwargs={"pk": config.pk}))

        assert response.status_code == 404
        assert not IMPORT_JOB_MODELS[kind].objects.exists()

    @pytest.mark.parametrize("kind", IMPORT_JOB_MODELS)
    def test_import_requires_post(self, client, user_admin, test_org, kind):
        config = make_config(kind, test_org)
        client.force_login(user_admin)
        url = reverse(f"import-{kind}", kwargs={"pk": config.pk})

        assert client.get(url).status_code == 405
        assert not IMPORT_JOB_MODELS[kind].objects.exists()

        response = client.post(url, headers={"Referer": reverse("organization-list")})

        assert response.status_code == 302
        assert IMPORT_JOB_MODELS[kind].objects.count() == 1

    @pytest.mark.parametrize("kind", IMPORT_JOB_MODELS)
    def test_import_without_csrf_token_is_403(self, user_admin, test_org, kind):
        config = make_config(kind, test_org)
        client = Client(enforce_csrf_checks=True)
        client.force_login(user_admin)

        response = client.post(reverse(f"import-{kind}", kwargs={"pk": config.pk}))

        assert response.status_code == 403
        assert not IMPORT_JOB_MODELS[kind].objects.exists()

    def test_googleworkspace_add_offers_only_own_grants(
            self, client, user_admin, test_org, test_org2):
        own_grant = make_grant("googleapi", test_org)
        make_grant("googleapi", test_org2)
        client.force_login(user_admin)

        response = client.get(reverse("add-googleworkspace", kwargs={"org_id": test_org.pk}))

        assert list(response.context["form"].fields["grant"].queryset) == [own_grant]

    def test_googleworkspace_edit_offers_only_own_grants(
            self, client, user_admin, test_org, test_org2):
        config = make_config("googleworkspace", test_org)
        make_grant("googleapi", test_org2)
        client.force_login(user_admin)

        response = client.get(reverse("edit-googleworkspace", kwargs={"pk": config.pk}))

        assert list(response.context["form"].fields["grant"].queryset) == [config.grant]

    def test_ldap_test_connection_with_other_client_config_is_404(
            self, client, user_admin, test_org2):
        config = make_ldap_config(test_org2)
        client.force_login(user_admin)

        response = client.post(
            reverse("ldap-test"),
            {"ldap_config": config.pk, "connection_protocol": "ldap://",
             "connection_url": "zhentil-keep.example:389", "bind_dn": "cn=fzoul"},
            headers={"HX-Request": "true", "HX-Trigger-Name": "button-auth"})

        assert response.status_code == 404
