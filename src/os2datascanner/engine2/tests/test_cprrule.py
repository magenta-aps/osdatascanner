import pytest

from os2datascanner.engine2.rules.cpr import CPRRule, WordOrSymbol


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
        ("1111119990", False, []),
        ("1111119991", False, []),
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
