# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from collections.abc import Generator
from typing import Any
import random
import structlog
from urllib.error import HTTPError

from os2datascanner.engine2.model.core.utilities import SourceManager
from .utilities.stage import dispatch
from .. import settings
from ..model.core import Source
from ..utilities.backoff import TimeoutRetrier
from ..conversions import convert, conversion_exists
from ..conversions.types import OutputType, encode_dict
from . import messages
logger = structlog.get_logger("processor")


def check(source_manager, handle):
    """
    Runs Resource.check() on the top-level Handle behind a given Handle.
    """

    # In most cases top-level is the >ultimate top-level<, for example a container of files. In
    # cases where the next "layer" up has yields_independent_sources set true, f.e. email
    # accounts, we stop traversing. Thus checking the email's existence and not the mail
    # account's.
    while handle.source.handle:
        if not handle.source.handle.source.yields_independent_sources:
            handle = handle.source.handle
        else:
            break

    # Resource.check() returns False if the object has been deleted, True if it
    # still exists, and raises an exception if something unexpected happened.
    # Instead of trying to interpret that exception, we should let it bubble up
    # and be converted into a ProblemMessage
    return handle.follow(source_manager).check()


def format_exception_message(ex: Exception, conversion: messages.ConversionMessage) -> str:
    '''Utility function for formating exception messages depending on the exception type.'''
    exception_message = "Processing error. {0}: ".format(type(ex).__name__)

    path = str(conversion.handle)

    if ex is HTTPError and ex.code == 400:
        # We have a special case for HTTP 400: Bad Request.
        exception_message += f"Found broken URL: {str(ex.url)} while scanning: {path}"
    else:
        # This just formats generic errors.
        exception_message += ", ".join([str(a) for a in ex.args])

    return exception_message


def message_received(
        conversion: messages.ConversionMessage,
        sm: SourceManager,
        *,
        _check: bool = True) -> Generator[messages.SerialisableMessage]:
    tr = TimeoutRetrier(
        seconds=settings.pipeline["op_timeout"],
        max_tries=settings.pipeline["op_tries"]
    )

    try:
        if _check and not tr.run(check, sm, conversion.handle):
            yield messages.ContentMissingMessage(
                    scan_tag=conversion.scan_spec.scan_tag,
                    handle=conversion.handle)
            # stop the generator immediately
            return

        if conversion.handle not in conversion.scan_spec.source:
            return  # handle points outside original scan_spec source, do nothing.

        fail_percent = settings.pipeline["processor"]["fail_percentage"]
        if (fail_percent and settings.DEBUG
                and (rand := random.randint(0, 100)) <= fail_percent):
            raise ArithmeticError(
                    "conversion failed due to inauspicious numbers:"
                    f" {rand} ≤ {fail_percent}")

        resource = conversion.handle.follow(sm)
        representation = do_conversion(resource, conversion, tr, sm)

        yield from emit_representation(conversion, representation)

    except KeyError:
        yield from handle_conversion_key_error(conversion, sm)
    except Exception as e:
        yield from handle_conversion_exception(conversion, e)


def message_received_raw(body, channel, source_manager, *, _check=True):
    yield from dispatch(
            message_received(
                    messages.ConversionMessage.from_json_object(body),
                    source_manager, _check=_check),
            (messages.ProblemMessage, ["os2ds_problems", "os2ds_checkups"]),
            (messages.ContentMissingMessage, ["os2ds_checkups", "os2ds_problems"]),
            # (messages.ContentSkippedMessage, ["os2ds_checkups", "os2ds_problems"]),
            (messages.RepresentationMessage, ["os2ds_representations"]),
            (messages.ScanSpecMessage, ["os2ds_scan_specs"]))


def do_conversion(resource, conversion, retrier, source_manager):
    required = conversion.progress.rule.split()[0].operates_on
    configuration = conversion.scan_spec.configuration
    skip_mime_types = configuration.get("skip_mime_types", [])

    mime_type = resource.compute_type()

    # Check if we're supposed to handle images (OCR)
    if required in (OutputType.Text, OutputType.MRZ):
        for mt in skip_mime_types:
            if (mt.endswith("*") and mime_type.startswith(mt[:-1])) or (mime_type == mt):
                # mt is a simple wildcard ("image/*") that matches the
                # computed MIME type of this file.
                # If that, or mt matches the computed MIME type of this file exactly then ...
                return None  # ... skip conversion

    # If we have an appropriate conversion registered, go ahead.
    if conversion_exists(resource, required):
        return retrier.run(convert, resource, required)

    else:
        # Hm, we didn't have any appropriate conversion at hand.
        # Maybe there's one in the parent hierarchy?
        for handle in conversion.handle.walk_up():
            if conversion_exists(resource := handle.follow(source_manager), required):
                logger.info(
                         "hierarchy rewound for conversion",
                         original_handle=conversion.handle,
                         rewound_handle=handle,
                         output_type=required
                )
                return retrier.run(convert, resource, required)

        # There wasn't any in the parent hierarchy. Let it run, raise a KeyError and be handled
        # by the handle_conversion_key_error function. Likely we can reinterpret as a Source.
        return retrier.run(convert, resource, required)


def emit_representation(
        conversion: messages.ConversionMessage, representation: Any):
    required = conversion.progress.rule.split()[0].operates_on

    # If the conversion also produced other values at the same
    # time, then include all of those as well; they might also be
    # useful for the rule engine
    if representation and getattr(representation, "parent", None):
        dv = {
            k.value: v
            for k, v in representation.parent.items()
            if isinstance(k, OutputType)
        }
        dv[required.value] = representation
    else:
        dv = {required.value: representation}

    logger.info(f"Required representation for {conversion.handle} is {required}")
    yield messages.RepresentationMessage(
            scan_spec=conversion.scan_spec,
            handle=conversion.handle,
            progress=conversion.progress,
            representations=encode_dict(dv))


def handle_conversion_key_error(
        conversion: messages.ConversionMessage, source_manager: SourceManager):
    try:
        derived_source = Source.from_handle(conversion.handle, source_manager)
        if derived_source:
            yield messages.replace(conversion.scan_spec,
                                   source=derived_source,
                                   progress=conversion.progress)
        else:
            # If we can't recurse any deeper, then produce an empty conversion
            # so that the matcher stage has something to work with
            # (XXX: is this always the right approach?)
            yield messages.RepresentationMessage(
                    scan_spec=conversion.scan_spec,
                    handle=conversion.handle,
                    progress=conversion.progress,
                    representations={conversion.progress.rule.split()[0].operates_on.value: None})
    except Exception as e:
        yield from handle_conversion_exception(conversion, e)


def handle_conversion_exception(
        conversion: messages.ConversionMessage, exception: Exception):
    exception_message = format_exception_message(exception, conversion)
    logger.warning(exception_message, exc_info=exception)

    yield messages.ProblemMessage(
            scan_tag=conversion.scan_spec.scan_tag,
            source=None,
            handle=conversion.handle,
            message=exception_message)


if __name__ == "__main__":
    from .run_stage import _compatibility_main  # noqa
    _compatibility_main("processor")
