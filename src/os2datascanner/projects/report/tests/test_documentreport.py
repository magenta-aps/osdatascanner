import pytest

from datetime import datetime
from django.utils import timezone
from dateutil import tz

from ..reportapp.models.scanner_reference import ScannerReference
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

    def test_document_report_resolution_time_when_status_is_none(self, test_org):
        """ If the resolution_status field is set to None the resolution_time field should be set
            to None as well """

        # Arrange
        scanner, _ = ScannerReference.objects.get_or_create(
            scanner_pk=20,
            scanner_name='scanner_job_name',
            organization=test_org,
        )

        dr = DocumentReport.objects.create(
            path='test',
            sort_key='test',
            source_type='test',
            resolution_status=2,
            scanner_job=scanner,
            resolution_time=datetime(2025, 1, 1, 19, 0, tzinfo=timezone.get_default_timezone())
        )
        expected_resolution_time = None

        # Act
        dr.resolution_status = None
        dr.save()

        # Assert
        dr.refresh_from_db()
        assert expected_resolution_time == dr.resolution_time

    def test_document_report_resolution_time_when_status_is_not_none(self, test_org):
        """ The resolution_time field should be updated to the current date and time if
            resolution_status is not None """

        # Arrange
        scanner, _ = ScannerReference.objects.get_or_create(
            scanner_pk=20,
            scanner_name='test_scanner',
            organization=test_org,
        )

        dr = DocumentReport.objects.create(
            path='test',
            sort_key='test',
            source_type='test',
            resolution_status=None,
            scanner_job=scanner,
            resolution_time=datetime(2025, 1, 1, 19, 0).replace(tzinfo=tz.gettz(), microsecond=0)
        )

        expected_resolution_time = datetime.now().replace(
            tzinfo=tz.gettz(),
            microsecond=0
        )

        # Act
        dr.resolution_status = 4
        dr.save()

        # Assert
        dr.refresh_from_db()
        assert expected_resolution_time == dr.resolution_time

    def test_document_report_resolution_time_field_when_resolution_status_has_not_changed(
            self,
            test_org):
        """ The resolution_time field should not be updated if resolution status has not changed """

        # Arrange
        scanner, _ = ScannerReference.objects.get_or_create(
            scanner_pk=20,
            scanner_name='test_scanner',
            organization=test_org,
        )
        dr = DocumentReport.objects.create(
            path='test',
            sort_key='test',
            source_type='test',
            resolution_status=2,
            scanner_job=scanner,
            resolution_time=datetime(2025, 1, 1, 19, 0).replace(tzinfo=tz.gettz(), microsecond=0)
        )

        expected_resolution_time = datetime(2025, 1, 1, 19, 0).replace(
            tzinfo=tz.gettz(),
            microsecond=0
        )

        # Act
        dr.resolution_status = 2
        dr.save()

        # Assert
        dr.refresh_from_db()

        assert expected_resolution_time == dr.resolution_time
