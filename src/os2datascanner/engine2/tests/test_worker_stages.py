# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""The worker's relaying of one stage's output to the next.

The worker runs the explorer, processor, matcher and tagger in one process, so
what would be a queue between two stages is a function call here. The route
covered below is the one with no queue equivalent to fall back on: a rule tree
that needs a representation the first conversion did not produce, which sends the
object back through the processor from inside the matcher."""

import os
import shutil
import tempfile

import pytest

from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.file import FilesystemHandle, FilesystemSource
from os2datascanner.engine2.pipeline import messages, worker
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
from os2datascanner.engine2.rules.logical import AndRule
from os2datascanner.engine2.utilities.datetime import parse_datetime

CONTENT = "Sagsbehandler noter. Borgerens CPR er 1111111118.\n"


@pytest.fixture
def two_representations():
    """A scan asking a question that cannot be answered by one conversion.

    LastModifiedRule is answered from the object's modification date and CPRRule
    from its text, so the matcher concludes the first and then has to ask the
    processor for a representation it was not given. The cutoff is far enough in
    the past that the first half always concludes in favour of the second."""
    root = tempfile.mkdtemp()
    with open(os.path.join(root, "report.txt"), "w") as fp:
        fp.write(CONTENT)

    source = FilesystemSource(root)
    yield messages.ConversionMessage(
            scan_spec=messages.ScanSpecMessage(
                    scan_tag=messages.ScanTagFragment.make_dummy(),
                    source=source,
                    rule=(rule := AndRule(
                            LastModifiedRule(
                                    parse_datetime("2000-01-01T00:00:00+00:00")),
                            CPRRule())),
                    configuration={}, filter_rule=None, progress=None),
            handle=FilesystemHandle(source, "report.txt"),
            progress=messages.ProgressFragment(rule=rule, matches=[]))

    shutil.rmtree(root, ignore_errors=True)


def matches_in(emitted):
    return [body for queue, body, *_ in emitted if queue == "os2ds_matches"]


def fragments_in(emitted):
    return {
        fragment["rule"]["type"]: fragment
        for body in matches_in(emitted)
        for fragment in body["matches"]}


class TestASecondRepresentation:
    def test_the_object_goes_back_through_the_processor(
            self, two_representations):
        """Both halves of the question are answered, which can only happen if
        the matcher's request for a second representation reached the processor
        and came back."""
        with SourceManager() as sm:
            emitted = list(worker.message_received_raw(
                    two_representations.to_json_object(),
                    "os2ds_conversions", sm))

        fragments = fragments_in(emitted)
        assert "last-modified" in fragments, (
                f"the first representation was never evaluated: {fragments}")
        assert "cpr" in fragments, (
                "the matcher's request for a second representation did not come"
                f" back: {fragments}")
        assert fragments["cpr"]["matches"], fragments["cpr"]
        assert all(body["matched"] for body in matches_in(emitted))

    def test_the_object_is_reported_once(self, two_representations):
        """Being converted twice is not being scanned twice."""
        with SourceManager() as sm:
            emitted = list(worker.message_received_raw(
                    two_representations.to_json_object(),
                    "os2ds_conversions", sm))

        scanned = [
                body for queue, body, *_ in emitted
                if queue == "os2ds_status"
                and body.get("object_size") is not None]
        assert len(scanned) == 1, scanned
        assert len(matches_in(emitted)) == 1, matches_in(emitted)
