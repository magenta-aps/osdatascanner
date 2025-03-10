import pytest
from datetime import datetime, timezone

from os2datascanner.engine2.rules.address import AddressRule
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.dimensions import DimensionsRule
from os2datascanner.engine2.rules.dummy import (
        NeverMatchesRule, AlwaysMatchesRule)
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
from os2datascanner.engine2.rules.logical import (
    OrRule,
    AndRule,
    NotRule,
    AllRule,
    oxford_comma,
)
from os2datascanner.engine2.rules.meta import HasConversionRule
from os2datascanner.engine2.rules.name import NameRule
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.engine2.rules.wordlists import OrderedWordlistRule
from os2datascanner.engine2.rules.rule import Sensitivity
from os2datascanner.engine2.rules.dict_lookup import EmailHeaderRule
from os2datascanner.engine2.rules.passport import PassportRule

from os2datascanner.engine2.conversions.types import OutputType


simple_candidates = [
    (
        CPRRule(modulus_11=False, ignore_irrelevant=False),
        """
2205995008: forbryder,
230500 0003: forbryder,
240501-0006: forbryder,
250501-1987: forbryder""",
        ["2205XXXXXX", "2305XXXXXX", "2405XXXXXX", "2505XXXXXX"],
    ),
    (
        CPRRule(modulus_11=True, ignore_irrelevant=True),
        """
2205995008: forbryder,
230500 0003: forbryder,
240501-0006: forbryder,
250501-1987: forbryder""",
        ["2205XXXXXX", "2305XXXXXX", "2405XXXXXX"],
    ),
    (
        CPRRule(
            modulus_11=True, ignore_irrelevant=True, examine_context=False
        ),
        """
Vejstrand Kommune, Børn- og Ungeforvaltningen. P-nr. 2205995008
Vejstrand Kommune, Børn- og Ungeforvaltningen. P-nummer: 2305000003
240501-0006""",
        ["2205XXXXXX", "2305XXXXXX", "2405XXXXXX"],
    ),
    (
        CPRRule(
            modulus_11=True, ignore_irrelevant=True, examine_context=True,
            blacklist=[],
        ),
        """
Vejstrand Kommune, Børn- og Ungeforvaltningen. P-nr. 2205995008
Vejstrand Kommune, Børn- og Ungeforvaltningen. P-nummer: 2305000003
240501-0006""",
        ["2205XXXXXX", "2305XXXXXX", "2405XXXXXX"],
    ),
    (
        CPRRule(
            modulus_11=True, ignore_irrelevant=True, examine_context=True,
        ),
        """
Vejstrand Kommune, Børn- og Ungeforvaltningen. P-nr. 2205995008
Vejstrand Kommune, Børn- og Ungeforvaltningen. P-nummer: 2305000003
240501-0006""",
        [],
    ),
    (
        CPRRule(
            modulus_11=True, ignore_irrelevant=True, examine_context=True,
            whitelist=["whiteword"]
        ),
        """
Vejstrand Kommune, Børn- og Ungeforvaltningen. WhiteWord 2205995008
Vejstrand Kommune, Børn- og Ungeforvaltningen. NotAcceptedCase 2305000003
Vejstrand Kommune, 240501-0006""",
        ["2205XXXXXX", "2405XXXXXX"],
    ),
    (
        CPRRule(
            modulus_11=True, ignore_irrelevant=True, examine_context=True,
            surrounding_exceptions=["account"]
        ),
        """
Vejstrand Kommune, Børn- og Ungeforvaltningen, Account: 2205995008
Vejstrand Kommune, Børn- og Ungeforvaltningen, Num: 2305000003
240501-0006""",
        ["2305XXXXXX", "2405XXXXXX"],
    ),
    (
        RegexRule("((four|six)( [aopt]+)?|(one|seven) [aopt]+)"),
        """
one
one potato
two potato
three potato
four
five potato
six potato
seven potato
more!""",
        ["one potato", "four", "six potato", "seven potato"],
    ),
    (
        LastModifiedRule(
            datetime(2019, 12, 24, 23, 59, 59, tzinfo=timezone.utc)
        ),
        datetime(2019, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        ["2019-12-31T23:59:59+0000"],
    ),
    (
        LastModifiedRule(
            datetime(2019, 12, 24, 23, 59, 59, tzinfo=timezone.utc)
        ),
        datetime(2019, 5, 22, 0, 0, 1, tzinfo=timezone.utc),
        None,
    ),
    (
        DimensionsRule(
            width_range=range(0, 16385),
            height_range=range(0, 16385),
            min_dim=256,
        ),
        (128, 256),
        [[128, 256]],
    ),
    (
        DimensionsRule(
            width_range=range(0, 16385),
            height_range=range(0, 16385),
            min_dim=256,
        ),
        (128, 255),
        [],
    ),
    (
        DimensionsRule(
            width_range=range(256, 1024),
            height_range=range(256, 1024),
            min_dim=0,
        ),
        (256, 256),
        [[256, 256]],
    ),
    (
        DimensionsRule(
            width_range=range(256, 1024),
            height_range=range(256, 1024),
            min_dim=0,
        ),
        (32, 32),
        [],
    ),
    (
        # This rule will find a match since the dict has a "subject"
        # property whos value matches the regex 'test'.
        EmailHeaderRule(
            prop="subject",
            rule=RegexRule('test'),
        ),
        dict(subject="This is a test subject"),
        ['test'],
    ),
    (
        # This rule will not match since the dict does not
        # have a "subject" property.
        EmailHeaderRule(
            prop="subject",
            rule=RegexRule('test'),
        ),
        dict(field="This is a test subject"),
        [],
    ),
    (
        PassportRule(),
        """
P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<< L898902C36UTO7408122F1204159ZE184226B<<<<<10
P<GBRMASTERSON<<EDMUND<<<<<<<<<<<<<<<<<<<<<<4145681380GBR5110205M1601013<<<<<<<<<<<<<<00
P<NLDDE<BRUIJN<<WILLEKE<LISELOTTE<<<<<<<<<<<,SPECI20142NLD6503101F2403096999999990<<<<<84
P<AUSCITIZEN<<JANE<<<<<<<<<<<<<<<<<<<<<<<<<<	PX09153981AUS8406077F1503014<61047007L<<<<24
P<USATRAVELER<<HAPPY<<<<<<<<<<<<<<<<<<<<<<<<-1500000035USA5609165M0811150<<<<<<<<<<<<<<08

P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<< L898902C37UTO7408122F1204159ZE184226B<<<<<10
P<GBRMASTERSON<<EDMUND<<<<<<<<<<<<<<<<<<<<<<4145681380GBR5110204M1601013<<<<<<<<<<<<<<00
P<NLDDE<BRUIJN<<WILLEKE<LISELOTTE<<<<<<<<<<<,SPECI20142NLD6503101F2403097999999990<<<<<84
P<AUSCITIZEN<<JANE<<<<<<<<<<<<<<<<<<<<<<<<<<	PX09153981AUS8406077F1503014<61047007L<<<<34
P<USATRAVELER<<HAPPY<<<<<<<<<<<<<<<<<<<<<<<<-1500000035USA5609165M0811150<<<<<<<<<<<<<<09
""",
        ["Passport number L898902C3 (issued by UTO)",
            "Passport number 414568138 (issued by GBR)",
            "Passport number SPECI2014 (issued by NLD)",
            "Passport number PX0915398 (issued by AUS)",
            "Passport number 150000003 (issued by USA)", ],
    ),
]


compound_candidates = [
    (
        AndRule(RegexRule("A"), OrRule(RegexRule("B"), RegexRule("C"))),
        [
            ("A", False, 3),
            ("AB", True, 2),
            ("ABC", True, 2),
            ("BC", False, 1),
            ("AC", True, 3),
        ],
    ),
    (
        NotRule(AndRule(RegexRule("A"), OrRule(RegexRule("B"), RegexRule("C")))),
        [
            ("A", True, 3),
            ("AB", False, 2),
            ("ABC", False, 2),
            ("BC", True, 1),
            ("AC", False, 3),
        ],
    ),
    (
        AndRule(NotRule(OrRule(RegexRule("B"), RegexRule("C"))), RegexRule("A")),
        [
            ("A", True, 3),
            ("AB", False, 1),
            ("ABC", False, 1),
            ("BC", False, 1),
            ("AC", False, 2),
        ],
    ),
    (
        AndRule(AllRule(RegexRule("A"), RegexRule("B")), RegexRule("C")),
        [
            ("A", False, 3),
            ("AB", False, 3),
            ("ABC", True, 3),
            ("BC", True, 3),
            ("AC", True, 3),
            ("C", False, 2),
        ],
    ),
]


class TestRules:
    @pytest.mark.parametrize("rule,in_value,expected", simple_candidates)
    def test_simplerule_json_conversion(self, rule, in_value, expected):
        json = rule.to_json_object()
        back_again = rule.from_json_object(json)
        assert rule == back_again

    @pytest.mark.parametrize("rule,in_value,expected", simple_candidates)
    def test_simplerule_matches(self, rule, in_value, expected):
        matches = rule.match(in_value)
        if expected:
            assert [match["match"] for match in matches] == expected
        else:
            assert not list(matches)

    @pytest.mark.parametrize("rule,tests", compound_candidates)
    def test_compound_rule_matches(self, rule, tests):
        for input_string, outcome, evaluation_count in tests:
            representations = {"text": input_string}
            conclusion, evaluations = rule.try_match(representations.get)

            assert outcome == conclusion
            assert evaluation_count == len(evaluations)

    def test_or_rule_one_component(self):
        """Even though users shouldn't be allowed to create rules with one components,
        they should still be able to run without problems."""
        representations = {"text": "Testing Testing"}
        rule = OrRule(RegexRule("Test"))
        conclusion, evaluations = rule.try_match(representations.get)
        assert conclusion

    def test_and_rule_one_component(self):
        """Even though users shouldn't be allowed to create rules with one components,
        they should still be able to run without problems."""
        representations = {"text": "Testing Testing"}
        rule = AndRule(RegexRule("Test"))
        conclusion, evaluations = rule.try_match(representations.get)
        assert conclusion

    def test_resume(self):
        """Resuming execution of a rule after its try_match method has returned
        should complete the execution correctly."""
        rule = AndRule(
            RegexRule("First fragment"),
            AlwaysMatchesRule(),
            RegexRule("second fragment"),
            AlwaysMatchesRule()
        )

        representations = {"text": "First fragment goes here, and then the second fragment"}
        remaining, matches1 = rule.try_match(lambda k: representations[k])
        representations["fallback"] = True
        remaining, matches2 = remaining.try_match(lambda k: representations[k])

        assert remaining
        # Because Rule.try_match is allowed to perform optimisation, we can't
        # rely on rules being executed in any particular order or number, so
        # all we do here is to ensure that all of the rules we expect to see
        # executed were actually executed
        expected = {
            RegexRule("First fragment"),
            RegexRule("second fragment"),
            AlwaysMatchesRule()
        }
        assert set(r for r, _ in matches1) | set(r for r, _ in matches2) == expected

    @pytest.mark.parametrize("rule,tests", compound_candidates)
    def test_json_round_trip(self, rule, tests):
        json = rule.to_json_object()
        back_again = rule.from_json_object(json)
        assert rule == back_again

    def test_oxford_comma(self):
        assert oxford_comma(["Monday"], "and") == "Monday"
        assert oxford_comma(["Monday", "Tuesday"], "and") == "Monday and Tuesday"
        assert oxford_comma(["Monday", "Tuesday", "Wednesday"],
                            "and") == "Monday, Tuesday, and Wednesday"

    def test_rule_names(self):
        A = RegexRule("A", name="Fragment A")
        B = RegexRule("B", name="Fragment B")
        C1 = RegexRule("C1", name="Fragment C1")
        C2 = RegexRule("C2", name="Fragment C2")
        C = OrRule(C1, C2, name="Fragment C")
        assert AndRule(A, B).presentation == "(Fragment A and Fragment B)"
        assert OrRule(A, B, C).presentation == "(Fragment A, Fragment B, or Fragment C)"

    def test_json_backwards_compatibility(self):
        assert CPRRule.from_json_object({"type": "cpr"}) == CPRRule()

    def test_name_rule_json_conversion(self):
        rule = NameRule(
            expansive=True,
            whitelist=["Joakim"], blacklist=["Malkeko"]
        )

        json = rule.to_json_object()
        back_again = rule.from_json_object(json)
        assert rule == back_again

    def test_name_rule_matches(self):
        rule = NameRule(
            expansive=True,
            whitelist=["Joakim"], blacklist=["Malkeko"]
        )
        in_value = (
            "Anders\n"           # match standalone name.
            "Anders and\n"       # match standalone name
            "Anders      And\n"  # match full name. Only first name in namelist
            "Anders And\n"       # match full name
            "A. And\n"           # match regex, but not in namelist -> not returned
            "J.-V And\n"         # -"-
            "J-V. And\n"         # -"-
            "J.V. And\n"         # -"-
            "J.v. And\n"         # Does not match regex
            "Joakim And\n"       # match regex and namelist, but in whitelist
            "Andrea V. And\n"    # First name in namelist
            "Joakim Nielsen\n"   # last name in namelist and not whitelisted.
            "Anders Andersine Mickey Per Nielsen\n"
            # match full name
            "Nora Malkeko\n"     # In blacklist
        )
        expected = sorted([    # expected matches
            ["Anders", 0.1],
            ["Anders", 0.1],
            ["Anders And", 0.5],
            ["Anders      And", 0.5],
            ["Joakim Nielsen", 0.5],
            ["Andrea V. And", 0.5],
            ["Anders Andersine Mickey Per Nielsen", 1.0],
            ["Nora Malkeko", 1.0],
        ])

        matches = rule.match(in_value)
        assert sorted([[match["match"], match['probability']] for match in matches]) == expected

    def test_address_rule_json_conversion(self):
        rule = AddressRule(whitelist=["Tagensvej"], blacklist=["PilÆstræde"])

        json = rule.to_json_object()
        back_again = rule.from_json_object(json)
        assert rule == back_again

    def test_address_rule_matches(self):
        # user supplied sensitivity is not used
        rule = AddressRule(whitelist=["Tagensvej"], blacklist=["PilÆstræde"])
        in_value = (
            "H.C. Andersens Boul 15, 2. 0006, 1553 København V, Danmark\n"
            "H.C. Andersens Boul, 1553 Kbh. V\n"
            "10. Februar Vej 75\n"                    # unusual names from the list
            "400-Rtalik\n"
            "H/F Solpl-Lærkevej\n"
            "H. H. Hansens Vej\n"
            "H H Kochs Vej\n"
            "Øer I Isefjord 15\n"                     # does unicode work?
            "Tagensvej 15\n"                          # whitelisted
            "der er en bygning på PilÆstræde, men\n"  # not in address list/blacklisted
            "Magenta APS, PilÆstræde 43,  3. sal, 1112 København\n"
        )
        expected = {
            ("H.C. Andersens Boul 15, 2. 0006, 1553 København V",
             Sensitivity.CRITICAL.value),
            ("H.C. Andersens Boul, 1553 Kbh. V", Sensitivity.PROBLEM.value),
            ("10. Februar Vej 75", Sensitivity.CRITICAL.value),
            ("400-Rtalik", Sensitivity.PROBLEM.value),
            ("H/F Solpl-Lærkevej", Sensitivity.PROBLEM.value),
            ("H. H. Hansens Vej", Sensitivity.PROBLEM.value),
            ("H H Kochs Vej", Sensitivity.PROBLEM.value),
            ("Øer I Isefjord 15", Sensitivity.CRITICAL.value),
            ("PilÆstræde", Sensitivity.CRITICAL.value),
            ("PilÆstræde 43,  3. sal, 1112 København", Sensitivity.CRITICAL.value)
        }

        matches = rule.match(in_value)
        assert {(match["match"], match['sensitivity']) for match in matches} == expected

    @pytest.mark.parametrize("in_value,expected", [
        (
            "This is a really good dog!",
            ({
                "match": "good",
                "offset": 17,
                "context": "This is a really good dog!",
                "context_offset": 17
            }, {
                "match": "dog",
                "offset": 22,
                "context": "This is a really good dog!",
                "context_offset": 22
            },)
        ),
        (
            "This dog is really good!",
            ({
                "match": "dog",
                "offset": 5,
                "context": "This dog is really good!",
                "context_offset": 5
            }, {
                "match": "good",
                "offset": 19,
                "context": "This dog is really good!",
                "context_offset": 19
            },)
        ),
        (
            f"This is a good{'dog':>32}",
            ({
                "match": "good",
                "offset": 10,
                "context": f"This is a good{'':>29}dog",
                "context_offset": 10
            }, {
                "match": "dog",
                "offset": 43,
                "context": f"This is a good{'':>29}dog",
                "context_offset": 43
            },)
        ),
        (
            "This CRAZY cat's a good dog!",
            ({
                "match": "CRAZY",
                "offset": 5,
                "context": "This CRAZY cat's a good dog!",
                "context_offset": 5
            }, {
                "match": "cat",
                "offset": 11,
                "context": "This CRAZY cat's a good dog!",
                "context_offset": 11
            },
             {
                "match": "good",
                "offset": 19,
                "context": "This CRAZY cat's a good dog!",
                "context_offset": 19
            }, {
                "match": "dog",
                "offset": 24,
                "context": "This CRAZY cat's a good dog!",
                "context_offset": 24
            },)
        ),
        (
            "Der står en mand på gaden",
            ()
        ),
        (
            "En skole er en læringsanstalt",
            ()
        ),
        (
            "De måtte overnatte i en afleveringshal",
            ()
        ),
        (
            "Medlidenhed er ikke en sårbarhed",
            ()
        ),
        (
            "En konklusion skal være kort og konkret",
            ()
        ),
        (
            "Skraldemænd er eksperter i affaldsbehandling",
            ()
        ),
        (
            "Hjælpestoffer kan være harmløse",
            ()
        ),
        (
            "Din lever er lidt plettet idag",
            ({
                "match": "lever",
                "offset": 4,
                "context": "Din lever er lidt plettet idag",
                "context_offset": 4
            },)
        ),
        (
            "Kol er noget farligt noget",
            ({
                "match": "Kol",
                "offset": 0,
                "context": "Kol er noget farligt noget",
                "context_offset": 0
            },)
        ),
    ])
    def test_wordlists_rule(self, in_value, expected):
        wrl = OrderedWordlistRule("en_20211018_unit_test_words")
        assert tuple(wrl.match(in_value)) == expected

    @pytest.mark.parametrize("in_value,expected", [
        (
            """
REGION NORDSTRAND -- PERSONFØLSOMT MATERIALE UNDER TAVSHEDSPLIGT

Nordstrand Sygehus
Strandvej 17
9999 Vejstrand

Patient: Jens Testsen
Konsultationsdato: 2021-10-18

Ifølge analyseresultater lider patienten af akut arteriel insufficiens i alle
ekstremiteterne. Han selv tilføjer, at han har ondt i albuen. Der er også
indledende tegn på AUTOIMMUNT POLYGLANDULÆRT SYNDROM. Henvist til
speciellæger.""",
            ({
                "match": "akut",
                "offset": 212,
                "context": (
                    "0-18\n\n"
                    "Ifølge analyseresultater lider patienten af akut arteriel "
                    "insufficiens i alle\n"
                    "ekstremiteterne. Han"
                    ),
                "context_offset": 50
            }, {
                "match": "arteriel",
                "offset": 217,
                "context": (
                    "\n"
                    "Ifølge analyseresultater lider patienten af akut arteriel "
                    "insufficiens i alle\n"
                    "ekstremiteterne. Han selv til"
                    ),
                "context_offset": 50
            }, {
                "match": "AUTOIMMUNT",
                "offset": 339,
                "context": (
                    "har ondt i albuen. Der er også\n"
                    "indledende tegn på AUTOIMMUNT POLYGLANDULÆRT SYNDROM. Henvist til\n"
                    "speciellæger."
                ),
                "context_offset": 50
            }, {
                "match": "POLYGLANDULÆRT",
                "offset": 350,
                "context": (
                    "albuen. Der er også\n"
                    "indledende tegn på AUTOIMMUNT POLYGLANDULÆRT SYNDROM. Henvist til\n"
                    "speciellæger."
                ),
                "context_offset": 50
            }, {
                "match": "SYNDROM",
                "offset": 365,
                "context": (
                    "også\n"
                    "indledende tegn på AUTOIMMUNT POLYGLANDULÆRT SYNDROM. Henvist til\n"
                    "speciellæger."
                    ),
                "context_offset": 50
            },)
        ),
    ])
    def test_medical_combinations(self, in_value, expected):
        wrl = OrderedWordlistRule("da_20211018_laegehaandbog_stikord")
        assert tuple(wrl.match(in_value)) == expected

    def test_all_of_them(self):
        rule = AndRule(
                HasConversionRule(OutputType.Text),
                CPRRule(),
                NameRule(),
                OrRule(NeverMatchesRule(), AlwaysMatchesRule()),
                NotRule(HasConversionRule(OutputType.ImageDimensions)),
                AddressRule())
        rhu = rule.try_match({
            OutputType.Text.value: (
                    "Jens Jensen, 111111-1118,"
                    " Strandvej 198, 1tv, 2000 Frederiksberg"),
            OutputType.NoConversions.value: None,
            OutputType.AlwaysTrue.value: True,
            OutputType.ImageDimensions.value: None,
        })
        assert rhu[0]

    @pytest.mark.parametrize("obj_limit,match_count", [
        (None, 15),
        (10, 10)
    ])
    def test_cutoff(self, obj_limit, match_count):
        """The number of matches produced by Rule.try_match can be truncated
        with the obj_limit parameter."""
        rule = RegexRule(r"A")

        conclusion, matches = rule.try_match({
            OutputType.Text.value: "A0A1A2A3A4A5A6A7A8A9A10A11A12A13A14"
        }, obj_limit=obj_limit)
        assert conclusion
        assert len(matches[0][1]) == match_count
