import pytest

from django.db import transaction
from django.db.utils import DataError

from ..adminapp.management.commands import checkup_collector
from ..adminapp.management.commands.checkup_collector import (
    create_usererrorlog, checkup_message_received_raw)
from ..adminapp.management.commands.status_collector import status_message_received_raw
from ..adminapp.models.usererrorlog import UserErrorLog
from ..adminapp.models.scannerjobs.scanner import ScanStatus, ScheduledCheckup


@pytest.mark.django_db
class TestPipelineCollector:

    @pytest.mark.parametrize(
        ("status_message_name,expected_total_objects,expected_is_error,"
         "expected_scanned_objects,expected_scanned_size"),
        [
            ("status_message_10_objects", 18020, False, 0, 0),
            ("status_message_with_error", 0, True, 0, 0),
            ("status_message_with_object_size", 0, False, 1, 100),
        ])
    def test_scan_status_update(self, status_message_name, expected_total_objects,
                                expected_is_error, expected_scanned_objects,
                                expected_scanned_size, basic_scanner, status_messages):
        status_message = status_messages[status_message_name]
        ScanStatus.objects.create(
                scanner=basic_scanner,
                scan_tag=status_message.scan_tag.to_json_object(),
                total_sources=11,
                total_objects=expected_total_objects - 10 if expected_total_objects > 0 else 0,
                scanned_objects=0,
                scanned_size=0
        )
        body = status_message.to_json_object()
        [s for s in status_message_received_raw(body)]
        scan_status = ScanStatus.objects.get(scan_tag=body["scan_tag"])

        assert scan_status.total_objects == expected_total_objects
        assert scan_status.message == status_message_name
        assert scan_status.status_is_error == expected_is_error
        assert scan_status.scanned_objects == expected_scanned_objects
        assert scan_status.scanned_size == expected_scanned_size

    def test_surrogate_errors_are_caught(self, positive_corrupt_match_message):
        """How to test an exception is caught?
        We expect that no object is created if a DataError occurs. Reason being
        if it is the file path (as in this case) that is corrupt we cannot visit
        the file again, and then there is no reason to store the data.
        We could consider checking the file path. For now, we log the dataerror.
        """
        try:
            with transaction.atomic():
                checkup_collector.update_scheduled_checkup(
                        handle=positive_corrupt_match_message.handle,
                        matches=positive_corrupt_match_message,
                        problem=None,
                        scan_time=positive_corrupt_match_message.scan_spec.scan_tag.time,
                        scanner=None)
        except DataError:
            # Expected behaviour
            pass

        with pytest.raises(DataError):
            ScheduledCheckup.objects.select_for_update().get(
                handle_representation=positive_corrupt_match_message.handle.to_json_object()
            )

    def test_problem_message_is_logged(self, basic_problem_message, basic_scanstatus):
        """Test that a UserErrorLog object is successfully created when the pipeline_collector
        recieves a problem message."""

        # Make sure a scan status exists with the correct scan tag
        basic_scanstatus.scan_tag = basic_problem_message.scan_tag.to_json_object()
        basic_scanstatus.save()

        create_usererrorlog(basic_problem_message)

        assert UserErrorLog.objects.all().exists()
        assert UserErrorLog.objects.first().error_message == basic_problem_message.message

    def test_hints_removed(self, positive_web_match_message, basic_scanner):
        """Hints should be removed from a WebHandle when one is received by the
        checkup collector."""
        positive_web_match_message = positive_web_match_message._deep_replace(
                scan_spec__scan_tag__scanner__pk=basic_scanner.pk)
        ScanStatus.objects.create(
                scanner=basic_scanner,
                scan_tag=positive_web_match_message.scan_spec.scan_tag.to_json_object(),
                total_sources=1,
                total_objects=1)

        [s for s in checkup_message_received_raw(
                positive_web_match_message.to_json_object())]

        sc = ScheduledCheckup.objects.get(scanner=basic_scanner)
        for hint in ("fresh", "last_modified",):
            assert sc.handle.hint(hint) is None
