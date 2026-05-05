# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from datetime import date

from os2datascanner.engine2.rules.cpr import CPRRule, WordOrSymbol
from os2datascanner.engine2.rules.utilities.cpr_probability import CprProbabilityCalculator


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


class TestCprProbabilityCacheKeyBug:
    """Regression test for a bug where the probability cache used only the birth
    date as the key, ignoring the mod11_check parameter.

    Scenario: the same date is evaluated first with mod11_check=True (yielding a
    short list of ~60 valid CPRs) and then with mod11_check=False (yielding ~6000
    valid CPRs). With the old key, the second call would hit the first result and
    return an artificially low probability — or no match at all — for CPRs that
    fall beyond position 100 in the mod11 list.

    1111119990 born 1911-11-11 fails the mod11 check:
      - mod11_check=True  → not in the legal list → CPRRule returns []
      - mod11_check=False → in the legal list at a high index → probability 0.1
    With the old key both calls shared the same cache entry, so the second call
    returned [] instead of a match.
    """

    def test_cache_key_includes_mod11_flag(self):
        calc = CprProbabilityCalculator()
        birth = date(1911, 11, 11)

        cprs_with_mod11 = calc._calc_all_cprs(birth, mod11_check=True)
        cprs_without_mod11 = calc._calc_all_cprs(birth, mod11_check=False)

        # Without mod11 the list must be much larger (all 10-digit combinations
        # for that date), so the two results must differ.
        assert cprs_with_mod11 != cprs_without_mod11
        # Sanity: both cache entries must be stored independently.
        assert len(calc.cached_cprs) == 2

    def test_mod11_false_result_not_poisoned_by_prior_mod11_true_call(self):
        """Calling with mod11=True first must not corrupt the mod11=False result."""
        calc = CprProbabilityCalculator()

        # Prime the cache with mod11=True (1111119990 fails → not in this list).
        result_true = calc.cpr_check("1111119990", do_mod11_check=True)
        assert result_true == "Modulus 11 does not match"

        # Now call with mod11=False — must return a probability, not a poisoned result.
        result_false = calc.cpr_check("1111119990", do_mod11_check=False)
        assert isinstance(result_false, float), (
            f"Expected a probability float but got {result_false!r}. "
            "This indicates the cache returned the mod11=True result for the "
            "mod11=False query (the old cache-key bug)."
        )

    def test_cprrule_mod11_false_not_poisoned_by_same_birth_date(self):
        """The real-world trigger: two CPRs sharing the same birth date (2011-11-11),
        one passing mod11 ('1111119992') and one failing it ('1111119990').

        With the old single-string cache key:
          1. mod11=True scan of '1111119992' → passes mod11 → _calc_all_cprs(2011-11-11,
             mod11=True) called → cache['2011-11-11'] = <~60 valid CPRs>
          2. mod11=False scan of '1111119990' → same birth date → cache hit →
             returns the mod11=True list → '1111119990' not in it →
             cpr_check returns 'CPR is not a legal value' → no match reported

        With the fix (tuple key), step 2 builds its own cache['2011-11-11', False]
        and correctly finds '1111119990' at probability 0.1.
        """
        rule_strict = CPRRule(ignore_irrelevant=True, modulus_11=True, examine_context=False)
        rule_loose = CPRRule(ignore_irrelevant=True, modulus_11=False, examine_context=False)

        # Step 1: strict scan primes the cache for birth date 2011-11-11.
        strict_matches = list(rule_strict.match("1111119992"))
        assert strict_matches != [], "Setup failed: expected 1111119992 to match with mod11=True"

        # Step 2: loose scan for a different CPR with the same birth date
        # must NOT hit the mod11=True cache entry.
        loose_matches = list(rule_loose.match("1111119990"))
        assert loose_matches != [], (
            "Got no matches for '1111119990' with mod11=False after '1111119992' was "
            "scanned with mod11=True. Both share birth date 2011-11-11. This is the "
            "old cache-key bug: the mod11=True list was returned for the mod11=False query."
        )
