# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from typing import Iterable


def is_one_of(mime_type: str, patterns: Iterable[str]) -> bool:
    """Whether @mime_type is named by any of @patterns.

    A pattern is either a MIME type ("application/pdf") or one ending in a
    trailing wildcard ("image/*")."""
    if not mime_type:
        return False

    return any(
            mime_type.startswith(pattern[:-1]) if pattern.endswith("*")
            else mime_type == pattern
            for pattern in patterns)
