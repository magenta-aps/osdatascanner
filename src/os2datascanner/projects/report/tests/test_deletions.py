# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from dataclasses import replace
from types import SimpleNamespace

import pytest
from django.core.exceptions import PermissionDenied
from django.utils import translation

from os2datascanner.engine2.model.smbc import SMBCSource, SMBCHandle
from os2datascanner.projects.grants.models.smbgrant import SMBGrant
from os2datascanner.projects.report.reportapp.views.utilities import (
    msgraph_utilities, smb_utilities)
from os2datascanner.projects.report.reportapp.views.utilities.document_report_utilities \
        import validate_delete_request, DeleteRequestError, format_delete_result
from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
from os2datascanner.projects.report.tests.test_utilities import create_reports_for


@pytest.mark.django_db
class TestValidateDeleteRequest:

    def test_success(self, *, egon_account, egon_email_alias):
        """A valid request raises no exception."""
        create_reports_for(egon_email_alias, num=2)
        pks = list(DocumentReport.objects.filter(
            alias_relations__in=egon_account.aliases.all()
        ).values_list("pk", flat=True))

        validate_delete_request(egon_account.user, pks)

    def test_raises_when_reports_not_found(self, *, egon_account):
        """Raises when no DocumentReports exist for the given PKs."""
        with pytest.raises(DeleteRequestError):
            validate_delete_request(egon_account.user, [999999])

    def test_raises_when_no_alias_association(
            self, *, egon_account, benny_account, benny_email_alias):
        """Raises when the reports are not associated with the requesting user's aliases."""
        create_reports_for(benny_email_alias, num=1)
        pks = list(DocumentReport.objects.filter(
            alias_relations__in=benny_account.aliases.all()
        ).values_list("pk", flat=True))

        with pytest.raises(DeleteRequestError):
            validate_delete_request(egon_account.user, pks)

    def test_raises_when_report_has_no_matches(self, *, egon_account, egon_email_alias):
        """Raises when a report carries no matches (e.g. it is a problem/error report)."""
        create_reports_for(egon_email_alias, num=1, matched=False)
        pks = list(DocumentReport.objects.filter(
            alias_relations__in=egon_account.aliases.all()
        ).values_list("pk", flat=True))

        with pytest.raises(DeleteRequestError):
            validate_delete_request(egon_account.user, pks)


@translation.override("en")
@pytest.mark.parametrize("errors,expected", [
    ([], (True, "ok")),
    (["boom", "boom"], (False, "2 results could not be deleted: boom")),
])
def test_format_delete_result(errors, expected):
    assert format_delete_result(errors) == expected


@pytest.mark.django_db
@translation.override("en")
def test_msgraph_file_delete_counts_every_failure(
        monkeypatch, olsenbanden_organization, egon_account, egon_email_alias):
    olsenbanden_organization.onedrive_delete_permission = True
    olsenbanden_organization.save()
    create_reports_for(egon_email_alias, num=2)
    failures = iter([PermissionDenied("denied"), AttributeError("no handle")])

    def fake_delete_file(report, account):
        raise next(failures)

    monkeypatch.setattr(msgraph_utilities, "delete_file", fake_delete_file)

    assert msgraph_utilities.try_msgraph_file_delete(
        SimpleNamespace(user=egon_account.user),
        list(DocumentReport.objects.values_list("pk", flat=True)),
    ) == (False, "2 results could not be deleted")


@pytest.mark.django_db
@translation.override("en")
def test_smb_delete_continues_past_non_smb_result(
        monkeypatch, olsenbanden_organization, egon_account, egon_email_alias):
    olsenbanden_organization.smb_delete_permission = True
    olsenbanden_organization.save()
    SMBGrant.objects.create(
        organization=olsenbanden_organization, username="os2", password="swordfish")
    create_reports_for(egon_email_alias, num=2)
    smb_report, other_report = DocumentReport.objects.all()
    smb_report.raw_matches = replace(
        smb_report.matches,
        handle=SMBCHandle(SMBCSource("//samba/e2test"), "file.txt")).to_json_object()
    smb_report.save()
    monkeypatch.setattr(
        smb_utilities.smbc, "Context", lambda **kw: SimpleNamespace(unlink=lambda url: None))

    assert smb_utilities.try_smb_delete_1(
        SimpleNamespace(user=egon_account.user), [smb_report.pk, other_report.pk],
    ) == (False, "Target file is not on a Windows network drive")
    smb_report.refresh_from_db()
    assert smb_report.resolution_status == DocumentReport.ResolutionChoices.REMOVED
