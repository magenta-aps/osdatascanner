from django.test import RequestFactory, TestCase
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from os2datascanner.engine2.model.derived import mail
from os2datascanner.engine2.model.msgraph import mail as graph_mail
from os2datascanner.engine2.rules import logical, regex
from os2datascanner.engine2.rules.cpr import CPRRule

from os2datascanner.projects.admin.core.models.client import Client
from os2datascanner.projects.admin.grants.models import GraphGrant
from os2datascanner.projects.admin.adminapp.views.webscanner_views \
    import WebScannerUpdate
from os2datascanner.projects.admin.adminapp.models.rules \
    import CustomRule
from os2datascanner.projects.admin.adminapp.models.sensitivity_level \
    import Sensitivity
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner \
    import Scanner, ScheduledCheckup
from os2datascanner.projects.admin.adminapp.models.scannerjobs.webscanner \
    import WebScanner
from os2datascanner.projects.admin.adminapp.models.scannerjobs.msgraph \
    import MSGraphMailScanner
from os2datascanner.projects.admin.organizations.models.organization \
    import Organization
from os2datascanner.projects.admin.organizations.models.organizational_unit \
    import OrganizationalUnit
from os2datascanner.projects.admin.organizations.models.account \
    import Account


User = get_user_model()


class ScannerTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # create organisations
        client1 = Client.objects.create(name="client1")
        magenta_org = Organization.objects.create(
            name="Magenta",
            uuid="b560361d-2b1f-4174-bb03-55e8b693ad0c",
            slug=slugify("Magenta"),
            client=client1, )

        client2 = Client.objects.create(name="client2")
        theydontwantyouto_org = Organization.objects.create(
            name="IANA (example.com)",
            slug=slugify("IANA (example.com)"),
            uuid="a3575dec-8d92-4266-a8d1-97b7b84817c0",
            client=client2,)

        # create scanners
        magenta_scanner = WebScanner(
            name="Magenta",
            url="http://magenta.dk",
            organization=magenta_org,
            validation_status=WebScanner.VALID,
            download_sitemap=False,
        )
        theydontwantyouto_scanner = WebScanner(
            name="TheyDontWantYouTo",
            url="http://theydontwantyou.to",
            organization=theydontwantyouto_org,
            download_sitemap=False,
        )
        magenta_scanner.save()
        theydontwantyouto_scanner.save()

        # create Rules and rulesets

        reg1 = regex.RegexRule(r'fællesskaber')
        reg2 = regex.RegexRule(r'Ombudsmand')
        reg3 = regex.RegexRule(r'projektnetwerk')

        # Create rule sets
        tr_set1 = CustomRule.objects.create(
            name='MagentaTestRule1',
            description="Test rule 1",
            sensitivity=Sensitivity.OK,
            organization=magenta_org,
            _rule=logical.OrRule.make(
                reg1, reg2, reg3).to_json_object(),
        )

        magenta_scanner.rules.add(tr_set1)
        magenta_scanner.save()

    def setUp(self) -> None:
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='britney',
            email='britney@spears.com',
            password='top_secret'
        )
        self.org = Organization.objects.first()

    def test_superuser_can_validate_scannerjob(self):
        self.user.is_superuser = True
        self.user.save()
        view = self.get_webscannerupdate_view()
        form_fields = view.get_form_fields()
        self.assertIn(
                      'validation_status', str(form_fields),
                      msg="No validation_status field in WebscannerUpdate get_form_fields"
                      )

    def test_user_cannot_validate_scannerjob(self):
        self.user.is_superuser = False
        self.user.save()
        view = self.get_webscannerupdate_view()
        form_fields = view.get_form_fields()
        self.assertNotIn(
            'validation_status', str(form_fields),
            msg="User not superuser but validation_status"
            "field present in WebscannerUpdate get_form_fields"
        )

    def test_synchronize_covered_accounts(self):
        """Make sure that synchronizing covered accounts on the Scanner works
        correctly."""
        # Creating some test objects...
        scanner = Scanner.objects.create(name="Scanner", organization=self.org)
        unit = OrganizationalUnit.objects.create(
            name="Unit", organization=Organization.objects.first())
        hansi = Account.objects.create(username="Hansi", organization=self.org)
        hansi.units.add(unit)
        scanner.org_unit.add(unit)
        Account.objects.create(username="Günther", organization=self.org)
        Account.objects.create(username="Fritz", organization=self.org)

        scanner.sync_covered_accounts()

        self.assertEqual(
            scanner.covered_accounts.count(),
            1,
            f"Found {scanner.covered_accounts.count()} accounts "
            "in covered_accounts-field, but only expected 1.")
        self.assertEqual(
            scanner.covered_accounts.first(),
            hansi,
            "Wrong account found in covered_accounts! Found "
            f"{scanner.covered_accounts.first} but expected {hansi}.")

    def test_get_stale_accounts(self):
        """The get_stale_account-method should return all accounts, which are
        in the 'covered_accounts'-field of the scanner, but are not in any
        of the organizational units on the scanner."""
        # Creating some test objects...
        scanner = Scanner.objects.create(name="Scanner", organization=self.org)
        unit = OrganizationalUnit.objects.create(
            name="Unit", organization=self.org)
        hansi = Account.objects.create(username="Hansi", organization=self.org)
        günther = Account.objects.create(
            username="Günther",
            organization=self.org)
        fritz = Account.objects.create(username="Fritz", organization=self.org)
        hansi.units.add(unit)
        scanner.org_unit.add(unit)
        scanner.covered_accounts.add(hansi, günther, fritz)

        stale_accounts = scanner.get_stale_accounts()

        self.assertEqual(
            stale_accounts.count(),
            2,
            f"Expected 2 stale accounts, but found {stale_accounts.count()}.")
        self.assertIn(
            günther,
            stale_accounts,
            f"Account: {günther} not found in get_stale_accounts as expected.")
        self.assertIn(
            fritz,
            stale_accounts,
            f"Account: {fritz} not found in get_stale_accounts as expected.")

    def test_remove_stale_accounts(self):
        """The 'remove_stale_accounts'-method should remove all accounts from
        the 'covered_accounts'-field, which are no longer associated with the
        scanner through an organizational unit."""
        # Creating some test objects...
        scanner = Scanner.objects.create(name="Scanner", organization=self.org)
        unit = OrganizationalUnit.objects.create(
            name="Unit", organization=self.org)
        hansi = Account.objects.create(username="Hansi", organization=self.org)
        günther = Account.objects.create(
            username="Günther",
            organization=self.org)
        fritz = Account.objects.create(username="Fritz", organization=self.org)
        hansi.units.add(unit)
        scanner.org_unit.add(unit)
        scanner.covered_accounts.add(hansi, günther, fritz)

        scanner.remove_stale_accounts()

        self.assertEqual(scanner.get_stale_accounts().count(), 0,
                         "Found stale accounts, when none should be left after removal.")
        self.assertNotIn(
            günther,
            scanner.covered_accounts.all(),
            f"Account {günther} still present in covered_accounts, when it should be removed.")
        self.assertNotIn(
            fritz,
            scanner.covered_accounts.all(),
            f"Account {fritz} still present in covered_accounts, when it should be removed.")
        self.assertIn(hansi, scanner.covered_accounts.all(),
                      f"Account {hansi} not present in covered_accounts as expected.")

    def get_webscannerupdate_view(self):
        request = self.factory.get('/')
        request.user = self.user
        view = WebScannerUpdate()
        view.setup(request)
        return view

    def test_scheduled_checkup_cleanup_bug(self):
        """ScheduledCheckups for Microsoft Graph mails are not erroneously
        deleted during RabbitMQ message preparation."""
        client = Client.objects.create(name="Test Industries smba")
        org = Organization.objects.create(
                client=client, name="Test Industries smba")
        grant = GraphGrant.objects.create(organization=org)
        scanner = MSGraphMailScanner.objects.create(
                organization=org,
                name="Test Department",
                grant=grant)
        cpr_rule = CustomRule.objects.create(
            name="Test CPR rule",
            description="A rule for testing CPR in admin",
            sensitivity=Sensitivity.CRITICAL,
            organization=org,
            _rule=CPRRule().to_json_object(),
            )
        scanner.rules.add(cpr_rule)

        top_source = list(scanner.generate_sources())[0]
        account_handle = graph_mail.MSGraphMailAccountHandle(
                top_source, "honcho@testind.example")
        account_source = graph_mail.MSGraphMailAccountSource(account_handle)
        mail_handle = graph_mail.MSGraphMailMessageHandle(
                account_source, "idfieldscancontainanythingiftheyrefake",
                "Re: Re: Re: You may already have WONE!!!",
                "gopher://testind.example/cgi-bin/getMail.exe?idfi..fake")
        mail_source = mail.MailSource(mail_handle)
        mail_body_handle = mail.MailPartHandle(mail_source, "0/", "text/plain")

        sc = ScheduledCheckup.objects.create(
                handle_representation=mail_body_handle.to_json_object(),
                scanner=scanner)

        sst = scanner._construct_scan_spec_template(user=None, force=False)
        scanner._add_checkups(sst, [], force=False)

        self.assertEqual(ScheduledCheckup.objects.count(), 1)
        self.assertEqual(ScheduledCheckup.objects.first(), sc)
