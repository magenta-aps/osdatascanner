import pytest

from os2datascanner.engine2.rules.rule import Rule, Sensitivity

from os2datascanner.engine2.rules.dummy import AlwaysMatchesRule
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.engine2.rules.logical import OrRule, AndRule


def run_rule(rule, in_v):
    results = {}
    while isinstance(rule, Rule):
        imm, pve, nve = rule.split()

        if imm in results:
            matches = imm[results]
        else:
            matches = list(imm.match(in_v))
            results[imm] = matches

        if matches:
            rule = pve
        else:
            rule = nve
    return rule, results


class TestRuleSensitivity:
    @pytest.mark.parametrize("in_v,expected", [
        ("very bad thing", Sensitivity.CRITICAL),
        ("moderately bad thing", Sensitivity.PROBLEM),
        ("moderately bad very bad thing", Sensitivity.CRITICAL),
        ("slightly moderately bad thing", Sensitivity.PROBLEM),
        ("moderately slightly bad thing", Sensitivity.WARNING),
        ("bad thing", Sensitivity.INFORMATION),
        ("moderately quite bad thing", Sensitivity.INFORMATION)])
    def test_sensitivity_matches(self, in_v, expected):
        rule = AndRule(
                RegexRule("bad thing"),
                OrRule(
                        RegexRule("very bad", sensitivity=Sensitivity.CRITICAL),
                        RegexRule("moderately bad", sensitivity=Sensitivity.PROBLEM),
                        RegexRule("slightly bad", sensitivity=Sensitivity.WARNING),
                        AlwaysMatchesRule(sensitivity=Sensitivity.INFORMATION)
                    ))

        matched, results = run_rule(rule, in_v)
        assert matched is True
        sensitivity = max(
            [rule.sensitivity for rule, matches in results.items()
                if rule.sensitivity is not None and matches],
            key=lambda sensitivity: sensitivity.value)
        assert sensitivity == expected
