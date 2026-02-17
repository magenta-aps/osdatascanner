# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import email

from .types import OutputType
from .registry import conversion


@conversion(OutputType.EmailHeaders,
            "message/rfc822")
def headers_processor(r, **kwargs):
    with r.make_stream() as fp:
        message = email.message_from_binary_file(
                fp, policy=email.policy.default)
    return dict((k.lower(), v) for k, v in message.items())
