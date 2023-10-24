import unittest
from os2datascanner.engine2.rules.logical import OrRule

from os2datascanner.engine2.rules.rule import Rule
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.wordlists import OrderedWordlistRule
from os2datascanner.engine2.rules.utilities.properties import RulePrecedence
from os2datascanner.engine2.rules.utilities.invariants import (
    RuleInvariantViolationError, precedence_invariant, standalone_invariant,
)


class RulePropertyTests(unittest.TestCase):
    def test_rule_has_default_properties(self):
        r = Rule

        self.assertEqual(r.properties.precedence, RulePrecedence.UNDEFINED)
        self.assertTrue(r.properties.standalone)

    def test_cprrule_has_left_precedence(self):
        cpr = CPRRule()

        self.assertEqual(cpr.properties.precedence, RulePrecedence.LEFT)
        self.assertTrue(cpr.properties.standalone)

    def test_wordlist_has_right_precedence_and_cannot_stand_alone(self):
        wrl = OrderedWordlistRule("en_20211018_unit_test_words")

        self.assertEqual(wrl.properties.precedence, RulePrecedence.RIGHT)
        self.assertFalse(wrl.properties.standalone)

    def test_precedence_ordering_holds(self):
        left = RulePrecedence.LEFT
        undefined = RulePrecedence.UNDEFINED
        right = RulePrecedence.RIGHT

        # Left is less than everything, but left.
        self.assertTrue(left < right)
        self.assertTrue(left < undefined)
        self.assertFalse(left < left)

        # Undefined is less than right and itself.
        self.assertTrue(undefined < right)
        self.assertTrue(undefined < undefined)
        self.assertFalse(undefined < left)

        # Right is greater than everything, but right.
        self.assertTrue(right > left)
        self.assertTrue(right > undefined)
        self.assertFalse(right > right)


class RuleInvariantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cpr = CPRRule()
        self.wrl = OrderedWordlistRule("en_20211018_unit_test_words")

    def test_standalone_invariant_holds_for_cpr(self):
        self.assertTrue(standalone_invariant(self.cpr))

    def test_standalone_invariant_violated_for_wordlist(self):
        self.assertRaises(RuleInvariantViolationError,
                          standalone_invariant, self.wrl)

    def test_standalone_invariant_holds_for_or_with_single_cpr(self):
        rule = OrRule(self.cpr, name="A single CPRRule")

        self.assertTrue(standalone_invariant(rule))

    def test_standalone_invariant_violated_for_or_with_single_wordlist(self):
        rule = OrRule(self.wrl, name="A single Wordlist")

        self.assertRaises(RuleInvariantViolationError,
                          standalone_invariant, rule)

    def test_standalone_invariant_holds_for_compound_rule(self):
        rule = OrRule(self.wrl, self.cpr, name="Wordlist then CPR")

        self.assertTrue(standalone_invariant(rule))

    def test_precedence_invariant_holds_for_wellordered_or_rule(self):
        rule = OrRule(self.cpr, self.wrl, name="CPR then Wordlist")

        self.assertTrue(precedence_invariant(rule))

    def test_precedence_invariant_violated_for_illordered_or_rule(self):
        rule = OrRule(self.wrl, self.cpr, name="Wordlist then CPR")

        self.assertRaises(RuleInvariantViolationError,
                          precedence_invariant, rule)
