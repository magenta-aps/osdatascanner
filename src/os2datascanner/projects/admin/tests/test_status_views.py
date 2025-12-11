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
            assert response.status_code == 302
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

    def test_status_cancel_without_permission(self, client, user_admin, basic_scanstatus):
        client.force_login(user_admin)
        response = client.post(reverse_lazy("status-cancel", kwargs={"pk": basic_scanstatus.pk}))
        assert response.status_code == 403
        basic_scanstatus.refresh_from_db()
        assert not basic_scanstatus.cancelled

    def test_status_cancel_with_permission(self, client, user_admin, basic_scanstatus):
        user_admin.user_permissions.add(Permission.objects.get(codename="cancel_scanstatus"))
        client.force_login(user_admin)
        response = client.post(reverse_lazy("status-cancel", kwargs={"pk": basic_scanstatus.pk}))
        assert response.status_code == 302
        basic_scanstatus.refresh_from_db()
        assert basic_scanstatus.cancelled

    def test_status_timeline_context_data_format(self, client, superuser, scanstatus_with_process):
        client.force_login(superuser)
        response = client.get(reverse_lazy("status-timeline",
                                           kwargs={"pk": scanstatus_with_process.pk}))

        bytes_data = response.context_data["bytes_data"]
        time_data = response.context_data["time_data"]

        process_stats = scanstatus_with_process.process_stats.all()

        assert len(bytes_data) == len(time_data) == process_stats.count()

        for obj in bytes_data:
            ps = process_stats.get(mime_type=obj["label"])
            assert ps.total_size == obj["count"]

        for obj in time_data:
            ps = process_stats.get(mime_type=obj["label"])
            assert ps.total_time.total_seconds() == obj["count"]
