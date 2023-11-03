"""
Functions and utilities for performing inspection of rule properties
by checking invariants.
"""
from dataclasses import dataclass
import functools
from itertools import pairwise
from typing import Callable, Optional

from os2datascanner.engine2.rules.rule import Rule, SimpleRule
from os2datascanner.engine2.rules.logical import CompoundRule

__all__ = [
    'RuleInvariant',
    'RuleInvariantViolationException',
    'RuleInvariantViolationError',
    'RuleInvariantViolationWarning',
]

"""
Function signature for a rule invariant.
An invariant is a test based on the properties of a rule
that should hold for some rule (and perhaps its components).
"""
RuleInvariant = Callable[[Rule], Optional[bool]]


@dataclass
class RuleInvariantViolationException(BaseException):
    """
    This exception is intended to be raised whenever an invariant has
    violated with regards to the properties of a rule.

    When raised, it should carry information about which rule(s) did
    not uphold a given invariant.
    """
    message: str
    rules: list[Rule]


class RuleInvariantViolationError(RuleInvariantViolationException):
    """
    This exception is used to communicate that violation of the raising
    invariant is unacceptable and further usage of the violating rule
    should be discontinued until the invariant has been restored.
    """


class RuleInvariantViolationWarning(RuleInvariantViolationException):
    """
    This exception is used to communicate that violation of the raising
    invariant is not ideal, but it is not critical to the functioning
    of the rule, so usage of the violating rule can continue.
    """


def rule_invariant_type_error(rule):
    """
    Helper function for raising an informative, nicely-formatted TypeError
    when trying to apply an invariant to a non-rule object.
    """
    raise TypeError(
        f"Cannot apply invariant check to {rule} of type {type(rule)}")


class RuleInvariantChecker:
    """
    Utility class for checking invariants.
    """
    default_invariants = [
        "precedence",
        "standalone",
        ]

    def __init__(self, *invariants: list) -> None:
        if not invariants:
            invariants = self.default_invariants

        self._invariants = []

        for invariant in invariants:
            if callable(invariant):
                self._invariants.append(invariant)
            elif isinstance(invariant, str):
                try:
                    self._invariants.append(getattr(self, f"{invariant}_invariant"))
                except AttributeError:
                    continue

    def check_invariants(self, rule: Rule) -> bool:
        """
        Utility function for checking multiple invariants on a rule.

        :param rule:
        """

        return all(invariant(rule) for invariant in self._invariants)

    @staticmethod
    @functools.cache
    def precedence_invariant(rule: Rule) -> Optional[bool]:
        """
        Invariant which checks that the precedence of a rule
        and its components are well-ordered, i.e. 'LEFT' < 'UNDEFINED' < 'RIGHT'.

        For a 'SimpleRule'/'Rule' this is always True.
        For a 'CompoundRule' this is True if and only if all the components
        are sorted according to their 'RulePrecedence'.

        :param rule:
        """
        if not isinstance(rule, Rule):
            rule_invariant_type_error(rule)

        if isinstance(rule, CompoundRule):
            for r1, r2 in pairwise(rule._components):
                if not (r1.properties.precedence <= r2.properties.precedence):
                    raise RuleInvariantViolationError("precedence", rules=[r1, r2])

        return True

    @staticmethod
    @functools.cache
    def standalone_invariant(rule: Rule) -> Optional[bool]:
        """
        Invariant which checks that a given rule may be used without
        being combined with other rules.

        :param rule:
        """
        if not isinstance(rule, Rule):
            rule_invariant_type_error(rule)

        if isinstance(rule, CompoundRule) and len(rule._components) == 1:
            rule = rule._components[0]

        if not rule.properties.standalone:
            raise RuleInvariantViolationError("standalone", rules=[rule])

        return True

    @staticmethod
    @functools.cache
    def outputtype_invariant(rule: Rule) -> Optional[bool]:
        """
        Invariant which checks that a rule (and its components)
        all work on a single OutputType in order to avoid duplicate
        conversions.

        :param rule:
        """

        if not isinstance(rule, Rule):
            rule_invariant_type_error(rule)

        @functools.cache
        def get_otype(rule: Rule):
            """
            Checks and gets the OutputType for a rule.
            OutputType is only well-defined for SimpleRule,
            but since we require that components of a CompoundRule
            all have the same OutputType for this invariant, we
            check that they do indeed have the same OutputType and
            return that.

            If the OutputTypes don't match, we raise an exception.
            """

            match rule:
                case CompoundRule() as cr:
                    def check(left_otype, right_otype, i):
                        if left_otype != right_otype:
                            raise RuleInvariantViolationWarning(
                                "outputtype", rules=[cr._components[i],
                                                     cr._components[i+1]])
                        return True

                    otypes = [get_otype(c) for c in cr._components]

                    if all(check(l, r, i) for i, (l, r) in enumerate(pairwise(otypes))):
                        return otypes[0]
                case SimpleRule():
                    return rule.operates_on
                case _:
                    rule_invariant_type_error(rule)

        if isinstance(rule, CompoundRule):
            return all(get_otype(left) == get_otype(right)
                       for left, right in pairwise(rule._components))
        return True
