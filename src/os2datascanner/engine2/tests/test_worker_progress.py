# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from os2datascanner.engine2.pipeline import worker, messages
from os2datascanner.engine2.pipeline.messages import ScanTagFragment, ScannerFragment


def _scan_tag():
    return ScanTagFragment(
            time=messages.parse_datetime("2026-06-22T10:00:00+02:00"),
            scanner=ScannerFragment(pk=1, name="test"),
            user=None, organisation=None, destination=None)


def _fresh_tracker():
    t = worker._ProgressTracker()
    t.reset(scan_tag=_scan_tag(), object_key="k", object_path="top.zip")
    # Make the threshold trivially crossable in tests.
    t.threshold = 0
    t.interval = 0
    return t


def test_tick_increments_and_emits_after_threshold(monkeypatch):
    clock = {"t": 1000.0}
    monkeypatch.setattr(worker.time, "monotonic", lambda: clock["t"])
    t = _fresh_tracker()
    t.started_at = 1000.0

    clock["t"] = 1000.5
    msg = t.tick("page 12 (in report.pdf (in top.zip))")
    assert isinstance(msg, messages.ObjectProgressMessage)
    assert msg.items_processed == 1
    assert msg.final is False
    assert msg.current_path == "page 12 (in report.pdf (in top.zip))"


def test_tick_respects_interval(monkeypatch):
    clock = {"t": 1000.0}
    monkeypatch.setattr(worker.time, "monotonic", lambda: clock["t"])
    t = _fresh_tracker()
    t.started_at = 1000.0
    t.threshold = 0
    t.interval = 10

    clock["t"] = 1001.0
    assert t.tick("a") is not None      # first emission
    clock["t"] = 1005.0
    assert t.tick("b") is None          # within interval, suppressed
    assert t.items_processed == 2       # but still counted
    clock["t"] = 1012.0
    assert t.tick("c") is not None      # interval elapsed, emits again


def test_no_heartbeat_means_no_terminal():
    t = worker._ProgressTracker()
    t.reset(scan_tag=_scan_tag(), object_key="k", object_path="top.zip")
    t.threshold = 999999       # never crosses
    assert t.tick("x") is None
    assert t.terminal() is None    # nothing was tracked, so no terminal


def test_terminal_emitted_after_heartbeat(monkeypatch):
    clock = {"t": 1000.0}
    monkeypatch.setattr(worker.time, "monotonic", lambda: clock["t"])
    t = _fresh_tracker()
    t.started_at = 1000.0
    clock["t"] = 1001.0
    assert t.tick("sub.pdf") is not None
    term = t.terminal()
    assert term is not None
    assert term.final is True
    assert term.object_key == "k"
