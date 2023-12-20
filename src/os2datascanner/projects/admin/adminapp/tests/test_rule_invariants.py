import unittest

from os2datascanner.engine2.rules.logical import OrRule
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.wordlists import OrderedWordlistRule
from os2datascanner.engine2.rules.utilities.invariants import (
    RuleInvariantViolationError, precedence_invariant, standalone_invariant,
)


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
