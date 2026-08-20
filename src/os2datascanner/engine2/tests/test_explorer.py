# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from unittest.mock import patch

from os2datascanner.engine2.model.core.utilities import SourceManager
from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.pipeline.explorer import (
        message_received, process_exploration_error)

from .model import DummySource, DummyHandle
from ..rules.regex import RegexRule

ACCOUNT_UUID = "11111111-1111-1111-1111-111111111111"


def _make_spec(account_uuid=None):
    return messages.ScanSpecMessage(
            scan_tag=messages.ScanTagFragment.make_dummy(),
            source=DummySource(3, secret="hunter2"),
            rule=RegexRule("dummy"),
            configuration={},
            progress=None,
            filter_rule=None,
            account_uuid=account_uuid)


def _failer(sm, **kwargs):
    raise ValueError("boom")
    yield from ()


def test_exploration_failure_forwards_account_uuid_to_problem_message():
    spec = _make_spec(account_uuid=ACCOUNT_UUID)

    with SourceManager() as sm, patch.object(spec.source, "handles", _failer):
        results = list(message_received(spec, sm))

    problems = [m for m in results if isinstance(m, messages.ProblemMessage)]
    assert len(problems) == 1
    assert problems[0].account_uuid == ACCOUNT_UUID


def test_exploration_failure_with_no_account_uuid_leaves_it_none():
    spec = _make_spec(account_uuid=None)

    with SourceManager() as sm, patch.object(spec.source, "handles", _failer):
        results = list(message_received(spec, sm))

    problems = [m for m in results if isinstance(m, messages.ProblemMessage)]
    assert len(problems) == 1
    assert problems[0].account_uuid is None


def test_process_exploration_error_never_sets_account_uuid():
    """process_exploration_error fires for a single broken object inside a
    Source that otherwise explored fine - it must never be able to flag a
    whole account as errored, regardless of the ScanSpecMessage's own
    account_uuid."""
    spec = _make_spec(account_uuid=ACCOUNT_UUID)
    handle_candidate = DummyHandle(spec.source, "1")

    problems = list(process_exploration_error(
            spec, handle_candidate, ValueError("boom")))

    assert len(problems) == 1
    assert isinstance(problems[0], messages.ProblemMessage)
    assert problems[0].account_uuid is None


def test_exploration_failure_with_no_account_uuid_still_marks_status_message_as_error():
    """Unchanged behaviour check: a top-level exploration failure that isn't
    tied to a specific account still has to flag the whole scan as errored --
    there's no CoveredAccount to carry that information instead."""
    spec = _make_spec(account_uuid=None)

    with SourceManager() as sm, patch.object(spec.source, "handles", _failer):
        results = list(message_received(spec, sm))

    statuses = [m for m in results if isinstance(m, messages.StatusMessage)]
    assert len(statuses) == 1
    assert statuses[0].status_is_error is True


def test_account_attributed_failure_does_not_mark_scan_as_errored():
    """A top-level exploration failure tied to a specific account must not
    flag the whole scan as errored: other accounts covered by the same scan
    may still be explored successfully. The failure is instead tracked
    per-account via the ProblemMessage's account_uuid (see
    checkup_collector.record_account_exploration_error)."""
    spec = _make_spec(account_uuid=ACCOUNT_UUID)

    with SourceManager() as sm, patch.object(spec.source, "handles", _failer):
        results = list(message_received(spec, sm))

    statuses = [m for m in results if isinstance(m, messages.StatusMessage)]
    assert len(statuses) == 1
    assert statuses[0].status_is_error is False
