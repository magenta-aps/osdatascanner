import pytest

from django.urls import reverse_lazy
from django.contrib.auth.models import Permission


@pytest.mark.django_db
class TestUserDetailView:

    @pytest.fixture
    def user_admin_url(self, user_admin):
        return reverse_lazy("user", kwargs={"pk": user_admin.pk})

    def test_myuser_view_redirect(self, client, user_admin, user_admin_url):
        client.force_login(user_admin)
        response = client.get(reverse_lazy("my-user"))
        assert response.status_code == 302
        assert response["Location"] == user_admin_url

    def test_user_detail_access(self, client, user_admin, user_admin_url):
        client.force_login(user_admin)
        response = client.get(user_admin_url)
        assert response.status_code == 200

    def test_user_detail_other_user(self, client, other_admin, user_admin_url):
        client.force_login(other_admin)
        response = client.get(user_admin_url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestUserUpdateView:

    @pytest.fixture
    def user_admin_url(self, user_admin):
        return reverse_lazy("user-edit", kwargs={"pk": user_admin.pk})

    def test_user_update_access(self, client, user_admin, user_admin_url):
        user_admin.user_permissions.add(Permission.objects.get(codename="change_user"))
        client.force_login(user_admin)
        response = client.get(user_admin_url)
        assert response.status_code == 200

    def test_user_update_other_user(self, client, other_admin, user_admin_url):
        other_admin.user_permissions.add(Permission.objects.get(codename="change_user"))
        client.force_login(other_admin)
        response = client.get(user_admin_url)
        assert response.status_code == 404

    def test_user_update_no_permission(self, client, user_admin, user_admin_url):
        client.force_login(user_admin)
        response = client.get(user_admin_url)
        assert response.status_code == 403

    def test_user_update_post_permission(self, client, user_admin, user_admin_url):
        user_admin.user_permissions.add(Permission.objects.get(codename="change_user"))
        client.force_login(user_admin)
        response = client.post(user_admin_url, {"first_name": "Mike",
                                                "last_name": "Wazowski",
                                                "email": "mike@monsters.inc"})
        assert response.status_code == 302
        assert response["Location"] == reverse_lazy("user", kwargs={"pk": user_admin.pk})

        user_admin.refresh_from_db()
        assert user_admin.first_name == "Mike"
        assert user_admin.last_name == "Wazowski"
        assert user_admin.email == "mike@monsters.inc"

    def test_user_update_post_no_permission(self, client, user_admin, user_admin_url):
        client.force_login(user_admin)
        response = client.post(user_admin_url, {"first_name": "Mike",
                                                "last_name": "Wazowski",
                                                "email": "mike@monsters.inc"})
        assert response.status_code == 403
