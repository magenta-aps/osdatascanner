import pytest

from django.contrib.auth.models import Permission
from django.urls import reverse_lazy


@pytest.mark.django_db
class TestGrantViews:

    @pytest.mark.parametrize("url,codename,status", [
        ("ewsgrant-create", "add_ewsgrant", 200),
        ("ewsgrant-create", None, 403),
        ("msgraphgrant-create", "add_graphgrant", 200),
        ("msgraphgrant-create", None, 403),
        ("smbgrant-create", "add_smbgrant", 200),
        ("smbgrant-create", None, 403),
        ("googleapigrant-create", "add_googleapigrant", 200),
        ("googleapigrant-create", None, 403),
    ])
    def test_add_grant_access_permission(self, url, codename, status, user_admin, client, test_org):
        if codename:
            user_admin.user_permissions.add(Permission.objects.get(codename=codename))

        client.force_login(user_admin)
        response = client.get(reverse_lazy(url, kwargs={"org": test_org.uuid}))

        assert response.status_code == status

    @pytest.mark.parametrize("method,permission,code", [
        ("GET", True, 200),
        ("GET", False, 403),
        ("POST", True, 302),
        ("POST", False, 403)
    ])
    def test_change_msgraph_grant_access_permission(self, client, user_admin, msgraph_grant,
                                                    method, permission, code):
        if permission:
            user_admin.user_permissions.add(Permission.objects.get(codename="change_graphgrant"))

        client.force_login(user_admin)
        if method == "GET":
            response = client.get(
                reverse_lazy(
                    "msgraphgrant-update",
                    kwargs={
                        "pk": msgraph_grant.pk}))
        elif method == "POST":
            response = client.post(
                reverse_lazy(
                    "msgraphgrant-update",
                    kwargs={
                        "pk": msgraph_grant.pk}))

        assert response.status_code == code

    @pytest.mark.parametrize("method,permission,code", [
        ("GET", True, 200),
        ("GET", False, 403),
        ("POST", True, 200),
        ("POST", False, 403)
    ])
    def test_change_smb_grant_access_permission(self, client, user_admin, smb_grant,
                                                method, permission, code):
        if permission:
            user_admin.user_permissions.add(Permission.objects.get(codename="change_smbgrant"))

        client.force_login(user_admin)
        if method == "GET":
            response = client.get(reverse_lazy("smbgrant-update", kwargs={"pk": smb_grant.pk}))
        elif method == "POST":
            response = client.post(reverse_lazy("smbgrant-update", kwargs={"pk": smb_grant.pk}))

        assert response.status_code == code

    @pytest.mark.parametrize("method,permission,code", [
        ("GET", True, 200),
        ("GET", False, 403),
        ("POST", True, 200),
        ("POST", False, 403)
    ])
    def test_change_ews_grant_access_permission(self, client, user_admin, exchange_grant,
                                                method, permission, code):
        if permission:
            user_admin.user_permissions.add(Permission.objects.get(codename="change_ewsgrant"))

        client.force_login(user_admin)
        if method == "GET":
            response = client.get(reverse_lazy("ewsgrant-update", kwargs={"pk": exchange_grant.pk}))
        elif method == "POST":
            response = client.post(
                reverse_lazy(
                    "ewsgrant-update",
                    kwargs={
                        "pk": exchange_grant.pk}))

        assert response.status_code == code

    @pytest.mark.parametrize("method,permission,code", [
        ("GET", True, 200),
        ("GET", False, 403),
        ("POST", True, 302),
        ("POST", False, 403)
    ])
    def test_change_googleapi_grant_access_permission(self, client, user_admin, google_api_grant,
                                                      method, permission, code):
        if permission:
            user_admin.user_permissions.add(
                Permission.objects.get(
                    codename="change_googleapigrant"))

        client.force_login(user_admin)
        if method == "GET":
            response = client.get(
                reverse_lazy(
                    "googleapigrant-update",
                    kwargs={
                        "pk": google_api_grant.pk}))
        elif method == "POST":
            response = client.post(
                reverse_lazy(
                    "googleapigrant-update",
                    kwargs={
                        "pk": google_api_grant.pk}))

        assert response.status_code == code
