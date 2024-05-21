import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from unittest import skip

from os2datascanner.engine2.model.data import unpack_data_url
from os2datascanner.engine2.model.smbc import SMBCSource, SMBCHandle
from os2datascanner.engine2.model.msgraph import (
        mail as graph_mail, files as graph_files)
from os2datascanner.engine2.model.derived import mail
from os2datascanner.projects.admin.organizations.models.account \
    import Account
from os2datascanner.projects.admin.organizations.models.organizational_unit \
    import OrganizationalUnit
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner \
    import Scanner, ScheduledCheckup
from os2datascanner.projects.admin.adminapp.views.webscanner_views \
    import WebScannerUpdate
from ..adminapp.models.scannerjobs.scanner_helpers import CoveredAccount


def get_webscannerupdate_view(user):
    request = RequestFactory().get('/')
    request.user = user
    view = WebScannerUpdate()
    view.setup(request)
    return view


@pytest.mark.django_db
class TestScanners:

    def test_superuser_can_validate_scannerjob(self, superuser):

        view = get_webscannerupdate_view(superuser)
        form_fields = view.get_form_fields()
        assert 'validation_status' in str(form_fields)

    def test_user_cannot_validate_scannerjob(self, user):
        view = get_webscannerupdate_view(user)
        form_fields = view.get_form_fields()
        assert 'validation_status' not in str(form_fields)

    def test_scanner_job_sitemap(self, web_scanner):
        # Arrange...
        sitemap_content = b"<urlset><url>https://example.com</url></urlset>"
        web_scanner.sitemap = SimpleUploadedFile("sitemap.xml", sitemap_content)
        web_scanner.save()
        web_scanner.refresh_from_db()

        # ... act...
        ws = list(web_scanner.generate_sources())[0]
        sitemap = ws._sitemap

        # ... and assert
        assert sitemap is not None
        assert unpack_data_url(ws._sitemap)[1] == sitemap_content

    def test_synchronize_covered_accounts(
            self,
            basic_scanner,
            basic_scanstatus,
            nisserne,
            fritz,
            oluf,
            gertrud):
        """Make sure that synchronizing covered accounts on the Scanner works
        correctly."""
        # Creating some test objects...
        basic_scanner.org_unit.add(nisserne)

        basic_scanner.record_covered_accounts(basic_scanstatus)

        covered_accounts = Account.objects.filter(
                pk__in=CoveredAccount.objects.filter(
                        scanner=basic_scanner).values_list("account_id", flat=True))

        assert covered_accounts.count() == 1
        assert covered_accounts.first() == fritz

    def test_compute_stale_accounts(
            self,
            basic_scanner,
            basic_scanstatus,
            familien_sand,
            bingoklubben,
            oluf,
            gertrud,
            benny):
        """The get_stale_account-method should return all accounts, which are
        in the 'covered_accounts'-field of the scanner, but are not in any
        of the organizational units on the scanner."""

        gertrud.units.add(bingoklubben)
        benny.units.add(familien_sand)

        basic_scanner.org_unit.add(familien_sand, bingoklubben)
        basic_scanner.record_covered_accounts(basic_scanstatus)
        basic_scanner.org_unit.remove(familien_sand)  # Now only Getrud is covered

        stale_accounts = basic_scanner.compute_stale_accounts()

        assert stale_accounts.count() == 2
        assert oluf in stale_accounts and benny in stale_accounts
        assert gertrud not in stale_accounts

    def test_compute_covered_accounts(
            self,
            basic_scanner,
            oluf,
            gertrud,
            benny,
            familien_sand,
            bingoklubben,
            kok_sokker,
            nørre_snede_if):
        """When used with specific organisational units,
        Scanner.compute_covered_accounts() returns each covered account
        precisely once."""
        gertrud.units.add(bingoklubben)
        oluf.units.add(nørre_snede_if)
        benny.units.add(familien_sand, kok_sokker)

        basic_scanner.org_unit.add(familien_sand, bingoklubben, nørre_snede_if, kok_sokker)

        covered_accounts = basic_scanner.compute_covered_accounts()

        assert covered_accounts.count() == 3
        assert all(acc in covered_accounts for acc in (oluf, gertrud, benny))

    def test_compute_all_covered_accounts(
            self,
            test_org,
            basic_scanner,
            nisserne,
            fritz,
            günther,
            hansi):
        """When used on a complete organisation,
        Scanner.compute_covered_accounts() returns each account precisely
        once."""
        # Pretend this Scanner can associate Accounts with Sources
        basic_scanner.generate_sources_with_accounts = "doesn't really"

        everybody = OrganizationalUnit.objects.create(
            name="Everybody", organization=test_org)
        everybody.account_set.add(fritz, günther, hansi)

        covered_accounts = basic_scanner.compute_covered_accounts()

        assert covered_accounts.count() == 3
        assert all(acc in covered_accounts for acc in (fritz, günther, hansi))

    @skip("Accounts are now required, but this test doesn't create one")
    def test_scheduled_checkup_cleanup_bug(
            self,
            msgraph_mailscanner,
            test_org,
            fritz,
            fritz_email_alias,
            nisserne):
        """ScheduledCheckups for Microsoft Graph mails are not erroneously
        deleted during RabbitMQ message preparation."""

        def mock_generate_sources():
            top_source = msgraph_mailscanner._make_base_source()
            yield top_source
            account_handle = graph_mail.MSGraphMailAccountHandle(
                    top_source, fritz.email)
            account_source = graph_mail.MSGraphMailAccountSource(account_handle)
            yield account_source
            mail_handle = graph_mail.MSGraphMailMessageHandle(
                    account_source, "idfieldscancontainanythingiftheyrefake",
                    "Re: Re: Re: You may already have WONE!!!",
                    "gopher://testind.example/cgi-bin/getMail.exe?idfi..fake")
            mail_source = mail.MailSource(mail_handle)
            yield mail_source

        def make_mail_body_handle():
            mail_source = list(mock_generate_sources())[-1]
            mail_body_handle = mail.MailPartHandle(mail_source, "0/", "text/plain")
            return mail_body_handle

        msgraph_mailscanner.generate_sources = mock_generate_sources

        mail_body_handle = make_mail_body_handle()

        sc = ScheduledCheckup.objects.create(
                handle_representation=mail_body_handle.to_json_object(),
                scanner=msgraph_mailscanner)

        sst = msgraph_mailscanner._construct_scan_spec_template(user=None, force=False)
        msgraph_mailscanner._add_checkups(sst, [], force=False)

        assert ScheduledCheckup.objects.count() == 1
        assert ScheduledCheckup.objects.first() == sc

    @pytest.mark.parametrize('true_handle,sources', [
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

        assert true_handle != censored_handle
        assert Scanner._uncensor_handle(
            Scanner._make_remap_dict(sources),
            censored_handle) == (
            True,
            true_handle)
