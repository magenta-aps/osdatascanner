import pytest

from django.contrib.auth.models import Permission
from django.urls import reverse_lazy


@pytest.mark.django_db
class TestStatusViews:

    @pytest.mark.parametrize("has_perm", [True, False])
    def test_status_delete_with_permission(self, client, user_admin, has_perm, basic_scanstatus):
        if has_perm:
            user_admin.user_permissions.add(Permission.objects.get(codename="delete_scanstatus"))
        client.force_login(user_admin)
        response = client.post(reverse_lazy("status-delete", kwargs={"pk": basic_scanstatus.pk}))

        if has_perm:
            assert response.status_code == 200
        else:
            assert response.status_code == 403

    def test_status_overview_as_superuser(self, client, superuser):
        client.force_login(superuser)
        response = client.get(reverse_lazy("status"))
        assert response.status_code == 200
        # TODO: Check that superuser can see status for multiple clients

    def test_status_overview_as_administrator(self, client, user_admin):
        client.force_login(user_admin)
        response = client.get(reverse_lazy("status"))
        assert response.status_code == 200

    def test_status_timeline_as_superuser(self, client, superuser, basic_scanstatus):
        client.force_login(superuser)
        response = client.get(reverse_lazy("status-timeline", kwargs={"pk": basic_scanstatus.pk}))
        assert response.status_code == 200

    def test_status_timeline_as_administrator(self, client, user_admin, basic_scanstatus):
        client.force_login(user_admin)
        response = client.get(reverse_lazy("status-timeline", kwargs={"pk": basic_scanstatus.pk}))
        assert response.status_code == 200

    def test_status_timeline_as_unprivileged_user(self, client, user, basic_scanstatus):
        client.force_login(user)
        response = client.get(reverse_lazy("status-timeline", kwargs={"pk": basic_scanstatus.pk}))
        assert response.status_code == 404
