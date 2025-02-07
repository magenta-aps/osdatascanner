import structlog

from ..utilities.backoff import TimeoutRetrier
from .explorer import message_received_raw as explorer_handler
from .processor import message_received_raw as processor_handler
from .matcher import message_received_raw as matcher_handler
from .tagger import message_received_raw as tagger_handler
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


def explore(sm, msg, *, check=True):
    """ Worker-internal explorer, channels are pseudo-queues, i.e. not RabbitMQ """
    for channel, message in explorer_handler(msg, "os2ds_scan_specs", sm):
        # Determine channels
        conversion_channel = "os2ds_conversions"
        explorer_channel = "os2ds_scan_specs"
        if scan_spec := message.get("scan_spec"):
            conversion_channel = determine_channel(scan_spec, "conversion")
            explorer_channel = determine_channel(scan_spec, "explorer")

        # Routing
        if channel == conversion_channel:
            yield from process(sm, message, check=check)
        elif channel == explorer_channel:
            # Huh? Surely a standalone explorer should have handled this
            logger.warning("worker exploring unexpected nested Source")
            yield from explore(sm, message, check=check)
        elif channel == "os2ds_status":
            # Explorer status messages are not interesting in the worker
            # context
            pass
        else:
            yield channel, message


def process(sm, msg, *, check=True):
    """ Worker-internal processor, channels are pseudo-queues, i.e. not RabbitMQ """
    for channel, message in processor_handler(
            msg, "os2ds_conversions", sm, _check=check):

        # Determine channel
        explorer_channel = "os2ds_scan_specs"
        if scan_spec := message.get("scan_spec"):
            explorer_channel = determine_channel(scan_spec, "explorer")

        if channel == "os2ds_representations":
            # Processing this object has produced a request for a new
            # conversion; there's no need to call Resource.check() a second
            # time
            yield from match(sm, message, check=False)
        elif channel == explorer_channel:
            # Processing this object has given us a new source to scan. Make
            # sure we don't call Resource.check() on the objects under it
            yield from explore(sm, message, check=False)
        else:
            yield channel, message


total_matches = 0


def match(sm, msg, *, check=True):
    """ Worker-internal matcher, channels are pseudo-queues, i.e. not RabbitMQ """
    for channel, message in matcher_handler(msg, "os2ds_representations", sm):
        # Determine channel
        conversion_channel = "os2ds_conversions"
        if scan_spec := message.get("scan_spec"):
            conversion_channel = determine_channel(scan_spec, "conversion")

        if channel == "os2ds_handles":
            global total_matches
            total_matches += 1
            yield from tag(sm, message)
        elif channel == conversion_channel:
            yield from process(sm, message, check=check)
        else:
            yield channel, message


def tag(sm, msg):
    """ Worker-internal tagger, channels are pseudo-queues, i.e. not RabbitMQ """
    yield from tagger_handler(msg, "os2ds_handles", sm)


def message_received_raw(body, channel, source_manager):  # noqa: CCR001, E501 too high cognitive complexity
    global total_matches
    total_matches = 0

    process_time_start = time.process_time()

    try:
        for channel, message in process(source_manager, body):
            if channel in WRITES_QUEUES:
                yield (channel, message)
            else:
                logger.error(f"unexpected message to queue {channel}")
    finally:
        process_time_total = time.process_time() - process_time_start

        message = messages.ConversionMessage.from_json_object(body)
        object_size = 0

        computed_type = "application/octet-stream"
        try:
            resource = message.handle.follow(source_manager)
            object_size = TimeoutRetrier(max_tries=3, seconds=10).run(
                    resource.get_size)
            computed_type = TimeoutRetrier(max_tries=3, seconds=10).run(
                    resource.compute_type)
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
                matches_found=total_matches).to_json_object())

        # Clean up after temporary files, but leave connections open
        source_manager.clear_dependents()


if __name__ == "__main__":
    from .run_stage import _compatibility_main  # noqa
    _compatibility_main("worker")
