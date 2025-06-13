import structlog

from os2datascanner.projects.report.organizations.models import Account
from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
from os2datascanner.engine2.model._staging.sbsysdb_rule import SBSYSDBRule
from django.utils.translation import gettext_lazy as _

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
        if not frag.matches:
            continue

        rule = frag.rule

        if isinstance(rule, SBSYSDBRule):
            format_str = None
            # normalize both contains and icontains to the same label
            match rule._op:
                case rule.Op.EQ:
                    format_str = _("{field} is {value!r}")
                case rule.Op.NEQ:
                    format_str = _("{field} is not {value!r}")
                case rule.Op.LT:
                    format_str = _("{field} is less than {value!r}")
                case rule.Op.LTE:
                    format_str = _(
                            "{field} is less than or equal to {value!r}")
                case rule.Op.GT:
                    format_str = _("{field} is greater than {value!r}")
                case rule.Op.GTE:
                    format_str = _(
                            "{field} is greater than"
                            " or equal to {value!r}")
                case rule.Op.CONTAINS | rule.Op.ICONTAINS:
                    format_str = _(
                            "{field} contains {value!r}")
                case e:
                    raise ValueError(e)

            field_name = rule._field
            if field_name == "?Age?":
                field_name = _("number of days since last update")

            label = format_str.format(field=field_name, value=rule._value)
        else:
            # use any user-friendly name if present
            name = getattr(rule, "name", None) or getattr(rule, "_name", None)
            label = name or rule.type_label

        if label not in seen:
            seen.add(label)
            out.append(label)

    return out
