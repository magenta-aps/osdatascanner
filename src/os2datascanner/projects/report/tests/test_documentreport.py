import pytest

from ..reportapp.models.documentreport import DocumentReport, count_matches
from .test_utilities import create_reports_for, raw_matches_json_matched


@pytest.mark.django_db
class TestCountMatchesDocumentReport:
    """The 'number_of_matches' field value should always represent the number of matches
    in the 'raw_matches' JSON field."""

    def test_count_matches_on_create(self, egon_email_alias):
        create_reports_for(egon_email_alias, num=1)

        dr = DocumentReport.objects.get()
        matches = count_matches(dr.matches)

        assert dr.number_of_matches == matches

    def test_count_matches_on_save_with_more_matches(self, egon_email_alias):
        create_reports_for(egon_email_alias, num=1)

        dr = DocumentReport.objects.get()

        old_matches = count_matches(dr.matches)

        dr.raw_matches["matches"][0]["matches"].append(
            {
                "match": "1234XXXXXX",
                "offset": 420,
                "context": "XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX",
                "probability": 1.0,
                "sensitivity": 1000,
                "context_offset": 50
            }
        )

        dr.save()

        dr.refresh_from_db()

        matches = count_matches(dr.matches)

        assert dr.number_of_matches == matches
        assert dr.number_of_matches == old_matches + 1

    def test_count_matches_on_save_with_fewer_matches(self, egon_email_alias):
        create_reports_for(egon_email_alias, num=1)

        dr = DocumentReport.objects.get()

        old_matches = count_matches(dr.matches)

        dr.raw_matches["matches"][0]["matches"].pop()

        dr.save()

        dr.refresh_from_db()

        matches = count_matches(dr.matches)

        assert dr.number_of_matches == matches
        assert dr.number_of_matches == old_matches - 1

    def test_count_matches_on_update_or_create_with_more_matches(self, egon_email_alias):
        create_reports_for(egon_email_alias, num=1)

        dr = DocumentReport.objects.get()

        old_matches = count_matches(dr.matches)

        raw_matches_add_match = raw_matches_json_matched
        raw_matches_add_match["matches"][0]["matches"].append(
            {
                "match": "1234XXXXXX",
                "offset": 420,
                "context": "XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX XXXXXX-XXXX",
                "probability": 1.0,
                "sensitivity": 1000,
                "context_offset": 50
            }
        )

        dr, _ = DocumentReport.objects.update_or_create(
            pk=dr.pk,
            defaults={"raw_matches": raw_matches_add_match})

        dr.refresh_from_db()

        matches = count_matches(dr.matches)

        assert dr.number_of_matches == matches
        assert dr.number_of_matches == old_matches + 1

    def test_count_matches_on_update_or_create_with_fewer_matches(self, egon_email_alias):
        create_reports_for(egon_email_alias, num=1)

        dr = DocumentReport.objects.get()

        old_matches = count_matches(dr.matches)

        raw_matches_rem_match = raw_matches_json_matched
        raw_matches_rem_match["matches"][0]["matches"].pop()

        dr, _ = DocumentReport.objects.update_or_create(
            pk=dr.pk,
            defaults={"raw_matches": raw_matches_rem_match})

        dr.refresh_from_db()

        matches = count_matches(dr.matches)

        assert dr.number_of_matches == matches
        assert dr.number_of_matches == old_matches - 1
