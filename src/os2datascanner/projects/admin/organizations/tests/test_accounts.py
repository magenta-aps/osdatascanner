from django.test import TestCase

from ...core.models.client import Client
from ..models import OrganizationalUnit, Organization, Account
from ...adminapp.models.scannerjobs.scanner import Scanner


class AccountMethodTests(TestCase):

    def setUp(self):
        # Create new org for the sake of these tests.
        self.client = Client.objects.create(
            name="OS2datascanner Test",
            contact_email="info@magenta-aps.dk",
            contact_phone="+45 3336 9696")

        self.org = Organization.objects.create(
            name="OS2datascanner Test",
            contact_email="info@magenta-aps.dk",
            contact_phone="+45 3336 9696",
            client_id=self.client.uuid,
            slug="os2datascanner-test")

        # Create objects
        self.unit1 = OrganizationalUnit.objects.create(
            name="Unit1", organization=self.org)
        self.unit2 = OrganizationalUnit.objects.create(
            name="Unit2", organization=self.org)
        self.scanner1 = Scanner.objects.create(
            name="Hansi & Günther", organization=self.org)
        self.scanner2 = Scanner.objects.create(
            name="Hansi", organization=self.org)
        self.hansi = Account.objects.create(username="Hansi", organization=self.org)
        self.günther = Account.objects.create(username="Günther", organization=self.org)
        self.fritz = Account.objects.create(username="Fritz", organization=self.org)

        # Assign accounts to a unit
        self.unit1.account_set.add(self.hansi, self.günther)
        self.unit2.account_set.add(self.hansi)

    def tearDown(self):
        # Clean up this mess...
        self.fritz.delete()
        self.günther.delete()
        self.hansi.delete()

        self.scanner2.delete()
        self.scanner1.delete()

        self.unit2.delete()
        self.unit1.delete()

        self.org.delete()
        self.client.delete()

    def test_get_stale_scanners(self):
        """Make sure, that accounts can correctly identify, when they have
        been dropped from a scanner."""

        # Hansi and Günther are both assigned to scanner1. Only Hansi is
        # assigned to scanner2. Both are added to 'covered_accounts' of both
        # scanners. Fritz is not covered in any way.
        self.scanner1.org_unit.add(self.unit1)
        self.scanner2.org_unit.add(self.unit2)
        self.scanner1.covered_accounts.add(self.hansi, self.günther)
        self.scanner2.covered_accounts.add(self.hansi, self.günther)

        # Hansi has not been dropped, and should get an empty queryset here.
        hansi_dropped = self.hansi.get_stale_scanners()
        # Günther has been dropped from scanner2, and should see that here.
        günther_dropped = self.günther.get_stale_scanners()
        # Fritz has not been dropped, and should get an empty queryset here.
        fritz_dropped = self.fritz.get_stale_scanners()

        self.assertFalse(hansi_dropped.exists())
        self.assertFalse(fritz_dropped.exists())
        self.assertTrue(günther_dropped.exists())
        self.assertEqual(günther_dropped.count(), 1)
        self.assertEqual(günther_dropped.first(), self.scanner2)
