# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Putting a conversion message down and picking it up again later.

A worker that cannot get on with an object yet, another worker being busy with
its content (see deduplication), republishes it into a queue that holds it for a
while and then dead-letters it back to the conversion queue it came from, and
acks the original delivery.

Three properties of the topology are load-bearing: nothing consumes the delay
queues, one queue per delay rather than a per-message expiry, and routing in by
header so that the routing key survives for the return hop.

The settings this reads live under [pipeline.worker.dedup], deduplication being
the only caller.
"""

from dataclasses import dataclass
from typing import Optional

import structlog

from ... import settings

logger = structlog.get_logger("deferral")


DEFERRAL_EXCHANGE = "osds_dedup_deferral"
DEFERRAL_QUEUE_PREFIX = "osds_dedup_deferred"
DEFERRAL_HEADER = "dedup-delay-ms"

# Where the bookkeeping lives on a ConversionMessage.
DEFERRAL_KEY = "dedup_deferral"


def _conf() -> dict:
    return settings.pipeline["worker"]["dedup"]


def backoff_steps() -> list[int]:
    return [int(ms) for ms in _conf()["backoff_ms"]]


@dataclass(frozen=True, slots=True, kw_only=True)
class Deferral:
    """An instruction to put this object back and pick it up later, because
    another worker is converting its content right now."""
    delay_ms: int
    body: dict


def plan_deferral(body: dict, message):
    """Returns the Deferral that puts an object down for a while, or None once it
    has waited as long as it is allowed to and should convert instead."""
    if (plan := next_deferral(body)) is not None:
        delay_ms, deferred_body = plan
        return Deferral(delay_ms=delay_ms, body=deferred_body)

    # This copy has waited as long as it is allowed to. Convert it rather than
    # risk never scanning it at all.
    logger.warning(
            "deferral budget spent, converting duplicate anyway",
            handle=str(message.handle))
    return None


def queue_name(delay_ms: int) -> str:
    """Names the delay queue holding messages for delay_ms.

    The delay is part of the name because a queue's TTL is fixed at declaration,
    so changing the configured backoff brings new queues into use rather than
    colliding with the old ones."""
    return f"{DEFERRAL_QUEUE_PREFIX}.{delay_ms}"


def declare_queues(channel) -> None:
    """Declares the exchange and delay queues."""
    channel.exchange_declare(
            DEFERRAL_EXCHANGE,
            exchange_type="headers", durable=True, auto_delete=False)

    for delay_ms in backoff_steps():
        name = queue_name(delay_ms)
        channel.queue_declare(
                name, durable=True, exclusive=False, auto_delete=False,
                arguments={
                    "x-message-ttl": delay_ms,
                    # The empty exchange is the default one, which routes on the
                    # message's own routing key.
                    "x-dead-letter-exchange": "",
                })
        channel.queue_bind(
                exchange=DEFERRAL_EXCHANGE, queue=name,
                arguments={
                    "x-match": "all",
                    DEFERRAL_HEADER: str(delay_ms),
                })

    logger.info("deferral queues declared", delays=backoff_steps())


def publication(routing_key: str, delay_ms: int, body: dict) -> tuple:
    """Builds the tuple a stage yields to defer.

    The routing key stays the queue the message came from: the delay queue
    selects itself on the header, so that when the message expires the
    dead-letter hop routes it back."""
    return (routing_key, body, DEFERRAL_EXCHANGE,
            {"headers": {DEFERRAL_HEADER: str(delay_ms)}})


def next_deferral(body: dict) -> Optional[tuple[int, dict]]:
    """Plans the next deferral for a conversion message: how long to hold it and
    a copy of the body carrying the updated bookkeeping.

    None once the object has waited as long as it is allowed to."""
    state = body.get(DEFERRAL_KEY) or {}
    attempts = int(state.get("attempts", 0))
    waited = int(state.get("waited_ms", 0))

    if not (steps := backoff_steps()):
        # Nowhere to put the object down, so the caller gets on with converting
        # it. Configuring no delays at all is how deferral is switched off.
        return None

    # Once past the end of the list the final delay repeats, so waiting settles
    # into a steady poll rather than growing without bound.
    delay = steps[min(attempts, len(steps) - 1)]

    if waited + delay > int(_conf()["max_deferral_ms"]):
        return None

    return delay, body | {
        DEFERRAL_KEY: {
            "attempts": attempts + 1,
            "waited_ms": waited + delay,
        },
    }
