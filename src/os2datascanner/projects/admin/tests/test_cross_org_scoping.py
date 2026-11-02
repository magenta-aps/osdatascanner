# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import json
from uuid import uuid4

import pytest
from django.contrib.auth.models import Permission
from django.test import RequestFactory
from django.urls import reverse, reverse_lazy

from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.projects.admin import settings as admin_settings
from os2datascanner.projects.grants.models import GoogleApiGrant, GraphGrant

from ..adminapp.models.MSGraphSharePointSite import MSGraphSharePointSite
from ..adminapp.models.rules import Rule
from ..adminapp.models.scannerjobs.analysisscanner import AnalysisJob
from ..adminapp.models.scannerjobs.gmail import GmailScanner
from ..adminapp.models.scannerjobs.googledrivescanner import GoogleDriveScanner
from ..adminapp.models.scannerjobs.scanner import Scanner
from ..adminapp.views.miniscanner_views import MiniScanner
from ..adminapp.views.scanner_views import ScannerCreate
from ..organizations.models import Account, Alias, AliasType, OrganizationalUnit


def _grant_perm(user, *codenames):
    for codename in codenames:
        user.user_permissions.add(Permission.objects.get(codename=codename))


def _make_google_grant(org):
    grant = GoogleApiGrant.objects.create(organization=org)
    grant.service_account = json.dumps({"client_email": f"beholder@{org.name}.example"})
    grant.save()
    return grant


@pytest.fixture
def underdark_grant(test_org2):
    return _make_google_grant(test_org2)


@pytest.fixture
def underdark_gmail_scanner(test_org2, underdark_grant, basic_rule):
    return GmailScanner.objects.create(
        name="Menzoberranzan Mail", organization=test_org2,
        google_api_grant=underdark_grant, rule=basic_rule)


@pytest.fixture
def underdark_rule(test_org2):
    return Rule.objects.create(
        name="Lolth's Web", description="Spider queen", organization=test_org2,
        raw_rule=RegexRule(r"drow").to_json_object())


@pytest.fixture
def harpers(test_org):
    return OrganizationalUnit.objects.create(name="Harpers", organization=test_org)


@pytest.fixture
def bregan_daerthe(test_org2):
    return OrganizationalUnit.objects.create(name="Bregan D'aerthe", organization=test_org2)


@pytest.mark.django_db
class TestScannerCopyScoping:

    def test_copy_other_tenant_scanner_404(self, client, user_admin, underdark_gmail_scanner):
        _grant_perm(user_admin, "add_scanner")
        client.force_login(user_admin)

        response = client.get(
            reverse("gmailscanner_copy", kwargs={"pk": underdark_gmail_scanner.pk}))

        assert response.status_code == 404

    @pytest.mark.parametrize("model,url_name", [
        (GmailScanner, "gmailscanner_copy"),
        (GoogleDriveScanner, "googledrivescanner_copy"),
    ])
    def test_copy_grant_choices_own_tenant_only(
            self, client, user_admin, test_org, basic_rule, google_api_grant, underdark_grant,
            model, url_name):
        scanner = model.objects.create(
            name="Waterdeep Archive", organization=test_org,
            google_api_grant=google_api_grant, rule=basic_rule)
        _grant_perm(user_admin, "add_scanner")
        client.force_login(user_admin)

        response = client.get(reverse(url_name, kwargs={"pk": scanner.pk}))

        assert response.status_code == 200
        grants = response.context["form"].fields["google_api_grant"].queryset
        assert google_api_grant in grants
        assert underdark_grant not in grants

    def _post_drive_copy(self, client, scanner, grant):
        return client.post(reverse("googledrivescanner_copy", kwargs={"pk": scanner.pk}), {
            "name": "Candlekeep Copy",
            "organization": scanner.organization.uuid,
            "rule": scanner.rule.pk,
            "google_api_grant": grant.pk,
            "scan_entire_org": True,
            "validation_status": 0,
        })

    @pytest.fixture
    def candlekeep_scanner(self, test_org, basic_rule, google_api_grant):
        return GoogleDriveScanner.objects.create(
            name="Candlekeep", organization=test_org,
            google_api_grant=google_api_grant, rule=basic_rule)

    def test_copy_saves_new_scanner(
            self, client, user_admin, candlekeep_scanner, google_api_grant):
        _grant_perm(user_admin, "add_scanner")
        client.force_login(user_admin)

        response = self._post_drive_copy(client, candlekeep_scanner, google_api_grant)

        assert response.status_code == 302
        copy = GoogleDriveScanner.objects.get(name="Candlekeep Copy")
        assert copy.pk != candlekeep_scanner.pk
        assert copy.google_api_grant == google_api_grant

    def test_copy_rejects_other_tenant_grant(
            self, client, user_admin, candlekeep_scanner, underdark_grant):
        _grant_perm(user_admin, "add_scanner")
        client.force_login(user_admin)

        response = self._post_drive_copy(client, candlekeep_scanner, underdark_grant)

        assert response.status_code == 200
        assert response.context["form"].has_error("google_api_grant")
        assert not GoogleDriveScanner.objects.filter(name="Candlekeep Copy").exists()


@pytest.mark.django_db
class TestScannerFormScoping:

    def test_remediator_aliases_ignore_other_tenant_accounts(
            self, basic_scanner, test_org, test_org2):
        drizzt = Account.objects.create(username="drizzt", organization=test_org)
        jarlaxle = Account.objects.create(username="jarlaxle", organization=test_org2)
        view = ScannerCreate()
        view.object = basic_scanner
        request = RequestFactory().post(
            "/", {"remediators": [str(drizzt.uuid), str(jarlaxle.uuid)]})

        view.create_remediator_aliases(request)

        remediators = Alias.objects.filter(
            _alias_type=AliasType.REMEDIATOR, _value=basic_scanner.pk)
        assert {a.account for a in remediators} == {drizzt}

    def test_create_form_querysets_own_tenant_only(
            self, client, user_admin, other_admin, google_api_grant, harpers, bregan_daerthe):
        _grant_perm(user_admin, "add_scanner")
        client.force_login(user_admin)

        response = client.get(reverse("googledrivescanner_add"))

        fields = response.context["form"].fields
        assert harpers in fields["org_units"].queryset
        assert bregan_daerthe not in fields["org_units"].queryset
        assert user_admin in fields["contacts"].queryset
        assert other_admin not in fields["contacts"].queryset

    def test_sharepoint_site_choices_own_tenant_only(
            self, client, user_admin, test_org, test_org2, msgraph_grant):
        candlekeep = MSGraphSharePointSite.objects.create(
            uuid="candlekeep", name="Candlekeep", organization=test_org)
        blingdenstone = MSGraphSharePointSite.objects.create(
            uuid="blingdenstone", name="Blingdenstone", organization=test_org2)
        _grant_perm(user_admin, "add_scanner")
        client.force_login(user_admin)

        response = client.get(reverse("msgraphsharepointscanner_add"))

        sites = response.context["form"].fields["sharepoint_sites"].queryset
        assert candlekeep in sites
        assert blingdenstone not in sites


@pytest.mark.django_db
class TestRecreateScannerScoping:

    def test_cannot_recreate_other_tenant_scanner(
            self, client, user_admin, test_org2, basic_rule):
        tomb = Scanner.objects.create(
            name="Tomb of Annihilation", organization=test_org2, rule=basic_rule, hidden=True)
        _grant_perm(user_admin, "unhide_scanner")
        client.force_login(user_admin)

        response = client.post(reverse("recreate_scanner", kwargs={"pk": tomb.pk}))

        assert response.status_code == 404
        tomb.refresh_from_db()
        assert tomb.hidden


@pytest.mark.django_db
class TestListingScoping:

    @pytest.mark.parametrize("url_name", ["org-units-listing", "sharepoint-listing"])
    def test_anonymous_denied(self, client, url_name):
        response = client.get(reverse(url_name))

        assert response.status_code == 403

    def test_org_units_own_tenant_only(self, client, user_admin, harpers, bregan_daerthe):
        client.force_login(user_admin)
        url = reverse("org-units-listing")

        own = client.get(url, {"organizationId": str(harpers.organization.uuid)}).json()
        other = client.get(url, {"organizationId": str(bregan_daerthe.organization.uuid)}).json()

        assert [ou["name"] for ou in own] == ["Harpers"]
        assert other == []

    def test_sharepoint_sites_own_tenant_only(
            self, client, user_admin, test_org, test_org2, msgraph_grant):
        underdark_graph = GraphGrant.objects.create(
            organization=test_org2, app_id=uuid4(), tenant_id=uuid4(),
            _client_secret=msgraph_grant._client_secret)
        MSGraphSharePointSite.objects.create(
            uuid="candlekeep", name="Candlekeep", organization=test_org,
            graph_grant=msgraph_grant)
        MSGraphSharePointSite.objects.create(
            uuid="blingdenstone", name="Blingdenstone", organization=test_org2,
            graph_grant=underdark_graph)
        client.force_login(user_admin)
        url = reverse("sharepoint-listing")

        own = client.get(url, {"grantId": str(msgraph_grant.uuid)}).json()
        other = client.get(url, {"grantId": str(underdark_graph.uuid)}).json()

        assert [s["name"] for s in own] == ["Candlekeep"]
        assert other == []


@pytest.mark.django_db
class TestAnalysisJobRunScoping:

    def test_cannot_run_other_tenant_analysis(self, client, user_admin, basic_scanner2):
        client.force_login(user_admin)

        response = client.post(
            reverse("run-analysis-job", kwargs={"pk": basic_scanner2.pk}),
            HTTP_REFERER="/analysis/overview/")

        assert response.status_code == 404
        assert not AnalysisJob.objects.filter(scanner=basic_scanner2).exists()

    def test_can_run_own_analysis(self, client, user_admin, basic_scanner):
        client.force_login(user_admin)

        response = client.post(
            reverse("run-analysis-job", kwargs={"pk": basic_scanner.pk}),
            HTTP_REFERER="/analysis/overview/")

        assert response.status_code == 302
        assert AnalysisJob.objects.filter(scanner=basic_scanner).exists()


@pytest.mark.django_db
class TestCustomRuleConnectScoping:

    def test_cannot_connect_other_tenant_rule(
            self, client, user_admin, test_org, underdark_rule):
        client.force_login(user_admin)

        response = client.post(
            reverse("connect-rule-to-org", kwargs={"pk": underdark_rule.pk}),
            {"selected_org": str(test_org.uuid), "table-checkbox": underdark_rule.pk})

        assert response.status_code == 404
        assert test_org not in underdark_rule.organizations.all()

    def test_can_connect_system_rule(self, client, user_admin, test_org, disabled_system_rule):
        client.force_login(user_admin)

        response = client.post(
            reverse("connect-rule-to-org", kwargs={"pk": disabled_system_rule.pk}),
            {"selected_org": str(test_org.uuid), "table-checkbox": disabled_system_rule.pk})

        assert response.status_code == 200
        assert test_org in disabled_system_rule.organizations.all()


@pytest.mark.django_db
class TestMiniScannerScoping:

    @pytest.fixture(autouse=True)
    def no_login_required(self, monkeypatch):
        monkeypatch.setattr(admin_settings, "MINISCAN_REQUIRES_LOGIN", False)

    def _context(self, user, **params):
        request = RequestFactory().get("/miniscan/", params)
        request.user = user
        return MiniScanner.as_view()(request).context_data

    def test_rules_own_tenant_only(self, user_admin, org_rule, underdark_rule, basic_rule):
        context = self._context(user_admin)

        rules = set(context["customrule_list"])
        assert {org_rule, basic_rule} <= rules
        assert underdark_rule not in rules

    def test_other_tenant_rule_by_pk_ignored(self, user_admin, underdark_rule):
        context = self._context(user_admin, customrulepk=underdark_rule.pk)

        assert "custom_rule" not in context

    def test_anonymous_sees_no_org_rules(self, anonymous_user, org_rule, underdark_rule):
        context = self._context(anonymous_user)

        assert not context["customrule_list"].filter(organization__isnull=False).exists()


@pytest.mark.django_db
class TestDialogSuccessScoping:

    def test_anonymous_redirected(self, client, gmail_scanner):
        response = client.get(f"/gmailscanners/{gmail_scanner.pk}/created/")

        assert response.status_code == 302
        assert response["Location"].startswith(str(reverse_lazy("login")))

    def test_other_tenant_scanner_404(self, client, user_admin, underdark_gmail_scanner):
        client.force_login(user_admin)

        response = client.get(f"/gmailscanners/{underdark_gmail_scanner.pk}/created/")

        assert response.status_code == 404

    def test_own_scanner_ok(self, client, user_admin, gmail_scanner):
        client.force_login(user_admin)

        response = client.get(f"/gmailscanners/{gmail_scanner.pk}/created/")

        assert response.status_code == 200
