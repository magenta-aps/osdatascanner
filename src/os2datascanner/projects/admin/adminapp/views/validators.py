"""
Custom validators for form fields.
"""
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from os2datascanner.engine2.rules.rule import Rule as E2Rule
from os2datascanner.projects.admin.adminapp.views.utils.invariants import (
    check_invariants, standalone_invariant, precedence_invariant,
    RuleInvariantViolationError,
)

# This is not the cleanest way to do translations, but django cannot detect what
# to translate from variables defined outside the django app, so this is
# probably the best we can do for now.
error_table = {
    "precedence":
    _("Invariant violation - precedence: %(r1)s has lower precedence than %(r2)s."),
    "standalone":
    _("Invariant violation - standalone: %(r1)s must be used in a compound rule."),
}


def customrule_validator(value):
    """
    Builts the rule from json representation and applies
    invariant checks on the built rule. If any of the invariants
    fail, then a ValidationError is thrown.
    """
    try:
        check_invariants(E2Rule.from_json_object(value),
                         precedence_invariant, standalone_invariant)
    except RuleInvariantViolationError as rive:
        raise ValidationError(
            error_table.get(rive.message) % {f"r{i+1}": str(r)
                                             for i, r in enumerate(rive.rules)})
