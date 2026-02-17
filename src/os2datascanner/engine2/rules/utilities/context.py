# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

def make_context(match, text, func=None):
    """Returns the (optionally postprocessed) context surrounding a match."""
    if isinstance(match, tuple):
        low, high = match
    else:
        low, high = match.span()
    ctx_low, ctx_high = max(low - 50, 0), high + 50
    # Extract context, remove newlines and tabs for better representation
    match_context = " ".join(text[ctx_low:ctx_high].split())

    return {
        "offset": low,
        "context": match_context,
        "context_offset": low - ctx_low
    }
