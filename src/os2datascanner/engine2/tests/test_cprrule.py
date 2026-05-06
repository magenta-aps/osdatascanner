# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import os
import pytest
from datetime import date

from os2datascanner.engine2.rules.cpr import CPRRule, WordOrSymbol
from os2datascanner.engine2.rules.utilities.cpr_probability import CprProbabilityCalculator

here_path = os.path.dirname(__file__)
test_data_path = os.path.join(here_path, "data")


class TestCPRRule:
    @pytest.mark.parametrize("blacklisted_word", [
        "p-nr", "p.nr", "p-nummer", "pnr", "customer no", "customer-no",
        "bilagsnummer", "order number", "ordrenummer", "fakturanummer",
        "faknr", "fak-nr", "tullstatistisk", "tullstatistik", "test report no",
        "protocol no.", "dhk:tx",
    ])
    def test_blacklisted_words(self, blacklisted_word):
        rule = CPRRule(modulus_11=True, ignore_irrelevant=False, examine_context=True)
        matches = list(rule.match(blacklisted_word + " 1111111118"))

        assert not matches

    def test_presentation_raw(self):
        rule = CPRRule()
        assert rule.presentation_raw == (
            "CPR number (with modulus 11, relevance check, and context check)")

    def test_presentation_raw_no_settings(self):
        rule = CPRRule(modulus_11=False, ignore_irrelevant=False, examine_context=False)
        assert rule.presentation_raw == "CPR number"

    @pytest.mark.parametrize("content,ignore_irrelevant,prob", [
        ("1111111118", True, 1.0),
        ("1111119992", True, 0.1),
        ("1111118880", True, 0.1),
        ("1111117779", True, 0.25),
        ("1111119992", False, 1.0),
        ("1111118880", False, 1.0),
        ("1111117779", False, 1.0)
    ])
    def test_probability_check(self, content, ignore_irrelevant, prob):
        rule = CPRRule(ignore_irrelevant=ignore_irrelevant, modulus_11=True, examine_context=False)
        matches = list(rule.match(content))

        assert matches[0]["probability"] == prob

    @pytest.mark.parametrize("content,mod11,result", [
        ("1111119990", True, []),
        ("1111119991", True, []),
        ("1111119993", True, []),
        ("1111119994", True, []),
        ("1111119995", True, []),
        ("1111119996", True, []),
        ("1111119997", True, []),
        ("1111119998", True, []),
        ("1111119999", True, []),
        ("1111119990", False, [
            {'match': '1111XXXXXX',
             'offset': 0,
             'context': '1111119990',
             'context_offset': 0,
             'sensitivity': None,
             'probability': 0.1}
            ]),
        ("1111119991", False, [
            {'match': '1111XXXXXX',
             'offset': 0,
             'context': '1111119991',
             'context_offset': 0,
             'sensitivity': None,
             'probability': 0.1}
            ]),
        ("1111119992", False, [
            {'match': '1111XXXXXX',
             'offset': 0,
             'context': '1111119992',
             'context_offset': 0,
             'sensitivity': None,
             'probability': 0.1}
            ]),
    ])
    def test_probability_number_ignore_irrelevant(self, content, mod11, result):
        rule = CPRRule(ignore_irrelevant=True, modulus_11=mod11, examine_context=False)
        matches = list(rule.match(content))

        assert matches == result


@pytest.fixture
def word_tuple():
    return ("wordiwordi", "")


@pytest.fixture
def symbol_tuple():
    return ("", "]")


class TestWordOrSymbol:
    def test_word_tuple(self, word_tuple):
        word_or_sym = WordOrSymbol(*word_tuple)

        assert bool(word_or_sym.word)
        assert not bool(word_or_sym.symbol)

    def test_symbol_tuple(self, symbol_tuple):
        word_or_sym = WordOrSymbol(*symbol_tuple)

        assert not bool(word_or_sym.word)
        assert bool(word_or_sym.symbol)

    def test_empty_tuple(self):
        word_or_sym = WordOrSymbol(*("", ""))

        assert not bool(word_or_sym.word)
        assert not bool(word_or_sym.symbol)


class TestCprProbabilityCacheKey:
    """The probability cache must store results separately per (birth_date, mod11_check) pair."""

    def test_cache_key_includes_mod11_flag(self):
        calc = CprProbabilityCalculator()
        birth = date(1911, 11, 11)

        cprs_with_mod11 = calc._calc_all_cprs(birth, mod11_check=True)
        cprs_without_mod11 = calc._calc_all_cprs(birth, mod11_check=False)

        assert cprs_with_mod11 != cprs_without_mod11
        assert len(calc.cached_cprs) == 2

    def test_mod11_false_not_poisoned_by_mod11_true_same_birth_date(self):
        """A mod11=False scan for 1111119990 must still find a match even if
        a mod11=True scan for a CPR sharing the same birth date ran first."""
        rule_mod11 = CPRRule(ignore_irrelevant=True, modulus_11=True, examine_context=False)
        rule_no_mod11 = CPRRule(ignore_irrelevant=True, modulus_11=False, examine_context=False)

        mod11_matches = list(rule_mod11.match("1111119992"))
        assert mod11_matches != [], "Setup failed: expected 1111119992 to match with mod11=True"

        no_mod11_matches = list(rule_no_mod11.match("1111119990"))
        assert no_mod11_matches != []

    def test_scenario_from_data_file(self):
        """A mod11=False scan must find 1111119990 even after a mod11=True scan
        of the same content with a CPR sharing the same birth date."""
        with open(os.path.join(test_data_path, "cpr_same_birth_date.txt")) as f:
            content = f.read()

        rule_mod11 = CPRRule(ignore_irrelevant=True, modulus_11=True, examine_context=False)
        rule_no_mod11 = CPRRule(ignore_irrelevant=True, modulus_11=False, examine_context=False)

        list(rule_mod11.match(content))

        no_mod11_matches = [m for m in rule_no_mod11.match(content)
                            if "1111119990" in str(m)]
        assert no_mod11_matches != []
