import structlog

from ..conversions.types import decode_dict, OutputType
from . import messages
from .. import settings
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
from os2datascanner.engine2.rules.rule import Rule, SimpleRule

logger = structlog.get_logger("matcher")

READS_QUEUES = ("os2ds_representations",)
WRITES_QUEUES = (
    "os2ds_handles",
    "os2ds_matches",
    "os2ds_checkups",
    "os2ds_conversions",)
PROMETHEUS_DESCRIPTION = "Representations examined"
PREFETCH_COUNT = 8


def censor_context(context, rules):
    """Given a text and an iterable of rules, will censor the text,
    using the get_censor_intervals method of each SimpleTextRule."""
    censor_intervals = []
    for r in rules:
        if hasattr(r, "get_censor_intervals"):
            censor_intervals.extend(r.get_censor_intervals(context))

    censor_intervals.sort()
    censored_context = ""
    next_interval = 0
    mx = -1
    for i, char in enumerate(context):
        while next_interval < len(censor_intervals) and i >= censor_intervals[next_interval][0]:
            mx = max(mx, censor_intervals[next_interval][1])
            next_interval += 1

        censored_context += char if i >= mx else 'X'

    return censored_context


def postprocess_match(
        base_rule: Rule,
        match_object: tuple[SimpleRule, list[dict]]):
    rule, matches = match_object
    """Goes through all found matches and censors their context, if the rule operates on text."""

    if not matches:
        return (rule, None)

    if rule.operates_on == OutputType.Text:
        all_rules = base_rule.flatten()
        for match_dict in matches:
            if context := match_dict.get("context", None):
                match_dict["context"] = censor_context(context, all_rules)

    return (rule, matches)


def message_received_raw(body, channel, source_manager):  # noqa: CCR001,E501 too high cognitive complexity
    message = messages.RepresentationMessage.from_json_object(body)
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
            yield ("os2ds_status", messages.StatusMessage(
                scan_tag=message.scan_spec.scan_tag,
                skipped_by_last_modified=1).to_json_object())

    except Exception as e:
        exception_message = "Matching error"
        exception_message += ". {0}: ".format(type(e).__name__)
        exception_message += ", ".join([str(a) for a in e.args])
        logger.warning(exception_message)
        for problems_q in ("os2ds_problems", "os2ds_checkups",):
            yield (problems_q, messages.ProblemMessage(
                    scan_tag=message.scan_spec.scan_tag,
                    source=None, handle=message.handle,
                    message=exception_message).to_json_object())
        return

    final_matches = message.progress.matches
    for match in new_matches:
        sub_rule, matches = postprocess_match(rule, match)
        final_matches.append(messages.MatchFragment(sub_rule, matches))

    if isinstance(conclusion, bool):
        # We've come to a conclusion!

        logger.info(
                f"{message.handle} done."
                f" Matched status: {conclusion}")

        for matches_q in ("os2ds_matches", "os2ds_checkups",):
            yield (matches_q,
                   messages.MatchesMessage(
                       message.scan_spec, message.handle,
                       matched=conclusion,
                       matches=final_matches).to_json_object())

        # Only trigger metadata scanning if the match succeeded
        if conclusion:
            yield ("os2ds_handles",
                   messages.HandleMessage(
                            message.scan_spec.scan_tag,
                            message.handle).to_json_object())
    else:
        new_rep = conclusion.split()[0].operates_on
        # We need a new representation to continue
        logger.debug(
                f"{message.handle} needs"
                f" new representation: [{new_rep}].")
        yield ("os2ds_conversions",
               messages.ConversionMessage(
                            message.scan_spec, message.handle,
                            message.progress._replace(
                                    rule=conclusion,
                                    matches=final_matches)).to_json_object())


if __name__ == "__main__":
    from .run_stage import _compatibility_main  # noqa
    _compatibility_main("matcher")
