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
from ..adminapp.models.scannerjobs.msgraph import MSGraphMailScanner
from ..adminapp.models.scannerjobs.scanner import Scanner
from ..adminapp.views.miniscanner_views import MiniScanner
from ..adminapp.views.scanner_views import ScannerCreate
from ..organizations.models import (
    Account, Alias, AliasType, Organization, OrganizationalUnit)


@pytest.fixture
def admin_client(client, user_admin):
    """A client logged in as user_admin, who may add scanners."""
    user_admin.user_permissions.add(Permission.objects.get(codename="add_scanner"))
    client.force_login(user_admin)
    return client


@pytest.fixture
def sibling_org(test_org):
    """A second organization belonging to the Client of test_org."""
    return Organization.objects.create(name="Neverwinter", client=test_org.client)


@pytest.fixture
def own_org_unit(test_org):
    return OrganizationalUnit.objects.create(name="Harpers", organization=test_org)


@pytest.fixture
def other_tenant_graph_grant(test_org2):
    grant = GraphGrant(organization=test_org2, app_id=uuid4(), tenant_id=uuid4())
    grant.client_secret = "Vecna's secret"
    grant.save()
    return grant


@pytest.fixture
def sibling_org_graph_grant(sibling_org):
    grant = GraphGrant(organization=sibling_org, app_id=uuid4(), tenant_id=uuid4())
    grant.client_secret = "Mordenkainen's secret"
    grant.save()
    return grant


@pytest.fixture
def other_tenant_google_grant(test_org2):
    grant = GoogleApiGrant.objects.create(organization=test_org2)
    grant.service_account = json.dumps({"client_email": "beholder@underdark.example"})
    grant.save()
    return grant


@pytest.fixture
def other_tenant_mailscanner(test_org2, other_tenant_graph_grant, basic_rule):
    return MSGraphMailScanner.objects.create(
        name="Menzoberranzan Mail", organization=test_org2,
        graph_grant=other_tenant_graph_grant, rule=basic_rule)


@pytest.fixture
def own_sharepoint_site(test_org, msgraph_grant):
    return MSGraphSharePointSite.objects.create(
        uuid="candlekeep", name="Candlekeep", organization=test_org,
        graph_grant=msgraph_grant)


@pytest.fixture
def other_tenant_sharepoint_site(test_org2, other_tenant_graph_grant):
    return MSGraphSharePointSite.objects.create(
        uuid="blingdenstone", name="Blingdenstone", organization=test_org2,
        graph_grant=other_tenant_graph_grant)


@pytest.mark.django_db
class TestScannerCopyScoping:

    def test_copy_other_tenant_scanner_404(self, admin_client, other_tenant_mailscanner):
        response = admin_client.get(other_tenant_mailscanner.get_copy_url())

        assert response.status_code == 404

    def test_copy_own_scanner_ok(self, admin_client, msgraph_mailscanner):
        response = admin_client.get(msgraph_mailscanner.get_copy_url())

        assert response.status_code == 200

    @pytest.mark.parametrize("model", [GmailScanner, GoogleDriveScanner])
    def test_copy_grant_choices_own_tenant_only(
            self, admin_client, test_org, basic_rule, google_api_grant,
            other_tenant_google_grant, model):
        scanner = model.objects.create(
            name="Waterdeep Archive", organization=test_org,
            google_api_grant=google_api_grant, rule=basic_rule)

        response = admin_client.get(scanner.get_copy_url())

        assert response.status_code == 200
        grants = response.context["form"].fields["google_api_grant"].queryset
        assert google_api_grant in grants
        assert other_tenant_google_grant not in grants

    @pytest.fixture
    def own_drive_scanner(self, test_org, basic_rule, google_api_grant):
        return GoogleDriveScanner.objects.create(
            name="Candlekeep", organization=test_org,
            google_api_grant=google_api_grant, rule=basic_rule)

    def _post_drive_copy(self, client, scanner, grant):
        return client.post(scanner.get_copy_url(), {
            "name": "Candlekeep Copy",
            "organization": scanner.organization.uuid,
            "rule": scanner.rule.pk,
            "google_api_grant": grant.pk,
            "scan_entire_org": True,
            "validation_status": 0,
        })

    def test_copy_saves_new_scanner(self, admin_client, own_drive_scanner, google_api_grant):
        response = self._post_drive_copy(admin_client, own_drive_scanner, google_api_grant)

        assert response.status_code == 302
        copy = GoogleDriveScanner.objects.get(name="Candlekeep Copy")
        assert copy.pk != own_drive_scanner.pk
        assert copy.google_api_grant == google_api_grant

    def test_copy_rejects_other_tenant_grant(
            self, admin_client, own_drive_scanner, other_tenant_google_grant):
        response = self._post_drive_copy(
            admin_client, own_drive_scanner, other_tenant_google_grant)

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
            self, admin_client, user_admin, other_admin, msgraph_grant, own_org_unit,
            olsen_banden):
        response = admin_client.get(reverse("msgraphmailscanner_add"))

        fields = response.context["form"].fields
        assert own_org_unit in fields["org_units"].queryset
        assert olsen_banden not in fields["org_units"].queryset
        assert user_admin in fields["contacts"].queryset
        assert other_admin not in fields["contacts"].queryset

    def test_sharepoint_site_choices_own_tenant_only(
            self, admin_client, own_sharepoint_site, other_tenant_sharepoint_site):
        response = admin_client.get(reverse("msgraphsharepointscanner_add"))

        sites = response.context["form"].fields["sharepoint_sites"].queryset
        assert own_sharepoint_site in sites
        assert other_tenant_sharepoint_site not in sites


@pytest.mark.django_db
class TestScannerFormOrgValidation:

    def _post_mail_scanner(self, client, org, rule, grant, **data):
        return client.post(reverse("msgraphmailscanner_add"), {
            "name": "Neverwinter Wood",
            "organization": org.uuid,
            "rule": rule.pk,
            "graph_grant": grant.pk,
            "scan_entire_org": True,
            "validation_status": 0,
        } | data)

    def test_org_units_of_other_org_in_client_are_rejected(
            self, admin_client, test_org, sibling_org, basic_rule, msgraph_grant):
        lords_alliance = OrganizationalUnit.objects.create(
            name="Lords' Alliance", organization=sibling_org)

        response = self._post_mail_scanner(
            admin_client, test_org, basic_rule, msgraph_grant, org_units=[lords_alliance.uuid])

        assert response.status_code == 200
        assert response.context["form"].has_error("org_units")
        assert not MSGraphMailScanner.objects.exists()

    def test_org_units_of_selected_org_are_accepted(
            self, admin_client, test_org, own_org_unit, basic_rule, msgraph_grant):
        response = self._post_mail_scanner(
            admin_client, test_org, basic_rule, msgraph_grant, org_units=[own_org_unit.uuid])

        assert response.status_code == 302
        assert list(MSGraphMailScanner.objects.get().org_units.all()) == [own_org_unit]

    def test_system_rules_follow_posted_org(
            self, admin_client, test_org, sibling_org, msgraph_grant):
        sibling_org_rule = Rule.objects.create(
            name="Harpers' Cipher", description="Neverwinter only",
            raw_rule=RegexRule(r"harper").to_json_object())
        sibling_org_rule.organizations.add(sibling_org)

        rejected = self._post_mail_scanner(
            admin_client, test_org, sibling_org_rule, msgraph_grant)
        accepted = self._post_mail_scanner(
            admin_client, sibling_org, sibling_org_rule, msgraph_grant)

        assert rejected.context["form"].has_error("rule")
        assert accepted.status_code == 302
        assert MSGraphMailScanner.objects.get().organization == sibling_org

    def test_contacts_from_other_client_are_rejected(
            self, client, superuser, other_admin, test_org, basic_rule, msgraph_grant):
        client.force_login(superuser)

        response = self._post_mail_scanner(
            client, test_org, basic_rule, msgraph_grant, contacts=[other_admin.pk])

        assert response.status_code == 200
        assert response.context["form"].has_error("contacts")
        assert not MSGraphMailScanner.objects.exists()

    def test_sharepoint_sites_must_match_grant_org(
            self, admin_client, test_org, sibling_org, basic_rule, msgraph_grant,
            sibling_org_graph_grant):
        cragmaw = MSGraphSharePointSite.objects.create(
            uuid="cragmaw", name="Cragmaw Castle", organization=sibling_org,
            graph_grant=sibling_org_graph_grant)

        response = admin_client.post(reverse("msgraphsharepointscanner_add"), {
            "name": "Phandelver",
            "organization": test_org.uuid,
            "rule": basic_rule.pk,
            "graph_grant": msgraph_grant.pk,
            "sharepoint_sites": [cragmaw.pk],
            "scan_drives": True,
        })

        assert response.status_code == 200
        assert response.context["form"].has_error("sharepoint_sites")


@pytest.mark.django_db
class TestRecreateScannerScoping:

    def test_cannot_recreate_other_tenant_scanner(
            self, client, user_admin, test_org2, basic_rule):
        tomb = Scanner.objects.create(
            name="Tomb of Annihilation", organization=test_org2, rule=basic_rule, hidden=True)
        user_admin.user_permissions.add(Permission.objects.get(codename="unhide_scanner"))
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

    def test_org_units_own_tenant_only(self, client, user_admin, own_org_unit, olsen_banden):
        client.force_login(user_admin)
        url = reverse("org-units-listing")

        own = client.get(url, {"organizationId": str(own_org_unit.organization.uuid)}).json()
        other = client.get(url, {"organizationId": str(olsen_banden.organization.uuid)}).json()

        assert [ou["name"] for ou in own] == ["Harpers"]
        assert other == []

    def test_sharepoint_sites_own_tenant_only(
            self, client, user_admin, msgraph_grant, other_tenant_graph_grant,
            own_sharepoint_site, other_tenant_sharepoint_site):
        client.force_login(user_admin)
        url = reverse("sharepoint-listing")

        own = client.get(url, {"grantId": str(msgraph_grant.uuid)}).json()
        other = client.get(url, {"grantId": str(other_tenant_graph_grant.uuid)}).json()

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
            self, client, user_admin, test_org, org2_rule):
        client.force_login(user_admin)

        response = client.post(
            reverse("connect-rule-to-org", kwargs={"pk": org2_rule.pk}),
            {"selected_org": str(test_org.uuid), "table-checkbox": org2_rule.pk})

        assert response.status_code == 404
        assert test_org not in org2_rule.organizations.all()

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

    def test_rules_own_tenant_only(self, user_admin, org_rule, org2_rule, basic_rule):
        context = self._context(user_admin)

        rules = set(context["customrule_list"])
        assert {org_rule, basic_rule} <= rules
        assert org2_rule not in rules

    def test_other_tenant_rule_by_pk_ignored(self, user_admin, org2_rule):
        context = self._context(user_admin, customrulepk=org2_rule.pk)

        assert "custom_rule" not in context

    def test_anonymous_sees_no_org_rules(self, anonymous_user, org_rule, org2_rule):
        context = self._context(anonymous_user)

        assert not context["customrule_list"].filter(organization__isnull=False).exists()


@pytest.mark.django_db
class TestDialogSuccessScoping:

    def test_anonymous_redirected(self, client, msgraph_mailscanner):
        response = client.get(f"/msgraphmailscanners/{msgraph_mailscanner.pk}/created/")

        assert response.status_code == 302
        assert response["Location"].startswith(str(reverse_lazy("login")))

    def test_other_tenant_scanner_404(self, client, user_admin, other_tenant_mailscanner):
        client.force_login(user_admin)

        response = client.get(f"/msgraphmailscanners/{other_tenant_mailscanner.pk}/created/")

        assert response.status_code == 404

    def test_own_scanner_ok(self, client, user_admin, msgraph_mailscanner):
        client.force_login(user_admin)

        response = client.get(f"/msgraphmailscanners/{msgraph_mailscanner.pk}/created/")

        assert response.status_code == 200
