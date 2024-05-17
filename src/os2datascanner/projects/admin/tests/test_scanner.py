from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from unittest import skip
from parameterized import parameterized

from os2datascanner.utils.system_utilities import time_now
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules import logical, regex
from os2datascanner.engine2.model.data import unpack_data_url
from os2datascanner.engine2.model.smbc import SMBCSource, SMBCHandle
from os2datascanner.engine2.model.msgraph import (
        mail as graph_mail, files as graph_files)
from os2datascanner.engine2.model.derived import mail
from os2datascanner.projects.admin.tests.test_utilities import dummy_rule_dict
from os2datascanner.projects.admin.organizations.models.account \
    import Account
from os2datascanner.projects.admin.organizations.models.organizational_unit \
    import OrganizationalUnit
from os2datascanner.projects.admin.organizations.models.organization \
    import Organization
from os2datascanner.projects.admin.adminapp.models.scannerjobs.msgraph \
    import MSGraphMailScanner
from os2datascanner.projects.admin.adminapp.models.scannerjobs.webscanner \
    import WebScanner
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner \
    import Scanner, ScheduledCheckup
from os2datascanner.projects.admin.adminapp.models.sensitivity_level \
    import Sensitivity
from os2datascanner.projects.admin.adminapp.models.rules \
    import CustomRule
from os2datascanner.projects.admin.adminapp.views.webscanner_views \
    import WebScannerUpdate
from os2datascanner.projects.grants.models import GraphGrant
from os2datascanner.projects.admin.core.models.client import Client
from ..adminapp.models.scannerjobs.scanner_helpers import ScanStatus, CoveredAccount


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
        dummy_rule = CustomRule.objects.create(**dummy_rule_dict)
        magenta_scanner = WebScanner(
            name="Magenta",
            url="http://magenta.dk",
            organization=magenta_org,
            validation_status=WebScanner.VALID,
            download_sitemap=False,
            rule=dummy_rule
        )
        theydontwantyouto_scanner = WebScanner(
            name="TheyDontWantYouTo",
            url="http://theydontwantyou.to",
            organization=theydontwantyouto_org,
            download_sitemap=False,
            rule=dummy_rule
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

        magenta_scanner.rule = tr_set1
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
        self.dummy_rule = CustomRule.objects.get(name=dummy_rule_dict.get("name"))

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

    def test_scanner_job_sitemap(self):
        # Arrange...
        sitemap_content = b"<urlset><url>https://example.com</url></urlset>"
        scanner = WebScanner.objects.get(name="TheyDontWantYouTo")
        scanner.sitemap = SimpleUploadedFile("sitemap.xml", sitemap_content)
        scanner.save()
        scanner.refresh_from_db()

        # ... act...
        ws = list(scanner.generate_sources())[0]
        sitemap = ws._sitemap

        self.assertIsNotNone(
                sitemap,
                "WebScanner did not respect uploaded sitemap file")

        # ... and assert
        self.assertEqual(
                unpack_data_url(ws._sitemap)[1],
                sitemap_content,
                "Uploaded sitemap file content is invalid")

    def test_synchronize_covered_accounts(self):
        """Make sure that synchronizing covered accounts on the Scanner works
        correctly."""
        # Creating some test objects...
        scanner = Scanner.objects.create(
            name="Scanner",
            organization=self.org,
            rule=self.dummy_rule)
        scan_status = ScanStatus.objects.create(
            scan_tag={"time": time_now().isoformat()},
            scanner=scanner)
        unit = OrganizationalUnit.objects.create(
            name="Unit", organization=Organization.objects.first())
        hansi = Account.objects.create(username="Hansi", organization=self.org)
        hansi.units.add(unit)
        scanner.org_unit.add(unit)
        Account.objects.create(username="Günther", organization=self.org)
        Account.objects.create(username="Fritz", organization=self.org)

        scanner.record_covered_accounts(scan_status)

        covered_accounts = Account.objects.filter(
                pk__in=CoveredAccount.objects.filter(
                        scanner=scanner).values_list("account_id", flat=True))

        self.assertEqual(
            covered_accounts.count(),
            1,
            f"Found {covered_accounts.count()} accounts "
            "in covered_accounts-field, but only expected 1.")
        self.assertEqual(
            covered_accounts.first(),
            hansi,
            "Wrong account found in covered_accounts! Found "
            f"{covered_accounts.first()} but expected {hansi}.")

    def test_compute_stale_accounts(self):
        """The get_stale_account-method should return all accounts, which are
        in the 'covered_accounts'-field of the scanner, but are not in any
        of the organizational units on the scanner."""
        # Creating some test objects...
        scanner = Scanner.objects.create(
            name="Scanner",
            organization=self.org,
            rule=self.dummy_rule)
        everybody = OrganizationalUnit.objects.create(
            name="Everybody", organization=self.org)
        somebody = OrganizationalUnit.objects.create(
            name="Somebody", organization=self.org)
        hansi, günther, fritz = (
                Account.objects.create(username=u, organization=self.org)
                for u in ("Hansi", "Günther", "Fritz"))
        for person in (hansi, günther, fritz):
            person.units.add(everybody)
        hansi.units.add(somebody)

        scan_status = ScanStatus.objects.create(
            scan_tag={"time": time_now().isoformat()},
            scanner=scanner)

        scanner.org_unit.add(somebody, everybody)
        scanner.record_covered_accounts(scan_status)
        scanner.org_unit.remove(everybody)  # Now only Hansi is covered

        stale_accounts = scanner.compute_stale_accounts()

        self.assertEqual(
            stale_accounts.count(),
            2,
            f"Expected 2 stale accounts, but found {stale_accounts.count()}.")
        self.assertIn(
            günther,
            stale_accounts,
            f"Account: {günther} not found in compute_stale_accounts as expected.")
        self.assertIn(
            fritz,
            stale_accounts,
            f"Account: {fritz} not found in compute_stale_accounts as expected.")

    def test_compute_covered_accounts(self):
        """When used with specific organisational units,
        Scanner.compute_covered_accounts() returns each covered account
        precisely once."""
        # Creating some test objects...
        scanner = Scanner.objects.create(
            name="Scanner",
            organization=self.org,
            rule=self.dummy_rule)

        one_guy = OrganizationalUnit.objects.create(
            name="A Guy", organization=self.org)
        other_guy = OrganizationalUnit.objects.create(
            name="The Other Guy", organization=self.org)
        guys = OrganizationalUnit.objects.create(
            name="The Guys", organization=self.org)
        team = OrganizationalUnit.objects.create(
            name="The Team", organization=self.org)
        gang = OrganizationalUnit.objects.create(
            name="The Gang", organization=self.org)

        hansi, günther, fritz, karlheinz = (
                Account.objects.create(username=u, organization=self.org)
                for u in ("Hansi", "Günther", "Fritz", "Karlheinz"))

        for person in (hansi, günther, fritz):
            person.units.add(guys)

        hansi.units.add(one_guy)

        for person in (hansi, fritz,):
            person.units.add(team)

        for person in (günther, hansi):
            person.units.add(gang)

        karlheinz.units.add(other_guy)

        scanner.org_unit.add(guys, one_guy, team, gang)

        print(scanner.compute_covered_accounts())
        self.assertCountEqual(
                scanner.compute_covered_accounts(),
                {hansi, günther, fritz},
                "account set mismatch")

    def test_compute_all_covered_accounts(self):
        """When used on a complete organisation,
        Scanner.compute_covered_accounts() returns each account precisely
        once."""
        # Creating some test objects...
        scanner = Scanner.objects.create(
            name="Scanner",
            organization=self.org,
            rule=self.dummy_rule)
        # Pretend this Scanner can associate Accounts with Sources
        scanner.generate_sources_with_accounts = "doesn't really"

        everybody = OrganizationalUnit.objects.create(
            name="Everybody", organization=self.org)
        everybody_as_well = OrganizationalUnit.objects.create(
            name="Everybody as Well!", organization=self.org)

        hansi, günther, fritz, karlheinz = (
                Account.objects.create(username=u, organization=self.org)
                for u in ("Hansi", "Günther", "Fritz", "Karlheinz"))

        for person in (hansi, günther, fritz, karlheinz):
            person.units.add(everybody, everybody_as_well)

        print(scanner.compute_covered_accounts())
        self.assertCountEqual(
                scanner.compute_covered_accounts(),
                {hansi, günther, fritz, karlheinz},
                "account set mismatch")

    def get_webscannerupdate_view(self):
        request = self.factory.get('/')
        request.user = self.user
        view = WebScannerUpdate()
        view.setup(request)
        return view

    @skip("Accounts are now required, but this test doesn't create one")
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
                grant=grant, rule=self.dummy_rule)
        cpr_rule = CustomRule.objects.create(
            name="Test CPR rule",
            description="A rule for testing CPR in admin",
            sensitivity=Sensitivity.CRITICAL,
            organization=org,
            _rule=CPRRule().to_json_object(),
            )
        scanner.rule = cpr_rule

        top_source = scanner._make_base_source()
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
        # FIXME: this /does/ delete the mail, because honcho@testind.example doesn't have an
        # Account
        scanner._add_checkups(sst, [], force=False)

        self.assertEqual(ScheduledCheckup.objects.count(), 1)
        self.assertEqual(ScheduledCheckup.objects.first(), sc)

    @parameterized.expand([
        (
            SMBCHandle(
                    SMBCSource("//SERVER/Share", "svcacct", "SVCPASSWD0"),
                    "path/to/file.txt"),
            [
                SMBCSource("//SERVER/Files", "svcacct", "SVCPASSWD0"),
                SMBCSource("//SERVER/Share", "svcacct", "SVCPASSWD0"),
                SMBCSource("//SERVER/Home", "svcacct", "SVCPASSWD0")
            ],
        ),
        (
            graph_mail.MSGraphMailMessageHandle(
                    graph_mail.MSGraphMailAccountSource._make(
                            graph_mail.MSGraphMailSource(
                                    client_id="4",
                                    tenant_id="5",
                                    client_secret="6"),
                            "jens@tester.invalid"),
                    "idvaluegoeshere",
                    "Re: Yyuo haev won teh priez!",
                    "https://example.invalid/mail/idvaluegoeshere"),
            [
                graph_mail.MSGraphMailSource(
                        client_id="4",
                        tenant_id="5",
                        client_secret="6")
            ],
        ),
        (
            graph_files.MSGraphFileHandle(
                    graph_files.MSGraphDriveSource._make(
                            graph_files.MSGraphFilesSource(
                                    client_id="4",
                                    tenant_id="5",
                                    client_secret="6"),
                            "DRIVEHANDLEISALONGSTRINGWITH"
                            "NOCLEARMEANINGINITSCONTENT",
                            "Jens Testers OneDrive",
                            "jens@tester.invalid"),
                    "Path/To/Document.TXT"),
            [
                graph_files.MSGraphFilesSource(
                        client_id="4",
                        tenant_id="5",
                        client_secret="6")
            ],
        ),
    ])
    def test_uncensoring(self, true_handle, sources):
        censored_handle = true_handle.censor()

        self.assertNotEqual(
                true_handle,
                censored_handle,
                "censoring did not affect equality check; this may confuse"
                " SourceManager into restoring censored credentials!")

        self.assertEqual(
                Scanner._uncensor_handle(
                        Scanner._make_remap_dict(sources),
                        censored_handle),
                (True, true_handle),
                "uncensoring did not restore the original handle")
