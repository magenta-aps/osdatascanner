import pytest

from django.contrib.auth.models import AnonymousUser

from ..reportapp.views.report_views import UserReportView


@pytest.mark.django_db
class TestLoginRequired:

    def test_index_anonymous_user(self, rf):
        # Tries to hit path "/" with no login
        request = rf.get('/')
        request.user = AnonymousUser()
        response = UserReportView.as_view()(request)
        assert response.status_code == 302

    def test_index_as_user(self, rf, egon_account):
        # Tries to hit path "/" as user
        request = rf.get('/')
        user = egon_account.user
        request.user = user
        response = UserReportView.as_view()(request)

        # Should get status code 200 OK and index.html template
        assert response.status_code == 200
        assert "index.html" in response.template_name
