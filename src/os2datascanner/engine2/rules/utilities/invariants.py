"""
Functions and utilities for performing inspection of rule properties
by checking invariants.
"""
from itertools import pairwise
from typing import Callable, Optional

from ..rule import Rule
from ..logical import CompoundRule
# from .properties import RulePrecedence, RuleProperties

__all__ = [
    'RuleInvariant',
    'RuleInvariantViolationError',
    'check_invariants',
    'precedence_invariant',
    'standalone_invariant',
]

"""
Function signature for a rule invariant.
An invariant is a test based on the properties of a rule
that should hold for some rule (and perhaps its components).
"""
RuleInvariant = Callable[[Rule], Optional[bool]]


class RuleInvariantViolationError(BaseException):
    """
    This exception is intended to be raised whenever an invariant has
    violated with regards to the properties of a rule.

    When raised, it should carry information about which rule(s) did
    not uphold a given invariant.
    """


def check_invariants(rule: Rule, *invariants: list[RuleInvariant]) -> Optional[bool]:
    """
    Utility function for checking multiple invariants on a rule.
    """
    return all(invariant(rule) for invariant in invariants)


def precedence_invariant(rule: Rule) -> Optional[bool]:
    """
    Invariant which checks that the precedence of a rule
    and its components are well-ordered, i.e. 'LEFT' < 'UNDEFINED' < 'RIGHT'.

    For a 'SimpleRule'/'Rule' this is always True.
    For a 'CompoundRule' this is True if and only if all the components
    are sorted.
    """
    match rule:
        case CompoundRule():
            for r1, r2 in pairwise(rule._components):
                if not (r1.properties.precedence <= r2.properties.precedence):
                    raise RuleInvariantViolationError(
                        f"Invariant violation - precedence: {r1} has lower precedence than {r2}")
            return True
        case Rule():
            return True
        case _:
            raise TypeError(f"Cannot apply invariant check to {rule} of type {type(rule)}")


def standalone_invariant(rule: Rule) -> Optional[bool]:
    """
    Invariant which checks that a given rule may be used without
    being combined with other rules.
    """
    match rule:
        case CompoundRule() as cr if len(cr._components) == 1:
            if not cr._components[0].properties.standalone:
                raise RuleInvariantViolationError(
                    f"Invariant violation - standalone: {rule} must be used a compound rule")
            return True
        case Rule():
            if not rule.properties.standalone:
                raise RuleInvariantViolationError(
                    f"Invariant violation - standalone: {rule} must be used a compound rule")
            return True
        case _:
            raise TypeError(f"Cannot apply invariant check to {rule} of type {type(rule)}")
