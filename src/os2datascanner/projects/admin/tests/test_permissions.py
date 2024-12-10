import pytest
from django.contrib.auth.models import Permission
from django.shortcuts import reverse


@pytest.mark.django_db
class TestUserErrorLogPermissions:

    @pytest.mark.parametrize('has_perm', [True, False])
    def test_view_usererrorlog(
            self,
            client,
            user_admin,
            basic_usererrorlog,
            basic_usererrorlog2,
            has_perm):
        if has_perm:
            user_admin.user_permissions.add(Permission.objects.get(codename="view_usererrorlog"))

        client.force_login(user_admin)
        url = reverse("error-log")
        response = client.get(url)

        if has_perm:
            assert response.status_code == 200
        else:
            assert response.status_code == 403
