# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Convenience imports for using engine2 interactively."""
# flake8: noqa

from os2datascanner.engine2.model.core import (
        Source, Handle, SourceManager)
from os2datascanner.engine2.rules.cpr import CPRRule
# Don't shadow the admin database's Rule model
from os2datascanner.engine2.rules.rule import Rule as E2Rule
from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.conversions.types import OutputType
from os2datascanner.engine2.conversions.registry import convert
