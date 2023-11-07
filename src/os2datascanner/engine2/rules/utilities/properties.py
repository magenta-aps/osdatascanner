"""
Properties for simple rules that can be used to enforce
invariants when combining using compound rules.
"""
from enum import Enum
from typing import NamedTuple

__all__ = [
    'RulePrecedence',
    'RuleProperties',
]


class RulePrecedence(Enum):
    """
    Definitions for precedence for a rule.
    This is similar to associativity in programming language theory,
    but here we are dealing with operands instead of operators.

    Some SimpleRules are expensive, and some are cheap: checking when a file
    was last modified requires much less work than unpacking a 400MB PDF and
    doing OCR on the second massive JPEG on its 2,500th page, for example. The
    hints given by the RulePrecedence enumeration can be used to warn the user
    if a proposed Rule performs expensive (right) operations before cheaper
    (left) ones.

    Note that these hints are not used by the rule engine itself; if a user of
    the rule engine wants to enforce precedence constraints, it should do so
    /before/ submitting a Rule for execution.

    An example:
    Let's say that for some rules 'r1' and 'r2', we want to create a third
    rule 'r3 = r1 (or) r2'. We have to take into account that
    the compound-rule implements short-circuiting for efficiency
    reasons, so it would make sense to evaluate the 'cheapest' rule
    first. Let's say that 'r2' is cheaper in this case. To express that,
    we could say that 'r2' has left-precedence, so when making 'r3 = r1 (or) r2',
    we can check that 'r2' is left of 'r1', i.e. enforce an invariant.
    If the invariant is violated, then we can either raise an error or
    reorder based on operand-precedence so we get 'r3 = r2 (or) r1' instead and
    thus restore the invariant, depending on what is appropriate for the given
    situation.

    - 'UNDEFINED':
      'UNDEFINED' is the neutral element of precedence.

    - 'LEFT':
      'LEFT' means that a rule should be composed to the left of
      all rules that don't have left-precedence.

    - 'RIGHT':
      'RIGHT' means that a rule should be composed to the right of
      all rules that don't have right-precedence.
    """
    UNDEFINED = 'UNDEFINED'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'

    def __lt__(self, other):
        if self.__class__ != other.__class__:
            return NotImplemented

        match (self, other):
            case (RulePrecedence.LEFT | RulePrecedence.UNDEFINED,
                  RulePrecedence.UNDEFINED | RulePrecedence.RIGHT):
                return True
            case _:
                return False

    def __gt__(self, other):
        if self.__class__ != other.__class__:
            return NotImplemented

        match (self, other):
            case (RulePrecedence.RIGHT | RulePrecedence.UNDEFINED,
                  RulePrecedence.UNDEFINED | RulePrecedence.LEFT):
                return True
            case _:
                return False

    def __le__(self, other):
        if self.__class__ != other.__class__:
            return NotImplemented

        match (self, other):
            case ((RulePrecedence.LEFT, _)
                  | (RulePrecedence.UNDEFINED, RulePrecedence.UNDEFINED | RulePrecedence.RIGHT)
                  | (RulePrecedence.RIGHT, RulePrecedence.RIGHT)):
                return True
            case _:
                return False

    def __ge__(self, other):
        if self.__class__ != other.__class__:
            return NotImplemented

        match (self, other):
            case ((RulePrecedence.RIGHT, _)
                  | (RulePrecedence.UNDEFINED, RulePrecedence.UNDEFINED | RulePrecedence.LEFT)
                  | (_, RulePrecedence.LEFT)):
                return True
            case _:
                return False


class RuleProperties(NamedTuple):
    """
    A collection of immutable properties for a rule.

    - 'precedence':
      Defines how a rule may be combined using a compound rule.

    - 'standalone':
      Defines whether a user is allowed to create compound rules
      with only a single instance of this rule.

      Note that this property is only intended to be enforced
      through the invariant checking and has nothing to do
      with constructing instances of the rule.
    """
    precedence: RulePrecedence
    standalone: bool
