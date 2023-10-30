import unittest

from os2datascanner.engine2.rules.logical import OrRule
from os2datascanner.engine2.rules.rule import Rule
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.wordlists import OrderedWordlistRule
from os2datascanner.engine2.rules.utilities.properties import RulePrecedence


class RulePropertyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cpr = CPRRule()
        self.wrl = OrderedWordlistRule("en_20211018_unit_test_words")
        self.or_rule = OrRule(self.cpr, self.wrl, name="CPR then wordlist")

    def test_rule_has_default_properties(self):
        self.assertEqual(Rule.properties.precedence, RulePrecedence.UNDEFINED)
        self.assertTrue(Rule.properties.standalone)

    def test_cprrule_has_left_precedence(self):
        self.assertEqual(self.cpr.properties.precedence, RulePrecedence.LEFT)
        self.assertTrue(self.cpr.properties.standalone)

    def test_wordlist_has_right_precedence_and_cannot_stand_alone(self):
        self.assertEqual(self.wrl.properties.precedence, RulePrecedence.RIGHT)
        self.assertFalse(self.wrl.properties.standalone)

    def test_orrule_has_default_properties(self):
        self.assertEqual(self.or_rule.properties.precedence, RulePrecedence.UNDEFINED)
        self.assertTrue(self.or_rule.properties.standalone)

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
