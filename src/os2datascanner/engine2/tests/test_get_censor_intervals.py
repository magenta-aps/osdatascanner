import pytest
from ..rules.cpr import CPRRule
from ..rules.regex import RegexRule
from ..rules.address import AddressRule
from ..rules.name import NameRule


class TestCensorMethods:
    @pytest.mark.parametrize("text,expected",
                             [("1111111118", [(0, 6), (6, 10)]),
                              ("1111111118 111111-1118", [(0, 6), (6, 10), (11, 17), (18, 22)]),
                              ("nothing", [])])
    def test_cpr(self, text, expected):
        """Should find all intervals corresponding to numbers matching the cpr-regex."""
        rule = CPRRule()

        response = list(rule.get_censor_intervals(text))

        assert response == expected

    @pytest.mark.parametrize("text,expected",
                             [("protestation", [(3, 7)]),
                              ("testing detestation", [(0, 4), (10, 14)]),
                              ("nothing", [])])
    def test_regex(self, text, expected):
        """Should find all intervals of substrings matching the regex"""
        rule = RegexRule("test")

        response = list(rule.get_censor_intervals(text))

        assert response == expected

    @pytest.mark.parametrize("expression", ["A|B", "(A)|B", "A|(B)", "(A)|(B)"])
    def test_regex_groups(self, expression):
        rule = RegexRule(expression)

        response = list(rule.get_censor_intervals("AB"))

        expected = [(0, 1), (1, 2)]
        assert response == expected

    def test_adress(self):
        """Not implemented, returns []"""
        rule = AddressRule()

        response = list(rule.get_censor_intervals("Pilestræde 43"))

        assert response == []

    def test_name(self):
        """Not implemented, returns []"""
        rule = NameRule()

        response = list(rule.get_censor_intervals("Ole Jakobsen"))

        assert response == []
