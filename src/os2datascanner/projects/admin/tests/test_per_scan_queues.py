# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import datetime
from unittest.mock import patch

import pytest

from os2datascanner.engine2.pipeline import messages
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner_helpers import (
        ScanStatus, _per_scan_queue_name)
from os2datascanner.projects.admin.adminapp.management.commands.status_collector import (
        status_message_received_raw)


def _make_scan_tag(pk, time):
    """Return a serialised ScanTagFragment dict with the given scanner pk and time."""
    return messages.ScanTagFragment(
        user=None,
        time=time,
        scanner=messages.ScannerFragment(pk=pk, name="test", test=False, keep_fp=False),
        organisation=messages.OrganisationFragment(name="org", uuid=None),
    ).to_json_object()


class TestPerScanQueueName:
    def test_valid_tag_produces_expected_name(self):
        t = datetime.datetime(2024, 1, 1, 12, 0, 0,
                              tzinfo=datetime.timezone.utc)
        tag = _make_scan_tag(pk=42, time=t)
        assert _per_scan_queue_name(tag) == "osds_conversions.42_20240101T120000"

    def test_old_string_tag_returns_none(self):
        # Tags in the old "plain ISO string" format have no scanner pk
        tag = "2019-12-20T09:00:00+01:00"
        # ScanTagFragment.from_json_object accepts this format but .scanner is None
        assert _per_scan_queue_name(tag) is None

    def test_queue_name_uses_local_time_digits(self):
        """The time part must be compact YYYYMMDDTHHMMSS (no TZ, no separators)."""
        t = datetime.datetime(2025, 11, 5, 8, 3, 7,
                              tzinfo=datetime.timezone.utc)
        tag = _make_scan_tag(pk=1, time=t)
        name = _per_scan_queue_name(tag)
        assert name == "osds_conversions.1_20251105T080307"


@pytest.mark.django_db
class TestScanStatusConversionQueueTag:
    def test_default_tag_is_full(self, basic_scanstatus):
        assert basic_scanstatus.conversion_queue_tag == "full"

    def test_tag_persists(self, basic_scanstatus):
        basic_scanstatus.conversion_queue_tag = "delta"
        basic_scanstatus.save()
        basic_scanstatus.refresh_from_db()
        assert basic_scanstatus.conversion_queue_tag == "delta"


@pytest.mark.django_db
class TestQueueDeletionOnCompletion:
    def _make_finishing_status_message(self, scan_tag):
        """Build a StatusMessage that, when applied to a ScanStatus where
        scanned_objects == total_objects - 1, pushes it to finished."""
        return messages.StatusMessage(
            scan_tag=messages.ScanTagFragment.from_json_object(scan_tag),
            message="done",
            object_size=100,
            object_type="text/plain",
            process_time_worker=0.01,
        )

    def test_delete_per_scan_queue_called_on_finish(self, basic_scanner):
        """When a scan transitions to finished for the first time,
        delete_per_scan_queue should be called with the scan's tag."""
        scan_tag_obj = basic_scanner._construct_scan_tag()
        scan_tag = scan_tag_obj.to_json_object()

        ScanStatus.objects.create(
            scanner=basic_scanner,
            scan_tag=scan_tag,
            total_sources=1,
            explored_sources=1,
            total_objects=5,
            scanned_objects=4,
        )

        body = self._make_finishing_status_message(scan_tag).to_json_object()

        with (
            patch(
                "os2datascanner.projects.admin.adminapp"
                ".management.commands.status_collector.delete_per_scan_queue"
            ) as mock_delete,
            patch(
                "os2datascanner.projects.admin.adminapp"
                ".management.commands.status_collector"
                ".FinishedScannerNotificationEmail"
            ),
        ):
            [_ for _ in status_message_received_raw(body)]

        mock_delete.assert_called_once_with(scan_tag)

    def test_delete_not_called_when_scan_not_finished(self, basic_scanner):
        """Queue deletion must NOT happen if the scan is still in progress."""
        scan_tag_obj = basic_scanner._construct_scan_tag()
        scan_tag = scan_tag_obj.to_json_object()

        ScanStatus.objects.create(
            scanner=basic_scanner,
            scan_tag=scan_tag,
            total_sources=1,
            explored_sources=1,
            total_objects=5,
            scanned_objects=2,  # still 2 objects to go
        )

        body = self._make_finishing_status_message(scan_tag).to_json_object()

        with patch(
            "os2datascanner.projects.admin.adminapp"
            ".management.commands.status_collector.delete_per_scan_queue"
        ) as mock_delete:
            [_ for _ in status_message_received_raw(body)]

        mock_delete.assert_not_called()

    def test_delete_not_called_twice_for_same_scan(self, basic_scanner):
        """If a duplicate status message arrives after the scan is already marked
        finished (email_sent=True), delete_per_scan_queue must NOT fire again."""
        scan_tag_obj = basic_scanner._construct_scan_tag()
        scan_tag = scan_tag_obj.to_json_object()

        ScanStatus.objects.create(
            scanner=basic_scanner,
            scan_tag=scan_tag,
            total_sources=1,
            explored_sources=1,
            total_objects=5,
            scanned_objects=5,
            email_sent=True,  # already completed once
        )

        body = self._make_finishing_status_message(scan_tag).to_json_object()

        with patch(
            "os2datascanner.projects.admin.adminapp"
            ".management.commands.status_collector.delete_per_scan_queue"
        ) as mock_delete:
            [_ for _ in status_message_received_raw(body)]

        mock_delete.assert_not_called()
