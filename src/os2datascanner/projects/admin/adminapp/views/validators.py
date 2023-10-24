"""
Custom validators for form fields.
"""
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from os2datascanner.engine2.rules.rule import Rule
from os2datascanner.engine2.rules.utilities.invariants import (
    RuleInvariantViolationError, check_invariants,
    standalone_invariant, precedence_invariant,
)


def customrule_validator(value):
    """
    Builts the rule from json representation and applies
    invariant checks on the built rule. If any of the invariants
    fail, then a ValidationError is thrown.
    """
    try:
        built_rule = Rule.from_json_object(value)
        print(f"\n!!! built_rule: {built_rule} has type {type(built_rule)}, "
              "precedence: {built_rule.properties.precedence}, "
              "standalone: {built_rule.properties.standalone}!!!\n")
        check_invariants(built_rule, precedence_invariant, standalone_invariant)
    except RuleInvariantViolationError as rive:
        raise ValidationError(_("Rule violates invariants")) from rive
