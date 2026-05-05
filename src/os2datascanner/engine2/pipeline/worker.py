# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import json
from collections.abc import Generator
import structlog

from os2datascanner.engine2.model.core.utilities import SourceManager
from os2datascanner.engine2 import settings

from ..utilities.backoff import TimeoutRetrier
from .utilities.stage import dispatch
from .explorer import message_received as explorer_handler
from .processor import message_received as processor_handler
from .matcher import message_received as matcher_handler
from .tagger import message_received as tagger_handler
from . import messages
import time

logger = structlog.get_logger("worker")


READS_QUEUES = ("os2ds_conversions",)  # INTERNAL PYTHON PSEUDO-QUEUE AND LEGACY RABBITMQ QUEUE
WRITES_QUEUES = (
    "os2ds_matches",
    "os2ds_checkups",
    "os2ds_problems",
    "os2ds_metadata",
    "os2ds_status",)
PROMETHEUS_DESCRIPTION = "Messages handled by worker"

# Let the Pika background thread aggressively collect tasks. Workers should
# always be doing something -- every centisecond of RabbitMQ overhead is time
# wasted!
# TODO: This was once 8, but has been turned down to 2 for consumer switching purposes, revisit
# this if performance issues occur.
PREFETCH_COUNT = 2

_cancelled_tags: set = set()
"""Scan tags for which processing should be aborted as soon as possible.
Populated by notify_abort() when the runner receives an abort command while
a worker is mid-processing. Checked in explore() between sub-items so that
a large scan (e.g. a 1000-page PDF) stops between pages rather than running
to completion."""


def notify_abort(scan_tag) -> None:
    """Register a scan tag as cancelled so that in-progress processing stops
    at the next inter-page boundary in explore()."""
    logger.info("scan abort received, will stop at next checkpoint", scan_tag=scan_tag)
    _cancelled_tags.add(scan_tag)


def determine_channel(scan_spec, for_type: str) -> str:
    scan_spec_obj = messages.ScanSpecMessage.from_json_object(scan_spec)
    if for_type == "explorer":
        return scan_spec_obj.explorer_queue
    elif for_type == "conversion":
        return scan_spec_obj.conversion_queue
    else:
        logger.warning("Asked to determine channel for unknown type", for_type=for_type)


def explore(
        sm: SourceManager, msg: messages.ScanSpecMessage,
        *, check=True) -> Generator[messages.SerialisableMessage]:
    for m in explorer_handler(msg, sm):
        if msg.scan_tag in _cancelled_tags:
            # Scan has been cancelled, stop processing
            return
        if isinstance(m, messages.ConversionMessage):
            yield from process(sm, m, check=check)
        elif isinstance(m, messages.ScanSpecMessage):
            # Huh? Surely a standalone explorer should have handled this
            logger.warning("worker exploring unexpected nested Source")
            yield from explore(sm, m, check=check)
        elif isinstance(m, messages.StatusMessage):
            # Explorer status messages are not interesting in the worker
            # context
            pass
        else:
            yield m


def process(
        sm: SourceManager, msg: messages.ConversionMessage,
        *, check=True) -> Generator[messages.SerialisableMessage]:

    scan_tag = msg.scan_spec.scan_tag

    def should_abort():
        return scan_tag in _cancelled_tags

    if should_abort():
        # Scan has been cancelled, stop processing
        return

    for m in processor_handler(msg, sm, _check=check, should_abort=should_abort):
        if should_abort():
            # Scan has been cancelled, stop processing
            return
        if isinstance(m, messages.RepresentationMessage):
            # Processing this object has produced a request for a new
            # conversion; there's no need to call Resource.check() a second
            # time
            yield from match(sm, m, check=False)
        elif isinstance(m, messages.ScanSpecMessage):
            # Processing this object has given us a new source to scan. Make
            # sure we don't call Resource.check() on the objects under it
            yield from explore(sm, m, check=False)
        else:
            yield m


total_matches = 0


def match(
        sm: SourceManager, msg: messages.RepresentationMessage,
        *, check=True) -> Generator[messages.SerialisableMessage]:
    for m in matcher_handler(msg, sm):
        if isinstance(m, messages.HandleMessage):
            global total_matches
            total_matches += 1
            yield from tag(sm, m)
        elif isinstance(m, messages.ConversionMessage):
            yield from process(sm, m, check=check)
        else:
            yield m


def tag(sm, msg):
    yield from tagger_handler(msg, sm)


def message_received_raw(body, channel, source_manager):  # noqa: CCR001, E501 too high cognitive complexity
    global total_matches
    total_matches = 0

    process_time_start = time.perf_counter()

    message = messages.ConversionMessage.from_json_object(body)

    content_identifier = None

    try:
        yield from dispatch(
                process(source_manager, message),
                (messages.ProblemMessage, ["os2ds_checkups", "os2ds_problems"]),
                (messages.ContentMissingMessage, ["os2ds_checkups", "os2ds_problems"]),
                # (messages.ContentSkippedMessage, ["os2ds_checkups", "os2ds_problems"]),
                (messages.MatchesMessage, ["os2ds_checkups", "os2ds_matches"]),
                (messages.MetadataMessage, ["os2ds_metadata"]),
                (messages.StatusMessage, ["os2ds_status"]))
    finally:
        process_time_total = time.perf_counter() - process_time_start

        object_size = 0
        computed_type = "application/octet-stream"
        try:
            resource = message.handle.follow(source_manager)
            object_size = TimeoutRetrier(max_tries=3, seconds=10).run(
                    resource.get_size)
            computed_type = TimeoutRetrier(max_tries=3, seconds=10).run(
                    resource.compute_type)

            if settings.pipeline['worker']['CHECK_DUPLICATION']:
                content_identifier = TimeoutRetrier(max_tries=3, seconds=60).run(
                        resource.compute_content_identifier)

        except TimeoutError:
            # FileResource.get_size has timed out. This method should (in
            # principle) be lightweight, so there may be something wrong with
            # our state object: we err on the side of caution and clear it
            logger.warning(
                    f"{message.handle}.follow(...).get_size()"
                    " took too long, clearing SourceManager state")
            source_manager.clear()
        except Exception:
            pass
        yield ("os2ds_status", messages.StatusMessage(
                scan_tag=message.scan_spec.scan_tag,
                message="", status_is_error=False,
                object_size=object_size,
                # Computing the MIME type is unnecessary -- we don't use it for
                # anything, we just need it to be present(?)
                object_type=computed_type,
                process_time_worker=process_time_total,
                matches_found=total_matches,
                content_identifier=content_identifier).to_json_object())

        # Clean up after temporary files, but leave connections open
        source_manager.clear_dependents()


def basic_consume_hook(runner):
    """Called after the worker's consumers are registered.

    Announces this worker's presence to the status_collector by broadcasting
    a worker_hello message that includes our anonymous command queue name.
    The status_collector responds by sending us all active per-scan queue
    names directly, so we can subscribe to any ongoing scans we missed."""
    hello = messages.CommandMessage(worker_hello=runner._anon_queue_name)
    runner.channel.basic_publish(
            exchange="broadcast",
            routing_key="",
            body=json.dumps(hello.to_json_object()).encode())


def new_queue_hook(runner, queue_name, tag):
    """Called when the runner receives a new_queue command.

    Workers subscribe to each per-scan conversion queue so they can pick up
    conversion jobs for that scan. Other stage types (explorer, exporter)
    must not subscribe, as they cannot process ConversionMessages.

    If the worker has a conversion_priority list, only queues whose tag
    appears in that list are subscribed to. Untagged queues (empty tag)
    are always accepted when there is no conversion_priority filter."""
    if runner._conversion_priority and tag not in runner._conversion_priority:
        return
    runner._subscribe_to_queue(queue_name, tag)


def tick_hook(runner):
    """Called every 50 ticks to adjust which queues this worker consumes.

    Two independent priority mechanisms run here:
    - Queue priority switching: if multiple named queues are configured via
      --queue-priority, the worker focuses on the highest-priority non-empty
      queue and cancels consumers for lower-priority ones.
    - Per-scan priority: if --conversion-priority is set, the worker focuses
      on the highest-priority tag with active deliveries and pauses
      lower-priority tags."""
    if runner._queue_priorities:
        runner._check_and_switch_priority()
    if runner._conversion_priority and runner._per_scan_queue_priorities:
        runner._check_per_scan_priority()


if __name__ == "__main__":
    from .run_stage import _compatibility_main  # noqa
    _compatibility_main("worker")
