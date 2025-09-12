import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import Permission
from unittest import skip
from django.urls import reverse_lazy

from os2datascanner.utils.ref import Counter
from os2datascanner.engine2.model.data import unpack_data_url
from os2datascanner.engine2.model.smbc import SMBCSource, SMBCHandle
from os2datascanner.engine2.model.msgraph import (
        mail as graph_mail, files as graph_files)
from os2datascanner.engine2.model.derived import mail
from os2datascanner.engine2.rules.logical import OrRule
from os2datascanner.engine2.rules.dict_lookup import EmailHeaderRule
from os2datascanner.projects.admin.organizations.models import OrganizationalUnit, Alias, Account
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner \
    import Scanner, ScheduledCheckup
from ..adminapp.models.scannerjobs.scanner_helpers import CoveredAccount


@pytest.mark.django_db
class TestScanners:

    def test_superuser_can_validate_scannerjob(self, superuser, client, web_scanner):
        """Make sure the "validation_status" field is included in the scanner form for superusers"""

        client.force_login(superuser)
        response = client.get(reverse_lazy("webscanner_update", kwargs={"pk": web_scanner.pk}))
        assert 'validation_status' in str(response.context_data["form"].fields)

    def test_user_without_permission_cannot_validate_scannerjob(self, user_admin, client,
                                                                web_scanner):
        """Make sure the "validation_status" field is disabled in the scanner form for admins
        without permission"""

        user_admin.user_permissions.add(Permission.objects.get(codename='change_scanner'))
        client.force_login(user_admin)
        response = client.get(reverse_lazy("webscanner_update", kwargs={"pk": web_scanner.pk}))
        validation_status_field = response.context_data["form"].fields["validation_status"]
        assert validation_status_field.disabled

    def test_user_with_permission_can_validate_scannerjob(self, user_admin, client, web_scanner):
        """Make sure the "validation_status" field is included in the scanner form for admins
        with permission"""

        user_admin.user_permissions.add(*Permission.objects.filter(codename__in=['can_validate',
                                                                                 'change_scanner']))
        client.force_login(user_admin)
        response = client.get(reverse_lazy("webscanner_update", kwargs={"pk": web_scanner.pk}))
        assert 'validation_status' in str(response.context_data["form"].fields)

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
        basic_scanner.org_units.add(nisserne)

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

        basic_scanner.org_units.add(familien_sand, bingoklubben)
        basic_scanner.record_covered_accounts(basic_scanstatus)
        basic_scanner.org_units.remove(familien_sand)  # Now only Getrud is covered

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

        basic_scanner.org_units.add(familien_sand, bingoklubben, nørre_snede_if, kok_sokker)

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
        basic_scanner.scan_entire_org = True
        # Pretend this Scanner can associate Accounts with Sources
        basic_scanner.generate_sources_with_accounts = "doesn't really"

        everybody = OrganizationalUnit.objects.create(
            name="Everybody", organization=test_org)
        everybody.account_set.add(fritz, günther, hansi)

        covered_accounts = basic_scanner.compute_covered_accounts()

        assert covered_accounts.count() == 3
        assert all(acc in covered_accounts for acc in (fritz, günther, hansi))

    def test_compute_no_covered_accounts(
            self,
            test_org,
            basic_scanner,
            nisserne,
            fritz,
            günther,
            hansi):
        """When used on a organisation, with scan_entire_org set to False
        Scanner.compute_covered_accounts() returns no accounts."""
        basic_scanner.scan_entire_org = False
        # Pretend this Scanner can associate Accounts with Sources
        basic_scanner.generate_sources_with_accounts = "doesn't really"

        everybody = OrganizationalUnit.objects.create(
            name="Everybody", organization=test_org)
        everybody.account_set.add(fritz, günther, hansi)

        covered_accounts = basic_scanner.compute_covered_accounts()

        assert not covered_accounts.exists()

    def test_add_checkups_appends_problem_message_when_source_missing(self, msgraph_mailscanner,
                                                                      web_scan_spec):
        """ Tests that a ProblemMessage is appended to outbox and ScheduledCheckup is deleted,
        when a Source is missing. """

        # We're mismatching GraphMail scan with a WebScan scanspec, but that doesn't matter
        # for this test - in a way, it highlights that we're definitely not still covering
        # whatever Source we had a reference to. (and it was easier available when writing this)

        # Arrange
        # Build a valid handle representation
        fake_source = graph_mail.MSGraphMailSource(
                        client_id="4",
                        tenant_id="5",
                        client_secret="6")
        fake_handle = graph_mail.MSGraphMailMessageHandle(
            fake_source,
            "idvaluegoeshere",
            "Re: Yyuo haev won teh priez!",
            "https://example.invalid/mail/idvaluegoeshere")
        handle_repr = fake_handle.to_json_object()

        # Create ScheduledCheckup
        ScheduledCheckup.objects.create(
            handle_representation=handle_repr,
            scanner=msgraph_mailscanner
        )

        # Act
        checkup_counter = Counter()
        outbox = list(
                msgraph_mailscanner._yield_checkups(web_scan_spec, False,
                                                    False, checkup_counter))

        # Assert
        assert int(checkup_counter) == 0
        assert len(outbox) == 1
        problem_msg = outbox[0]
        assert problem_msg.irrelevant is True
        assert not msgraph_mailscanner.checkups.exists()

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
        list(msgraph_mailscanner._yield_checkups(
                sst, force=False, dry_run=False))

        assert ScheduledCheckup.objects.count() == 1
        assert ScheduledCheckup.objects.first() == sc

    def test_msgraph_mailscanner_construct_rule(self, msgraph_mailscanner):
        # Arrange
        basic_rule = msgraph_mailscanner.rule.customrule.make_engine2_rule()
        expected = OrRule(EmailHeaderRule("subject", basic_rule), basic_rule)

        # Act
        rule = msgraph_mailscanner._construct_rule(force=False)

        # Assert
        assert rule == expected

    def test_msgraph_mailscanner_construct_rule_scan_subject_false(self, msgraph_mailscanner):
        # Arrange
        msgraph_mailscanner.scan_subject = False
        basic_rule = msgraph_mailscanner.rule.customrule.make_engine2_rule()

        # Act
        rule = msgraph_mailscanner._construct_rule(force=False)

        # Assert
        assert rule == basic_rule

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

    def test_scanner_hide(self, basic_scanner):
        """Calling the 'hide'-method on a scanner should set the 'hidden'-field to True."""
        basic_scanner.hide()
        basic_scanner.refresh_from_db()
        assert basic_scanner.hidden

    def test_scanner_unhide(self, hidden_scanner):
        """Calling the 'unhide'-method on a scanner should set the 'hidden'-field to False."""
        hidden_scanner.unhide()
        hidden_scanner.refresh_from_db()
        assert not hidden_scanner.hidden

    def test_hidden_scanners_in_queryset(self, basic_scanner, hidden_scanner):
        """Querying for scanners should only return unhidden scanners, except when applying
        'unfiltered' to the manager class."""

        scanners = Scanner.objects.all()
        unfiltered_scanners = Scanner.objects.unfiltered()

        assert scanners.count() == 1
        assert scanners[0] == basic_scanner
        assert unfiltered_scanners.count() == 2
        assert all([basic_scanner in unfiltered_scanners, hidden_scanner in unfiltered_scanners])

    def test_hiding_scanner_cancels_scannerjob(self, basic_scanner, basic_scanstatus):
        basic_scanner.hide()
        basic_scanstatus.refresh_from_db()

        assert basic_scanstatus.cancelled


@pytest.fixture
def accounts_without_emails(oluf, gertrud, benny):
    """Returns three accounts without an email value, but with associated email aliases."""

    # Creating email aliases for all these accounts
    accounts = (oluf, gertrud)
    for acc in accounts:
        assert not acc.email
        Alias.objects.create(
            account=acc,
            _alias_type="email",
            _value=f"{acc.username}@yahoo.com")
    return accounts


@pytest.fixture
def accounts_with_emails(fritz, günther, hansi):
    """Returns three accounts with an email value, but without associated email aliases."""
    accounts = (fritz, günther, hansi)
    for acc in accounts:
        assert acc.email
    return accounts


@pytest.mark.django_db
class TestScannerSourcesWithAccounts:

    def test_exchangescanner_generate_sources_with_accounts(
            self, accounts_without_emails, accounts_with_emails, nisserne, familien_sand,
            exchange_scanner):
        """Make sure the 'generate_sources_with_accounts'-method on the ExchangeScanner-model
        only returns emails from the associated accounts' 'email'-field, not the email-aliases."""

        exchange_scanner.org_units.set((nisserne, familien_sand))

        for acc, _ in exchange_scanner.generate_sources_with_accounts():
            assert acc in accounts_with_emails
            assert acc not in accounts_without_emails

    def test_gmailscanner_generate_sources_with_accounts(
            self, accounts_without_emails, accounts_with_emails, nisserne, familien_sand,
            gmail_scanner):
        """Make sure the 'generate_sources_with_accounts'-method on the GmailScanner-model
        only returns emails from the associated accounts' 'email'-field, not the email-aliases."""
        gmail_scanner.org_units.set((nisserne, familien_sand))

        for acc, _ in gmail_scanner.generate_sources_with_accounts():
            assert acc in accounts_with_emails
            assert acc not in accounts_without_emails

    def test_msgraphmailscanner_generate_sources_with_accounts(
            self, accounts_without_emails, accounts_with_emails, nisserne, familien_sand,
            msgraph_mailscanner):
        """Make sure the 'generate_sources_with_accounts'-method on the MSGraphMailScanner-model
        only returns emails from the associated accounts' 'email'-field, not the email-aliases."""
        msgraph_mailscanner.org_units.set((nisserne, familien_sand))

        for acc, _ in msgraph_mailscanner.generate_sources_with_accounts():
            assert acc in accounts_with_emails
            assert acc not in accounts_without_emails

    def test_msgraphfilescanner_generate_sources_with_accounts(
            self, accounts_without_emails, accounts_with_emails, nisserne, familien_sand,
            msgraph_filescanner):
        """Make sure the 'generate_sources_with_accounts'-method on the MSGraphMailScanner-model
        only returns emails from the associated accounts' 'email'-field, not the email-aliases."""
        msgraph_filescanner.org_units.set((nisserne, familien_sand))

        for acc, _ in msgraph_filescanner.generate_sources_with_accounts():
            assert acc in accounts_with_emails
            assert acc not in accounts_without_emails

    def test_msgraphcalendarscanner_generate_sources_with_accounts(
            self, accounts_without_emails, accounts_with_emails, nisserne, familien_sand,
            msgraph_calendarscanner):
        """Make sure the 'generate_sources_with_accounts'-method on the MSGraphMailScanner-model
        only returns emails from the associated accounts' 'email'-field, not the email-aliases."""
        msgraph_calendarscanner.org_units.set((nisserne, familien_sand))

        for acc, _ in msgraph_calendarscanner.generate_sources_with_accounts():
            assert acc in accounts_with_emails
            assert acc not in accounts_without_emails

    def test_first_run_with_delta_on_is_a_full_scan(self, basic_scanner,
                                                    test_client_with_queue_priority):
        """ The first ever run of a do_last_modified_check enabled scanner, should be
        considered a full scan, as there is no previous run providing any cutoff timestamp. """

        # Arrange through fixtures

        # By default, true, assuring it's the case we're testing on.
        assert basic_scanner.do_last_modified_check

        # Act
        scan_spec = basic_scanner._construct_scan_spec_template(user=None, force=False)

        assert scan_spec.explorer_queue == test_client_with_queue_priority.explorer_full_queue
        assert scan_spec.conversion_queue == test_client_with_queue_priority.conversion_full_queue

    def test_second_run_with_delta_on_is_a_delta_scan(self, basic_scanner,
                                                      test_client_with_queue_priority,
                                                      basic_scanstatus_completed):
        """ A do_last_modified_check enabled scanner with a previous run, should
         respect client queue configuration. I.e. use delta queues. """

        # Arrange through fixtures

        # By default, true, assuring it's the case we're testing on.
        assert basic_scanner.do_last_modified_check

        # Act
        scan_spec = basic_scanner._construct_scan_spec_template(user=None, force=False)

        assert scan_spec.explorer_queue == test_client_with_queue_priority.explorer_delta_queue
        assert scan_spec.conversion_queue == test_client_with_queue_priority.conversion_delta_queue

    def test_force_run_on_delta_scan_is_full(self, basic_scanner,
                                             test_client_with_queue_priority,
                                             basic_scanstatus_completed):
        """ Running a thorough scan (force=True) on a do_last_modified_check enabled scanner with
        a previous run, should result in a full scan. """

        # Arrange through fixtures

        # By default, true, assuring it's the case we're testing on.
        assert basic_scanner.do_last_modified_check

        # Act
        scan_spec = basic_scanner._construct_scan_spec_template(user=None, force=True)

        assert scan_spec.explorer_queue == test_client_with_queue_priority.explorer_full_queue
        assert scan_spec.conversion_queue == test_client_with_queue_priority.conversion_full_queue

    def test_disabled_last_modified_check_is_a_full_scan(self, basic_scanner,
                                                         test_client_with_queue_priority):
        """ A do_last_modified_check disabled scanner with no previous run, should
        be a full scan"""

        # Arrange
        basic_scanner.do_last_modified_check = False
        basic_scanner.save()

        # Act
        scan_spec = basic_scanner._construct_scan_spec_template(user=None, force=False)

        assert scan_spec.explorer_queue == test_client_with_queue_priority.explorer_full_queue
        assert scan_spec.conversion_queue == test_client_with_queue_priority.conversion_full_queue

    def test_disabled_last_modified_check_with_previous_run_is_full(self, basic_scanner,
                                                                    test_client_with_queue_priority,
                                                                    basic_scanstatus_completed):
        """ A do_last_modified_check disabled scanner with a previous run, should
        be a full scan"""

        # Arrange
        basic_scanner.do_last_modified_check = False
        basic_scanner.save()

        # Act
        scan_spec = basic_scanner._construct_scan_spec_template(user=None, force=False)

        assert scan_spec.explorer_queue == test_client_with_queue_priority.explorer_full_queue
        assert scan_spec.conversion_queue == test_client_with_queue_priority.conversion_full_queue
