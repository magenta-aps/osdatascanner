import pytest

from django.contrib.auth.models import Permission
from django.urls import reverse_lazy


@pytest.mark.django_db
class TestStatusViews:

    @pytest.mark.parametrize("has_perm", [True, False])
    # TODO: Run this test again after fixing #63270
    @pytest.mark.skip("Fails since StatusDelete is based on faulty parent view")
    def test_status_delete_with_permission(self, client, user_admin, has_perm, basic_scanstatus):
        if has_perm:
            user_admin.user_permissions.add(Permission.objects.get(codename="delete_scanstatus"))
        client.force_login(user_admin)
        response = client.post(reverse_lazy("status-delete", kwargs={"pk": basic_scanstatus.pk}))

        if has_perm:
            assert response.status_code == 200
        else:
            assert response.status_code == 403
