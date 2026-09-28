# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""What a worker does once coordination has decided something.

deduplication.plan_conversion answers one of three ways; the two that need work
doing are here. Claimed means converting on behalf of every copy of this
content, which is share(): run the conversion, watch what it produces, and
publish that if it adds up to a whole answer. Stored means another worker has
already done it, which is replay(): report what it found against this copy.

Neither drives the pipeline itself. The worker hands in the callables that do
that, so that deciding what a result may be used for stays separable from the
generator plumbing that produces one.
"""

from collections.abc import Generator

import structlog

from . import deduplication
from .. import messages

logger = structlog.get_logger("sharing")


class Capture:
    """The rule results produced while converting one object, and whether they
    add up to something another copy could safely be told about."""

    def __init__(self):
        self.results = []
        self.usable = True

    @property
    def shareable(self) -> bool:
        # An object that was scanned successfully always produces at least one
        # result, even when nothing matched, so an empty capture means the run
        # did not finish rather than that the document was clean.
        return self.usable and bool(self.results)


def capture_matches(generator: Generator[messages.SerialisableMessage],
                    capture: Capture) -> Generator[messages.SerialisableMessage]:
    """Passes messages straight through, noting the rule results as they go by so
    they can be shared with the other copies of this content.

    Synthetic rules are left out."""
    for m in generator:
        if isinstance(m, messages.MatchesMessage):
            capture.results.append(
                    (m.handle, m.matched,
                     [mf.to_json_object()
                      for mf in m.matches if not mf.rule.synthetic]))
        elif isinstance(
                m, (messages.ProblemMessage, messages.ContentMissingMessage)):
            # Something about this object could not be read, so whatever results
            # came out are an incomplete picture of it.
            capture.usable = False
        yield m


def share(
        claim: deduplication.Claimed, message, stream, *,
        relay, should_abort, cancelled) -> Generator[
            messages.SerialisableMessage]:
    """Relays the rest of a conversion this worker holds a claim on, capturing
    what it produces and publishing that for the other copies to replay."""
    store = deduplication.get_store()
    capture = Capture()

    with deduplication.settled(message.handle), deduplication.hold_lease(
            deduplication.Lease(store, claim.scan_id, claim.key)):
        for m in stream:
            if should_abort():
                return
            yield from capture_matches(relay(m), capture)

        if cancelled():
            # Nothing is stored for a cancelled scan.
            return

        result = deduplication.UNSHAREABLE_RESULT
        if capture.shareable:
            try:
                result = deduplication.encode_result(
                        message.handle, capture.results)
            except Exception:
                logger.warning(
                        "could not encode deduplication result",
                        handle=str(message.handle), exc_info=True)

        store.store_result(claim.scan_id, claim.key, result)

        if result is deduplication.UNSHAREABLE_RESULT:
            # Tell the other copies not to wait for a result that is never
            # coming, so they convert now rather than cycling through the
            # deferral queues until their budget expires.
            logger.info(
                    "conversion did not produce a shareable result,"
                    " other copies will convert",
                    handle=str(message.handle),
                    results=len(capture.results), usable=capture.usable)
        else:
            logger.info(
                    "converted on behalf of every copy of this content",
                    handle=str(message.handle),
                    results=len(capture.results))


def replay(payload: dict, message, *, convert) -> Generator[
        messages.SerialisableMessage]:
    """Reports the result of a conversion someone else already did, against this
    copy of the content. Falls back to converting on failure."""
    with deduplication.settled(message.handle):
        yield from _replay(payload, message, convert=convert)


def _replay(payload, message, *, convert):
    try:
        replayed = [
            messages.MatchesMessage(
                    scan_spec=message.scan_spec,
                    handle=handle,
                    matched=matched,
                    matches=[messages.MatchFragment.from_json_object(m)
                             for m in matches])
            for handle, matched, matches in deduplication.decode_result(
                    payload, message.handle)]
    except Exception:
        logger.warning(
                "could not replay stored result, converting instead",
                handle=str(message.handle), exc_info=True)
        yield from convert()
        return

    logger.info(
            "reusing a conversion done for identical content elsewhere",
            handle=str(message.handle), results=len(replayed))
    for m in replayed:
        yield m
        if m.matched:
            yield messages.HandleMessage(
                    scan_tag=message.scan_spec.scan_tag, handle=m.handle)
