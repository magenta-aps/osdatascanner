# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from collections.abc import Generator
import structlog

from os2datascanner.engine2.model.core.utilities import SourceManager
from os2datascanner.engine2.utilities.i18n import gettext as _
from ..model.core import (
        Source, takes_named_arg, UnknownSchemeError, DeserialisationError)
from ..model.core.errors import (ModelException,
                                 UncontactableError,
                                 UnauthorisedError,
                                 UnavailableError)
from . import messages
from .utilities.stage import dispatch
from .utilities.filtering import is_handle_relevant

logger = structlog.get_logger("explorer")

READS_QUEUES = ("os2ds_scan_specs",)
WRITES_QUEUES = ("os2ds_problems", "os2ds_status",
                 "os2ds_scan_specs", "os2ds_checkups",
                 "os2ds_conversions")

PROMETHEUS_DESCRIPTION = "Sources explored"
# An individual exploration task is typically the longest kind of task, so we
# want to do as little prefetching as possible here. (If we're doing an
# agonisingly slow web scan, we don't want to hog scan specs we're not ready
# to use yet!)
PREFETCH_COUNT = 1


def process_exploration_error(scan_spec, handle_candidate, ex):
    exception_message = (
            f"Exploration error. {type(ex).__name__}: "
            + ", ".join(str(a) for a in ex.args))
    yield messages.ProblemMessage(
            scan_tag=scan_spec.scan_tag, source=scan_spec.source,
            handle=handle_candidate, message=exception_message)
    logger.info(
            "found problem",
            scan_tag=scan_spec.scan_tag, handle=handle_candidate)


def message_received(  # noqa: CCR001
        message: messages.ScanSpecMessage,
        sm: SourceManager) -> Generator[messages.SerialisableMessage]:
    error_count = 0
    handle_count = 0
    source_count = None
    exception_message = ""

    if message.progress:
        # This is an internal message from a processor, informing us that some
        # part of the rule has already been evaluated. Move that part out of
        # the ScanSpecMessage; we'll attach it to the ConversionMessages we
        # produce
        progress = message.progress
        message = message._replace(progress=None)
    else:
        # This is a fresh Source with no rule execution done so far. Make a
        # blank ProgressFragment to attach to the ConversionMessages we produce
        progress = messages.ProgressFragment(
                rule=message.rule, matches=[])

    # Update the configuration of the source manager.
    # Yes, this is dreaded mutable state... Just don't go change it
    # somewhere else.
    sm.configuration = message.configuration

    handles_method = message.source.handles

    # Inspect the handles() method to see if it can take any extra hints
    extra_kwargs = {}
    if takes_named_arg(handles_method, "rule"):
        extra_kwargs["rule"] = progress.rule

    handle_iterator = message.source.handles(sm, **extra_kwargs)

    log = logger.bind(scan_tag=message.scan_tag)

    try:
        for handle in handle_iterator:
            if isinstance(handle, tuple) and handle[1]:
                # We were able to construct a Handle for something that
                # exists, but then something unexpected (that we can tie to
                # that specific Handle) went wrong. Send a problem message
                yield from process_exploration_error(message, *handle)
                error_count += 1
            elif not message.source.yields_independent_sources:
                # This Handle is just a normal reference to a scannable object.
                # Send it on to be processed

                yield messages.ConversionMessage(message, handle, progress)
                handle_count += 1
            else:
                # Check if the handle should be excluded.
                if is_handle_relevant(handle, message.filter_rule):
                    # This Handle is a thin wrapper around an independent Source.
                    # Construct that Source and enqueue it for further exploration
                    new_source = Source.from_handle(handle)
                    yield message._replace(source=new_source)
                    source_count = (source_count or 0) + 1
                else:
                    log.info("handle excluded", handle=handle)

        # Exploration is complete
        log.info(
                "finished",
                error_count=error_count, handle_count=handle_count,
                source_count=source_count)
    except Exception as e:
        exp_args = {
            "type": type(e).__name__,
        }
        exp_fmt = _("Unknown exploration error of type {type}")
        if isinstance(e, ModelException):
            exp_args["server"] = e.server
            if isinstance(e, UncontactableError):
                exp_fmt = _(
                        "Exploration error: could not communicate with the"
                        " server at {server}")
            if isinstance(e, UnauthorisedError):
                exp_fmt = _(
                        "Exploration error: no valid authentication for server"
                        " {server}")
            if isinstance(e, UnavailableError):
                exp_fmt = _(
                        "Exploration error: authenticated successfully against"
                        " {server}, but source not found")

        yield messages.ProblemMessage(
                scan_tag=message.scan_tag, source=message.source, handle=None,
                message=exp_fmt.format(**exp_args))
        log.warning(
                "finished unsuccessfully",
                handle_count=handle_count, source_count=source_count,
                exc_info=e)
    finally:
        # Closing a generator that has already closed is harmless, and it's
        # good form to clean up
        if hasattr(handle_iterator, "close"):
            handle_iterator.close()
        yield messages.StatusMessage(
                scan_tag=message.scan_tag,
                total_objects=handle_count, new_sources=source_count,
                message=exception_message,
                status_is_error=exception_message != "")


def message_received_raw(body, channel, source_manager):
    if "scan_tag" not in body:
        # Scan specifications with no scan tag are simply invalid and should be
        # dropped (... and shouldn't have been produced since 2020)
        return
    # Store the scan_tag separately so we can use it as a scan identifier even
    # if the ScanSpecMessage factory fails
    scan_tag = messages.ScanTagFragment.from_json_object(body["scan_tag"])

    problem: messages.ProblemMessage | None = None
    try:
        scan_spec = messages.ScanSpecMessage.from_json_object(body)

        yield from dispatch(
            message_received(scan_spec, source_manager),
            (messages.StatusMessage, ["os2ds_status"]),
            (messages.ScanSpecMessage, [scan_spec.explorer_queue]),
            (messages.ConversionMessage, [scan_spec.conversion_queue]),
            # Top-level exploration problems should go to the admin system so
            # they can become a UserErrorLog, and are for historical and
            # compatibility reasons also sent to the report module, although
            # this makes much less sense
            (messages.ProblemMessage, ["os2ds_checkups", "os2ds_problems"]))
        return
    except UnknownSchemeError as ex:
        scheme, = ex.args
        problem = messages.ProblemMessage(
                scan_tag=scan_tag,
                source=None, handle=None,
                message=f"Unknown scheme '{scheme}'")
    except DeserialisationError as ex:
        type_, field = ex.args
        problem = messages.ProblemMessage(
                scan_tag=scan_tag,
                source=None, handle=None,
                message=f"{type_}: missing field '{field}'")
    except Exception:
        problem = messages.ProblemMessage(
                scan_tag=scan_tag,
                source=None, handle=None,
                message="Unexpected error")

    if problem:
        json_form = problem.to_json_object()
        for queue in ["os2ds_problems", "os2ds_checkups"]:
            yield (queue, json_form)


if __name__ == "__main__":
    from .run_stage import _compatibility_main  # noqa
    _compatibility_main("explorer")
