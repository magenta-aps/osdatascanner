# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.utilities.datetime import parse_datetime
from os2datascanner.projects.admin.adminapp.management.commands.status_collector import (
        object_progress_received_raw)
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import ScanStatus
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner_helpers import (
        ActiveObjectStatus)

_SCAN_TIME = "2026-06-22T10:00:00+02:00"


@pytest.fixture
def scan_tag_fragment(basic_scanner):
    # Build a real scan tag with organisation so from_json_object
    tag = basic_scanner._construct_scan_tag()
    # Force a fixed, known time so the ORM lookup (scan_tag__time) can match
    # the heartbeat body's scan_tag.time.
    from dataclasses import replace
    return replace(tag, time=parse_datetime(_SCAN_TIME))


@pytest.fixture
def scan_status(db, basic_scanner, scan_tag_fragment):
    return ScanStatus.objects.create(
            scanner=basic_scanner,
            scan_tag=scan_tag_fragment.to_json_object())


def _heartbeat_body(scan_tag_fragment, *, items, final=False, current_path=""):
    return messages.ObjectProgressMessage(
            scan_tag=scan_tag_fragment,
            object_key="key-1",
            object_path="huge.zip (in /share)",
            current_path=current_path,
            items_processed=items, elapsed_seconds=600,
            final=final).to_json_object()


@pytest.mark.django_db
def test_heartbeat_creates_then_updates_row(scan_status, scan_tag_fragment, basic_scanner):
    list(object_progress_received_raw(_heartbeat_body(
            scan_tag_fragment, items=10, current_path="a.pdf (in huge.zip)")))
    row = ActiveObjectStatus.objects.get(scan_status=scan_status, object_key="key-1")
    assert row.items_processed == 10
    assert row.current_path == "a.pdf (in huge.zip)"

    list(object_progress_received_raw(_heartbeat_body(
            scan_tag_fragment, items=50, current_path="z.pdf (in huge.zip)")))
    row.refresh_from_db()
    assert row.items_processed == 50
    # The current sub-object tracks the latest heartbeat.
    assert row.current_path == "z.pdf (in huge.zip)"
    assert ActiveObjectStatus.objects.filter(scan_status=scan_status).count() == 1


@pytest.mark.django_db
def test_final_heartbeat_removes_row(scan_status, scan_tag_fragment, basic_scanner):
    list(object_progress_received_raw(_heartbeat_body(scan_tag_fragment, items=10)))
    list(object_progress_received_raw(
            _heartbeat_body(scan_tag_fragment, items=10, final=True)))
    assert not ActiveObjectStatus.objects.filter(object_key="key-1").exists()


@pytest.mark.django_db
def test_old_worker_payload_without_additive_fields(
        scan_status, scan_tag_fragment, basic_scanner):
    # A worker from before this feature (or mid rolling-upgrade) sends only the
    # required fields. The collector must tolerate the missing fields
    # and fall back to the defaults.
    body = {
        "type": "object_progress",
        "scan_tag": scan_tag_fragment.to_json_object(),
        "object_key": "key-1",
    }
    list(object_progress_received_raw(body))

    row = ActiveObjectStatus.objects.get(scan_status=scan_status, object_key="key-1")
    assert row.object_path == ""
    assert row.current_path == ""
    assert row.items_processed == 0
    assert row.elapsed_seconds == 0
