# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from datetime import timedelta

import pytest
from django.conf import settings
from os2datascanner.utils.system_utilities import time_now
from os2datascanner.projects.admin.adminapp.management.commands import status_collector
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner_helpers import (
    ESTIMATE_STEPS, ScanStatusSnapshot, average_speed_end, fitted_end, pick_estimate_step)
from os2datascanner.projects.admin.adminapp.notification import (
    FinishedScannerNotificationEmail, get_scanner_time)


def record_status(status):
    """Records a status message to the database as though it were received by
    the administration system's pipeline collector."""
    return list(status_collector.status_message_received_raw(
            status.to_json_object()))


@pytest.fixture
def scanning_status(basic_scanstatus):
    """basic_scanstatus 100 seconds into a scan, done listing and half scanned."""
    basic_scanstatus.scan_tag["time"] = (time_now() - timedelta(seconds=100)).isoformat()
    basic_scanstatus.explored_sources = 1
    basic_scanstatus.total_objects = 1000
    basic_scanstatus.scanned_objects = 500
    basic_scanstatus.save()
    return basic_scanstatus


def add_snapshots(status, points):
    """Adds a snapshot for each (seconds into the scan, scanned, total)."""
    for seconds, scanned, total in points:
        ScanStatusSnapshot.objects.create(
                scan_status=status, scanned_objects=scanned, total_objects=total,
                time_stamp=status.start_time + timedelta(seconds=seconds))


def test_fitted_end_reaches_the_current_total():
    # 5 objects a second, so 1000 objects at 200 seconds
    assert fitted_end([(t, 5 * t) for t in range(10, 101, 10)], 1000, 100) == pytest.approx(200)


def test_fitted_end_with_identical_snapshot_times():
    assert fitted_end([(50, 250)] * 10, 1000, 100) is None


def test_average_speed_end():
    # 450 objects in the 90 seconds since the first snapshot, 500 left
    assert average_speed_end((10, 50), 500, 1000, 100) == pytest.approx(200)


@pytest.mark.parametrize("seconds_left, step", [
    (5 * 60, 0),                          # less than 10 minutes
    (15 * 60, 1),                         # about 10 to 30 minutes
    (3 * 3600, 4),                        # about 2 to 4 hours
    (200 * 86400, len(ESTIMATE_STEPS) - 1),  # more than 4 months
])
def test_estimate_step(seconds_left, step):
    assert pick_estimate_step(seconds_left) == step


@pytest.mark.django_db
class TestStatus:

    @pytest.mark.parametrize(
        ('total_sources,explored_sources,total_objects,scanned_objects,'
         'fraction_explored,fraction_scanned,finished'), [
            (0, 0, 0, 0, None, None, False),
            (2, 0, 0, 0, 0.0, None, False),
            (2, 1, 20, 0, 0.5, None, False),
            (2, 2, 20, 0, 1.0, 0.0, False),
            (2, 2, 20, 10, 1.0, 0.5, False),
            (2, 2, 20, 20, 1.0, 1.0, True),
            ])
    def test_estimates(
            self,
            basic_scanstatus,
            total_sources,
            explored_sources,
            total_objects,
            scanned_objects,
            fraction_explored,
            fraction_scanned,
            finished):

        basic_scanstatus.total_sources = total_sources
        basic_scanstatus.explored_sources = explored_sources
        basic_scanstatus.total_objects = total_objects
        basic_scanstatus.scanned_objects = scanned_objects
        basic_scanstatus.save()

        assert basic_scanstatus.fraction_explored == fraction_explored
        assert basic_scanstatus.fraction_scanned == fraction_scanned
        assert basic_scanstatus.finished == finished

    def test_broken(self, basic_scanstatus):
        """Trying to derive properties for broken ScanStatus objects should
        fail cleanly."""
        basic_scanstatus.total_sources = 5
        basic_scanstatus.explored_sources = 5
        basic_scanstatus.save()

        assert basic_scanstatus.fraction_scanned is None

    def test_no_updates_on_save(self, basic_scanstatus, basic_scanner):
        basic_scanner.save()
        basic_scanstatus.save()
        last_modified = basic_scanstatus.last_modified
        # save should not update last_modified field on scannerStatus
        basic_scanstatus.save()

        assert basic_scanstatus.last_modified == last_modified

    def test_counting_broken_sources(
            self,
            basic_scan_tag,
            basic_scanstatus,
            status_message_10_objects,
            status_message_with_error):

        basic_scanstatus.total_sources = 5
        basic_scanstatus.save()

        record_status(status_message_10_objects)

        for _ in range(0, 4):
            record_status(status_message_with_error)

        basic_scanstatus.refresh_from_db()
        assert basic_scanstatus.explored_sources == 5

    def test_mail_context_user(self,
                               basic_scanner,
                               basic_scanstatus,
                               superuser,
                               danish_translation
                               ):

        assert (FinishedScannerNotificationEmail(basic_scanner, basic_scanstatus)
                .create_context(superuser) ==
                {
            'admin_login_url': settings.SITE_URL,
            'completion_time': get_scanner_time(basic_scanstatus),  # Inconsistent, 0s or 1s
            'full_name': 'mr_superuserman',
            'institution': 'DUMMY',
            'object_plural': 'objekter',
            'object_size': 0,
            'scanner_name': 'SomeScanner-test_org',
            'total_objects': 0,
            'usererrorlogs': 0,
            'zero_bytes': False}
                )

    def test_cancel_running_status(self, basic_scanstatus):
        basic_scanstatus.cancel()

        assert basic_scanstatus.cancelled
        assert not basic_scanstatus.finished
        assert not basic_scanstatus.is_running

    def test_cancel_finished_status(self, basic_scanstatus_completed):
        basic_scanstatus_completed.cancel()

        assert not basic_scanstatus_completed.cancelled
        assert basic_scanstatus_completed.finished

    def test_estimate_falls_back_to_average_speed_instead_of_hiding(self, scanning_status):
        # Stalled for the whole fitting window
        add_snapshots(scanning_status,
                      [(t, min(20 * t, 500), 1000) for t in range(5, 101, 5)])

        assert scanning_status.estimated_completion_time > time_now()
