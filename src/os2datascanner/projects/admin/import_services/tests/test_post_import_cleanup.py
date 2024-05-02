import pytest

from ...adminapp.models.scannerjobs.scanner_helpers import CoveredAccount
from ..utils import construct_dict_from_scanners_stale_accounts


@pytest.mark.django_db
class TestPostImportCleanup:

    @pytest.fixture(autouse=True)
    def scanner_with_covered_accounts_and_benny(
            self,
            basic_scanner,
            basic_scanstatus_completed,
            oluf,
            gertrud,
            benny,
            fritz,
            günther,
            hansi,
            familien_sand,
            nisserne):

        CoveredAccount.objects.bulk_create(
            [
                CoveredAccount(scanner=basic_scanner, account=oluf,
                               scan_status=basic_scanstatus_completed),
                CoveredAccount(scanner=basic_scanner, account=gertrud,
                               scan_status=basic_scanstatus_completed),
                CoveredAccount(scanner=basic_scanner, account=benny,
                               scan_status=basic_scanstatus_completed),
                CoveredAccount(scanner=basic_scanner, account=fritz,
                               scan_status=basic_scanstatus_completed),
                CoveredAccount(scanner=basic_scanner, account=günther,
                               scan_status=basic_scanstatus_completed),
                CoveredAccount(scanner=basic_scanner, account=hansi,
                               scan_status=basic_scanstatus_completed),

            ]
        )

        basic_scanner.org_unit.add(familien_sand, nisserne)

        return basic_scanner, benny

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
