import pytest

from django.urls import reverse_lazy
from django.contrib.auth.models import Permission

from ..adminapp.views.scanner_views import RemovedScannersView
from ..adminapp.models.scannerjobs.scanner import Scanner


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
