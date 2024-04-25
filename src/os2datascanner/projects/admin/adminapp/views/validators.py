"""
Custom validators for form fields.
"""
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from os2datascanner.engine2.rules.rule import Rule as E2Rule
from os2datascanner.projects.admin.adminapp.views.utils.invariants import (
    RuleInvariantChecker,
    RuleInvariantViolationError,
)

# This is not the cleanest way to do translations, but django cannot detect what
# to translate from variables defined outside the django app, so this is
# probably the best we can do for now.
error_table = {
    "precedence":
    _("Cannot build rule: %(r1)s may not precede %(r2)s. Please change the order."),
    "standalone":
    _("Cannot build rule: %(r1)s must be used in conjunction with another rule."),
}


def customrule_validator(value):
    """
    Builts the rule from json representation and applies
    invariant checks on the built rule. If any of the invariants
    fail, then a ValidationError is thrown.
    """
    checker = RuleInvariantChecker()

    try:
        checker.check_invariants(E2Rule.from_json_object(value))
    except RuleInvariantViolationError as rive:
        raise ValidationError(
            error_table.get(rive.message) % {f"r{i+1}": str(r)
                                             for i, r in enumerate(rive.rules)})
