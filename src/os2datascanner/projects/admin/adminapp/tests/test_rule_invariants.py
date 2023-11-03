import unittest

from os2datascanner.engine2.rules.logical import OrRule
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.name import NameRule
from os2datascanner.engine2.rules.wordlists import OrderedWordlistRule
from os2datascanner.projects.admin.adminapp.views.utils.invariants import (
    RuleInvariantViolationError, RuleInvariantChecker,
)


class RuleInvariantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.checker = RuleInvariantChecker()
        self.cpr = CPRRule()
        self.name = NameRule()
        self.wrl = OrderedWordlistRule("en_20211018_unit_test_words")

    def test_standalone_invariant_holds_for_cpr(self):
        self.assertTrue(self.checker.standalone_invariant(self.cpr))

    def test_standalone_invariant_holds_for_name(self):
        self.assertTrue(self.checker.standalone_invariant(self.name))

    def test_standalone_invariant_violated_for_wordlist(self):
        self.assertRaises(RuleInvariantViolationError,
                          self.checker.standalone_invariant, self.wrl)

    def test_standalone_invariant_holds_for_or_with_single_cpr(self):
        rule = OrRule(self.cpr, name="A single CPRRule")

        self.assertTrue(self.checker.standalone_invariant(rule))

    def test_standalone_invariant_holds_for_or_with_single_name(self):
        rule = OrRule(self.name, name="A single NameRule")

        self.assertTrue(self.checker.standalone_invariant(rule))

    def test_standalone_invariant_violated_for_or_with_single_wordlist(self):
        rule = OrRule(self.wrl, name="A single Wordlist")

        self.assertRaises(RuleInvariantViolationError,
                          self.checker.standalone_invariant, rule)

    def test_standalone_invariant_holds_for_compound_rule(self):
        rule = OrRule(self.wrl, self.cpr, name="Wordlist then CPR")

        self.assertTrue(self.checker.standalone_invariant(rule))

    def test_precedence_invariant_holds_for_cpr_then_health(self):
        rule = OrRule(self.cpr, self.wrl, name="CPR then Wordlist")

        self.assertTrue(self.checker.precedence_invariant(rule))

    def test_precedence_invariant_holds_for_cpr_then_name(self):
        rule = OrRule(self.cpr, self.name, name="CPR then Name")

        self.assertTrue(self.checker.precedence_invariant(rule))

    def test_precedence_invariant_holds_for_name_then_healthe(self):
        rule = OrRule(self.name, self.wrl, name="Name then Wordlist")

        self.assertTrue(self.checker.precedence_invariant(rule))

    def test_precedence_invariant_violated_for_wordlist_then_cpr(self):
        rule = OrRule(self.wrl, self.cpr, name="Wordlist then CPR")

        self.assertRaises(RuleInvariantViolationError,
                          self.checker.precedence_invariant, rule)

    def test_precedence_invariant_violated_for_name_then_cpr(self):
        rule = OrRule(self.name, self.cpr, name="Name then CPR")

        self.assertRaises(RuleInvariantViolationError,
                          self.checker.precedence_invariant, rule)

    def test_precedence_invariant_violated_for_wordlist_then_name(self):
        rule = OrRule(self.wrl, self.name, name="Wordlist then Name")

        self.assertRaises(RuleInvariantViolationError,
                          self.checker.precedence_invariant, rule)
