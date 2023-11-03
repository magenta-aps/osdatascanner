"""
Custom validators for form fields.
"""
from django.forms import ValidationError

from os2datascanner.engine2.rules.rule import Rule as E2Rule
from os2datascanner.engine2.rules.utilities.invariants import (
    check_invariants, standalone_invariant, precedence_invariant,
)


def format_rule_invariant_error(error):
    """
    Formats an error message for use in ValidatorError
    """
    return error.message % {f"r{i+1}": str(r) for i, r in enumerate(error.rules)}


def customrule_validator(value):
    """
    Builts the rule from json representation and applies
    invariant checks on the built rule. If any of the invariants
    fail, then a ValidationError is thrown.
    """
    if errors := check_invariants(E2Rule.from_json_object(value),
                                  precedence_invariant, standalone_invariant):
        raise ValidationError(
            [ValidationError(format_rule_invariant_error(e)) for e in errors])
