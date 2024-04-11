import pytest

from ...core.models import Client
from ...adminapp.models.scannerjobs.scanner import Scanner
from ...adminapp.models.scannerjobs.scanner_helpers import CoveredAccount, ScanStatus
from ...organizations.models import Organization, OrganizationalUnit, Account
from ..utils import construct_dict_from_scanners_stale_accounts

from tests.test_utilities import dummy_rule_dict
from os2datascanner.utils.system_utilities import time_now
from os2datascanner.projects.admin.adminapp.models.rules import CustomRule


@pytest.mark.django_db
class TestPostImportCleanup:

    @pytest.fixture(autouse=True)
    def scanner_with_covered_accounts_and_benny(self):
        client = Client.objects.create(name='test_client')
        org = Organization.objects.create(name="test_org", client=client)
        rule = CustomRule.objects.create(**dummy_rule_dict)
        scanner = Scanner.objects.create(name="Scammer, I mean Scanner", organization=org,
                                         rule=rule)
        scan_status = ScanStatus.objects.create(
            scan_tag={"time": time_now().isoformat()},
            scanner=scanner,
            total_sources=1,
            total_objects=1,
            explored_sources=1,
            scanned_objects=1,
        )

        oluf = Account.objects.create(username="Oluf", organization=org)
        gertrud = Account.objects.create(username="Gertrud", organization=org)
        benny = Account.objects.create(username="Benny", organization=org)

        fritz = Account.objects.create(username="Fritz", organization=org)
        günther = Account.objects.create(username="Günther", organization=org)
        hansi = Account.objects.create(username="Hansi", organization=org)

        fam_sand = OrganizationalUnit.objects.create(name="Familien Sand", organization=org)
        nisser = OrganizationalUnit.objects.create(name="Nisserne", organization=org)

        fam_sand.account_set.add(oluf, gertrud)
        nisser.account_set.add(fritz, günther, hansi)

        CoveredAccount.objects.bulk_create(
            [
                CoveredAccount(scanner=scanner, account=oluf, scan_status=scan_status),
                CoveredAccount(scanner=scanner, account=gertrud, scan_status=scan_status),
                CoveredAccount(scanner=scanner, account=benny, scan_status=scan_status),
                CoveredAccount(scanner=scanner, account=fritz, scan_status=scan_status),
                CoveredAccount(scanner=scanner, account=günther, scan_status=scan_status),
                CoveredAccount(scanner=scanner, account=hansi, scan_status=scan_status),

            ]
        )

        scanner.org_unit.add(fam_sand, nisser)

        return scanner, benny

    def test_construct_dict_from_scanners_stale_accounts_one_stale_account(
            self,
            scanner_with_covered_accounts_and_benny):
        """When calling the 'construct_dict_from_scanners_stale_accounts' while
        one account is no longer in the org_units covered by the scanner, but
        is still in the covered_accounts-field of the scanner, the function
        should return a dict with that scanner and that account."""

        scanner, benny = scanner_with_covered_accounts_and_benny

        # Benny is in the covered_accounts field of the scanner, but not in
        # any org_unit covered by the scanner, so we expect:
        expected_out = {
            scanner.pk: {
                "uuids": [str(benny.uuid)],
                "usernames": [benny.username]
            }
        }

        real_out = construct_dict_from_scanners_stale_accounts()
        assert real_out == expected_out
