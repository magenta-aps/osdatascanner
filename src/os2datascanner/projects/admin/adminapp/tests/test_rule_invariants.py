import pytest

from os2datascanner.engine2.rules.logical import OrRule
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.name import NameRule
from os2datascanner.engine2.rules.wordlists import OrderedWordlistRule
from os2datascanner.projects.admin.adminapp.views.utils.invariants import (
    RuleInvariantViolationError, RuleInvariantChecker,
)


class TestRuleInvariant:

    @pytest.fixture(scope="class")
    def invariant_checker(self):
        return RuleInvariantChecker()

    @pytest.fixture(scope="class")
    def cpr_rule(self):
        return CPRRule()

    @pytest.fixture(scope="class")
    def name_rule(self):
        return NameRule()

    @pytest.fixture(scope="class")
    def wordlist_rule(self):
        return OrderedWordlistRule("en_20211018_unit_test_words")

    def test_standalone_invariant_holds_for_cpr(self, invariant_checker, cpr_rule):
        assert invariant_checker.check_invariants(cpr_rule)

    def test_standalone_invariant_holds_for_name(self, invariant_checker, name_rule):
        assert invariant_checker.check_invariants(name_rule)

    def test_standalone_invariant_violated_for_wordlist(self, invariant_checker, wordlist_rule):
        with pytest.raises(RuleInvariantViolationError):
            invariant_checker.check_invariants(wordlist_rule)

    def test_standalone_invariant_holds_for_or_with_single_cpr(self, invariant_checker, cpr_rule):
        rule = OrRule(cpr_rule, name="A single CPRRule")
        assert invariant_checker.check_invariants(rule)

    def test_standalone_invariant_holds_for_or_with_single_name(self, invariant_checker, name_rule):
        rule = OrRule(name_rule, name="A single NameRule")

        assert invariant_checker.check_invariants(rule)

    def test_standalone_invariant_violated_for_or_with_single_wordlist(self, invariant_checker,
                                                                       wordlist_rule):
        rule = OrRule(wordlist_rule, name="A single Wordlist")

        with pytest.raises(RuleInvariantViolationError):
            invariant_checker.check_invariants(rule)

    def test_precedence_invariant_holds_for_cpr_then_health(self, invariant_checker, cpr_rule,
                                                            wordlist_rule):

        rule = OrRule(cpr_rule, wordlist_rule, name="CPR then Wordlist")

        assert invariant_checker.check_invariants(rule)

    def test_precedence_invariant_holds_for_cpr_then_name(self, invariant_checker, cpr_rule,
                                                          name_rule):

        rule = OrRule(cpr_rule, name_rule, name="CPR then Name")

        assert invariant_checker.check_invariants(rule)

    def test_precedence_invariant_holds_for_name_then_health(self, invariant_checker, name_rule,
                                                             wordlist_rule):
        rule = OrRule(name_rule, wordlist_rule, name="Name then Wordlist")

        assert invariant_checker.check_invariants(rule)

    def test_precedence_invariant_violated_for_wordlist_then_cpr(self, invariant_checker,
                                                                 wordlist_rule, cpr_rule):

        rule = OrRule(wordlist_rule, cpr_rule, name="Wordlist then CPR")
        with pytest.raises(RuleInvariantViolationError):
            invariant_checker.check_invariants(rule)

    def test_precedence_invariant_violated_for_name_then_cpr(self, invariant_checker, name_rule,
                                                             cpr_rule):

        rule = OrRule(name_rule, cpr_rule, name="Name then CPR")
        with pytest.raises(RuleInvariantViolationError):
            invariant_checker.check_invariants(rule)

    def test_precedence_invariant_violated_for_wordlist_then_name(self, invariant_checker,
                                                                  wordlist_rule, name_rule):

        rule = OrRule(wordlist_rule, name_rule, name="Wordlist then Name")

        with pytest.raises(RuleInvariantViolationError):
            invariant_checker.check_invariants(rule)
