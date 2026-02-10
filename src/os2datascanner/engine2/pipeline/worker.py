# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

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
    for m in processor_handler(msg, sm, _check=check):
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


if __name__ == "__main__":
    from .run_stage import _compatibility_main  # noqa
    _compatibility_main("worker")
