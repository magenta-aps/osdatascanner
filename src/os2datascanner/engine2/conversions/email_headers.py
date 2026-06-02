# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import email.policy
from collections.abc import Iterable
from email.parser import BytesHeaderParser

from .types import OutputType
from .registry import conversion


# TODO: #XXX, idea: these are just header values we can imagine someone might scan for,
# and it's very noisy to store the entire email-headers in our json messages and raw_X
# DocumentReport fields. A future version _may_ dynamically choose what to store, based on
# what Rule we're using?
HINTABLE_HEADERS = frozenset({
    "subject", "from", "sender", "to", "cc", "bcc", "date", "reply-to",
    "thread-topic",
})


def email_headers_hint(
        pairs: Iterable[tuple[str, str]]) -> dict[str, dict[str, str]] | None:
    """
    Helper function for use in Source classes that have to do with email.
    Helps to build a handle hint of email headers. Those are often cheap to get early, and can
    be handy if f.e. we're scanning an email attachment with an image in, with a rule that must
    also look at email headers. Child objects can then read this hint, instead of rewinding the
    hierarchy and redownloading the whole email again.

    @pairs is an iterable of (name, value) header pairs.

    Returns None if there are no headers, or a dictionary if there is at least one header.
    Returning None will mean using whatever fallback strategy is in place, i.e. downloading the
    email, so it's up the Source, to implement this.
    """
    headers = {
        name.lower(): value for name, value in pairs
        if name.lower() in HINTABLE_HEADERS
    }
    if not headers:
        return None
    return {OutputType.EmailHeaders.value: headers}


@conversion(OutputType.EmailHeaders,
            "message/rfc822")
def headers_processor(r, **kwargs):
    with r.make_stream() as fp:
        message = BytesHeaderParser(policy=email.policy.default).parse(fp)
    return dict((k.lower(), v) for k, v in message.items())
