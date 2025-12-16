import pytest

from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import Permission

all_scanner_create_urls = [
        reverse_lazy('exchangescanner_add'),
        reverse_lazy('filescanner_add'),
        reverse_lazy('webscanner_add'),
        reverse_lazy('dropboxscanner_add'),
        reverse_lazy('googledrivescanner_add'),
        reverse_lazy('gmailscanner_add'),
        reverse_lazy('msgraphcalendarscanner_add'),
        reverse_lazy('msgraphfilescanner_add'),
        reverse_lazy('msgraphmailscanner_add'),
        reverse_lazy('msgraphteamsfilescanner_add')
    ]


@pytest.mark.django_db
class TestCreateViews:

    @pytest.mark.parametrize("url", all_scanner_create_urls)
    def test_get_create_as_anonymous_user(self, url, client):
        """Anonymous users should be redirected to the login page."""
        response = client.get(url)

        assert response.status_code == 302
        assert response["Location"].startswith(reverse("login"))

    @pytest.mark.parametrize("url", all_scanner_create_urls)
    def test_post_create_as_anonymous_user(self, url, client):
        """Anonymous users should be redirected to the login page."""
        response = client.post(url)

        assert response.status_code == 302
        assert response["Location"].startswith(reverse("login"))

    @pytest.mark.parametrize("url", all_scanner_create_urls)
    def test_get_create_as_regular_user_no_permission(self, url, client, user):
        """A regular non-admin user without permission should not be allowed access."""
        client.force_login(user)

        response = client.get(url)

        assert response.status_code == 403

    @pytest.mark.parametrize("url", all_scanner_create_urls)
    def test_post_create_as_regular_user_no_permission(self, url, client, user):
        """A regular non-admin user without permission should not be allowed access."""
        client.force_login(user)

        response = client.post(url)

        assert response.status_code == 403

    @pytest.mark.parametrize("url", all_scanner_create_urls)
    def test_get_create_as_regular_user_permission(self, url, client, user):
        """A regular non-admin user with permission should not be allowed access."""
        user.user_permissions.add(Permission.objects.get(codename="add_scanner"))

        client.force_login(user)

        response = client.get(url)

        assert response.status_code == 403

    @pytest.mark.parametrize("url", all_scanner_create_urls)
    def test_post_create_as_regular_user_permission(self, url, client, user):
        """A regular non-admin user with permission should not be allowed access."""
        user.user_permissions.add(Permission.objects.get(codename="add_scanner"))

        client.force_login(user)

        response = client.post(url)

        assert response.status_code == 403

    @pytest.mark.parametrize("url", all_scanner_create_urls)
    def test_get_create_as_regular_user_permission_view_client(self, url, client, user, test_org):
        """A regular non-admin user with permission and with the 'view_client' permission should be
        able to create any scanner."""
        user.user_permissions.add(*Permission.objects.filter(codename__in=["add_scanner",
                                                                           "view_client"]))

        client.force_login(user)

        response = client.get(url)

        assert response.status_code == 200

    @pytest.mark.parametrize("url", all_scanner_create_urls)
    def test_post_create_as_regular_user_permission_view_client(self, url, client, user, test_org):
        """A regular non-admin user with permission and with the 'view_client' permission should be
        able to create any scanner."""
        user.user_permissions.add(*Permission.objects.filter(codename__in=["add_scanner",
                                                                           "view_client"]))

        client.force_login(user)

        response = client.post(url)

        assert response.status_code == 200

    @pytest.mark.parametrize("url", all_scanner_create_urls)
    def test_get_create_as_admin_no_permission(self, url, client, user_admin):
        """An admin without permission should not be allowed access."""
        client.force_login(user_admin)

        response = client.get(url)

        assert response.status_code == 403

    @pytest.mark.parametrize("url", all_scanner_create_urls)
    def test_post_create_as_admin_no_permission(self, url, client, user_admin):
        """An admin without permission should not be allowed access."""
        client.force_login(user_admin)

        response = client.post(url)

        assert response.status_code == 403

    @pytest.mark.parametrize("url", all_scanner_create_urls)
    def test_get_create_as_admin_permission(self, url, client, user_admin):
        """An admin with permission should be allowed access."""
        user_admin.user_permissions.add(Permission.objects.get(codename="add_scanner"))

        client.force_login(user_admin)

        response = client.get(url)

        assert response.status_code == 200

    @pytest.mark.parametrize("url", all_scanner_create_urls)
    def test_post_create_as_admin_permission(self, url, client, user_admin):
        """An admin with permission should be allowed access."""
        user_admin.user_permissions.add(Permission.objects.get(codename="add_scanner"))

        client.force_login(user_admin)

        response = client.post(url)

        assert response.status_code == 200

    @pytest.mark.parametrize("url", all_scanner_create_urls)
    def test_get_create_as_superuser(self, url, client, superuser, test_org):
        """A superuser should be able to do whatever they want."""
        client.force_login(superuser)

        response = client.get(url)

        assert response.status_code == 200

    @pytest.mark.parametrize("url", all_scanner_create_urls)
    def test_post_create_as_superuser(self, url, client, superuser, test_org):
        """A superuser should be able to do whatever they want."""
        client.force_login(superuser)

        response = client.post(url)

        assert response.status_code == 200
