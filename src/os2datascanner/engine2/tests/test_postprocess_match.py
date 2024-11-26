import pytest
from functools import reduce

from ..conversions.types import OutputType
from ..pipeline.matcher import postprocess_match
from ..rules.regex import RegexRule
from ..rules.cpr import CPRRule
from ..rules.logical import AndRule


class RuleCensorFirst:
    operates_on = OutputType.Text

    def get_censor_intervals(self, context):
        return [(0, 1)]

    def flatten(self):
        return {self}


class RuleCensorLast:
    operates_on = OutputType.ImageDimensions

    def get_censor_intervals(self, context):
        return [(len(context)-1, len(context))]

    def flatten(self):
        return {self}


class MockCompoundRule:
    operates_on = OutputType.Text

    def __init__(self, rules):
        self._rules = rules

    def flatten(self):
        return reduce(lambda s, rule: s | rule.flatten(), self._rules, set())


@pytest.fixture
def firstRule():
    return RuleCensorFirst()


@pytest.fixture
def lastRule():
    return RuleCensorLast()


@pytest.fixture
def compoundRule(firstRule, lastRule):
    return MockCompoundRule({firstRule, lastRule})


@pytest.fixture
def context():
    return "This is the context of a very real match"


class TestPostprocessMatch:
    def test_normal_match(self, firstRule, context):
        match_object = (firstRule, [{"offset": 5, "match": "thisIsTheMatch", "context": context}])
        response = postprocess_match(firstRule, match_object)

        expected = (firstRule,
                    [{"offset": 5,
                      "match": "thisIsTheMatch",
                      "context": "Xhis is the context of a very real match"}])

        assert response == expected

    def test_multiple_matches(self, firstRule, context):
        """It should be possible to postprocess multiple matches"""
        match_object = (firstRule,
                        [{"offset": 5, "match": "thisIsTheMatch", "context": context},
                         {"offset": 8, "match": "thisIsAnother", "context": context},
                         {"offset": 1, "match": "andAThird", "context": context}])
        response = postprocess_match(firstRule, match_object)

        expected = (firstRule,
                    [{"offset": 5,
                      "match": "thisIsTheMatch",
                      "context": "Xhis is the context of a very real match"},
                     {"offset": 8,
                      "match": "thisIsAnother",
                      "context": "Xhis is the context of a very real match"},
                     {"offset": 1,
                      "match": "andAThird",
                      "context": "Xhis is the context of a very real match"}])

        assert response == expected

    def test_compound_rule(self, firstRule, compoundRule, context):
        """All subrules of a compound rule should take part in postprocess."""
        match_object = (firstRule,
                        [{"offset": 5, "match": "thisIsTheMatch", "context": context}])
        response = postprocess_match(compoundRule, match_object)

        expected = (firstRule,
                    [{"offset": 5,
                      "match": "thisIsTheMatch",
                      "context": "Xhis is the context of a very real matcX"}])

        assert response == expected

    def test_operates_on_not_text(self, lastRule):
        """If the rule doesn't operate on text, nothing should be done."""
        match_object = (lastRule,
                        [{"offset": 5, "match": "thisIsTheMatch"}])
        response = postprocess_match(lastRule, match_object)

        expected = (lastRule, [{"offset": 5, "match": "thisIsTheMatch"}])

        assert response == expected

    def test_no_matches(self, firstRule):
        """With no matches, (rule, None) should be returned."""
        match_object = (firstRule, [])
        response = postprocess_match(firstRule, match_object)

        expected = (firstRule, None)

        assert response == expected

    def test_no_context(self, firstRule):
        match_object = (firstRule, [{"offset": 5, "match": "thisIsTheMatch"}])
        response = postprocess_match(firstRule, match_object)

        expected = (firstRule,
                    [{"offset": 5,
                      "match": "thisIsTheMatch"}])

        assert response == expected


@pytest.fixture
def regex_rule():
    return RegexRule("i[sn]")


@pytest.fixture
def cpr_rule():
    return CPRRule()


@pytest.fixture
def representations():
    return {"text": "Hi boss\n"
                    "This is the cpr: 1111111118\n"
                    "Sincerely"}


class TestPostprocessMatchRealRules:
    def test_regex_rule(self, regex_rule, representations):
        (_, matches) = regex_rule.try_match(representations)
        responses = [postprocess_match(regex_rule, match) for match in matches]

        expected = [(regex_rule,
                     [{"offset": 10,
                       "match": "is",
                       "context": "Hi boss ThXX XX the cpr: 1111111118 SXXcerely",
                       "context_offset": 10,
                       "sensitivity": None},
                      {"offset": 13,
                       "match": "is",
                       "context": "Hi boss ThXX XX the cpr: 1111111118 SXXcerely",
                       "context_offset": 13,
                       "sensitivity": None},
                      {"offset": 37,
                       "match": "in",
                       "context": "Hi boss ThXX XX the cpr: 1111111118 SXXcerely",
                       "context_offset": 37,
                       "sensitivity": None}])]

        assert responses == expected

    def test_cpr_rule(self, cpr_rule, representations):
        (_, matches) = cpr_rule.try_match(representations)
        responses = [postprocess_match(cpr_rule, match) for match in matches]

        expected = [(cpr_rule,
                     [{"offset": 25,
                       "match": "1111XXXXXX",
                       "context": "Hi boss This is the cpr: XXXXXXXXXX Sincerely",
                       "context_offset": 25,
                       "sensitivity": None,
                       "probability": 1.0}])]

        assert responses == expected

    def test_and_rule(self, regex_rule, cpr_rule, representations):
        rule = AndRule(regex_rule, cpr_rule)
        (_, matches) = rule.try_match(representations)
        responses = [postprocess_match(rule, match) for match in matches]

        expected = [(regex_rule,
                     [{"offset": 10,
                       "match": "is",
                       "context": "Hi boss ThXX XX the cpr: XXXXXXXXXX SXXcerely",
                       "context_offset": 10,
                       "sensitivity": None},
                      {"offset": 13,
                       "match": "is",
                       "context": "Hi boss ThXX XX the cpr: XXXXXXXXXX SXXcerely",
                       "context_offset": 13,
                       "sensitivity": None},
                      {"offset": 37,
                       "match": "in",
                       "context": "Hi boss ThXX XX the cpr: XXXXXXXXXX SXXcerely",
                       "context_offset": 37,
                       "sensitivity": None}
                      ]),
                    (cpr_rule,
                     [{"offset": 25,
                       "match": "1111XXXXXX",
                       "context": "Hi boss ThXX XX the cpr: XXXXXXXXXX SXXcerely",
                       "context_offset": 25,
                       "sensitivity": None,
                       "probability": 1.0}]
                     )]

        assert responses == expected
