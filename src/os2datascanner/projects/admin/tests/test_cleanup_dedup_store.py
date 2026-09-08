# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the command that clears the deduplication store, run against a
real store.

What the command is for is the keys the per-scan index has lost track of, so a
fake store standing in for the keyspace walk would test the wrong thing. The
tests skip themselves when no store is reachable."""

from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.pipeline.utilities import deduplication
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner_helpers import (
        ScanStatus)
# Borrowed rather than copied, so that the admin suite and the engine suite
# connect to the store the same way.
from os2datascanner.engine2.tests.conftest import dedup_client  # noqa: F401


@pytest.fixture
def store(dedup_client):  # noqa: F811
    """The store the engine settings name, emptied around each test."""
    return dedup_client


def _scan_id(scan_status) -> str:
    return deduplication.scan_identity(
            messages.ScanTagFragment.from_json_object(scan_status.scan_tag))


def _populate(client, scan_id, *, indexed=True):
    """Writes one scan's worth of keys: a claim, a result, and optionally the
    index that a well-behaved purge would have read."""
    client.set(f"claim:{scan_id}:deadbeef:text/plain:00", "worker")
    client.set(f"result:{scan_id}:deadbeef:text/plain:00", "{}")
    if indexed:
        client.sadd(
                f"keys:{scan_id}",
                f"claim:{scan_id}:deadbeef:text/plain:00",
                f"result:{scan_id}:deadbeef:text/plain:00")


def _keys(client) -> set[str]:
    return {k.decode() for k in client.keys("*")}


def _scan_tag(scanner, hour: int) -> dict:
    """This scanner's tag with an explicit start time, one scan per hour.

    A scan tag is unique, and _construct_scan_tag() reads the clock, so two
    scans built in the same second are the same scan."""
    return scanner._construct_scan_tag().to_json_object() | {
            "time": f"2026-01-01T{hour:02}:00:00+00:00"}


def _running(scanner, hour: int = 1) -> ScanStatus:
    return ScanStatus.objects.create(
            scanner=scanner, scan_tag=_scan_tag(scanner, hour),
            total_sources=1, explored_sources=1,
            total_objects=5, scanned_objects=4)


def _finished(scanner, hour: int = 2) -> ScanStatus:
    return ScanStatus.objects.create(
            scanner=scanner, scan_tag=_scan_tag(scanner, hour),
            total_sources=1, explored_sources=1,
            total_objects=5, scanned_objects=5)


def _run(**options) -> str:
    out = StringIO()
    call_command("cleanup_dedup_store", stdout=out, **options)
    return out.getvalue()


@pytest.mark.django_db
class TestCleanupDedupStore:
    def test_a_finished_scan_s_keys_go(self, store, basic_scanner):
        scan_id = _scan_id(_finished(basic_scanner))
        _populate(store, scan_id)

        _run()

        assert _keys(store) == set()

    def test_a_running_scan_s_keys_stay(self, store, basic_scanner):
        """Deleting these would cost the scan the conversions it is sharing,
        every copy converting the content again."""
        scan_id = _scan_id(_running(basic_scanner))
        _populate(store, scan_id)

        _run()

        assert len(_keys(store)) == 3

    def test_an_unindexed_scan_s_keys_go(self, store, basic_scanner):
        """The case the command exists for: a purge that never ran, or ran
        against an index that had already expired, leaves keys no index names.
        Walking the keyspace is what finds them."""
        scan_id = _scan_id(_finished(basic_scanner))
        _populate(store, scan_id, indexed=False)

        _run()

        assert _keys(store) == set()

    def test_keys_of_a_scan_nothing_knows_about_go(self, store):
        """A scan whose ScanStatus has been deleted leaves keys that no longer
        correspond to anything in the database."""
        _populate(store, "9999:2026-01-01T00:00:00+00:00")

        _run()

        assert _keys(store) == set()

    def test_include_running_spares_nothing(self, store, basic_scanner):
        scan_id = _scan_id(_running(basic_scanner))
        _populate(store, scan_id)

        _run(include_running=True)

        assert _keys(store) == set()

    def test_all_empties_the_store(self, store, basic_scanner):
        _populate(store, _scan_id(_running(basic_scanner)))
        _populate(store, _scan_id(_finished(basic_scanner)))
        _populate(store, "9999:2026-01-01T00:00:00+00:00")

        _run(everything=True)

        assert _keys(store) == set()

    def test_all_leaves_other_keys_alone(self, store, basic_scanner):
        """"Everything" means everything this feature wrote, not everything in
        the store, which need not be ours alone."""
        store.set("something:else", "1")
        _populate(store, _scan_id(_running(basic_scanner)))

        _run(everything=True)

        assert _keys(store) == {"something:else"}

    def test_all_refuses_to_be_narrowed(self, store, basic_scanner):
        """--all and the options that restrict what is deleted contradict each
        other, and guessing which the operator meant is not this command's
        business."""
        with pytest.raises(CommandError):
            _run(everything=True, scanner=basic_scanner.pk)
        with pytest.raises(CommandError):
            _run(everything=True, include_running=True)

    def test_scanner_restricts_to_one_job(self, store, basic_scanner):
        mine = _scan_id(_finished(basic_scanner))
        _populate(store, mine)
        _populate(store, "9999:2026-01-01T00:00:00+00:00")

        _run(scanner=basic_scanner.pk)

        assert _keys(store) == {
                "claim:9999:2026-01-01T00:00:00+00:00:deadbeef:text/plain:00",
                "result:9999:2026-01-01T00:00:00+00:00:deadbeef:text/plain:00",
                "keys:9999:2026-01-01T00:00:00+00:00"}

    def test_dry_run_deletes_nothing(self, store, basic_scanner):
        scan_id = _scan_id(_finished(basic_scanner))
        _populate(store, scan_id)

        output = _run(dry_run=True)

        assert len(_keys(store)) == 3
        assert "would delete 3 key(s)" in output

    def test_other_keys_are_left_alone(self, store, basic_scanner):
        """The store may not be ours alone, and nothing outside the three key
        families is any of this command's business."""
        store.set("something:else", "1")
        _populate(store, _scan_id(_finished(basic_scanner)))

        _run()

        assert _keys(store) == {"something:else"}

    def test_the_orphaned_scan_is_named(self, store, basic_scanner):
        scan_id = _scan_id(_finished(basic_scanner))
        _populate(store, scan_id)

        assert scan_id in _run()
