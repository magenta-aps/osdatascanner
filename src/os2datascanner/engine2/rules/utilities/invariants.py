"""
Functions and utilities for performing inspection of rule properties
by checking invariants.
"""
from typing import Callable, Optional

from ..rule import Rule
# from .properties import RulePrecedence, RuleProperties, RulePropertyInvariantViolation

"""
"""
RuleInvariant = Callable[[Rule], Optional[Exception]]


def check_invariants(rule: Rule, *invariants: list[RuleInvariant]) -> Optional[bool]:
    """

    """
    for invariant in invariants:
        if error := invariant(rule):
            raise error

    return True
