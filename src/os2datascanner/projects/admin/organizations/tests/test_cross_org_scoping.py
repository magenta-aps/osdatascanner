# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from unittest.mock import patch

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse

from os2datascanner.projects.admin.core.models.client import ImportSource
from os2datascanner.projects.admin.import_services.models import Realm
from os2datascanner.projects.admin.organizations.models import (
    Account, Alias, OrganizationalUnit, Position)


def add_perms(user, *codenames):
    user.user_permissions.add(*Permission.objects.filter(codename__in=codenames))


@pytest.fixture
def flaming_fist(test_org2):
    return OrganizationalUnit.objects.create(name="Flaming Fist", organization=test_org2)


@pytest.fixture
def jaheira(test_org2):
    return Account.objects.create(
        username="jaheira", first_name="Jaheira", last_name="Harper",
        organization=test_org2)


@pytest.fixture
def jaheira_alias(jaheira):
    return Alias.objects.create(
        account=jaheira, _alias_type="email", _value="jaheira@harpers.faerun")


@pytest.mark.django_db
class TestOrgUnitManagementScoping:
    def test_cannot_manage_other_client_units_or_accounts(
            self, client, user_admin, test_org, flaming_fist, jaheira):
        add_perms(user_admin, "view_organizationalunit")
        client.force_login(user_admin)
        url = reverse("orgunit-list", kwargs={"org_slug": test_org.slug})

        for data in (
                {"orgunit": flaming_fist.pk, "add-manager": jaheira.uuid},
                {"orgunit": flaming_fist.pk, "add-dpo": jaheira.uuid},
                {"add-uni-dpo": jaheira.uuid}):
            assert client.post(url, data).status_code == 404

        jaheira.refresh_from_db()
        assert not jaheira.is_universal_dpo
        assert not Position.objects.filter(account=jaheira).exists()

    def test_can_manage_own_units(self, client, user_admin, test_org):
        unit = OrganizationalUnit.objects.create(name="City Watch", organization=test_org)
        durnan = Account.objects.create(username="durnan", organization=test_org)
        add_perms(user_admin, "view_organizationalunit")
        client.force_login(user_admin)

        response = client.post(
            reverse("orgunit-list", kwargs={"org_slug": test_org.slug}),
            {"orgunit": unit.pk, "add-manager": durnan.uuid})

        assert response.status_code == 200
        assert Position.managers.filter(account=durnan, unit=unit).exists()


@pytest.mark.django_db
class TestAccountViewScoping:
    def test_account_detail_of_other_client_is_404(
            self, client, user_admin, test_org, jaheira):
        client.force_login(user_admin)
        url = reverse("account", kwargs={"org_slug": test_org.slug, "pk": jaheira.uuid})

        assert client.get(url).status_code == 404
        response = client.post(
            url, {"remediator-check": "on"}, headers={"HX-Trigger-Name": "remediator-check"})
        assert response.status_code == 404
        assert not jaheira.aliases.exists()

    def test_alias_create_for_other_client_account_is_404(
            self, client, user_admin, test_org, jaheira):
        client.force_login(user_admin)
        url = reverse("create-alias", kwargs={
            "org_slug": test_org.slug, "acc_uuid": jaheira.uuid})

        assert client.get(url).status_code == 404
        response = client.post(url, {"alias_type": "email", "value": "khalid@harpers.faerun"})
        assert response.status_code == 404
        assert not jaheira.aliases.exists()

    def test_alias_delete_of_other_client_account_is_404(
            self, client, user_admin, test_org, jaheira, jaheira_alias):
        client.force_login(user_admin)

        for acc_uuid in (jaheira.uuid, Account.objects.create(
                username="durnan", organization=test_org).uuid):
            response = client.post(reverse("delete-alias", kwargs={
                "org_slug": test_org.slug, "acc_uuid": acc_uuid, "pk": jaheira_alias.pk}))
            assert response.status_code == 404

        assert Alias.objects.filter(pk=jaheira_alias.pk).exists()


@pytest.mark.django_db
class TestSSOViewScoping:
    @pytest.fixture(autouse=True)
    def keycloak_enabled(self, settings, test_org2):
        settings.KEYCLOAK_ENABLED = True
        test_org2.client.import_source = ImportSource.LDAP
        test_org2.client.save()

    @patch("os2datascanner.projects.admin.organizations.views.keycloak_sso_views.create_realm")
    def test_anonymous_sso_create_has_no_side_effects(
            self, create_realm, client, test_org2):
        response = client.get(reverse("add-sso", kwargs={"org_id": test_org2.pk}))

        assert response.status_code == 302
        assert "login" in response.url
        assert not Realm.objects.exists()
        create_realm.assert_not_called()

    @pytest.mark.parametrize("url_name", ["add-sso", "edit-sso"])
    @patch("os2datascanner.projects.admin.organizations.views.keycloak_sso_views.create_realm")
    def test_sso_for_other_client_org_is_404(
            self, create_realm, client, user_admin, test_org2, url_name):
        client.force_login(user_admin)

        response = client.get(reverse(url_name, kwargs={"org_id": test_org2.pk}))

        assert response.status_code == 404
        assert not Realm.objects.exists()
        create_realm.assert_not_called()
