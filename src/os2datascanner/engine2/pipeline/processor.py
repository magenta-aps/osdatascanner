import structlog
from urllib.error import HTTPError
from .. import settings
from ..model.core import Source
from ..utilities.backoff import TimeoutRetrier
from ..conversions import convert, conversion_exists
from ..conversions.types import OutputType, encode_dict
from . import messages
logger = structlog.get_logger("processor")


SKIPPED = object()
"""A singleton returned by do_conversion when the scanner job's configuration
has blocked an otherwise supported conversion from taking place."""


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


def message_received_raw(body, channel, source_manager, *, _check=True):
    """ Reads from the python-internal conversions channel"""

    conversion = messages.ConversionMessage.from_json_object(body)
    tr = TimeoutRetrier(
        seconds=settings.pipeline["op_timeout"],
        max_tries=settings.pipeline["op_tries"]
    )

    try:
        if _check and not tr.run(check, source_manager, conversion.handle):
            logger.info(
                    "resource missing",
                    handle=str(conversion.handle))
            yield from generate_missing_resource_messages(conversion)
            # stop the generator immediately
            return

        if conversion.handle not in conversion.scan_spec.source:
            return  # handle points outside original scan_spec source, do nothing.

        resource = conversion.handle.follow(source_manager)
        representation = do_conversion(resource, conversion, tr, source_manager)

        yield from emit_representation(conversion, representation)

    except KeyError:
        yield from handle_conversion_key_error(conversion, source_manager)
    except Exception as e:
        yield from handle_conversion_exception(conversion, e)


def generate_missing_resource_messages(conversion):
    # The resource is missing (and we're in a context where we care).
    # Generate a problem message and a checkup.
    for problems_q in ("os2ds_problems", "os2ds_checkups"):
        yield (
            problems_q,
            messages.ProblemMessage(
                scan_tag=conversion.scan_spec.scan_tag,
                source=None,
                handle=conversion.handle,
                missing=True,
                message="Resource check failed"
            ).to_json_object()
        )


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
                logger.info(
                        "skipping conversion due to scanner config",
                        handle=str(conversion.handle),
                        conversion_type=required)
                return SKIPPED  # ... skip conversion

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
                         original_handle=str(conversion.handle),
                         rewound_handle=str(handle),
                         conversion_type=required)
                return retrier.run(convert, resource, required)

        # There wasn't any in the parent hierarchy. Let it run, raise a KeyError and be handled
        # by the handle_conversion_key_error function. Likely we can reinterpret as a Source.
        return retrier.run(convert, resource, required)


def emit_representation(conversion, representation):
    if representation is SKIPPED:
        yield (
            "os2ds_checkups",
            messages.ContentSkippedMessage(
                    scan_tag=conversion.scan_spec.scan_tag,
                    handle=conversion.handle).to_json_object()
        )
        return

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
    else:
        dv = {required.value: representation}

    logger.info(
            "emitting representation",
            handle=str(conversion.handle),
            conversion_type=required,
            representation=encode_dict(dv))
    yield (
        "os2ds_representations",
        messages.RepresentationMessage(
            conversion.scan_spec,
            conversion.handle,
            conversion.progress,
            encode_dict(dv)
        ).to_json_object()
    )


def handle_conversion_key_error(conversion, source_manager):
    try:
        derived_source = Source.from_handle(conversion.handle, source_manager)
        if derived_source:
            new_scan_spec = conversion.scan_spec._replace(
                source=derived_source,
                progress=conversion.progress
            )
            yield (
                "os2ds_scan_specs",
                new_scan_spec.to_json_object()
            )
        else:
            # If we can't recurse any deeper, then produce an empty conversion
            # so that the matcher stage has something to work with
            # (XXX: is this always the right approach?)
            yield (
                "os2ds_representations",
                messages.RepresentationMessage(
                    conversion.scan_spec,
                    conversion.handle,
                    conversion.progress,
                    {conversion.progress.rule.split()[0].operates_on.value: None}
                ).to_json_object()
            )
    except Exception as e:
        yield from handle_conversion_exception(conversion, e)


def handle_conversion_exception(conversion, exception):
    exception_message = format_exception_message(exception, conversion)
    logger.warning(exception_message, exc_info=exception)

    for problems_q in ("os2ds_problems", "os2ds_checkups"):
        yield (
            problems_q,
            messages.ProblemMessage(
                scan_tag=conversion.scan_spec.scan_tag,
                source=None,
                handle=conversion.handle,
                message=exception_message
            ).to_json_object()
        )


if __name__ == "__main__":
    from .run_stage import _compatibility_main  # noqa
    _compatibility_main("processor")
