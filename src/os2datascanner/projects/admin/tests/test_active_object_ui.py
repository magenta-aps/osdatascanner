# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from django.urls import reverse_lazy
from django.utils import timezone

from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import ScanStatus
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner_helpers import (
        ActiveObjectStatus)


@pytest.fixture
def running_status(db, basic_scanner):
    # total_sources > explored_sources keeps the scan in a running (indexing)
    # stage so it shows up in the status overview without being "completed".
    tag = basic_scanner._construct_scan_tag().to_json_object()
    return ScanStatus.objects.create(
            scanner=basic_scanner, scan_tag=tag,
            total_sources=10, explored_sources=2)


def _add_active(status, key, path, minutes, current_path=""):
    return ActiveObjectStatus.objects.create(
            scan_status=status, object_key=key, object_path=path,
            current_path=current_path,
            items_processed=100,
            elapsed_seconds=minutes * 60, last_heartbeat=timezone.now())


@pytest.mark.django_db
class TestActiveObjectSummary:

    def test_summary_is_none_when_no_active_objects(self, running_status):
        assert running_status.active_object_summary is None

    def test_summary_counts_rows_and_takes_longest_elapsed(self, running_status):
        _add_active(running_status, "k1", "a.zip", 5)
        _add_active(running_status, "k2", "b.zip", 14)
        summary = running_status.active_object_summary
        assert summary.count == 2
        assert summary.max_minutes == 14

    def test_poll_renders_oob_list_target_even_when_empty(
            self, client, superuser, running_status):
        # It has to exist, to be swapped in, when something comes along..
        client.force_login(superuser)
        response = client.get(
                reverse_lazy("status"),
                {"reload": "#status_table_poll", "scans": 1},
                HTTP_HX_REQUEST="true",
                HTTP_HX_TRIGGER_NAME="status_table_poll")
        content = response.content.decode()

        assert f'id="active_objects_list__{running_status.pk}"' in content
        assert "hx-swap-oob" in content
        # No objects, so no per-object rows yet.
        assert 'class="active-object ' not in content
