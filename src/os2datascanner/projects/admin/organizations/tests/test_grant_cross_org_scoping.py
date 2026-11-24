# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import json

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse

from os2datascanner.projects.grants.models import EWSGrant, GoogleApiGrant, GraphGrant, SMBGrant


def add_perms(user, *codenames):
    user.user_permissions.add(*Permission.objects.filter(codename__in=codenames))


def make_grant(grant_type, org):
    match grant_type:
        case "smb":
            return SMBGrant.objects.create(
                organization=org, username="volo", password="guide")
        case "ews":
            return EWSGrant.objects.create(
                organization=org, username="elminster", password="aumar")
        case "msgraph":
            grant = GraphGrant(
                organization=org, app_id="11111111-1111-1111-1111-111111111111",
                tenant_id="22222222-2222-2222-2222-222222222222")
            grant.client_secret = "Mystra's weave"
            grant.save()
            return grant
        case "googleapi":
            grant = GoogleApiGrant.objects.create(organization=org)
            grant.service_account = json.dumps({"client_email": "mordenkainen@greyhawk"})
            grant.save()
            return grant


GRANT_TYPES = ["smb", "ews", "msgraph", "googleapi"]
GRANT_CODENAMES = {
    "smb": "smbgrant",
    "ews": "ewsgrant",
    "msgraph": "graphgrant",
    "googleapi": "googleapigrant",
}
GRANT_CREATE_URLS = {
    "smb": "smbgrant-create",
    "ews": "ewsgrant-create",
    "msgraph": "msgraphgrant-create",
    "googleapi": "googleapigrant-create",
}


@pytest.mark.django_db
class TestGrantListScoping:
    def test_lists_only_own_client_orgs(
            self, client, user_admin, test_org, test_org2):
        make_grant("smb", test_org)
        make_grant("smb", test_org2)
        add_perms(user_admin, "view_smbgrant")
        client.force_login(user_admin)

        response = client.get(reverse("grant-list"))

        assert response.status_code == 200
        assert list(response.context["object_list"]) == [test_org]


@pytest.mark.django_db
class TestGrantViewScoping:
    @pytest.mark.parametrize("grant_type", GRANT_TYPES)
    def test_update_other_client_grant_is_404(
            self, client, user_admin, test_org2, grant_type):
        grant = make_grant(grant_type, test_org2)
        add_perms(user_admin, f"change_{GRANT_CODENAMES[grant_type]}")
        client.force_login(user_admin)
        url = reverse(f"{grant_type}grant-update", kwargs={"pk": grant.pk})

        assert client.get(url).status_code == 404
        assert client.post(url, {}).status_code == 404

    @pytest.mark.parametrize("grant_type", GRANT_TYPES)
    def test_update_own_grant_is_allowed(
            self, client, user_admin, test_org, grant_type):
        grant = make_grant(grant_type, test_org)
        add_perms(user_admin, f"change_{GRANT_CODENAMES[grant_type]}")
        client.force_login(user_admin)

        response = client.get(reverse(f"{grant_type}grant-update", kwargs={"pk": grant.pk}))

        assert response.status_code == 200
        assert list(response.context["form"].fields["organization"].queryset) == [test_org]

    def test_msgraph_fetch_expiry_date_other_client_grant_is_404(
            self, client, user_admin, test_org2):
        grant = make_grant("msgraph", test_org2)
        add_perms(user_admin, "change_graphgrant")
        client.force_login(user_admin)

        response = client.post(
            reverse("msgraphgrant-update", kwargs={"pk": grant.pk}), {},
            headers={"HX-Request": "true", "HX-Trigger-Name": "fetch-expiry-date"})

        assert response.status_code == 404

    @pytest.mark.parametrize("grant_type", GRANT_TYPES)
    def test_create_for_other_client_org_is_404(
            self, client, user_admin, test_org2, grant_type):
        add_perms(user_admin, f"add_{GRANT_CODENAMES[grant_type]}")
        client.force_login(user_admin)
        url = reverse(GRANT_CREATE_URLS[grant_type], kwargs={"org": test_org2.pk})

        assert client.get(url).status_code == 404
        assert client.post(url, {"username": "sarevok", "_password": "bhaal"}).status_code == 404
        assert not test_org2.grant.exists()

    @pytest.mark.parametrize("grant_type", GRANT_TYPES)
    def test_create_for_own_org_is_allowed(
            self, client, user_admin, test_org, grant_type):
        add_perms(user_admin, f"add_{GRANT_CODENAMES[grant_type]}")
        client.force_login(user_admin)

        response = client.get(
            reverse(GRANT_CREATE_URLS[grant_type], kwargs={"org": test_org.pk}))

        assert response.status_code == 200

    def test_msgraph_form_contacts_exclude_other_client_admins(
            self, client, user_admin, test_org, test_org2):
        from django.contrib.auth import get_user_model
        from os2datascanner.projects.admin.core.models import Administrator
        duke = get_user_model().objects.create(username="duke_ravengard")
        Administrator.objects.create(user=duke, client=test_org2.client)
        add_perms(user_admin, "add_graphgrant")
        client.force_login(user_admin)

        response = client.get(reverse("msgraphgrant-create", kwargs={"org": test_org.pk}))

        contacts = response.context["form"].fields["contacts"].queryset
        assert user_admin in contacts
        assert duke not in contacts
