from datetime import datetime
from dateutil.tz import gettz
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.urls.exceptions import Http404

from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner \
    import Scanner
from os2datascanner.projects.admin.adminapp.views.scanner_views import ScannerCleanupStaleAccounts
from os2datascanner.projects.admin.organizations.models import (
    Account, Organization, OrganizationalUnit)
from os2datascanner.projects.admin.core.models import Administrator, Client

from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner_helpers import (
    ScanStatus, CoveredAccount)


class CleanupScannerViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.user = get_user_model().objects.create(username="Fake user")

        self.client = Client.objects.first()

        org = Organization.objects.first()
        self.scanner = Scanner.objects.create(name="Fake scanner", organization=org)
        self.scan_status = ScanStatus.objects.create(
            scan_tag={"time": datetime.now(tz=gettz()).isoformat()},
            scanner=self.scanner
        )

        orgunit = OrganizationalUnit.objects.create(name="Fake Unit", organization=org)

        hansi = Account.objects.create(username="Hansi", organization=org)
        Account.objects.create(username="Fritz", organization=org)
        Account.objects.create(username="Günther", organization=org)

        CoveredAccount.objects.bulk_create(
            [CoveredAccount(account=account,
                            scanner=self.scanner,
                            scan_status=self.scan_status) for
             account in Account.objects.all()]
        )

        hansi.units.add(orgunit)

    def test_cleanup_view_regular_user(self):
        """Only an admin for the organization should be able to initialize a
        cleanup of the scanner. Regular users should be met with a 404 code."""

        self.assertRaises(Http404, self.get_cleanup_view)

    def test_cleanup_view_admin(self):
        """The admin of an organization should be able to initialize a cleanup
        of the scanner."""
        Administrator.objects.create(user=self.user, client=self.client)

        response = self.get_cleanup_view()

        self.assertEqual(response.status_code, 200)

    def test_cleanup_view_superuser(self):
        """A superuser should be able to initialize a cleanup of any scanner."""
        self.user.is_superuser = True

        response = self.get_cleanup_view()

        self.assertEqual(response.status_code, 200)

    def test_cleanup_view_not_logged_in(self):
        """An anonymous user should be redirected to a login page when trying
        to access the view."""
        self.user = AnonymousUser()
        response = self.get_cleanup_view()

        self.assertEqual(response.status_code, 302)

    def get_cleanup_view(self):
        request = self.factory.get('/')
        request.user = self.user
        response = ScannerCleanupStaleAccounts.as_view()(request, pk=self.scanner.pk)
        return response
