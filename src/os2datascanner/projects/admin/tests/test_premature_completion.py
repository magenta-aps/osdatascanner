# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Regression tests for scans that are declared finished while their sources
are still being explored.

An expanding Source (anything with yields_independent_sources, i.e. every
MSGraph scanner) publishes its sub-Sources to the explorer queue as it walks
them, but pre 3.32.4 only reported how many it found in its terminal StatusMessage. The
sub-Sources are therefore explored, and counted, before total_sources has
learned that they exist, so explored_sources overtakes total_sources. Because
fraction_explored clamps to 1.0, that overshoot sticks, and `finished`
becomes only a question of `scanned_objects >= total_objects` for the rest of the scan.

If that happens the status collector sends the completion mail and deletes
the per-scan conversion queue, which strands every conversion message that has
not been processed yet. The scan can then never complete, and because
_completed_Q disagrees with `finished` it stays in the active set forever.
"""

from unittest.mock import patch

import pytest

from os2datascanner.engine2.pipeline import messages

from ..adminapp.management.commands.status_collector import status_message_received_raw
from ..adminapp.models.scannerjobs.scanner import ScanStatus


def explorer_status(scan_tag, *, objects: int = 0, new_sources: int | None = None,
                    reported_individually: bool = False):
    """StatusMessage an explorer emits when it finishes a Source."""
    return messages.StatusMessage(
            scan_tag=scan_tag,
            message="",
            total_objects=objects,
            new_sources=new_sources,
            sources_reported_individually=reported_individually).to_json_object()


def source_discovered(scan_tag):
    """StatusMessage an explorer emits for each independent
    sub-Source it finds, as it finds it."""
    return messages.StatusMessage(
            scan_tag=scan_tag, message="", new_sources=1).to_json_object()


def worker_status(scan_tag):
    """StatusMessage a worker emits when it finishes a Handle."""
    return messages.StatusMessage(
            scan_tag=scan_tag,
            message="",
            object_size=100,
            object_type="text/plain",
            process_time_worker=0.01).to_json_object()


@pytest.mark.django_db
class TestPrematureCompletion:

    @pytest.mark.parametrize(
            "total_sources,explored_sources,total_objects,scanned_objects", [
                (1, 7, 15, 15),
                # Any overshoot at all is enough, because both counters only
                # ever grow and fraction_explored is clamped to 1.0.
                (1, 2, 1, 1),
                (113, 200, 3547, 3547),
            ])
    def test_finished_is_false_while_sources_are_undiscovered(
            self, basic_scanstatus, total_sources, explored_sources,
            total_objects, scanned_objects):
        """explored_sources exceeding total_sources means sub-Sources have been
        explored that total_sources doesn't know about yet, so exploration is
        incomplete and the scan cannot be finished."""
        basic_scanstatus.total_sources = total_sources
        basic_scanstatus.explored_sources = explored_sources
        basic_scanstatus.total_objects = total_objects
        basic_scanstatus.scanned_objects = scanned_objects
        basic_scanstatus.save()

        assert not basic_scanstatus.finished

    @pytest.mark.parametrize(
            "total_sources,explored_sources,total_objects,scanned_objects", [
                (0, 0, 0, 0),
                (1, 0, 11, 11),
                (1, 1, 0, 0),
                (1, 1, 15, 15),
                (1, 7, 15, 15),
                (2, 2, 20, 10),
                (2, 2, 20, 20),
                (113, 113, 3547, 15),
                (113, 113, 3547, 3547),
                # A scan consisting only of checkups explores no Sources at all
                (0, 0, 5, 5),
            ])
    def test_finished_agrees_with_completed_q(
            self, basic_scanstatus, total_sources, explored_sources,
            total_objects, scanned_objects):
        """ScanStatus.finished decides whether to send the completion mail and
        delete the conversion queue, _completed_Q decides whether the scan is
        still advertised to workers. If they disagree, a scan can be cleaned up
        and still be considered active, which strands a queue name in
        the status collector's re-broadcast forever."""
        basic_scanstatus.total_sources = total_sources
        basic_scanstatus.explored_sources = explored_sources
        basic_scanstatus.total_objects = total_objects
        basic_scanstatus.scanned_objects = scanned_objects
        basic_scanstatus.save()

        completed_in_db = ScanStatus.objects.filter(
                pk=basic_scanstatus.pk).filter(
                ScanStatus._completed_Q).exists()

        assert basic_scanstatus.finished == completed_in_db

    def test_queue_survives_children_reported_before_parent(
            self, basic_scanner, basic_scan_tag):
        """
        A delta scan starts with a non-zero total_objects (its checkups) and a
        single expanding Source. The sub-Sources that Source publishes are
        explored, and report in, before the parent reports how many there were.
        The workers drain everything announced so far, and the scan looks
        finished prematurely."""
        scan_tag = basic_scan_tag.to_json_object()
        ScanStatus.objects.create(
                scanner=basic_scanner,
                scan_tag=scan_tag,
                total_sources=1,
                explored_sources=0,
                total_objects=11,  # 11 checkups, dispatched straight to workers
                scanned_objects=0)

        with (
                patch(
                    "os2datascanner.projects.admin.adminapp.management"
                    ".commands.status_collector.delete_per_scan_queue"
                ) as mock_delete,
                patch(
                    "os2datascanner.projects.admin.adminapp.management"
                    ".commands.status_collector.FinishedScannerNotificationEmail"
                )):
            # The workers clear the checkups...
            for _ in range(11):
                list(status_message_received_raw(worker_status(basic_scan_tag)))

            # ... while seven sub-Sources finish exploring and report the four
            # objects they found between them. The parent Source is still
            # paginating its way through the source and has not yet said
            # that any of these sub-Sources exist.
            for objects in (2, 0, 0, 2, 0, 0, 0):
                list(status_message_received_raw(
                        explorer_status(basic_scan_tag, objects=objects)))
            for _ in range(4):
                list(status_message_received_raw(worker_status(basic_scan_tag)))

            status = ScanStatus.objects.get(scan_tag=scan_tag)
            assert status.explored_sources > status.total_sources, (
                    "test precondition: sub-Sources should have overtaken"
                    " total_sources")
            assert status.scanned_objects == status.total_objects, (
                    "test precondition: workers should have caught up")

            mock_delete.assert_not_called()

            # The parent finally reports, announcing 112 sub-Sources and
            # unlocking thousands of objects the queue is still needed for.
            list(status_message_received_raw(
                    explorer_status(basic_scan_tag, objects=0, new_sources=112)))

            mock_delete.assert_not_called()

        status.refresh_from_db()
        assert status.total_sources == 113
        assert not status.finished


@pytest.mark.django_db
class TestSourceCountCompatibility:
    """The engine and the admin system are separate services on
    separate hosts, so both can be a release ahead of the other. An explorer
    that reports sub-Sources individually still repeats the total when it
    finishes, because an older collector drops the individual reports on the
    floor and would otherwise never learn that the sub-Sources exist."""

    def count_sources(self, basic_scanner, basic_scan_tag, bodies):
        ScanStatus.objects.create(
                scanner=basic_scanner,
                scan_tag=basic_scan_tag.to_json_object(),
                total_sources=1)

        for body in bodies:
            list(status_message_received_raw(body))

        return ScanStatus.objects.get(
                scan_tag=basic_scan_tag.to_json_object()).total_sources

    def test_older_explorer_reports_only_the_total(
            self, basic_scanner, basic_scan_tag):
        """An explorer that predates individual reporting sends one closing
        message carrying the whole count and no marker."""
        assert self.count_sources(basic_scanner, basic_scan_tag, [
                explorer_status(basic_scan_tag, objects=0, new_sources=3),
                ]) == 4

    def test_current_explorer_is_not_counted_twice(
            self, basic_scanner, basic_scan_tag):
        """A current explorer sends three individual reports and then repeats
        the total, marked, on the way out. Only the three may count."""
        assert self.count_sources(basic_scanner, basic_scan_tag, [
                source_discovered(basic_scan_tag),
                source_discovered(basic_scan_tag),
                source_discovered(basic_scan_tag),
                explorer_status(
                        basic_scan_tag, objects=0, new_sources=3,
                        reported_individually=True),
                ]) == 4

    def test_individual_reports_do_not_count_as_exploration(
            self, basic_scanner, basic_scan_tag):
        """Discovering a Source is not exploring it. If these messages moved
        explored_sources, they would recreate the overshoot they exist to
        prevent."""
        ScanStatus.objects.create(
                scanner=basic_scanner,
                scan_tag=basic_scan_tag.to_json_object(),
                total_sources=1)

        for _ in range(3):
            list(status_message_received_raw(source_discovered(basic_scan_tag)))

        status = ScanStatus.objects.get(scan_tag=basic_scan_tag.to_json_object())
        assert status.total_sources == 4
        assert status.explored_sources == 0
