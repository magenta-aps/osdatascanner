# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from typing import Generator

from .. import messages


def dispatch(
        generator: Generator[messages.SerialisableMessage],
        *mapping: tuple[type, list[str]]) -> Generator[tuple[str, dict]]:
    """Converts messages produced by a generator into (queue_name, dict) pairs.
    (Intended to serve as a generic implementation of message_received_raw.)"""
    for message in generator:
        for type_, queues in mapping:
            if isinstance(message, type_):
                json_form = message.to_json_object()
                yield from ((q, json_form) for q in queues)
                break
        else:
            raise TypeError(type(message))
