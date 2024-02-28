from django.test import TestCase

from parameterized import parameterized

from ...core.models.client import Client
from ...adminapp.models.scannerjobs.scanner_helpers import ScanStatus
from ..models import OrganizationalUnit, Organization, Account
from ...adminapp.models.scannerjobs.scanner import Scanner
from ...adminapp.models.rules import CustomRule
from ...tests.test_utilities import dummy_rule_dict
from os2datascanner.utils.system_utilities import time_now


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

        # Create dummy rule for the sake of the tests
        self.rule = CustomRule.objects.create(**dummy_rule_dict)

        # Create objects
        self.unit1 = OrganizationalUnit.objects.create(
            name="Unit1", organization=self.org)
        self.unit2 = OrganizationalUnit.objects.create(
            name="Unit2", organization=self.org)
        self.scanner1 = Scanner.objects.create(
            name="Hansi & Günther", organization=self.org, rule=self.rule)
        self.scanner2 = Scanner.objects.create(
            name="Hansi", organization=self.org, rule=self.rule)
        self.hansi = Account.objects.create(username="Hansi", organization=self.org)
        self.günther = Account.objects.create(username="Günther", organization=self.org)
        self.fritz = Account.objects.create(username="Fritz", organization=self.org)
        # Avoid having an identical timestamps
        self.status1 = ScanStatus.objects.create(
            scan_tag={"time": time_now().replace(hour=11).isoformat()},
            scanner=self.scanner1
        )
        self.status2 = ScanStatus.objects.create(
            scan_tag={"time": time_now().replace(hour=12).isoformat()},
            scanner=self.scanner2
        )

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

        self.rule.delete()

    @parameterized.expand([
        (Account(username="superman", first_name="Clark", last_name="Kent"), "CK"),
        (Account(username="robin", first_name="Robin"), "R"),
        (Account(username="batman", last_name="Wayne"), "W"),
        (Account(username="wonder_woman"), None)
    ])
    def test_initials(self, account, expected_initials):
        """The 'initials'-method should return the first letter from the first
        and the last name. If the account only has a first name, only one
        letter should be returned. If the account has no names, None should be
        returned."""

        self.assertEqual(account.initials, expected_initials)
