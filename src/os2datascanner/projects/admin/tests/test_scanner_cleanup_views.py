import pytest

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls.exceptions import Http404

from os2datascanner.projects.admin.adminapp.views.scanner_views import ScannerCleanupStaleAccounts


def get_cleanup_view(user, scanner):
    request = RequestFactory().get('/')
    request.user = user
    response = ScannerCleanupStaleAccounts.as_view()(request, pk=scanner.pk)
    return response


@pytest.mark.django_db
class TestCleanupScannerViews:

    def test_cleanup_view_regular_user(self, user, basic_scanner):
        """Only an admin for the organization should be able to initialize a
        cleanup of the scanner. Regular users should be met with a 404 code."""

        with pytest.raises(Http404):
            get_cleanup_view(user, basic_scanner)

    def test_cleanup_view_admin(self, user_admin, basic_scanner):
        """The admin of an organization should be able to initialize a cleanup
        of the scanner."""
        response = get_cleanup_view(user_admin, basic_scanner)

        assert response.status_code == 200

    def test_cleanup_view_superuser(self, superuser, basic_scanner):
        """A superuser should be able to initialize a cleanup of any scanner."""
        response = get_cleanup_view(superuser, basic_scanner)

        assert response.status_code == 200

    def test_cleanup_view_not_logged_in(self, basic_scanner):
        """An anonymous user should be redirected to a login page when trying
        to access the view."""
        response = get_cleanup_view(AnonymousUser(), basic_scanner)

        assert response.status_code == 302
