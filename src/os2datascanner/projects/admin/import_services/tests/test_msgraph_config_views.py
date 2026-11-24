# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import uuid

import pytest
from django.urls import reverse

from os2datascanner.projects.grants.models import GraphGrant
from ..models import MSGraphConfiguration


def make_graph_grant(org, secret):
    grant = GraphGrant(organization=org, app_id=uuid.uuid4(), tenant_id=uuid.uuid4())
    grant.client_secret = secret
    grant.save()
    return grant


def add_url(org):
    return reverse("add-msgraph", kwargs={"org_id": org.pk})


@pytest.mark.django_db
class TestMSGraphAddView:
    def test_anonymous_is_redirected_to_login(self, client, test_org):
        response = client.get(add_url(test_org))

        assert response.status_code == 302
        assert reverse("login") in response.url

    def test_without_grant_shows_consent_page(self, client, user_admin, test_org):
        client.force_login(user_admin)

        response = client.get(add_url(test_org))

        assert response.status_code == 200
        assert "grants/grant_start.html" in [t.name for t in response.templates]

    def test_with_grant_shows_form(self, client, user_admin, test_org, msgraph_grant):
        client.force_login(user_admin)

        response = client.get(add_url(test_org))

        assert response.status_code == 200
        assert "import_services/msgraph_edit.html" in [t.name for t in response.templates]

    def test_post_saves_selected_grant(self, client, user_admin, test_org, msgraph_grant):
        make_graph_grant(test_org, "Lord Neverember's ledger")
        # The grant that is not the default (lowest primary key) choice
        chosen = GraphGrant.objects.filter(organization=test_org).order_by("pk").last()
        client.force_login(user_admin)

        response = client.post(add_url(test_org), {"grant": chosen.pk})

        assert response.status_code == 302
        config = MSGraphConfiguration.objects.get(organization=test_org)
        assert config.grant == chosen

    def test_post_rejects_grant_from_other_org(
            self, client, user_admin, test_org, test_org2, msgraph_grant):
        zhentil_keep = make_graph_grant(test_org2, "Manshoon's clone vat")
        client.force_login(user_admin)

        response = client.post(add_url(test_org), {"grant": zhentil_keep.pk})

        assert response.status_code == 200
        assert "grant" in response.context["form"].errors
        assert not MSGraphConfiguration.objects.exists()
