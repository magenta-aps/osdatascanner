import pytest

from os2datascanner.engine2.rules.cpr import CPRRule, WordOrSymbol, Context


@pytest.fixture
def content():
    return [
        """@ Godtages fordi det er et valid cpr der opfylder Modulus 11 tjek.
        Anders And 010180-0008""",
        """@ godtages fordi der indgår cpr i linjen
        Anders And, cpr: [020280-0009""",
        """@ godtages fordi parenteser er balanceret
        Anders And, [030380-0018], Paradisæblevej 111""",
        """@ godtages fordi der tillades ekstra ord ved parenteser.
        Anders (040480-0019 And), Andeby""",
        """@ godtages ikke fordi foranstående ord er et tal, der IKKE opfylder kriterium for cpr
        Anders And 113 050580-0001""",
        """@ godtages fordi bagvedstående/foranstående ord opfylder kriterium for cpr
        Anders And 060680-0002 070680-0018""",
        """@ godtages ikke fordi foranstående ord er et mix af store og små bogstaver
        "HOST/ABCD.intra.corp"], "uSNChanged": [070780-0003], "uSNCreated": [123456], "userAccountControl":""",  # noqa: E501
        """@ godtages ikke pga. omkringstående tal OG fordi kun to ord medtages, vil paranteser være ubalanceret.
        712000 0 0 WET} {080880-0004 3600 1 WEST} [090880-0001 0 0 WET]""",  # noqa: E501
        """@ godtages ikke pga foranstående er unær operatør(dvs. fortegns-minus. På eng: unary) eller specialsymbol
        16768 0 LMT} {090980-0005-} {+100980-0006} (#110980-0003)""",  # noqa: E501
        """@ godtages ikke pga. udgyldig opdeling Anders And 06 06 80-0002""",
        """@ godtages fordi efterfølgende tal er lukket inde i en parantes
        Anders And 070780-0003 (12345)""",
        """Følgende kriterier undersøges
        - Kontekst består af de `n_words=2` foranstående/bagvedstående ord incl. tegn.
        Ord med bindesteg(-), punktum(.) eller skråstreg(/) splittes ikke.
        - Konteksten bruges til at estimere en sandsynlighed for at et 10-cifret nummer
        der opfylder modulus 11, rent faktisk er et cpr-nummber.

        Følgende heuristik benyttes
        - indgår p-nr eller variant deraf noget sted i teksten
        - Er der unær operator før eller efter, fx -101080-0001 eller 111080-0009+
        - Er der ubalanceret symboler eller parenteser omkring, fx [111180-0002. Men [121180-0018] vil være ok.
        - Kommer der et tal der ikke ligner et cpr før eller efter, fx 113 121280-0003
        - Er ord før eller efter ikke ’alle små’-, ’stort begyndelsesbogstav’ eller ’alle caps’, fx uSNChanged 131280-0019
        resulterer alle i sandsynlighed=0.

        - indeholder ord før cpr, fx Anders cpr-nr [141280-0008]
        resulterer i  sandsynlighed=1

        Følgende symboler undersøges
        - unær operatører "+", "-"
        - parenteser "(", "[", "{", "<", "<?", "<%", "/*"
        - symboler "!", "#", "%"
        """,  # noqa: E501
    ]


# all possible matches
ALL_MATCHES = [
    {'match': '0101XXXXXX',
     'offset': 86,
     'context': 'der opfylder Modulus 11 tjek. Anders And XXXXXX-XXXX',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '0202XXXXXX',
     'offset': 67,
     'context': 'der indgår cpr i linjen Anders And, cpr: [XXXXXX-XXXX',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '0303XXXXXX',
     'offset': 63,
     'context': 'rdi parenteser er balanceret Anders And, [XXXXXX-XXXX], Paradisæblevej 111',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '0404XXXXXX',
     'offset': 73,
     'context': 'llades ekstra ord ved parenteser. Anders (XXXXXX-XXXX And), Andeby',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '0505XXXXXX',
     'offset': 109,
     'context': 'opfylder kriterium for cpr Anders And 113 XXXXXX-XXXX',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '0606XXXXXX',
     'offset': 94,
     'context': 'ord opfylder kriterium for cpr Anders And XXXXXX-XXXX XXXXXX-XXXX',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '0706XXXXXX',
     'offset': 106,
     'context': 'kriterium for cpr Anders And XXXXXX-XXXX XXXXXX-XXXX',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '0707XXXXXX',
     'offset': 123,
     'context': 'r "HOST/ABCD.intra.corp"], "uSNChanged": [XXXXXX-XXXX], '
     '"uSNCreated": [123456], "userAccountControl":',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '0808XXXXXX',
     'offset': 128,
     'context': 'nteser være ubalanceret. 712000 0 0 WET} {XXXXXX-XXXX 3600 1 WEST} '
     '[XXXXXX-XXXX 0 0 WET]',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '0908XXXXXX',
     'offset': 154,
     'context': '712000 0 0 WET} {XXXXXX-XXXX 3600 1 WEST} [XXXXXX-XXXX 0 0 WET]',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '0909XXXXXX',
     'offset': 128,
     'context': 'unary) eller specialsymbol 16768 0 LMT} {XXXXXX-XXXX-} {+XXXXXX-XXXX} '
     '(#XXXXXX-XXXX)',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '1009XXXXXX',
     'offset': 144,
     'context': 'ecialsymbol 16768 0 LMT} {XXXXXX-XXXX-} {+XXXXXX-XXXX} (#XXXXXX-XXXX)',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '1109XXXXXX',
     'offset': 159, 'context': '16768 0 LMT} {XXXXXX-XXXX-} {+XXXXXX-XXXX} (#XXXXXX-XXXX)',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '0707XXXXXX',
     'offset': 83,
     'context': 'l er lukket inde i en parantes Anders And XXXXXX-XXXX (12345)',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '1010XXXXXX',
     'offset': 497,
     'context': '- Er der unær operator før eller efter, fx -XXXXXX-XXXX eller XXXXXX-XXXX+ - '
     'Er der ubalanceret s',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '1110XXXXXX',
     'offset': 515,
     'context': 'r operator før eller efter, fx -XXXXXX-XXXX eller XXXXXX-XXXX+ - Er der '
     'ubalanceret symboler eller pare',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '1111XXXXXX',
     'offset': 596,
     'context': 'balanceret symboler eller parenteser omkring, fx [XXXXXX-XXXX. Men [XXXXXX-XXXX] '
     'vil være ok. - Kommer',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '1211XXXXXX',
     'offset': 614,
     'context': 'r eller parenteser omkring, fx [XXXXXX-XXXX. Men [XXXXXX-XXXX] vil være ok. - '
     'Kommer der et tal der ikk',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '1212XXXXXX',
     'offset': 715,
     'context': 'al der ikke ligner et cpr før eller efter, fx 113 XXXXXX-XXXX - Er ord før eller '
     'efter ikke ’alle små’-',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '1312XXXXXX',
     'offset': 838,
     'context': 'yndelsesbogstav’ eller ’alle caps’, fx uSNChanged XXXXXX-XXXX resulterer alle i '
     'sandsynlighed=0.',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0},
    {'match': '1412XXXXXX',
     'offset': 946,
     'context': '- indeholder ord før cpr, fx Anders cpr-nr [XXXXXX-XXXX] resulterer i '
     'sandsynlighed=1 F',
     'context_offset': 50,
     'sensitivity': None,
     'probability': 1.0}
]


class TestCPRRule:

    @pytest.mark.parametrize("rule,expected,description", [
        (
            CPRRule(modulus_11=True, ignore_irrelevant=False, examine_context=False,
                    blacklist=[]),
            ALL_MATCHES,
            "match all"
        ),
        (
            CPRRule(modulus_11=True, ignore_irrelevant=False, examine_context=True,
                    blacklist=[]),
            [ALL_MATCHES[i] for i in [0, 1, 2, 3, 5, 6, 13, 20]],
            "match using context rules"
        ),
        (
            CPRRule(modulus_11=True, ignore_irrelevant=False, examine_context=True,
                    blacklist=[], whitelist=[]),
            [ALL_MATCHES[i] for i in [0, 2, 3, 5, 6, 13, 20]],
            "match setting `whitelist=[]`"
        ),
        (
            CPRRule(modulus_11=True, ignore_irrelevant=False, examine_context=True,),
            [ALL_MATCHES[i] for i in [0, 1, 2, 3, 5, 6, 13]],
            "match with blacklist"
        ),
        (
            CPRRule(modulus_11=True, ignore_irrelevant=False, examine_context=True,
                    blacklist=[], whitelist=["anders", "and"]),
            [ALL_MATCHES[i] for i in [0, 1, 2, 3, 4, 5, 6, 13, 20]],
            "match setting `whitelist=['anders', 'and']`"
        ),
        (
            CPRRule(modulus_11=True, ignore_irrelevant=False, examine_context=True,
                    blacklist=[], whitelist=[],
                    exceptions=["0303800018", "0606800002"]),
            [ALL_MATCHES[i] for i in [0, 3, 6, 13, 20]],
            "match with some exceptions"
        ),
        (
            CPRRule(ignore_irrelevant=False, blacklist=[]),
            [ALL_MATCHES[i] for i in [0, 1, 2, 3, 5, 6, 13, 20]],
            "match using some default settings"
        ),
    ])
    def test_cpr_context(self, rule, expected, description, content):

        matches = []
        for string in content:
            matches.extend(rule.match(string))
        for match in matches:
            print(match)
        if expected:
            assert sorted(
                list(matches),
                key=lambda x: x["offset"]) == sorted(
                expected,
                key=lambda x: x["offset"])
        else:
            assert not list(matches)

    def test_cpr_probability(self, content):
        rule = CPRRule(examine_context=False, blacklist=[])
        expected_probs = [0.5] + [1.0]*20

        matches = []
        for string in content:
            matches.extend(rule.match(string))

        for match, expected_prob in zip(matches, expected_probs):
            assert match["probability"] == expected_prob

    @pytest.mark.parametrize("content", [
        "(1111111118)",
        "[1111111118]",
        "{1111111118}",
        "<1111111118>",
    ])
    def test_balanced_delimiters(self, content):
        rule = CPRRule(modulus_11=True, ignore_irrelevant=False, examine_context=True)
        matches = rule._compiled_expression.finditer(content)
        prob, ctype = rule.examine_context(next(matches))

        # Probability and ctype should not be defined for balanced delimiters
        assert prob is None
        assert ctype == []

    @pytest.mark.parametrize("content", [
        "+1111111118",
        "-1111111118",
        "!1111111118",
        "#1111111118",
        "%1111111118",
        "1111111118+",
        "1111111118-",
        "1111111118!",
        "1111111118#",
        "1111111118%",
    ])
    def test_surrounding_symbols(self, content):
        rule = CPRRule(modulus_11=True, ignore_irrelevant=False, examine_context=True)
        matches = rule._compiled_expression.finditer(content)
        prob, ctype = rule.examine_context(next(matches))

        # Probability and ctype should not be defined for balanced delimiters
        assert prob == 0.0
        assert ctype[0][0] == Context.SYMBOL

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
             'context': 'XXXXXX-XXXX',
             'context_offset': 0,
             'sensitivity': None,
             'probability': 0.1}
            ]),
    ])
    def test_probability_number_ignore_irrelevant(self, content, mod11, result):
        rule = CPRRule(ignore_irrelevant=True, modulus_11=mod11, examine_context=False)
        matches = list(rule.match(content))

        print(matches)

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
