# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from copy import copy
from collections.abc import Generator
import structlog

from os2datascanner.engine2.model.core.utilities import SourceManager

from ..conversions.types import decode_dict
from ...utils.replace_regions import replace_regions
from . import messages
from .utilities.stage import dispatch
from .. import settings
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
from os2datascanner.engine2.rules.rule import Rule, SimpleRule

logger = structlog.get_logger("matcher")


def censor_context(context, rules):
    """Given a text and an iterable of rules, will censor the text,
    using the get_censor_intervals method of each rule."""

    if not context:
        return context

    censor_intervals = []
    for r in rules:
        if hasattr(r, "get_censor_intervals"):
            censor_intervals.extend(r.get_censor_intervals(context))

    # Make sure no interval extends beyond the context
    censor_intervals = [(max(0, start), min(end, len(context))) for start, end in censor_intervals]
    # Make sure every interval starts before it ends,
    # and sort them in increasing order of beginning
    censor_intervals = sorted((start, end) for start, end in censor_intervals if start < end)

    if censor_intervals:
        # Combine overlapping intervals

        # The beginning and end of current interval
        interval_start, interval_end = censor_intervals[0]
        intervals = []

        for start, end in censor_intervals:
            if start >= interval_end:
                # If the next interval doesn't overlap with the current one,
                # save the current one and start a new
                intervals.append((interval_start, interval_end))
                interval_start = start
                interval_end = end

            else:
                # If the next interval overlaps with the current one, combine them
                interval_end = max(interval_end, end)

        intervals.append((interval_start, interval_end))

        return "".join(replace_regions(
            context,
            *[(start, 'X' * (end - start), end) for start, end in intervals]))

    else:
        return context


def postprocess_match(
        base_rule: Rule,
        match_object: tuple[SimpleRule, list[dict]]):
    rule, matches = match_object
    """Goes through all found matches and censors their context."""

    if not matches:
        return (rule, None)

    all_rules = base_rule.flatten()
    for match_dict in matches:
        if context := match_dict.get("context", None):
            match_dict["context"] = censor_context(context, all_rules)

    return (rule, matches)


def message_received(  # noqa: CCR001,E501 too high cognitive complexity
        message: messages.RepresentationMessage,
        sm: SourceManager) -> Generator[messages.SerialisableMessage]:
    representations = decode_dict(message.representations)
    rule = message.progress.rule
    logger.debug(f"{message.handle} with rules [{rule.presentation}] "
                 f"and representation [{list(representations.keys())}]")

    try:
        # Keep executing rules for as long as we can with the representations
        # we have
        conclusion, new_matches = rule.try_match(
                representations,
                obj_limit=max(1, settings.pipeline["matcher"]["obj_limit"]))

        # Convoluted way of checking if we _did not_ match on LastModifiedRule,
        # meaning that we won't be scanning its content again.
        if not conclusion and isinstance(new_matches[0][0], LastModifiedRule):
            yield messages.StatusMessage(
                scan_tag=message.scan_spec.scan_tag,
                skipped_by_last_modified=1)

    except Exception as e:
        exception_message = "Matching error"
        exception_message += ". {0}: ".format(type(e).__name__)
        exception_message += ", ".join([str(a) for a in e.args])
        logger.warning(exception_message)
        yield messages.ProblemMessage(
                scan_tag=message.scan_spec.scan_tag,
                source=None, handle=message.handle,
                message=exception_message)
        return

    final_matches = copy(message.progress.matches)
    for match in new_matches:
        sub_rule, matches = postprocess_match(message.scan_spec.rule, match)
        final_matches.append(messages.MatchFragment(sub_rule, matches))

    if isinstance(conclusion, bool):
        # We've come to a conclusion!

        logger.info(
                f"{message.handle} done."
                f" Matched status: {conclusion}")

        # Censor mail subject in handle
        if hasattr(message.handle, "_mail_subject"):
            censored_handle = message.handle
            rules = message.scan_spec.rule.flatten()
            censored_handle._mail_subject = censor_context(censored_handle._mail_subject, rules)
            message._replace(handle=censored_handle)

        # Censor item name in handle for sharepoint lists
        if hasattr(message.handle, "_item_name"):
            censored_handle = message.handle
            rules = message.scan_spec.rule.flatten()
            censored_handle._item_name = censor_context(censored_handle._item_name, rules)
            message._replace(handle=censored_handle)

        yield messages.MatchesMessage(
                message.scan_spec, message.handle,
                matched=conclusion,
                matches=final_matches)

        # Only trigger metadata scanning if the match succeeded
        if conclusion:
            yield messages.HandleMessage(
                    message.scan_spec.scan_tag,
                    message.handle)
    else:
        new_rep = conclusion.split()[0].operates_on
        # We need a new representation to continue
        logger.debug(
                f"{message.handle} needs"
                f" new representation: [{new_rep}].")

        yield messages.ConversionMessage(
                message.scan_spec, message.handle,
                messages.deep_replace(
                        message.progress,
                        rule=conclusion,
                        matches=final_matches))


def message_received_raw(body, channel, source_manager):
    message = messages.RepresentationMessage.from_json_object(body)
    yield from dispatch(
            message_received(message, source_manager),
            (messages.StatusMessage, ["os2ds_status"]),
            (messages.ProblemMessage, ["os2ds_problems", "os2ds_checkups"]),
            (messages.MatchesMessage, ["os2ds_matches", "os2ds_checkups"]),
            (messages.HandleMessage, ["os2ds_handles"]),
            (messages.ConversionMessage, [message.scan_spec.conversion_queue]))


if __name__ == "__main__":
    from .run_stage import _compatibility_main  # noqa
    _compatibility_main("matcher")
