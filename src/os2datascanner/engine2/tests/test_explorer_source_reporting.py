# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Tests that the explorer reports independent sub-Sources as it discovers
them.

The admin module counts a Source as explored when it receives that Source's
terminal StatusMessage, and counts it as existing when it receives a
StatusMessage carrying new_sources. If the second only arrives once the parent
has finished walking, then every sub-Source that is explored in the meantime is
counted as explored before it is counted as existing, and explored_sources
overtakes total_sources. The admin module reads that as a finished scan."""

import pytest

from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.pipeline import explorer, messages
from os2datascanner.engine2.rules.regex import RegexRule

from .model import DummySource


class ExpandingDummySource(DummySource):
    """A DummySource whose Handles are wrappers around independent Sources,
    the way every MSGraph Source's are."""
    type_label = "-test-dummy-expanding"
    yields_independent_sources = True


@pytest.fixture
def scan_spec():
    return messages.ScanSpecMessage(
            scan_tag=messages.ScanTagFragment.make_dummy(),
            source=ExpandingDummySource(3, secret="hemmelighed"),
            rule=RegexRule("dummy"),
            configuration={},
            progress=None,
            filter_rule=None)


def explore(scan_spec):
    with SourceManager() as sm:
        return list(explorer.message_received(scan_spec, sm))


class TestSubSourceReporting:

    def test_sub_sources_are_reported_as_they_are_found(self, scan_spec):
        """Every sub-Source must be announced, and announced before the scan
        spec that lets someone else explore it."""
        announced = 0
        for message in explore(scan_spec):
            match message:
                case messages.StatusMessage(
                        new_sources=int() as count,
                        sources_reported_individually=False):
                    announced += count
                case messages.ScanSpecMessage():
                    assert announced > 0, (
                            "a sub-Source was enqueued for exploration before"
                            " it was reported to the admin module")

        assert announced == 3

    def test_terminal_message_repeats_the_total_for_older_readers(self, scan_spec):
        """The terminal StatusMessage still carries the aggregate, because an
        admin system that predates individual reports has no other way
        to learn about these sub-Sources and silently drops the messages that
        announce them. Newer ones are told to disregard it."""
        *_, terminal = explore(scan_spec)

        assert terminal.total_objects == 0
        assert terminal.new_sources == 3
        assert terminal.sources_reported_individually

    def test_only_the_terminal_report_is_marked(self, scan_spec):
        """The marker means "these sources were already reported one by one",
        so it belongs on the terminal message and nowhere else. On a discovery
        report it would tell the collector to skip the very count that message
        exists to deliver."""
        *discoveries, terminal = [
                m for m in explore(scan_spec)
                if isinstance(m, messages.StatusMessage) and m.new_sources]

        assert len(discoveries) == 3
        assert not any(m.sources_reported_individually for m in discoveries)
        assert terminal.sources_reported_individually

    def test_aggregate_matches_the_individual_reports(self, scan_spec):
        """The two counts have different audiences and no reader ever sees
        both, so nothing can notice them drifting apart. If they
        ever do, two administration systems will derive different totals from
        the same scan, and only the older one will be wrong."""
        *discoveries, terminal = [
                m for m in explore(scan_spec)
                if isinstance(m, messages.StatusMessage) and m.new_sources]

        assert terminal.new_sources == sum(m.new_sources for m in discoveries)

    def test_marker_survives_serialisation(self, scan_spec):
        """The marker has to reach the admin module intact, and its absence
        from an older explorer's message has to read as False."""
        *_, terminal = explore(scan_spec)
        round_tripped = messages.StatusMessage.from_json_object(
                terminal.to_json_object())

        assert round_tripped.sources_reported_individually

        legacy = terminal.to_json_object()
        del legacy["sources_reported_individually"]

        assert not messages.StatusMessage.from_json_object(
                legacy).sources_reported_individually

    def test_announcement_precedes_every_spec(self, scan_spec):
        """Pairwise ordering, not just the aggregate: the nth announcement
        comes before the nth scan spec."""
        interesting = [
                type(m).__name__ for m in explore(scan_spec)
                if isinstance(m, messages.ScanSpecMessage)
                or (isinstance(m, messages.StatusMessage)
                    and m.new_sources
                    and not m.sources_reported_individually)]

        assert interesting == [
                "StatusMessage", "ScanSpecMessage"] * 3
