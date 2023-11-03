"""
Functions and utilities for performing inspection of rule properties
by checking invariants.
"""
from dataclasses import dataclass
from itertools import pairwise
from typing import Callable, Optional

from ..rule import Rule
from ..logical import CompoundRule

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


@dataclass
class RuleInvariantViolationError(BaseException):
    """
    This exception is intended to be raised whenever an invariant has
    violated with regards to the properties of a rule.

    When raised, it should carry information about which rule(s) did
    not uphold a given invariant.
    """
    message: str
    rules: list[Rule]


def check_invariants(
        rule: Rule,
        *
        invariants: list[RuleInvariant]) -> list[RuleInvariantViolationError]:
    """
    Utility function for checking multiple invariants on a rule.

    :param rule:
    :param invariants:
    """

    return all(invariant(rule) for invariant in invariants)


def precedence_invariant(rule: Rule) -> Optional[bool]:
    """
    Invariant which checks that the precedence of a rule
    and its components are well-ordered, i.e. 'LEFT' < 'UNDEFINED' < 'RIGHT'.

    For a 'SimpleRule'/'Rule' this is always True.
    For a 'CompoundRule' this is True if and only if all the components
    are sorted.
    :param rule:
    """
    if not isinstance(rule, Rule):
        raise TypeError(f"Cannot apply invariant check to {rule} of type {type(rule)}")

    if isinstance(rule, CompoundRule):
        for r1, r2 in pairwise(rule._components):
            if not (r1.properties.precedence <= r2.properties.precedence):
                raise RuleInvariantViolationError("precedence", rules=[r1, r2])

    return True


def standalone_invariant(rule: Rule) -> Optional[bool]:
    """
    Invariant which checks that a given rule may be used without
    being combined with other rules.

    :param rule:
    """
    if not isinstance(rule, Rule):
        raise TypeError(f"Cannot apply invariant check to {rule} of type {type(rule)}")

    if isinstance(rule, CompoundRule) and len(rule._components) == 1:
        rule = rule._components[0]

    if not rule.properties.standalone:
        raise RuleInvariantViolationError("standalone", rules=[rule])

    return True
