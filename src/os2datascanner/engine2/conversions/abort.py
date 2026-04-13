# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from collections.abc import Callable
from contextvars import ContextVar

"""A `() -> bool` callable that converters call to check if their scan was cancelled.

The processor sets it before running each conversion and it is wired by
workers process() method.

Converters that can't interrupt a blocking call (f.e. OCR) should poll it before starting
that call."""
current_abort_check: ContextVar[Callable[[], bool] | None] = ContextVar(
    'current_abort_check', default=None)
