import pytest

from .utilities import make_matched_document_reports_for
from ...reportapp.models.documentreport import DocumentReport


@pytest.mark.django_db
class TestOrganization:

    @pytest.mark.parametrize("egon_matches,benny_matches,egon_fp,benny_fp,rate", [
        (0, 0, 0, 0, 0),
        (10, 0, 10, 0, 1.0),
        (10, 0, 1, 0, 0.1),
        (10, 10, 5, 1, 0.3),
        (10, 20, 10, 1, 11/30),
    ])
    def test_false_positive_rate(
            self,
            egon_email_alias,
            benny_email_alias,
            olsenbanden_organization,
            egon_matches,
            benny_matches,
            egon_fp,
            benny_fp,
            rate):
        make_matched_document_reports_for(
            egon_email_alias,
            handled=egon_matches,
            amount=egon_matches)
        make_matched_document_reports_for(
            benny_email_alias,
            handled=benny_matches,
            amount=benny_matches)

        for report in DocumentReport.objects.filter(alias_relation=benny_email_alias)[:benny_fp]:
            report.resolution_status = DocumentReport.ResolutionChoices.FALSE_POSITIVE
            report.save()

        for report in DocumentReport.objects.filter(alias_relation=egon_email_alias)[:egon_fp]:
            report.resolution_status = DocumentReport.ResolutionChoices.FALSE_POSITIVE
            report.save()

        assert olsenbanden_organization.false_positive_rate == rate
