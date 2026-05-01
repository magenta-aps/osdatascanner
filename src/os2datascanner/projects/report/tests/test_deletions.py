# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from os2datascanner.projects.report.reportapp.views.utilities.document_report_utilities \
        import validate_delete_request, DeleteRequestError
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

        validate_delete_request(egon_account.user, pks, "test")

    def test_raises_when_reports_not_found(self, *, egon_account):
        """Raises when no DocumentReports exist for the given PKs."""
        with pytest.raises(DeleteRequestError):
            validate_delete_request(egon_account.user, [999999], "test")

    def test_raises_when_no_alias_association(
            self, *, egon_account, benny_account, benny_email_alias):
        """Raises when the reports are not associated with the requesting user's aliases."""
        create_reports_for(benny_email_alias, num=1)
        pks = list(DocumentReport.objects.filter(
            alias_relations__in=benny_account.aliases.all()
        ).values_list("pk", flat=True))

        with pytest.raises(DeleteRequestError):
            validate_delete_request(egon_account.user, pks, "test")

    def test_raises_when_report_has_no_matches(self, *, egon_account, egon_email_alias):
        """Raises when a report carries no matches (e.g. it is a problem/error report)."""
        create_reports_for(egon_email_alias, num=1, matched=False)
        pks = list(DocumentReport.objects.filter(
            alias_relations__in=egon_account.aliases.all()
        ).values_list("pk", flat=True))

        with pytest.raises(DeleteRequestError):
            validate_delete_request(egon_account.user, pks, "test")
