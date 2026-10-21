# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from django.urls import reverse_lazy

from os2datascanner.engine2.model.file import FilesystemSource, FilesystemHandle
from os2datascanner.engine2.model.smbc import SMBCSource, SMBCHandle
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.engine2.pipeline import messages
from ..reportapp.utils import create_alias_and_match_relations
from ..reportapp.models.documentreport import DocumentReport
from ..reportapp.models.scanner_reference import ScannerReference
from ..organizations.models import Alias, Account, Organization, AliasType
from .generate_test_data import record_match, record_metadata

HTMX = {"HTTP_HX-Request": "true"}
OwnerStatus = DocumentReport.OwnerStatus


@pytest.fixture
def waterdeep():
    return Organization.objects.create(name="Waterdeep")


def make_account(org, username, first_name, last_name):
    return Account.objects.create(
        username=username, first_name=first_name, last_name=last_name, organization=org)


@pytest.fixture
def drizzt(waterdeep):
    return make_account(waterdeep, "drizzt", "Drizzt", "Do'Urden")


@pytest.fixture
def drizzt_alias(drizzt):
    return Alias.objects.create(
        account=drizzt, user=drizzt.user,
        _alias_type=AliasType.EMAIL, _value="drizzt@waterdeep.gov")


@pytest.fixture
def volo(waterdeep):
    account = make_account(waterdeep, "volo", "Volothamp", "Geddarm")
    Alias.objects.create(
        account=account, user=account.user,
        _alias_type=AliasType.EMAIL, _value="volo@waterdeep.gov")
    return account


@pytest.fixture
def elminster(waterdeep):
    account = make_account(waterdeep, "elminster", "Elminster", "Aumar")
    Alias.objects.create(
        account=account, user=account.user,
        _alias_type=AliasType.REMEDIATOR, _value=0)
    return account


@pytest.fixture
def candlekeep_scanner(waterdeep):
    return ScannerReference.objects.create(
        scanner_pk=1492, scanner_name="Candlekeep library", organization=waterdeep)


def record_scroll(scanner, handle, owner="drizzt@waterdeep.gov"):
    """Records a match for @handle owned by @owner and returns its metadata message."""
    scan_tag = messages.deep_replace(
        messages.ScanTagFragment.make_dummy(),
        organisation__uuid=scanner.organization.uuid,
        scanner__pk=scanner.scanner_pk)
    scan_spec = messages.ScanSpecMessage(
        scan_tag=scan_tag,
        source=handle.source,
        rule=RegexRule("fireball"),
        configuration={}, progress=None, filter_rule=None)
    record_match(messages.MatchesMessage(
        scan_spec=scan_spec,
        handle=handle,
        matched=True,
        matches=[messages.MatchFragment(
            rule=RegexRule("fireball"), matches=[{"match": "fireball"}])]))
    return messages.MetadataMessage(
        scan_tag=scan_tag,
        handle=handle,
        metadata={"email-account": owner})


def scroll_handle():
    return SMBCHandle(SMBCSource("//candlekeep/library"), "Scroll of Fireball.pdf")


@pytest.fixture
def scroll_metadata(candlekeep_scanner):
    return record_scroll(candlekeep_scanner, scroll_handle())


@pytest.fixture
def scroll_report(drizzt_alias, scroll_metadata):
    record_metadata(scroll_metadata)
    return DocumentReport.objects.get()


def personal(account):
    return account.get_report(Account.ReportType.PERSONAL_AND_SHARED)


def remediator(account):
    return account.get_report(Account.ReportType.REMEDIATOR)


def decline(client, account, report):
    client.force_login(account.user)
    return client.post(reverse_lazy("decline-ownership", kwargs={"pk": report.pk}), **HTMX)


def return_to_owner(client, account, report):
    client.force_login(account.user)
    return client.post(reverse_lazy("return-ownership", kwargs={"pk": report.pk}), **HTMX)


@pytest.mark.django_db
class TestOwnerStatus:

    def test_decline_routes_to_remediator(self, client, drizzt, elminster, scroll_report):
        response = decline(client, drizzt, scroll_report)

        scroll_report.refresh_from_db()
        assert response.status_code == 200
        assert scroll_report.owner_status == OwnerStatus.DECLINED
        assert scroll_report.owner_status_time is not None
        assert scroll_report not in personal(drizzt)
        assert scroll_report in remediator(elminster)

    def test_decline_survives_rescan(
            self, client, drizzt, elminster, scroll_report, scroll_metadata):
        decline(client, drizzt, scroll_report)

        record_metadata(scroll_metadata)

        assert scroll_report not in personal(drizzt)
        assert scroll_report in remediator(elminster)

    def test_owner_change_clears_decline(
            self, client, drizzt, volo, elminster, candlekeep_scanner, scroll_report):
        decline(client, drizzt, scroll_report)

        record_metadata(record_scroll(
            candlekeep_scanner, scroll_handle(), owner="volo@waterdeep.gov"))

        scroll_report.refresh_from_db()
        assert scroll_report.owner_status is None
        assert scroll_report in personal(volo)
        assert scroll_report not in personal(drizzt)
        assert scroll_report not in remediator(elminster)

    def test_owner_case_change_keeps_decline(
            self, client, drizzt, elminster, candlekeep_scanner, scroll_report):
        decline(client, drizzt, scroll_report)

        record_metadata(record_scroll(
            candlekeep_scanner, scroll_handle(), owner="Drizzt@Waterdeep.gov"))

        scroll_report.refresh_from_db()
        assert scroll_report.owner_status == OwnerStatus.DECLINED
        assert scroll_report in remediator(elminster)

    def test_decline_survives_alias_sync(
            self, client, drizzt, drizzt_alias, elminster, scroll_report):
        decline(client, drizzt, scroll_report)

        create_alias_and_match_relations(drizzt_alias)

        assert scroll_report not in personal(drizzt)
        assert scroll_report in remediator(elminster)

    def test_decline_other_accounts_report(self, client, volo, elminster, scroll_report):
        response = decline(client, volo, scroll_report)

        scroll_report.refresh_from_db()
        assert response.status_code == 404
        assert scroll_report.owner_status is None

    def test_decline_shared_report(self, client, drizzt, volo, elminster, scroll_report):
        Alias.objects.create(
            account=volo, user=volo.user, shared=True,
            _alias_type=AliasType.EMAIL, _value="drizzt@waterdeep.gov")
        create_alias_and_match_relations(volo.aliases.get(shared=True))
        assert scroll_report in personal(volo)

        response = decline(client, volo, scroll_report)

        scroll_report.refresh_from_db()
        assert response.status_code == 404
        assert scroll_report.owner_status is None
        assert scroll_report in personal(drizzt)

    def test_decline_button_hidden_for_shared_report(
            self, client, drizzt, volo, elminster, scroll_report):
        Alias.objects.create(
            account=volo, user=volo.user, shared=True,
            _alias_type=AliasType.EMAIL, _value="drizzt@waterdeep.gov")
        create_alias_and_match_relations(volo.aliases.get(shared=True))

        client.force_login(drizzt.user)
        assert b'name="decline-ownership"' in client.get(reverse_lazy("index")).content

        client.force_login(volo.user)
        assert b'name="decline-ownership"' not in client.get(reverse_lazy("index")).content

    def test_decline_unsupported_source(
            self, client, drizzt, drizzt_alias, elminster, candlekeep_scanner):
        record_metadata(record_scroll(candlekeep_scanner, FilesystemHandle(
            FilesystemSource("/srv/candlekeep"), "Scroll of Fireball.pdf")))
        report = DocumentReport.objects.get()

        response = decline(client, drizzt, report)

        report.refresh_from_db()
        assert response.status_code == 404
        assert report.owner_status is None
        assert report in personal(drizzt)

    def test_decline_without_remediator(self, client, drizzt, scroll_report):
        response = decline(client, drizzt, scroll_report)

        scroll_report.refresh_from_db()
        assert response.status_code == 200
        assert scroll_report.owner_status is None
        assert scroll_report in personal(drizzt)

    def test_decline_with_scanner_remediator(self, client, drizzt, waterdeep, scroll_report):
        laeral = make_account(waterdeep, "laeral", "Laeral", "Silverhand")
        Alias.objects.create(
            account=laeral, user=laeral.user, _alias_type=AliasType.REMEDIATOR,
            _value=scroll_report.scanner_job.scanner_pk)

        decline(client, drizzt, scroll_report)

        scroll_report.refresh_from_db()
        assert scroll_report.owner_status == OwnerStatus.DECLINED
        assert scroll_report not in personal(drizzt)
        assert scroll_report in remediator(laeral)

    def test_decline_with_other_scanner_remediator(
            self, client, drizzt, waterdeep, scroll_report):
        laeral = make_account(waterdeep, "laeral", "Laeral", "Silverhand")
        Alias.objects.create(
            account=laeral, user=laeral.user, _alias_type=AliasType.REMEDIATOR,
            _value=scroll_report.scanner_job.scanner_pk + 1)

        decline(client, drizzt, scroll_report)

        scroll_report.refresh_from_db()
        assert scroll_report.owner_status is None
        assert scroll_report in personal(drizzt)
        assert scroll_report not in remediator(laeral)

    def test_return_to_owner(self, client, drizzt, elminster, scroll_report, scroll_metadata):
        decline(client, drizzt, scroll_report)

        response = return_to_owner(client, elminster, scroll_report)
        record_metadata(scroll_metadata)

        scroll_report.refresh_from_db()
        assert response.status_code == 200
        assert scroll_report.owner_status == OwnerStatus.RETURNED
        assert scroll_report in personal(drizzt)
        assert scroll_report not in remediator(elminster)

    def test_returned_report_can_be_declined_again(
            self, client, drizzt, elminster, scroll_report):
        decline(client, drizzt, scroll_report)
        return_to_owner(client, elminster, scroll_report)

        response = decline(client, drizzt, scroll_report)

        scroll_report.refresh_from_db()
        assert response.status_code == 200
        assert scroll_report.owner_status == OwnerStatus.DECLINED
        assert scroll_report not in personal(drizzt)
        assert scroll_report in remediator(elminster)

    def test_non_remediator_cannot_return(self, client, drizzt, volo, elminster, scroll_report):
        decline(client, drizzt, scroll_report)

        response = return_to_owner(client, volo, scroll_report)

        scroll_report.refresh_from_db()
        assert response.status_code == 404
        assert scroll_report.owner_status == OwnerStatus.DECLINED

    def test_return_without_owner_alias(self, client, drizzt, drizzt_alias, elminster,
                                        scroll_report):
        decline(client, drizzt, scroll_report)
        drizzt_alias.delete()

        response = return_to_owner(client, elminster, scroll_report)

        scroll_report.refresh_from_db()
        assert response.status_code == 200
        assert scroll_report.owner_status == OwnerStatus.DECLINED
        assert scroll_report in remediator(elminster)

    def test_return_succeeds_once_owner_alias_exists(
            self, client, drizzt, drizzt_alias, elminster, scroll_report):
        decline(client, drizzt, scroll_report)
        drizzt_alias.delete()
        return_to_owner(client, elminster, scroll_report)
        scroll_report.refresh_from_db()
        assert scroll_report.owner_status == OwnerStatus.DECLINED

        Alias.objects.create(
            account=drizzt, user=drizzt.user,
            _alias_type=AliasType.EMAIL, _value="drizzt@waterdeep.gov")

        response = return_to_owner(client, elminster, scroll_report)

        scroll_report.refresh_from_db()
        assert response.status_code == 200
        assert scroll_report.owner_status == OwnerStatus.RETURNED
        assert scroll_report in personal(drizzt)
        assert scroll_report not in remediator(elminster)

    def test_automated_no_access_routes_to_remediator(self, drizzt, elminster, scroll_report):
        scroll_report.set_owner_status(OwnerStatus.NO_ACCESS)

        scroll_report.refresh_from_db()
        assert scroll_report.owner_status == OwnerStatus.NO_ACCESS
        assert scroll_report.owner_status_time is not None
        assert scroll_report not in personal(drizzt)
        assert scroll_report in remediator(elminster)
