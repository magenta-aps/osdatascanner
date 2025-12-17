import pytest

from os2datascanner.engine2.rules.logical import OrRule
from os2datascanner.engine2.rules.regex import RegexRule

from ..adminapp.models.rules import Rule, Sensitivity


class TestRules:
    @pytest.mark.django_db
    def test_rule_reference_resolution(self):
        """Rule references are resolved at object save time and are not saved
        to the database."""
        # Arrange
        raw1 = {
            "type": "or",
            "components": [
                {
                    "type": "regex",
                    "expression": "Samus Aran"
                },
                {
                    "type": "regex",
                    "expression": "Ridley"
                }
            ]
        }
        r1 = Rule(
                name="Hello",
                description="This is an Elite Space Pirate."
                            "\nElite Space Pirate description 3.",
                sensitivity=Sensitivity.OK,
                raw_rule=raw1)
        r1.save()

        raw2 = {
            "type": "and",
            "components": [
                {"!ref": r1.pk},
                {"type": "cpr"}
            ]
        }
        r2 = Rule(
                name="Goodbye",
                description="Something",
                sensitivity=Sensitivity.CRITICAL,
                raw_rule=raw2)

        assert r2.raw_rule == raw2

        # Act
        r2.save()

        # Assert
        assert r2.raw_rule == {
            "type": "and",
            "components": [
                raw1,
                {"type": "cpr"}
            ]
        }

    def test_regexrule_translation(self):
        names = ("Jason", "Timothy", "Davina", "Kristi",)

        rules = (RegexRule(name) for name in names)

        r = Rule(
            name="Look for names",
            description="A rule that looks for some names",
            sensitivity=Sensitivity.CRITICAL,
            raw_rule=OrRule.make(*rules).to_json_object(),
            )

        e2r = r.make_engine2_rule()

        assert e2r._name == r.name
        assert e2r._sensitivity.value == 1000

        for name, rule in zip(names, rules):
            assert [m['match'] for m in rule.match(name)] == [name]

    def test_customrule_translation(self):
        document = """\
From the desk of Kristjan Evil
TO: David Jensen

We must make sure that Jens Davidsen doesn't find out about the plan. Do
everything in your power to keep it a secret!

The first steps will be taken on Tuesday. Mwahahahaha ha ha ha ha.

Yours in nastiness
Kristjan Evil
"""
        r = Rule(
                name="Look for names",
                raw_rule={
                    "type": "name",
                    "expansive": False,
                    "whitelist": [],
                    "blacklist": [],
                    "sensitivity": 1000
                },
                sensitivity=Sensitivity.LOW)

        e2r = r.make_engine2_rule()

        assert e2r._name == r.name
        assert e2r._sensitivity.value == 1000
        assert {m["match"] for m in e2r.match(document)} == {"Kristjan Evil", "David Jensen",
                                                             "Jens Davidsen", "Kristjan Evil"}
