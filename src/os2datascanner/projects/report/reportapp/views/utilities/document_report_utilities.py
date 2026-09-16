# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import structlog

from django.conf import settings
from django.utils.translation import ngettext

from os2datascanner.projects.report.organizations.models import Account
from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport

logger = structlog.get_logger("reportapp")


class DeleteRequestError(Exception):
    """Raised by validate_delete_request when a delete precondition fails."""


def validate_delete_request(user, pks: list[int]):
    """Verifies that the user is allowed to act on the requested DocumentReports.

    Raises DeleteRequestError if any report is missing, not associated with one of the
    user's aliases, or contains no matches.
    """

    reports = DocumentReport.objects.filter(pk__in=pks)
    if not reports.exists():
        raise DeleteRequestError("DocumentReports not found")

    aliases = user.aliases.all()

    illegal_reports = reports.exclude(alias_relations__in=aliases)
    if illegal_reports.exists():
        logger.warning(
            "Deletion request with no alias association!",
            user=user,
            reports=illegal_reports.values_list("pk", flat=True))
        raise DeleteRequestError("Account not associated with these DocumentReports")

    if reports.exclude(number_of_matches__gte=1).exists():
        raise DeleteRequestError("DocumentReport does not identify a match")


def handle_report(account: Account,
                  document_report: DocumentReport,
                  action: DocumentReport.ResolutionChoices):
    """ Given a User, DocumentReport and action (resolution choice),
    handles report accordingly and empties raw_problem."""
    try:
        account.update_last_handle()
    except Exception as e:
        logger.warning("Exception raised while trying to update last_handle field "
                       f"of account belonging to user {account}:", e)

    document_report.resolution_status = action
    document_report.raw_problem = None
    document_report.save()
    logger.info(f"Successfully handled DocumentReport {account} with "
                f"resolution_status {action}.")


def build_resolution_message(action, count: int | None = None, was_handled: bool = False) -> str:
    """
    Builds a human-readable, status-specific success message for handle/mass-handle
    actions (for use in the snackbar notification).

    `count` should be given (and the reports' previous state reflected in `was_handled`)
    for mass actions; omit it for single-report actions.
    """
    # Treat a single-report action as a mass action of exactly 1, so every string is always
    # routed through ngettext -- xgettext rejects a msgid that's used both as a plain string
    # and as the singular half of a plural pair.
    n = count if count is not None else 1

    if not action:
        # Reverting -- the report(s) had a resolution_status and now don't.
        if settings.HANDLED_TAB:
            return ngettext(
                'Status was changed to "unhandled" and the result has been moved to the '
                '"Results" tab.',
                '%(count)d results had their status changed to "unhandled" and have been '
                'moved to the "Results" tab.',
                n) % {"count": n}
        return ngettext(
            'Status was changed to "unhandled"',
            '%(count)d results had their status changed to "unhandled"',
            n) % {"count": n}

    label = DocumentReport.ResolutionChoices(int(action)).label

    if was_handled:
        # The report(s) already had a resolution_status, and it's being changed.
        return ngettext(
            'Status was changed to "%(label)s"',
            '%(count)d results had their status changed to "%(label)s"',
            n) % {"count": n, "label": label}
    else:
        # The report(s) had no resolution_status yet and are being handled for the first time.
        if settings.HANDLED_TAB:
            return ngettext(
                'The result was marked as "%(label)s" and has been moved to the "Handled" tab.',
                '%(count)d results were marked as "%(label)s" and have been moved to the '
                '"Handled" tab.',
                n) % {"count": n, "label": label}
        return ngettext(
            'The result was marked as "%(label)s"',
            '%(count)d results were marked as "%(label)s"',
            n) % {"count": n, "label": label}


def get_deviations(report: DocumentReport) -> list[str]:
    """
    Return a de-duplicated list of human-readable rule labels:
      - For SBSYSDBRule: "<field> contains '<value>'" (both 'contains' and 'icontains' become
        'contains')
      - Else if rule.name or rule._name: that name
      - Otherwise rule.type_label
    """
    seen = set()
    out: list[str] = []

    for frag in report.matches.matches:
        if frag.rule.synthetic or not frag.matches:
            continue

        rule = frag.rule
        label = str(rule.presentation)

        if label and label not in seen:
            seen.add(label)
            out.append(label)

    return out
