# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Utilities for filtering handles based on exclusion rules
and type rules."""
import structlog

from ...model.core import Handle
from ...rules.rule import Rule
from os2datascanner.engine2.conversions.types import OutputType

logger = structlog.get_logger("engine2")


def is_handle_relevant(handle: Handle, filter_rule: Rule) -> bool:
    """
    Checks whether a handle should be skipped based on the
    exclusion rule specified by a ScanSpecMessage and the global
    TypeRules.
    """

    # Let everything pass if there is no filter_rule set.
    if filter_rule is None:
        return True

    # Apply the rule to the presentation of the handle.
    try:
        representations = {output_type.value: None for output_type in OutputType}
        representations[OutputType.Presentation.value] = str(handle)
        if size := handle.hint("size"):
            representations[OutputType.Size.value] = size

        conclusion, _ = filter_rule.try_match(representations, obj_limit=1)
        return not conclusion
    except KeyError as error:
        exception_message = f"Filtering error. {type(error).__name__}: "
        exception_message += ", ".join([str(a) for a in error.args])

        logger.warning(exception_message)
        return True
