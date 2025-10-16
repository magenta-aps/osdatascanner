import structlog

from os2datascanner.projects.report.organizations.models import Account
from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport

logger = structlog.get_logger("reportapp")


def is_owner(owner: str, account: Account) -> bool:
    """ Checks if user has an alias with _value corresponding to owner value.
        Returns True/False"""
    return bool(account.aliases.filter(_value__iexact=owner))


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
