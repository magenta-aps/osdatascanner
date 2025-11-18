import pytest
import uuid

from datetime import datetime

from ..adminapp.management.commands.checkup_collector import recreate_account_coverage
from ..adminapp.models.scannerjobs.scanner_helpers import CoveredAccount


# TODO: Add tests for "normal" checkup messages

@pytest.fixture
def coverage_message_single_scanner(fritz, basic_scanner, basic_scanstatus):
    return [
        {
            "account": str(fritz.uuid),
            "scanner_id": basic_scanner.pk,
            "time": basic_scanstatus.start_time.isoformat()
        }
    ]


@pytest.fixture
def coverage_message_multiple_scanners(fritz, web_scanner, web_scanstatus,
                                       coverage_message_single_scanner):
    return [
        coverage_message_single_scanner[0],
        {
            "account": str(fritz.uuid),
            "scanner_id": web_scanner.pk,
            "time": web_scanstatus.start_time.isoformat()
        }
    ]


@pytest.fixture
def coverage_message_multiple_timestamps(fritz, basic_scanstatus_old, basic_scanner,
                                         coverage_message_single_scanner):
    return [
        coverage_message_single_scanner[0],
        {
            "account": str(fritz.uuid),
            "scanner_id": basic_scanner.pk,
            "time": basic_scanstatus_old.start_time.isoformat()
        }
    ]


@pytest.fixture
def coverage_message_multiple_accounts(coverage_message_single_scanner, hansi, basic_scanner,
                                       basic_scanstatus):
    return [
        coverage_message_single_scanner[0],
        {
            "account": str(hansi.uuid),
            "scanner_id": basic_scanner.pk,
            "time": basic_scanstatus.start_time.isoformat()
        }
    ]


@pytest.fixture
def coverage_message_invalid_timestamp(coverage_message_single_scanner, fritz, basic_scanner):
    return [
        # The invalid object should be first
        {
            "account": str(fritz.uuid),
            "scanner_id": basic_scanner.pk,
            "time": datetime(2000, 12, 24).astimezone(tz=None).isoformat()
        },
        coverage_message_single_scanner[0]
    ]


@pytest.fixture
def coverage_message_invalid_scanner(coverage_message_single_scanner, fritz, basic_scanstatus):
    return [
        # The invalid object should be first
        {
            "account": str(fritz.uuid),
            "scanner_id": 69420,
            "time": basic_scanstatus.start_time.isoformat()
        },
        coverage_message_single_scanner[0]
    ]


@pytest.fixture
def coverage_message_invalid_account(coverage_message_single_scanner, basic_scanner,
                                     basic_scanstatus):
    return [
        # The invalid object should be first
        {
            "account": uuid.uuid4(),
            "scanner_id": basic_scanner.pk,
            "time": basic_scanstatus.start_time.isoformat()
        },
        coverage_message_single_scanner[0]
    ]


@pytest.fixture
def coverage_message_organization_mismatch(coverage_message_single_scanner, basic_scanner,
                                           basic_scanstatus, frodo):
    return [
        # The invalid object should be first
        {
            "account": str(frodo.uuid),
            "scanner_id": basic_scanner.pk,
            "time": basic_scanstatus.start_time.isoformat()
        },
        coverage_message_single_scanner[0]
    ]


@pytest.mark.django_db
class TestRecreateCoveredAccounts:

    def test_received_messages_create_covered_accounts(self, coverage_message_single_scanner):
        """Receiving a message with an existing account, scanner and timestamp correlating with
        an existing ScanStatus for that scanner should create a CoveredAccount with those details.
        """
        recreate_account_coverage(coverage_message_single_scanner)

        covered_account = CoveredAccount.objects.get()

        assert str(covered_account.account.uuid) == coverage_message_single_scanner[0]["account"]
        assert covered_account.scanner.pk == \
            coverage_message_single_scanner[0]["scanner_id"]
        assert covered_account.scan_status.start_time.isoformat() == \
            coverage_message_single_scanner[0]["time"]

    def test_received_messages_multiple_scanners(self, coverage_message_multiple_scanners):
        """Receiving a message with multiple existing scanners should create CoveredAccounts for
        each one."""
        recreate_account_coverage(coverage_message_multiple_scanners)

        covered_accounts = CoveredAccount.objects.all()

        assert covered_accounts.count() == 2
        assert covered_accounts[0].scanner != covered_accounts[1].scanner

    def test_received_message_multiple_scan_times(self, coverage_message_multiple_timestamps):
        """Receiving a message with multiple scan times should create a CoveredAccount for each
        one."""
        recreate_account_coverage(coverage_message_multiple_timestamps)

        covered_accounts = CoveredAccount.objects.all()

        assert covered_accounts.count() == 2
        assert covered_accounts[0].scan_status != covered_accounts[1].scan_status

    def test_received_message_multiple_accounts(self, coverage_message_multiple_accounts):
        """Receiving a message with multiple accounts should create a CoveredAccount for each
        one."""
        recreate_account_coverage(coverage_message_multiple_accounts)

        covered_accounts = CoveredAccount.objects.all()

        assert covered_accounts.count() == 2
        assert covered_accounts[0].account != covered_accounts[1].account

    def test_received_message_one_invalid_timestamp(self, coverage_message_invalid_timestamp):
        """When receiving instructions to create multiple CoveredAccounts, if some can't be created,
        all which can should."""
        recreate_account_coverage(coverage_message_invalid_timestamp)

        # Implicitly check that only one CoveredAccount was created
        covered_account = CoveredAccount.objects.get()

        assert str(covered_account.account.uuid) == coverage_message_invalid_timestamp[1]["account"]
        assert covered_account.scanner.pk == \
            coverage_message_invalid_timestamp[1]["scanner_id"]
        assert covered_account.scan_status.start_time.isoformat() == \
            coverage_message_invalid_timestamp[1]["time"]

    def test_received_message_one_invalid_scanner(self, coverage_message_invalid_scanner):
        """When receiving instructions to create multiple CoveredAccounts, if some can't be created,
        all which can should."""
        recreate_account_coverage(coverage_message_invalid_scanner)

        # Implicitly check that only one CoveredAccount was created
        covered_account = CoveredAccount.objects.get()

        assert str(covered_account.account.uuid) == coverage_message_invalid_scanner[1]["account"]
        assert covered_account.scanner.pk == \
            coverage_message_invalid_scanner[1]["scanner_id"]
        assert covered_account.scan_status.start_time.isoformat() == \
            coverage_message_invalid_scanner[1]["time"]

    def test_received_message_one_invalid_account(self, coverage_message_invalid_account):
        """When receiving instructions to create multiple CoveredAccounts, if some can't be created,
        all which can should."""
        recreate_account_coverage(coverage_message_invalid_account)

        # Implicitly check that only one CoveredAccount was created
        covered_account = CoveredAccount.objects.get()

        assert str(covered_account.account.uuid) == coverage_message_invalid_account[1]["account"]
        assert covered_account.scanner.pk == \
            coverage_message_invalid_account[1]["scanner_id"]
        assert covered_account.scan_status.start_time.isoformat() == \
            coverage_message_invalid_account[1]["time"]

    def test_received_message_one_org_mismatch(self, coverage_message_organization_mismatch):
        """When receiving instructions to create multiple CoveredAccounts, if some can't be created,
        all which can should."""
        recreate_account_coverage(coverage_message_organization_mismatch)

        # Implicitly check that only one CoveredAccount was created
        covered_account = CoveredAccount.objects.get()

        assert str(covered_account.account.uuid) == \
            coverage_message_organization_mismatch[1]["account"]
        assert covered_account.scanner.pk == \
            coverage_message_organization_mismatch[1]["scanner_id"]
        assert covered_account.scan_status.start_time.isoformat() == \
            coverage_message_organization_mismatch[1]["time"]
