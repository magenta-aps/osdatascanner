# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from django.urls import reverse_lazy
from django.conf import settings
from django.utils.translation import gettext
from django.contrib.auth.models import Permission

from ..adminapp.views.scanner_views import RemovedScannersView
from ..adminapp.models.scannerjobs.scanner import Scanner
from ..adminapp.models.scannerjobs.sbsysdb import SBSYSDBScanner
from ..organizations.models import Alias, AliasType


@pytest.mark.django_db
class TestRemovedScannerViews:

    def test_removed_scanners_list_all_hidden(self, rf, superuser, basic_scanner, web_scanner,
                                              hidden_scanner):
        """The scanners included in the removed scanners list should all be hidden."""
        qs = self.get_removed_scanner_list_queryset(rf, superuser)

        assert hidden_scanner in qs
        assert basic_scanner not in qs
        assert web_scanner not in qs

    def test_removed_scanners_list_with_permission(self, client, user_admin, hidden_scanner):
        """Users with the 'view_hidden_scanner'-permission should be allowed to access the
        removed scanners list."""
        user_admin.user_permissions.add(Permission.objects.get(codename="view_hidden_scanner"))

        client.force_login(user_admin)
        response = client.get(reverse_lazy("removed_scanners"))

        assert response.status_code == 200

    def test_removed_scanners_list_without_permission(self, client, user_admin, hidden_scanner):
        """A user without the 'view_hidden_scanner'-permission should not be allowed to access the
        removed scanner list."""
        client.force_login(user_admin)
        response = client.get(reverse_lazy("removed_scanners"))

        assert response.status_code == 403

    def test_recreate_scanner_with_permission(self, client, user_admin, hidden_scanner):
        """Only users with the 'unhide_scanner'-permission should be able to recreate a scanner."""
        user_admin.user_permissions.add(Permission.objects.get(codename="unhide_scanner"))

        client.force_login(user_admin)
        response = client.post(reverse_lazy("recreate_scanner", kwargs={"pk": hidden_scanner.pk}))

        assert response.status_code == 302

        hidden_scanner.refresh_from_db()
        assert not hidden_scanner.hidden

    def test_recreate_scanner_without_permission(self, client, user_admin, hidden_scanner):
        """Users without the 'unhide_scanner'-permission should not be able to recreate a
        scanner."""
        client.force_login(user_admin)
        response = client.post(reverse_lazy("recreate_scanner", kwargs={"pk": hidden_scanner.pk}))

        assert response.status_code == 403

        hidden_scanner.refresh_from_db()
        assert hidden_scanner.hidden

    def test_delete_removed_scanner_with_permission(self, client, user_admin, hidden_scanner):
        """Only users with the 'delete_scanner'-permission should be able to delete removed
        scanners."""
        user_admin.user_permissions.add(Permission.objects.get(codename="delete_scanner"))

        client.force_login(user_admin)
        response = client.post(
            reverse_lazy(
                "delete_removed_scanner",
                kwargs={
                    "pk": hidden_scanner.pk}))

        assert response.status_code == 302

        with pytest.raises(Scanner.DoesNotExist):
            hidden_scanner.refresh_from_db()

    def test_delete_removed_scanner_without_permission(self, client, user_admin, hidden_scanner):
        """Users without the 'delete_scanner'-permission should not be able to delete removed
        scanners."""
        client.force_login(user_admin)
        response = client.post(
            reverse_lazy(
                "delete_removed_scanner",
                kwargs={
                    "pk": hidden_scanner.pk}))

        assert response.status_code == 403

        hidden_scanner.refresh_from_db()
        assert hidden_scanner

    def test_delete_removed_scanner_unhidden(self, client, user_admin, basic_scanner):
        """Scanners with 'hidden=False' should not be reachable by the DeleteRemovedScannerView."""
        user_admin.user_permissions.add(Permission.objects.get(codename="delete_scanner"))

        client.force_login(user_admin)
        response = client.post(
            reverse_lazy(
                "delete_removed_scanner",
                kwargs={
                    "pk": basic_scanner.pk}))

        assert response.status_code == 404

        basic_scanner.refresh_from_db()
        assert basic_scanner

    # Helper method

    def get_removed_scanner_list_queryset(self, rf, user, params=""):
        request = rf.get(reverse_lazy("removed_scanners") + params)
        request.user = user
        view = RemovedScannersView()
        view.setup(request)
        qs = view.get_queryset()
        return qs


@pytest.mark.django_db
class TestRevalidationScannerViews:

    def test_admin_change_revalidation(self, client, user_admin, web_scanner):
        user_admin.user_permissions.add(Permission.objects.get(codename="change_scanner"))
        client.force_login(user_admin)

        web_scanner.validation_status = 1
        web_scanner.save()

        response = client.post(reverse_lazy("webscanner_update", kwargs={"pk": web_scanner.pk}), {
            "name": web_scanner.name,
            "organization": web_scanner.organization.pk,
            "url": web_scanner.url,
            "rule": web_scanner.rule.pk,
            "do_ocr": True  # This is the changed setting
        })

        web_scanner.refresh_from_db()

        # Make sure the post request succeeded
        assert response.status_code == 302

        assert web_scanner.validation_status == 0

    def test_admin_change_no_revalidation(self, client, user_admin, web_scanner):
        user_admin.user_permissions.add(Permission.objects.get(codename="change_scanner"))

        # Users with the "can_validate"-permission should not trigger revalidation
        user_admin.user_permissions.add(Permission.objects.get(codename="can_validate"))

        client.force_login(user_admin)

        web_scanner.validation_status = 1
        web_scanner.save()

        response = client.post(reverse_lazy("webscanner_update", kwargs={"pk": web_scanner.pk}), {
            "name": web_scanner.name,
            "organization": web_scanner.organization.pk,
            "url": web_scanner.url,
            "rule": web_scanner.rule.pk,
            "validation_status": 1,
            "do_ocr": True  # This is the changed setting
        })

        web_scanner.refresh_from_db()

        # Make sure the post request succeeded
        assert response.status_code == 302

        assert web_scanner.validation_status == 1


@pytest.mark.django_db
class TestScannerViewsMethods:

    @pytest.mark.parametrize('enabled_scanners', [
        (False, False, False, False, False, False, False, False, False, False, False),
        (True, False, False, False, False, False, False, False, False, False, False),
        (False, True, False, False, False, False, False, False, False, False, False),
        (False, False, True, False, False, False, False, False, False, False, False),
        (False, False, False, True, False, False, False, False, False, False, False),
        (False, False, False, False, True, False, False, False, False, False, False),
        (False, False, False, False, False, True, False, False, False, False, False),
        (False, False, False, False, False, False, True, False, False, False, False),
        (False, False, False, False, False, False, False, True, False, False, False),
        (False, False, False, False, False, False, False, False, True, False, False),
        (False, False, False, False, False, False, False, False, False, True, False),
        (False, False, False, False, False, False, False, False, False, False, True),
        (False, False, False, False, False, False, False, False, False, False, False),
        (True, True, True, True, True, True, True, True, True, True, True),
    ])
    def test_scanner_tabs_context(self, client, user_admin, enabled_scanners, settings,
                                  monkeypatch):
        # We need to import the scanner models from the view files to mock their methods
        from os2datascanner.projects.admin.adminapp.views.webscanner_views import WebScanner
        from os2datascanner.projects.admin.adminapp.views.filescanner_views import FileScanner
        from os2datascanner.projects.admin.adminapp.views.exchangescanner_views import (
            ExchangeScanner, ExchangeCalendarScanner)
        from os2datascanner.projects.admin.adminapp.views.msgraph_views import (
            MSGraphMailScanner, MSGraphFileScanner, MSGraphCalendarScanner, MSGraphTeamsFileScanner,
            MSGraphSharepointScanner)
        from os2datascanner.projects.admin.adminapp.views.gmailscanner_views import GmailScanner
        from os2datascanner.projects.admin.adminapp.views.googledrivescanner_views import (
            GoogleDriveScanner)

        models = [
            WebScanner, FileScanner, ExchangeScanner, ExchangeCalendarScanner,
            MSGraphMailScanner, MSGraphFileScanner, MSGraphCalendarScanner,
            MSGraphTeamsFileScanner, MSGraphSharepointScanner, GmailScanner, GoogleDriveScanner,
        ]

        for scanner_model, enabled in zip(models, enabled_scanners):
            monkeypatch.setattr(scanner_model, "enabled", lambda enabled=enabled: enabled)

        client.force_login(user_admin)
        response = client.get(reverse_lazy("index"), follow=True)
        if not any(enabled_scanners):
            # None of the scanners are enabled, there should not even be a "scanners_tab" context
            # object
            assert "scanner_tabs" not in response.context
        else:
            scanner_tabs = response.context["scanner_tabs"]

            for scanner_model, enabled in zip(models, enabled_scanners):
                assert (scanner_model in scanner_tabs) == enabled


@pytest.mark.django_db
class TestScannerViewsPossibleContacts:

    def test_only_related_users_as_contacts_create(self, test_org, other_org, client, user_admin,
                                                   alt_admin, superuser, user):
        user_admin.user_permissions.add(Permission.objects.get(codename="add_scanner"))
        client.force_login(user_admin)
        response = client.get(reverse_lazy("webscanner_add"))
        possible_contacts = response.context_data["form"].fields["contacts"].queryset
        assert possible_contacts
        for contact in possible_contacts:
            assert \
                contact.has_perm("view_client") or \
                contact.administrator_for.client == user_admin.administrator_for.client

    def test_only_related_users_as_contacts_create2(self, test_org, other_org, client, user_admin,
                                                    alt_admin, superuser, user):
        alt_admin.user_permissions.add(Permission.objects.get(codename="add_scanner"))
        client.force_login(alt_admin)
        response = client.get(reverse_lazy("webscanner_add"))
        possible_contacts = response.context_data["form"].fields["contacts"].queryset
        assert possible_contacts
        for contact in possible_contacts:
            assert \
                contact.has_perm("view_client") or \
                contact.administrator_for.client == alt_admin.administrator_for.client

    def test_only_related_users_as_contacts_update(self, test_org, other_org, client, user_admin,
                                                   alt_admin, superuser, user, web_scanner):
        user_admin.user_permissions.add(Permission.objects.get(codename="change_scanner"))
        client.force_login(user_admin)
        response = client.get(reverse_lazy("webscanner_update", kwargs={"pk": web_scanner.pk}))
        possible_contacts = response.context_data["form"].fields["contacts"].queryset
        assert possible_contacts
        for contact in possible_contacts:
            assert \
                contact.has_perm("view_client") or \
                contact.administrator_for.client == user_admin.administrator_for.client

    def test_only_related_users_as_contacts_update2(self, test_org, other_org, client, user_admin,
                                                    alt_admin, superuser, user,
                                                    other_web_scanner):
        alt_admin.user_permissions.add(Permission.objects.get(codename="change_scanner"))
        client.force_login(alt_admin)
        response = client.get(reverse_lazy("webscanner_update",
                                           kwargs={"pk": other_web_scanner.pk}))
        possible_contacts = response.context_data["form"].fields["contacts"].queryset
        assert possible_contacts
        for contact in possible_contacts:
            assert \
                contact.has_perm("view_client") or \
                contact.administrator_for.client == alt_admin.administrator_for.client

    def test_only_related_users_as_contacts_update_superuser(
            self, test_org, other_org, client, user_admin, alt_admin, superuser, user,
            other_web_scanner):
        client.force_login(superuser)
        response = client.get(reverse_lazy("webscanner_update",
                                           kwargs={"pk": other_web_scanner.pk}))
        possible_contacts = response.context_data["form"].fields["contacts"].queryset
        org = response.context_data["object"].organization
        assert possible_contacts
        for contact in possible_contacts:
            assert \
                contact.has_perm("view_client") or \
                contact.administrator_for.client == org.client


@pytest.mark.django_db
class TestScannerViewsPossibleRemediators:

    def test_only_related_users_as_remediators_create(self, test_org, other_org, client, user_admin,
                                                      oluf, gertrud, benny, frodo, sam):
        user_admin.user_permissions.add(Permission.objects.get(codename="add_scanner"))
        client.force_login(user_admin)
        response = client.get(reverse_lazy("webscanner_add"))
        possible_rems = response.context_data["form"].fields["remediators"].queryset
        assert possible_rems
        for rem in possible_rems:
            assert rem.organization in user_admin.administrator_for.client.organizations.all()

    def test_only_related_users_as_remediators_create2(self, test_org, other_org, client, alt_admin,
                                                       oluf, gertrud, benny, frodo, sam):
        alt_admin.user_permissions.add(Permission.objects.get(codename="add_scanner"))
        client.force_login(alt_admin)
        response = client.get(reverse_lazy("webscanner_add"))
        possible_rems = response.context_data["form"].fields["remediators"].queryset
        assert possible_rems
        for rem in possible_rems:
            assert rem.organization in alt_admin.administrator_for.client.organizations.all()

    def test_only_related_users_as_remediator_update(self, test_org, other_org, client, user_admin,
                                                     oluf, gertrud, benny, frodo, sam, web_scanner):
        user_admin.user_permissions.add(Permission.objects.get(codename="change_scanner"))
        client.force_login(user_admin)
        response = client.get(reverse_lazy("webscanner_update", kwargs={"pk": web_scanner.pk}))
        possible_rems = response.context_data["form"].fields["remediators"].queryset
        assert possible_rems
        for rem in possible_rems:
            assert rem.organization in user_admin.administrator_for.client.organizations.all()

    def test_only_related_users_as_remediators_update2(self, test_org, other_org, client,
                                                       alt_admin, oluf, gertrud, benny, frodo, sam,
                                                       other_web_scanner):
        alt_admin.user_permissions.add(Permission.objects.get(codename="change_scanner"))
        client.force_login(alt_admin)
        response = client.get(reverse_lazy("webscanner_update",
                                           kwargs={"pk": other_web_scanner.pk}))
        possible_rems = response.context_data["form"].fields["remediators"].queryset
        assert possible_rems
        for rem in possible_rems:
            assert rem.organization in alt_admin.administrator_for.client.organizations.all()

    def test_only_related_users_as_contacts_update_superuser(
            self, test_org, other_org, client, superuser,
            other_web_scanner,
            oluf, gertrud, benny, frodo, sam):
        client.force_login(superuser)
        response = client.get(reverse_lazy("webscanner_update",
                                           kwargs={"pk": other_web_scanner.pk}))
        possible_rems = response.context_data["form"].fields["remediators"].queryset
        org = response.context_data["object"].organization
        assert possible_rems
        for rem in possible_rems:
            assert rem.organization == org


@pytest.mark.django_db
class TestScannerViewsPossibleRules:

    def test_only_organization_rules_possible_create(self, user_admin, org_rule, org2_rule,
                                                     disabled_system_rule, client, test_org):
        user_admin.user_permissions.add(Permission.objects.get(codename="add_scanner"))
        client.force_login(user_admin)
        response = client.get(reverse_lazy("webscanner_add"))
        possible_rules = response.context_data["form"].fields["rule"].queryset
        assert possible_rules
        for rule in possible_rules:
            assert rule.organization == test_org or test_org in rule.organizations.all()

    def test_only_organization_rules_possible_update(self, user_admin, org_rule, org2_rule,
                                                     disabled_system_rule, client, test_org,
                                                     web_scanner):
        user_admin.user_permissions.add(Permission.objects.get(codename="change_scanner"))
        client.force_login(user_admin)
        response = client.get(reverse_lazy("webscanner_update", kwargs={"pk": web_scanner.pk}))
        possible_rules = response.context_data["form"].fields["rule"].queryset
        assert possible_rules
        for rule in possible_rules:
            assert rule.organization == test_org or test_org in rule.organizations.all()


@pytest.mark.django_db
class TestIndexView:

    @pytest.mark.parametrize('enabled_scanners', [
        (False, False, False, False, False, False, False, False, False, False, False),
        (True, False, False, False, False, False, False, False, False, False, False),
        (False, True, False, False, False, False, False, False, False, False, False),
        (False, False, True, False, False, False, False, False, False, False, False),
        (False, False, False, True, False, False, False, False, False, False, False),
        (False, False, False, False, True, False, False, False, False, False, False),
        (False, False, False, False, False, True, False, False, False, False, False),
        (False, False, False, False, False, False, True, False, False, False, False),
        (False, False, False, False, False, False, False, True, False, False, False),
        (False, False, False, False, False, False, False, False, True, False, False),
        (False, False, False, False, False, False, False, False, False, True, False),
        (False, False, False, False, False, False, False, False, False, False, True),
        (False, False, False, False, False, False, False, False, False, False, False),
        (True, True, True, True, True, True, True, True, True, True, True),
    ])
    def test_indexview_redirect(self, enabled_scanners, client, user_admin, settings, monkeypatch):
        # We need to import the scanner models from the view files to mock their methods
        from os2datascanner.projects.admin.adminapp.views.views import (
            WebScanner, FileScanner, ExchangeScanner, ExchangeCalendarScanner,
            MSGraphMailScanner, MSGraphFileScanner, MSGraphCalendarScanner,
            MSGraphTeamsFileScanner, MSGraphSharepointScanner, GmailScanner, GoogleDriveScanner)

        models = [
            WebScanner, FileScanner, ExchangeScanner, ExchangeCalendarScanner,
            MSGraphMailScanner, MSGraphFileScanner, MSGraphCalendarScanner,
            MSGraphTeamsFileScanner, MSGraphSharepointScanner, GmailScanner, GoogleDriveScanner,
        ]

        def first_setting_index(settings):
            for i, setting in enumerate(settings):
                if setting:
                    return i
            else:
                # None of the settings are True :(
                return None

        for scanner_model, enabled in zip(models, enabled_scanners):
            monkeypatch.setattr(scanner_model, "enabled", lambda enabled=enabled: enabled)

        for scanner_model in models:
            print(scanner_model, scanner_model.enabled())

        client.force_login(user_admin)
        response = client.get(reverse_lazy("index"))

        if not any(enabled_scanners):
            # No scanners are enabled -- raise an error!
            assert response.status_code == 404
        else:
            # At least one scanner is enabled. We should be redirected
            assert response.status_code == 302
            response = client.get(reverse_lazy("index"), follow=True)

            expected_model_type = models[first_setting_index(enabled_scanners)].get_type()

            assert response.context["view"].model.get_type() == expected_model_type


@pytest.mark.django_db
class TestSBSYSDBScannerViewsAuth:
    @pytest.mark.parametrize("url_name", ["sbsysscanner_update", "sbsysscanner_copy"])
    def test_anonymous_redirected_to_login(self, client, sbsysdb_scanner, url_name):
        response = client.get(reverse_lazy(url_name, kwargs={"pk": sbsysdb_scanner.pk}))

        assert response.status_code == 302
        assert response.url.startswith(settings.LOGIN_URL)

    def test_anonymous_cannot_update(self, client, sbsysdb_scanner):
        name = sbsysdb_scanner.name
        response = client.post(
            reverse_lazy("sbsysscanner_update", kwargs={"pk": sbsysdb_scanner.pk}),
            {"name": "Tomb of Horrors"})

        assert response.status_code == 302
        assert response.url.startswith(settings.LOGIN_URL)
        sbsysdb_scanner.refresh_from_db()
        assert sbsysdb_scanner.name == name

    def test_anonymous_cannot_create(self, client, test_org, basic_rule):
        response = client.post(
            reverse_lazy("sbsysscanner_add"),
            {"name": "Castle Ravenloft", "organization": test_org.uuid, "rule": basic_rule.pk})

        assert response.status_code == 302
        assert response.url.startswith(settings.LOGIN_URL)
        assert not SBSYSDBScanner.objects.filter(name="Castle Ravenloft").exists()

    def test_anonymous_cannot_copy(self, client, sbsysdb_scanner):
        response = client.post(
            reverse_lazy("sbsysscanner_copy", kwargs={"pk": sbsysdb_scanner.pk}),
            {"name": "Castle Ravenloft", "organization": sbsysdb_scanner.organization.uuid,
             "rule": sbsysdb_scanner.rule.pk})

        assert response.status_code == 302
        assert response.url.startswith(settings.LOGIN_URL)
        assert SBSYSDBScanner.objects.count() == 1

    @pytest.mark.parametrize("url_name", ["sbsysscanner_update", "sbsysscanner_copy"])
    def test_user_without_permission_denied(self, client, user, sbsysdb_scanner, url_name):
        client.force_login(user)
        response = client.get(reverse_lazy(url_name, kwargs={"pk": sbsysdb_scanner.pk}))

        assert response.status_code == 403


@pytest.mark.django_db
class TestScannerDfOrgRestriction:
    @pytest.mark.parametrize("url_name,codename", [
        ("webscanner_update", "change_scanner"),
        ("webscanner_copy", "add_scanner"),
    ])
    def test_admin_cannot_access_other_org_scanner(
            self, client, user_admin, other_web_scanner, url_name, codename):
        user_admin.user_permissions.add(Permission.objects.get(codename=codename))
        client.force_login(user_admin)
        response = client.get(reverse_lazy(url_name, kwargs={"pk": other_web_scanner.pk}))

        assert response.status_code == 404

    def test_admin_cannot_copy_other_org_scanner_by_post(
            self, client, user_admin, test_org, basic_rule, other_web_scanner):
        user_admin.user_permissions.add(Permission.objects.get(codename="add_scanner"))
        client.force_login(user_admin)
        response = client.post(
            reverse_lazy("webscanner_copy", kwargs={"pk": other_web_scanner.pk}),
            {"name": "Barovia", "organization": test_org.uuid, "rule": basic_rule.pk,
             "url": "http://www.example.com/"})

        assert response.status_code == 404
        assert not Scanner.objects.filter(name="Barovia").exists()


@pytest.fixture(params=["web", "sbsys"])
def df_case(request, test_org, basic_rule):
    """A scanner, its URL name prefix and the POST data its form needs to validate."""
    base = {"organization": test_org.uuid, "rule": basic_rule.pk}
    if request.param == "web":
        scanner = request.getfixturevalue("web_scanner")
        extra = {"url": "http://www.example.com/"}
    else:
        scanner = request.getfixturevalue("sbsysdb_scanner")
        extra = {"grant": request.getfixturevalue("smb_grant").pk,
                 "db_server": "sbsys.waterdeep.internal", "db_port": 1433,
                 "db_name": "SbSysNetDrift", "owner_field": AliasType.USER_PRINCIPAL_NAME.value,
                 "scan_scope_mode": "all"}
    return scanner, request.param, base | extra


def _remediator_accounts(scanner):
    return {a.account for a in Alias.objects.filter(
        _alias_type=AliasType.REMEDIATOR.value, _value=str(scanner.pk))}


@pytest.mark.django_db
class TestScannerDfViews:

    def test_create(self, client, user_admin, test_org, oluf, df_case):
        scanner, prefix, data = df_case
        user_admin.user_permissions.add(Permission.objects.get(codename="add_scanner"))
        client.force_login(user_admin)

        response = client.post(
            reverse_lazy(f"{prefix}scanner_add"),
            data | {"name": "Neverwinter", "remediators": [oluf.pk]})

        assert response.status_code == 302
        created = type(scanner).objects.get(name="Neverwinter")
        assert created.organization == test_org
        assert _remediator_accounts(created) == {oluf}

    def test_update(self, client, user_admin, oluf, df_case):
        scanner, prefix, data = df_case
        user_admin.user_permissions.add(Permission.objects.get(codename="change_scanner"))
        client.force_login(user_admin)

        response = client.post(
            reverse_lazy(f"{prefix}scanner_update", kwargs={"pk": scanner.pk}),
            data | {"name": "Baldur's Gate", "remediators": [oluf.pk]})

        assert response.status_code == 302
        scanner.refresh_from_db()
        assert scanner.name == "Baldur's Gate"
        assert type(scanner).objects.count() == 1
        assert _remediator_accounts(scanner) == {oluf}

    def test_copy_initial(self, client, user_admin, oluf, df_case):
        scanner, prefix, _data = df_case
        Alias.objects.create(
            account=oluf, _alias_type=AliasType.REMEDIATOR.value, _value=str(scanner.pk))
        user_admin.user_permissions.add(Permission.objects.get(codename="add_scanner"))
        client.force_login(user_admin)

        response = client.get(reverse_lazy(f"{prefix}scanner_copy", kwargs={"pk": scanner.pk}))

        assert response.status_code == 200
        initial = response.context_data["form"].initial
        assert initial["name"] == f"{scanner.name} {gettext('Copy')}"
        assert initial["validation_status"] == Scanner.INVALID
        assert list(initial["remediators"]) == [oluf]

    def test_copy(self, client, user_admin, oluf, df_case):
        scanner, prefix, data = df_case
        scanner.validation_status = Scanner.VALID
        scanner.save()
        user_admin.user_permissions.add(Permission.objects.get(codename="add_scanner"))
        client.force_login(user_admin)

        response = client.post(
            reverse_lazy(f"{prefix}scanner_copy", kwargs={"pk": scanner.pk}),
            data | {"name": "Icewind Dale", "remediators": [oluf.pk]})

        assert response.status_code == 302
        copy = type(scanner).objects.get(name="Icewind Dale")
        assert copy.pk != scanner.pk
        assert copy.validation_status == Scanner.INVALID
        assert _remediator_accounts(copy) == {oluf}

        original_name = scanner.name
        scanner.refresh_from_db()
        assert scanner.name == original_name
        assert scanner.validation_status == Scanner.VALID
        assert _remediator_accounts(scanner) == set()
