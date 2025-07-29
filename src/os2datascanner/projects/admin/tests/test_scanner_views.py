import pytest

from django.urls import reverse_lazy
from django.contrib.auth.models import Permission

from ..adminapp.views.scanner_views import RemovedScannersView
from ..adminapp.models.scannerjobs.scanner import Scanner

from ..adminapp.models.scannerjobs.filescanner import FileScanner
from ..adminapp.models.scannerjobs.webscanner import WebScanner
from ..adminapp.models.scannerjobs.exchangescanner import ExchangeScanner
from ..adminapp.models.scannerjobs.msgraph import (MSGraphCalendarScanner, MSGraphFileScanner,
                                                   MSGraphMailScanner, MSGraphSharepointScanner,
                                                   MSGraphTeamsFileScanner)
from ..adminapp.models.scannerjobs.gmail import GmailScanner
from ..adminapp.models.scannerjobs.googledrivescanner import GoogleDriveScanner
from ..adminapp.models.scannerjobs.sbsysscanner import SbsysScanner


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
        (True, True, True, True, True, True, True, True, True, True, True),

    ])
    def test_scanner_tabs_context(self, client, user_admin, enabled_scanners, settings):
        models = [
            WebScanner, FileScanner, ExchangeScanner, MSGraphMailScanner, MSGraphFileScanner,
            MSGraphCalendarScanner, MSGraphTeamsFileScanner, MSGraphSharepointScanner,
            GmailScanner, GoogleDriveScanner, SbsysScanner
        ]

        (settings.ENABLE_WEBSCAN, settings.ENABLE_FILESCAN, settings.ENABLE_EXCHANGESCAN,
            settings.ENABLE_MSGRAPH_MAILSCAN, settings.ENABLE_MSGRAPH_FILESCAN,
            settings.ENABLE_MSGRAPH_CALENDARSCAN, settings.ENABLE_MSGRAPH_TEAMS_FILESCAN,
            settings.ENABLE_MSGRAPH_SHAREPOINTSCAN, settings.ENABLE_GMAILSCAN,
            settings.ENABLE_GOOGLEDRIVESCAN, settings.ENABLE_SBSYSSCAN) = enabled_scanners

        client.force_login(user_admin)
        response = client.get(reverse_lazy("index"))
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
        possible_contacts = response.context_data["possible_contacts"]
        assert possible_contacts
        for contact in possible_contacts:
            assert contact.is_superuser or \
                contact.has_perm("view_client") or \
                contact.administrator_for.client == user_admin.administrator_for.client

    def test_only_related_users_as_contacts_create2(self, test_org, other_org, client, user_admin,
                                                    alt_admin, superuser, user):
        alt_admin.user_permissions.add(Permission.objects.get(codename="add_scanner"))
        client.force_login(alt_admin)
        response = client.get(reverse_lazy("webscanner_add"))
        possible_contacts = response.context_data["possible_contacts"]
        assert possible_contacts
        for contact in possible_contacts:
            assert contact.is_superuser or \
                contact.has_perm("view_client") or \
                contact.administrator_for.client == alt_admin.administrator_for.client

    def test_only_related_users_as_contacts_update(self, test_org, other_org, client, user_admin,
                                                   alt_admin, superuser, user, web_scanner):
        user_admin.user_permissions.add(Permission.objects.get(codename="change_scanner"))
        client.force_login(user_admin)
        response = client.get(reverse_lazy("webscanner_update", kwargs={"pk": web_scanner.pk}))
        possible_contacts = response.context_data["possible_contacts"]
        assert possible_contacts
        for contact in possible_contacts:
            assert contact.is_superuser or \
                contact.has_perm("view_client") or \
                contact.administrator_for.client == user_admin.administrator_for.client

    def test_only_related_users_as_contacts_update2(self, test_org, other_org, client, user_admin,
                                                    alt_admin, superuser, user,
                                                    other_web_scanner):
        alt_admin.user_permissions.add(Permission.objects.get(codename="change_scanner"))
        client.force_login(alt_admin)
        response = client.get(reverse_lazy("webscanner_update",
                                           kwargs={"pk": other_web_scanner.pk}))
        possible_contacts = response.context_data["possible_contacts"]
        assert possible_contacts
        for contact in possible_contacts:
            assert contact.is_superuser or \
                contact.has_perm("view_client") or \
                contact.administrator_for.client == alt_admin.administrator_for.client

    def test_only_related_users_as_contacts_update_superuser(
            self, test_org, other_org, client, user_admin, alt_admin, superuser, user,
            other_web_scanner):
        client.force_login(superuser)
        response = client.get(reverse_lazy("webscanner_update",
                                           kwargs={"pk": other_web_scanner.pk}))
        possible_contacts = response.context_data["possible_contacts"]
        org = response.context_data["object"].organization
        assert possible_contacts
        for contact in possible_contacts:
            assert contact.is_superuser or \
                contact.has_perm("view_client") or \
                contact.administrator_for.client == org.client


@pytest.mark.django_db
class TestScannerViewsPossibleRemediators:

    def test_only_related_users_as_remediators_create(self, test_org, other_org, client, user_admin,
                                                      oluf, gertrud, benny, frodo, sam):
        user_admin.user_permissions.add(Permission.objects.get(codename="add_scanner"))
        client.force_login(user_admin)
        response = client.get(reverse_lazy("webscanner_add"))
        possible_rems = response.context_data["possible_remediators"]
        assert possible_rems
        for rem in possible_rems:
            assert rem.organization in user_admin.administrator_for.client.organizations.all()

    def test_only_related_users_as_remediators_create2(self, test_org, other_org, client, alt_admin,
                                                       oluf, gertrud, benny, frodo, sam):
        alt_admin.user_permissions.add(Permission.objects.get(codename="add_scanner"))
        client.force_login(alt_admin)
        response = client.get(reverse_lazy("webscanner_add"))
        possible_rems = response.context_data["possible_remediators"]
        assert possible_rems
        for rem in possible_rems:
            assert rem.organization in alt_admin.administrator_for.client.organizations.all()

    def test_only_related_users_as_remediator_update(self, test_org, other_org, client, user_admin,
                                                     oluf, gertrud, benny, frodo, sam, web_scanner):
        user_admin.user_permissions.add(Permission.objects.get(codename="change_scanner"))
        client.force_login(user_admin)
        response = client.get(reverse_lazy("webscanner_update", kwargs={"pk": web_scanner.pk}))
        possible_rems = response.context_data["possible_remediators"]
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
        possible_rems = response.context_data["possible_remediators"]
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
        possible_rems = response.context_data["possible_remediators"]
        org = response.context_data["object"].organization
        assert possible_rems
        for rem in possible_rems:
            assert rem.organization == org
