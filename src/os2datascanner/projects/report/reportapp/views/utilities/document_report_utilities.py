# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import structlog

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
