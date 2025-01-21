import pytest

from django.urls import reverse_lazy
from django.contrib.auth.models import Permission


@pytest.mark.django_db
class TestUserErrorLogView:
    url = reverse_lazy("error-log")

    @pytest.mark.parametrize('has_perm', [True, False])
    def test_view_access_permission(self, client, user_admin, has_perm):
        if has_perm:
            user_admin.user_permissions.add(
                Permission.objects.get(codename="view_usererrorlog"))

        client.force_login(user_admin)

        response = client.get(self.url)

        if has_perm:
            assert response.status_code == 200
        else:
            assert response.status_code == 403

    @pytest.mark.parametrize('has_perm', [True, False])
    def test_csv_export_permission(self, client, user_admin, has_perm):
        if has_perm:
            user_admin.user_permissions.add(
                Permission.objects.get(codename="export_usererrorlog"))

        client.force_login(user_admin)

        response = client.get(reverse_lazy("export-error-log"))

        if has_perm:
            assert response.status_code == 200
        else:
            assert response.status_code == 403

    def test_user_only_views_own_usererrorlogs(self, client, user_admin,
                                               basic_usererrorlog, basic_usererrorlog2):
        user_admin.user_permissions.add(
            Permission.objects.get(codename="view_usererrorlog"))
        client.force_login(user_admin)

        response = client.get(self.url)

        assert basic_usererrorlog in response.context["object_list"]
        assert basic_usererrorlog2 not in response.context["object_list"]

    @pytest.mark.parametrize('with_viewed', [True, False])
    def test_with_and_without_views_error_logs(self, client, user_admin, with_viewed,
                                               basic_usererrorlog, viewed_usererrorlog):
        user_admin.user_permissions.add(
            Permission.objects.get(codename="view_usererrorlog"))
        client.force_login(user_admin)

        if with_viewed:
            response = client.get(self.url + "?show_seen=on")
        else:
            response = client.get(self.url)

        if with_viewed:
            assert viewed_usererrorlog in response.context["object_list"]
        assert basic_usererrorlog in response.context["object_list"]

    def test_resolved_errors_are_not_shown(self, client, user_admin,
                                           basic_usererrorlog, resolved_usererrorlog):
        user_admin.user_permissions.add(
            Permission.objects.get(codename="view_usererrorlog"))
        client.force_login(user_admin)

        response = client.get(self.url + "?show_seen=on")

        assert basic_usererrorlog in response.context["object_list"]
        assert resolved_usererrorlog not in response.context["object_list"]

    @pytest.mark.parametrize("has_perm", [True, False])
    def test_resolving_errors_permission(self, client, user_admin, has_perm, basic_usererrorlog):
        # Users also needs access to view the error logs:
        user_admin.user_permissions.add(
            Permission.objects.get(codename="view_usererrorlog"))

        if has_perm:
            user_admin.user_permissions.add(
                Permission.objects.get(codename="resolve_usererrorlog"))

        client.force_login(user_admin)

        headers = {
            "HTTP_HX-REQUEST": "true",
            "HTTP_HX-TRIGGER-NAME": "remove_errorlog"
        }

        response = client.post(self.url,
                               data={
                                "pk": basic_usererrorlog.pk
                               },
                               **headers)

        basic_usererrorlog.refresh_from_db()

        if has_perm:
            assert response.status_code == 200
            assert basic_usererrorlog.is_resolved
        else:
            assert response.status_code == 403
            assert not basic_usererrorlog.is_resolved

    @pytest.mark.parametrize("has_perm", [True, False])
    def test_viewing_errors_permission(self, client, user_admin, has_perm, basic_usererrorlog):
        # Users also needs access to view the error logs:
        user_admin.user_permissions.add(
            Permission.objects.get(codename="view_usererrorlog"))

        if has_perm:
            user_admin.user_permissions.add(
                Permission.objects.get(codename="mark_view_usererrorlog"))

        client.force_login(user_admin)

        headers = {
            "HTTP_HX-REQUEST": "true",
            "HTTP_HX-TRIGGER-NAME": "see_errorlog"
        }

        response = client.post(self.url,
                               data={
                                "pk": basic_usererrorlog.pk
                               },
                               **headers)

        basic_usererrorlog.refresh_from_db()

        if has_perm:
            assert response.status_code == 200
            assert not basic_usererrorlog.is_new
        else:
            assert response.status_code == 403
            assert basic_usererrorlog.is_new

    def test_resolve_all_respects_ownership(self, client, user_admin,
                                            basic_usererrorlog, basic_usererrorlog2):
        user_admin.user_permissions.add(
            Permission.objects.get(codename="view_usererrorlog"),
            Permission.objects.get(codename="resolve_usererrorlog"))

        client.force_login(user_admin)

        headers = {
            "HTTP_HX-REQUEST": "true",
            "HTTP_HX-TRIGGER-NAME": "remove_all"
        }

        client.post(self.url, data={}, **headers)

        basic_usererrorlog.refresh_from_db()
        basic_usererrorlog2.refresh_from_db()

        assert basic_usererrorlog.is_resolved
        assert not basic_usererrorlog2.is_resolved

    def test_see_all_respects_ownership(self, client, user_admin,
                                        basic_usererrorlog, basic_usererrorlog2):
        user_admin.user_permissions.add(
            Permission.objects.get(codename="view_usererrorlog"),
            Permission.objects.get(codename="mark_view_usererrorlog"))

        client.force_login(user_admin)

        headers = {
            "HTTP_HX-REQUEST": "true",
            "HTTP_HX-TRIGGER-NAME": "see_all"
        }

        client.post(self.url, data={}, **headers)

        basic_usererrorlog.refresh_from_db()
        basic_usererrorlog2.refresh_from_db()

        assert not basic_usererrorlog.is_new
        assert basic_usererrorlog2.is_new
