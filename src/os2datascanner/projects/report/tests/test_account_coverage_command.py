import pytest
import uuid
from datetime import datetime

from django.core.management import call_command

from .test_utilities import create_reports_for
from ..organizations.models.organization import Organization
from ..reportapp.models.scanner_reference import ScannerReference


@pytest.mark.django_db
class TestAccountCoverageCommand:

    def test_command_scanner_with_org_units(self, enqueued_messages, egon_email_alias,
                                            scan_kun_egon):
        """Results from a scanner with related org units should enqueue some messages"""
        # scan_kun_egon uses org_units
        create_reports_for(egon_email_alias,
                           scanner_job_pk=scan_kun_egon.scanner_pk,
                           scanner_job_name=scan_kun_egon.scanner_name,
                           scan_time=datetime(1996, 3, 20))

        # We don't need to provide an organization, since only one exists in the DB
        call_command("account_coverage")

        assert len(enqueued_messages) == 1
        assert enqueued_messages[0][0] == "os2ds_checkups"
        message = enqueued_messages[0][1]["coverages"]

        assert message[0]["account"] == str(egon_email_alias.account.uuid)
        assert message[0]["time"] == datetime(1996, 3, 20).astimezone(tz=None).isoformat()
        assert message[0]["scanner_id"] == scan_kun_egon.scanner_pk

    def test_command_scanner_with_scan_entire_org(self, enqueued_messages, egon_email_alias,
                                                  scan_olsenbanden_org):
        """Results from a scanner with "scan_entire_org" should enqueue some messages"""
        # scan_olsenbanden_org uses scan_entire_org
        create_reports_for(egon_email_alias,
                           scanner_job_pk=scan_olsenbanden_org.scanner_pk,
                           scanner_job_name=scan_olsenbanden_org.scanner_name,
                           scan_time=datetime(1996, 3, 20))

        # We don't need to provide an organization, since only one exists in the DB
        call_command("account_coverage")

        assert len(enqueued_messages) == 1
        assert enqueued_messages[0][0] == "os2ds_checkups"
        message = enqueued_messages[0][1]["coverages"]

        assert message[0]["account"] == str(egon_email_alias.account.uuid)
        assert message[0]["time"] == datetime(1996, 3, 20).astimezone(tz=None).isoformat()
        assert message[0]["scanner_id"] == scan_olsenbanden_org.scanner_pk

    def test_command_scanner_without_covered_accounts(self, enqueued_messages, egon_sid_alias,
                                                      scan_owned_by_olsenbanden):
        """Results from a scanner without org_units or scan_entire_org does not use CoveredAccounts
        in the admin module, so we don't care about account coverage on those."""
        # scan_owned_by_olsenbanden does not use org_units or scan_entire_org
        create_reports_for(egon_sid_alias,
                           scanner_job_pk=scan_owned_by_olsenbanden.scanner_pk,
                           scanner_job_name=scan_owned_by_olsenbanden.scanner_name)

        # We don't need to provide an organization, since only one exists in the DB
        call_command("account_coverage")

        assert len(enqueued_messages) == 0

    def test_command_remediator_results(self, enqueued_messages, egon_remediator_alias,
                                        scan_olsenbanden_org):
        """Results delegated to a remediator should not be considered for account coverage"""
        create_reports_for(egon_remediator_alias,
                           scanner_job_pk=scan_olsenbanden_org.scanner_pk,
                           scanner_job_name=scan_olsenbanden_org.scanner_name)

        # We don't need to provide an organization, since only one exists in the DB
        call_command("account_coverage")

        assert len(enqueued_messages) == 0

    def test_command_withheld_results(self, enqueued_messages, egon_email_alias,
                                      scan_olsenbanden_org_withheld):
        """Withheld results should enqueue some messages as normal."""
        create_reports_for(egon_email_alias,
                           scanner_job_pk=scan_olsenbanden_org_withheld.scanner_pk,
                           scanner_job_name=scan_olsenbanden_org_withheld.scanner_name,
                           scan_time=datetime(1996, 3, 20))

        # We don't need to provide an organization, since only one exists in the DB
        call_command("account_coverage")

        assert len(enqueued_messages) == 1
        assert enqueued_messages[0][0] == "os2ds_checkups"
        message = enqueued_messages[0][1]["coverages"]

        assert message[0]["account"] == str(egon_email_alias.account.uuid)
        assert message[0]["time"] == datetime(1996, 3, 20).astimezone(tz=None).isoformat()
        assert message[0]["scanner_id"] == scan_olsenbanden_org_withheld.scanner_pk

    def test_command_multiple_organizations_no_argument(self, olsenbanden_organization,
                                                        marvel_organization):
        """Calling the command without an organization argument when multiple are present should
        raise an exception."""
        with pytest.raises(Organization.MultipleObjectsReturned):
            call_command("account_coverage")

    def test_command_multiple_organizations(self, olsenbanden_organization,
                                            marvel_organization, egon_email_alias,
                                            hulk_email_alias, scan_olsenbanden_org,
                                            scan_marvel, enqueued_messages):
        """When multiple organizations are present in the db, calling the command with the
        organization argument should only enqueue information from that organization."""
        create_reports_for(egon_email_alias,
                           scanner_job_pk=scan_olsenbanden_org.scanner_pk,
                           scanner_job_name=scan_olsenbanden_org.scanner_name,
                           scan_time=datetime(1996, 3, 20))
        create_reports_for(hulk_email_alias,
                           scanner_job_pk=scan_marvel.scanner_pk,
                           scanner_job_name=scan_marvel.scanner_name,
                           scan_time=datetime(1996, 3, 20))

        call_command("account_coverage", organization=olsenbanden_organization.uuid)

        assert len(enqueued_messages) == 1
        assert enqueued_messages[0][0] == "os2ds_checkups"

        for message in enqueued_messages[0][1]["coverages"]:
            assert message["account"] == str(egon_email_alias.account.uuid)
            assert message["time"] == datetime(1996, 3, 20).astimezone(tz=None).isoformat()
            assert message["scanner_id"] == scan_olsenbanden_org.scanner_pk

    def test_command_multiple_scanners(self, egon_email_alias, scan_olsenbanden_org, scan_kun_egon,
                                       enqueued_messages):
        """Calling the command with multiple scanners should enqueue a message for each scanner."""
        create_reports_for(egon_email_alias,
                           scanner_job_pk=scan_kun_egon.scanner_pk,
                           scanner_job_name=scan_kun_egon.scanner_name,
                           scan_time=datetime(1996, 3, 20))
        create_reports_for(egon_email_alias,
                           scanner_job_pk=scan_olsenbanden_org.scanner_pk,
                           scanner_job_name=scan_olsenbanden_org.scanner_name,
                           scan_time=datetime(1996, 3, 20))

        # We don't need to provide an organization, since only one exists in the DB
        call_command("account_coverage")

        assert len(enqueued_messages) == 1
        assert enqueued_messages[0][0] == "os2ds_checkups"
        coverages = enqueued_messages[0][1]["coverages"]
        assert len(coverages) == 2

        assert coverages[0] != coverages[1]

        for message in coverages:
            assert message["account"] == str(egon_email_alias.account.uuid)
            assert message["time"] == datetime(1996, 3, 20).astimezone(tz=None).isoformat()
            assert message["scanner_id"] == scan_kun_egon.scanner_pk \
                or scan_olsenbanden_org.scanner_pk

    def test_command_multiple_scanners_with_argument(self, egon_email_alias, scan_olsenbanden_org,
                                                     scan_kun_egon, enqueued_messages):
        """Calling the command with a scanner argument with multiple scanners present should only
        enqueue information related to that scanner."""
        create_reports_for(egon_email_alias,
                           scanner_job_pk=scan_kun_egon.scanner_pk,
                           scanner_job_name=scan_kun_egon.scanner_name,
                           scan_time=datetime(1996, 3, 20))
        create_reports_for(egon_email_alias,
                           scanner_job_pk=scan_olsenbanden_org.scanner_pk,
                           scanner_job_name=scan_olsenbanden_org.scanner_name,
                           scan_time=datetime(1996, 3, 20))

        # We don't need to provide an organization, since only one exists in the DB
        call_command("account_coverage", scanner=scan_olsenbanden_org.scanner_pk)

        assert len(enqueued_messages) == 1
        assert enqueued_messages[0][0] == "os2ds_checkups"
        message = enqueued_messages[0][1]["coverages"]
        assert len(message) == 1

        assert message[0]["account"] == str(egon_email_alias.account.uuid)
        assert message[0]["time"] == datetime(1996, 3, 20).astimezone(tz=None).isoformat()
        assert message[0]["scanner_id"] == scan_olsenbanden_org.scanner_pk

    def test_command_invalid_scanner_argument(self, olsenbanden_organization):
        """Calling the command with the scanner argument with a primary key, for which no
        ScannerReference object exists, an exception should be raised."""
        with pytest.raises(ScannerReference.DoesNotExist):
            call_command("account_coverage", scanner=1337)

    def test_command_invalid_organization_argument(self, olsenbanden_organization):
        """Calling the command with the organization argument with a primary key, for which no
        Organization object exists, an exception should be raised."""
        with pytest.raises(Organization.DoesNotExist):
            call_command("account_coverage", organization=uuid.uuid4())

    def test_command_multiple_timestamps(self, egon_email_alias, scan_olsenbanden_org,
                                         enqueued_messages):
        """When reports from the same scanner for the same account exist with different scan times,
        we should enqueue a message with coverage for both timestamps."""
        time1 = datetime(1996, 3, 20)
        time2 = datetime(2000, 12, 1)
        create_reports_for(egon_email_alias,
                           scanner_job_pk=scan_olsenbanden_org.scanner_pk,
                           scanner_job_name=scan_olsenbanden_org.scanner_name,
                           scan_time=time1)
        create_reports_for(egon_email_alias,
                           scanner_job_pk=scan_olsenbanden_org.scanner_pk,
                           scanner_job_name=scan_olsenbanden_org.scanner_name,
                           scan_time=time2,
                           offset=10)

        # We don't need to provide an organization, since only one exists in the DB
        call_command("account_coverage")

        assert len(enqueued_messages) == 1
        coverages = enqueued_messages[0][1]["coverages"]
        assert len(coverages) == 2

        assert coverages[0] != coverages[1]

        for message, timestamp in zip(coverages, [time1, time2]):
            assert message["account"] == str(egon_email_alias.account.uuid)
            assert message["time"] == timestamp.astimezone(tz=None).isoformat()
            assert message["scanner_id"] == scan_olsenbanden_org.scanner_pk
