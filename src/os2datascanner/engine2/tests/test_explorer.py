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

ACCOUNT_UUID = "11111111-1111-1111-1111-111111111111"


def _make_spec(account_uuid=None):
    scan_tag = messages.ScanTagFragment(
            time=None, user=None, scanner=None, organisation=None)
    return messages.ScanSpecMessage(
            scan_tag=scan_tag,
            source=DummySource(3, secret="hunter2"),
            rule=True,
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


def test_exploration_failure_still_marks_status_message_as_error():
    """Unchanged behaviour check: the StatusMessage emitted on failure must
    still have status_is_error=True regardless of account_uuid (StatusMessage
    itself does not carry account_uuid -- see design doc non-goals)."""
    spec = _make_spec(account_uuid=ACCOUNT_UUID)

    with SourceManager() as sm, patch.object(spec.source, "handles", _failer):
        results = list(message_received(spec, sm))

    statuses = [m for m in results if isinstance(m, messages.StatusMessage)]
    assert len(statuses) == 1
    assert statuses[0].status_is_error is True
    assert not hasattr(statuses[0], "account_uuid")
