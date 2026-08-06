# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.pipeline import explorer, messages
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.engine2.rules.presentation import PresentationRule

from .model import DummySource, DummyHandle


class FailingDummySource(DummySource):
    """A DummySource whose second Handle is reported alongside an exception,
    the way SMBCSource's is when it hits a MemoryError."""
    type_label = "-test-dummy-erring"

    def handles(self, sm, **kwargs):
        for k in range(0, self._count):
            handle = DummyHandle(self, str(k))
            if k == 1:
                yield (handle, ValueError("bad encoding"))
            else:
                yield handle


@pytest.fixture
def scan_spec():
    """A scan spec with a source producing 3 handles, the 2nd of which has an error."""
    return messages.ScanSpecMessage(
            scan_tag=messages.ScanTagFragment.make_dummy(),
            source=FailingDummySource(3, secret="hemmelighed"),
            rule=RegexRule("dummy"),
            configuration={},
            progress=None,
            filter_rule=PresentationRule(RegexRule("private")))  # Shouldn't match the handles


def explore(scan_spec):
    with SourceManager() as sm:
        return list(explorer.message_received(scan_spec, sm))


class TestHandleErrorReporting:
    def test_a_problem_message_is_sent_for_the_error_handle(self, scan_spec):
        """A (Handle, Exception) pair must turn into a ProblemMessage."""
        problems = [
                m for m in explore(scan_spec)
                if isinstance(m, messages.ProblemMessage)]

        assert len(problems) == 1

    def test_exploration_continues_past_the_error_handle(self, scan_spec):
        """A problem with one Handle must not stop the rest of the Source
        from being explored."""
        conversions = [
                m for m in explore(scan_spec)
                if isinstance(m, messages.ConversionMessage)]
        assert len(conversions) == 2
