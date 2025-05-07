import pytest

from ..pipeline.matcher import censor_context
from ..rules.regex import RegexRule
from ..rules.cpr import CPRRule


class MockRule:
    # Stub for unit testing
    def __init__(self, method):
        self.intervals = method

    def get_censor_intervals(self, context):
        return self.intervals(context)


@pytest.fixture
def censor_1_to_4():
    return MockRule(lambda _: [(1, 4)])


@pytest.fixture
def censor_3_to_6():
    return MockRule(lambda _: [(3, 6)])


@pytest.fixture
def censor_7_to_9():
    return MockRule(lambda _: [(7, 9)])


class TestCensorContextUnitTests:
    def test_censor(self, censor_3_to_6):
        actual = censor_context("DetteErKontekst", [censor_3_to_6])

        assert actual == "DetXXXrKontekst"

    def test_multiple_rules(self, censor_1_to_4, censor_7_to_9):
        """Multiple rules should be able to censor the same context"""
        actual = censor_context("DetteErKontekst", [censor_1_to_4, censor_7_to_9])

        assert actual == "DXXXeErXXntekst"

    def test_overlap(self, censor_1_to_4, censor_3_to_6):
        """Rules should be able to censor context with overlapping intervals,
        which shouldn't lead to extra 'X's"""
        actual = censor_context("DetteErKontekst", [censor_1_to_4, censor_3_to_6])

        assert actual == "DXXXXXrKontekst"

    def test_interval_out_of_context(self, censor_7_to_9):
        """Trying to censor something of outside the context, should do anything."""
        actual = censor_context("Hej", [censor_7_to_9])

        assert actual == "Hej"

    def test_rule_with_multiple_intervals(self):
        """A single rule should be able to censor multiple intervals."""
        censor_multiple = MockRule(lambda _: [(2, 5), (8, 9)])
        actual = censor_context("DetteErKontekst", [censor_multiple])

        assert actual == "DeXXXErKXntekst"

    def test_censor_everything(self):
        censor_all = MockRule(lambda context: [(0, len(context))])
        actual = censor_context("DetteErKontekst", [censor_all])

        assert actual == "XXXXXXXXXXXXXXX"

    def test_no_intervals(self):
        """Without any given intervals to be censored, the original string should be returned."""
        censor_nothing = MockRule(lambda _: [])
        actual = censor_context("DetteErKontekst", [censor_nothing])

        assert actual == "DetteErKontekst"

    def test_negative_interval(self):
        """Negative intervals shouldn't be given, but in case it is, nothing should be done."""
        censor_negative = MockRule(lambda _: [(-15, -5)])
        actual = censor_context("DetteErKontekst", [censor_negative])

        assert actual == "DetteErKontekst"

    def test_inverted_interval(self):
        """If the right side of interval is less than left, nothing should be done."""
        censor_inverted = MockRule(lambda _: [(6, 3)])
        actual = censor_context("DetteErKontekst", [censor_inverted])

        assert actual == "DetteErKontekst"

    def test_censor_none(self, censor_3_to_6):
        actual = censor_context(None, [censor_3_to_6])

        assert actual is None


class TestCensorContextRealRules:
    def test_regex_rule(self):
        """The RegexRule censors everything it matches."""
        actual = censor_context("acaabaaacaaabbb", [RegexRule("a{2}b+")])

        assert actual == "acXXXaaacaXXXXX"

    def test_cpr_rule(self):
        """CPRRule censors numbers matching its regex."""
        actual = censor_context("kontekst 111111-1118 omkring", [CPRRule()])

        assert actual == "kontekst XXXXXX-XXXX omkring"
