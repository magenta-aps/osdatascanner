"""
Functions and utilities for performing inspection of rule properties
by checking invariants.
"""
from itertools import all
from typing import Callable, Optional

from ..rule import Rule
# from .properties import RulePrecedence, RuleProperties

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
