"""
Functions and utilities for performing inspection of rule properties
by checking invariants.
"""
from dataclasses import dataclass
import functools
from itertools import pairwise
from typing import Callable

from os2datascanner.engine2.rules.rule import Rule, SimpleRule
from os2datascanner.engine2.rules.logical import CompoundRule, NotRule
from os2datascanner.engine2.rules.dict_lookup import DictLookupRule

"""
Function signature for a rule invariant.
An invariant is a test based on the properties of a rule
that should hold for some rule (and perhaps its components).
"""
RuleInvariant = Callable[[Rule], bool | None]

rule_invariants: dict[str, RuleInvariant] = {}


def register_invariant(name=None):
    """
    Registers a function that fulfills the type interface
    as a RuleInvariant.
    """
    def decorate(func):
        nonlocal name
        if not name:
            name = func.__name__

        if name in rule_invariants:
            raise ValueError("Duplicate registration - Invariant with "
                             f"name: {name} has already been registered.")

        rule_invariants[name] = func
        return func

    return decorate


@dataclass
class RuleInvariantViolationError(BaseException):
    """
    This exception is intended to be raised whenever an invariant has
    violated with regards to the properties of a rule.

    When raised, it should carry information about which rule(s) did
    not uphold a given invariant.

    This exception is used to communicate that violation of the raising
    invariant is unacceptable and further usage of the violating rule
    should be discontinued until the invariant has been restored.
    """
    message: str
    rules: list[Rule]
    is_warning: bool = False


def rule_invariant_type_error(rule):
    """
    Helper function for raising an informative, nicely-formatted TypeError
    when trying to apply an invariant to a non-rule object.
    """
    raise TypeError(
        f"Cannot apply invariant check to {rule} of type {type(rule)}")


def _get_checked_otype(cr: CompoundRule, *otypes):
    """
    Checks and gets the OutputType for a rule.
    OutputType is only well-defined for SimpleRule,
    but since we require that components of a CompoundRule
    all have the same OutputType for this invariant, we
    check that they do indeed have the same OutputType and
    return that.

    If the OutputTypes don't match, we raise an exception.
    """
    for i, (left_rule, right_rule) in enumerate(pairwise(otypes)):
        if left_rule != right_rule:
            raise RuleInvariantViolationError(
                "outputtype", rules=[cr._components[i], cr._components[i+1]],
                is_warning=True)

    return otypes[0]


@functools.cache
@register_invariant()
def precedence_invariant(rule: Rule) -> bool | None:
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


@functools.cache
@register_invariant()
def standalone_invariant(rule: Rule, is_top_rule: bool = True) -> bool | None:
    """
    Invariant which checks that a given rule may be used without
    being combined with other rules.

    :param rule:
    """

    match rule:
        case CompoundRule() if len(rule._components) == 0:
            standalone = False
        case CompoundRule():
            standalone = any(standalone_invariant(c, is_top_rule=False)
                             for c in rule._components)
        case NotRule() | DictLookupRule():
            standalone = standalone_invariant(rule._rule, is_top_rule=False)
        case SimpleRule() | Rule():
            standalone = rule.properties.standalone
        case _:
            rule_invariant_type_error(rule)

    if is_top_rule and not standalone:
        raise RuleInvariantViolationError("standalone", rules=[rule])

    return standalone


@functools.cache
@register_invariant()
def outputtype_invariant(rule: Rule) -> bool | None:
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
        Attempts to retrieve the OutputType of a rule.

        :param rule:
        """
        match rule:
            case CompoundRule() as cr:
                return _get_checked_otype(cr, [get_otype(c) for c in cr._components])
            case SimpleRule():
                return rule.operates_on
            case _:
                rule_invariant_type_error(rule)

    if isinstance(rule, CompoundRule):
        return all(get_otype(left) == get_otype(right)
                   for left, right in pairwise(rule._components))
    return True


@functools.cache
@register_invariant()
def components_invariant(rule: Rule) -> bool | None:
    """
    Invariant which checks that a compoundrule has at least one component.
    """

    match rule:
        case CompoundRule():
            if len(rule._components) < 2:
                raise RuleInvariantViolationError("components", rules=[rule])
            return all(components_invariant(c) for c in rule._components)
        case NotRule() | DictLookupRule():
            if not rule._rule:
                raise RuleInvariantViolationError("components", rules=[rule])
            return components_invariant(rule._rule)
        case SimpleRule() | Rule():
            return True
        case _:
            rule_invariant_type_error(rule)
    return True


class RuleInvariantChecker:
    """
    Utility class for checking invariants.
    """
    default_invariants = [
        "precedence_invariant",
        "standalone_invariant",
        "components_invariant",
        ]

    def __init__(self, *invariants: list) -> None:
        invariants = invariants or self.default_invariants
        self._invariants = [func or inv for inv in invariants
                            if (func := rule_invariants.get(inv)) or callable(inv)]

    def check_invariants(self, rule: Rule) -> bool:
        """
        Utility function for checking multiple invariants on a rule.
        Returns True if no invariant raises an exception.

        :param rule:
        """

        for invariant in self._invariants:
            invariant(rule)

        return True
