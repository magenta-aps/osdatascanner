from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.core.management.base import CommandError

from ..core.models.client import Client
from ..adminapp.models.scannerjobs.scanner import Scanner, ScanStatus
from ..organizations.models import Account, Organization


class CleanAccountResultsTests(TestCase):

    def setUp(self):
        self.client = Client.objects.create(
            name="OS2datascanner",
            contact_email="info@magenta-aps.dk",
            contact_phone="+45 3336 9696")

        self.org = Organization.objects.create(
            name="OS2datascanner",
            contact_email="info@magenta-aps.dk",
            contact_phone="+45 3336 9696",
            client_id=self.client.uuid,
            slug="os2datascanner")

    def tearDown(self):
        self.org.delete()
        self.client.delete()

    def call_command(self, *args, **kwargs):
        err = StringIO()
        call_command(
            "cleanup_account_results",
            *args,
            stdout=StringIO(),
            stderr=err,
            **kwargs
        )

        return err.getvalue()

    def test_invalid_account(self):
        """Calling the command with an invalid username should raise a
        CommandError."""

        scanner = Scanner.objects.create(name="SomeScanner")

        self.assertRaises(
            CommandError,
            lambda: self.call_command(
                accounts=["invalidAccount"],
                scanners=[
                    scanner.pk]))

    def test_invalid_scanner(self):
        """Calling the command with an invalid scanner pk should raise a
        CommandError."""

        account = Account.objects.create(
            username="Bøffen",
            organization=self.org)

        self.assertRaises(
            CommandError,
            lambda: self.call_command(
                accounts=[
                    account.username],
                scanners=[100]))

    def test_running_scanner(self):
        """Calling the command specifying a running scanner should write
        something to stderr."""
        account = Account.objects.create(
            username="Bøffen",
            organization=self.org)
        scanner = Scanner.objects.create(
            name="SomeScanner",
            organization=self.org)
        ScanStatus.objects.create(scanner=scanner,
                                  scan_tag=scanner._construct_scan_tag().to_json_object())

        self.assertRaises(CommandError, lambda: self.call_command(
                accounts=[
                    account.username], scanners=[
                    scanner.pk]))
