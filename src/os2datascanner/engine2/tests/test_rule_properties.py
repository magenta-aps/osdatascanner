import pytest

from os2datascanner.engine2.rules.logical import OrRule
from os2datascanner.engine2.rules.rule import Rule
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.wordlists import OrderedWordlistRule
from os2datascanner.engine2.rules.utilities.properties import RulePrecedence


class TestRuleProperty:

    @pytest.fixture(scope="module")
    def cpr_rule(self):
        return CPRRule()

    @pytest.fixture(scope="module")
    def wordlist_rule(self):
        return OrderedWordlistRule("en_20211018_unit_test_words")

    @pytest.fixture(scope="module")
    def or_rule(self, cpr_rule, wordlist_rule):
        return OrRule(cpr_rule, wordlist_rule, name="CPR then wordlist")

    def test_rule_has_default_properties(self):
        assert Rule.properties.precedence == RulePrecedence.UNDEFINED
        assert Rule.properties.standalone

    def test_cprrule_has_left_precedence(self, cpr_rule):
        assert cpr_rule.properties.precedence == RulePrecedence.LEFT
        assert cpr_rule.properties.standalone

    def test_wordlist_has_right_precedence_and_cannot_stand_alone(self, wordlist_rule):
        assert wordlist_rule.properties.precedence == RulePrecedence.RIGHT
        assert not wordlist_rule.properties.standalone

    def test_orrule_has_default_properties(self, or_rule):
        assert or_rule.properties.precedence == RulePrecedence.UNDEFINED
        assert or_rule.properties.standalone

    def test_precedence_ordering_lt(self):
        left = RulePrecedence.LEFT
        undefined = RulePrecedence.UNDEFINED
        right = RulePrecedence.RIGHT

        # Left is less than everything, but left.
        assert left < right
        assert left < undefined
        assert not left < left

        # Undefined is less than right and itself.
        assert undefined < right
        assert undefined < undefined
        assert not undefined < left

        # Right is less than nothing.
        assert not right < left
        assert not right < undefined
        assert not right < right

    def test_precedence_ordering_gt(self):
        left = RulePrecedence.LEFT
        undefined = RulePrecedence.UNDEFINED
        right = RulePrecedence.RIGHT

        # Left is greater than nothing.
        assert not left > left
        assert not left > undefined
        assert not left > right

        # Undefined is greater than left and itself.
        assert undefined > left
        assert undefined > undefined
        assert not undefined > right

        # Right is greater than everything, but right.
        assert right > left
        assert right > undefined
        assert not right > right

    def test_precedence_ordering_le(self):
        left = RulePrecedence.LEFT
        undefined = RulePrecedence.UNDEFINED
        right = RulePrecedence.RIGHT

        # Left is less-than-or-equal-to everything.
        assert left <= left
        assert left <= undefined
        assert left <= right

        # Undefined is less-than-or-equal-to right and itself.
        assert not undefined <= left
        assert undefined <= undefined
        assert undefined <= right

        # Right is less-than-or-equal-to only right.
        assert not right <= left
        assert not right <= undefined
        assert right <= right

    def test_precedence_ordering_ge(self):
        left = RulePrecedence.LEFT
        undefined = RulePrecedence.UNDEFINED
        right = RulePrecedence.RIGHT

        # Left is greater-than-or-equal-to only left.
        assert left >= left
        assert not left >= undefined
        assert not left >= right

        # Undefined is greater-than-or-equal-to left and itself.
        assert undefined >= left
        assert undefined >= undefined
        assert not undefined >= right

        # Right is greater-than-or-equal-to everything.
        assert right >= left
        assert right >= undefined
        assert right >= right
