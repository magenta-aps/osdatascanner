# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import copy

import pytest
from django.core.management import call_command

from ..reportapp.management.commands import result_collector
from ..reportapp.models.documentreport import DocumentReport
from .generate_test_data import record_match
from os2datascanner.engine2.pipeline import messages


@pytest.fixture
def sbsys_backfill_match(common_scan_spec, scan_tag0, common_rule, sbsys_document_handle):
    return messages.MatchesMessage(
        scan_spec=messages.replace(common_scan_spec, scan_tag=scan_tag0),
        handle=sbsys_document_handle,
        matched=True,
        matches=[messages.MatchFragment(rule=common_rule, matches=[{"dummy": "m"}])])


@pytest.mark.django_db
class TestBackfillSbsysContainers:
    def test_backfills_container_for_existing_report(self, sbsys_backfill_match):
        record_match(sbsys_backfill_match)
        dr = result_collector.DocumentReport.objects.get()
        # Simulate a report that predates this feature.
        dr.container = None
        dr.save(update_fields=["container"])

        call_command("backfill_sbsys_containers")

        dr.refresh_from_db()
        assert dr.container is not None

    def test_backfills_a_report_whose_match_count_is_stale(self, sbsys_backfill_match):
        """A legacy row whose stored number_of_matches disagrees with a fresh
        recount of its matches must still be linked. (Going through
        DocumentReport.save() would fail here: its recount expects
        update_fields to be a set.)"""
        record_match(sbsys_backfill_match)
        DocumentReport.objects.update(container=None, number_of_matches=99)

        call_command("backfill_sbsys_containers")

        dr = DocumentReport.objects.get()
        assert dr.container is not None
        # Purely additive: nothing but the container was written.
        assert dr.number_of_matches == 99

    def test_one_undeserialisable_report_does_not_stop_the_run(
            self, sbsys_match_document, sbsys_match_field):
        """A row the engine can no longer deserialise is skipped, and the
        remaining rows of the same run are still processed."""
        record_match(sbsys_match_document)
        record_match(sbsys_match_field)
        DocumentReport.objects.update(container=None)

        broken, healthy = list(DocumentReport.objects.order_by("pk"))
        broken_matches = copy.deepcopy(broken.raw_matches)
        broken_matches["handle"]["type"] = "no-such-scheme"
        DocumentReport.objects.filter(pk=broken.pk).update(raw_matches=broken_matches)

        call_command("backfill_sbsys_containers")

        broken.refresh_from_db()
        healthy.refresh_from_db()
        assert broken.container is None
        assert healthy.container is not None

    def test_leaves_already_linked_reports_alone(self, sbsys_backfill_match):
        record_match(sbsys_backfill_match)
        dr = result_collector.DocumentReport.objects.get()
        original_container_id = dr.container_id
        assert original_container_id is not None

        call_command("backfill_sbsys_containers")

        dr.refresh_from_db()
        assert dr.container_id == original_container_id
