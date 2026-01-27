import pytest

from os2datascanner.engine2.rules.cpr import CPRRule


class TestCPRRule:
    @classmethod
    def simplify_matches(cls, it):
        return [o["match"] for o in it]

    @pytest.mark.parametrize(
            "text,expected",
            [
                ("Borger Mark Nielsen (1911770055) har lige rapporteret, at",
                 ["1911XXXXXX"]),
                ("anmodning om ny tastatur for Grzegorz Brzęczyszczykiewicz"
                 ", 150643-2495, skal behandles af",
                 ["1506XXXXXX"],),
                ("Joanne Bloggs og hendes mand Joe Bloggs, hhv. med CPR-numre"
                 " 1412669300 og 150564-0701, vil få energirådgivning af",
                 ["1412XXXXXX", "1505XXXXXX"]),
                ("se om Brian Qvortrup-Larsen 080273-3941 kan have ret til"
                 " tillægsydelser jf. lov om aktiv",
                 ["0802XXXXXX"]),
                ("USA's tidligere forsvarsminister Robert McNamara,"
                 " 090616-1451, havde intet med Danmark at gøre, så det var"
                 " nok ikke hans CPR-nummer, det dér",
                 ["0906XXXXXX"]),
                ("fået at høre fra Sean O'Something (010182-4241), at Irland"
                 " er et sejt land at bo i. Det bør vi få undersøgt",
                 ["0101XXXXXX"]),
            ])
    def test_simple_matches(self, text, expected):
        assert self.simplify_matches(CPRRule().match(text)) == expected

    @pytest.mark.parametrize(
            "text,expected",
            [
                ("260153-0786 ＜script>window.analytics.record({\"visit",
                 ["2601XXXXXX"]),
                ("Du er her: Vejstrand Kommune > Sagsbehandlingssystem >"
                 " Mine sager > Tilgængelighedstilskud 150564-0701",
                 ["1505XXXXXX"]),
                ("# Rapport for Vejstrand Skoler\n"
                 "# Genereret af SKOLMAN v3.4.2 den 8. maj 2025 kl. 1150\n"
                 "Fornavn,Efternavn,Personnummer,Fraværsprocent\n"
                 "Frederik,Skolemanden,1505644847,7%",
                 ["1505XXXXXX"]),
            ])
    def test_simple_matches_with_symbols(self, text, expected):
        assert self.simplify_matches(CPRRule().match(text)) == expected

    @pytest.mark.parametrize(
            "text,potential",
            [
                # CPR numbers lying around next to other, non-CPR numbers are
                # ignored
                ("6742132882 1412661636 9424 1505642917 377377244444",
                 ["1412XXXXXX", "1505XXXXXX"]),
            ])
    def test_context_check(self, text, potential):
        """Test that the context check causes valid CPR numbers to be
        dismissed."""
        assert self.simplify_matches(
                CPRRule().match(text)) == []
        assert self.simplify_matches(
                CPRRule(examine_context=False).match(text)) == potential

    @pytest.mark.parametrize(
            "text,potential",
            [
                # Valid CPR numbers from the future are ignored
                # (note that the xxxx57-7xxx range is allocated to the year
                # 2057)
                ("Marsbo Rumvæsensen (220557-7451) ønsker adgang til"
                 " næringsmiddel-depotet på rådskibet",
                 ["2205XXXXXX"]),
            ])
    def test_relevance_check(self, text, potential):
        """Test that the relevance check causes valid CPR numbers to be
        dismissed."""
        assert self.simplify_matches(
                CPRRule().match(text)) == []
        assert self.simplify_matches(
                CPRRule(ignore_irrelevant=False).match(text)) == potential

    @pytest.mark.parametrize(
            "text,blacklist,potential",
            [
                ("Vejstrand Kommune - Skolevæsnets lønkonto - "
                 "NØK nummer 1505642348",
                 ["nøk"],  # Blacklist words must always be given in lower case
                 ["1505XXXXXX"]),
                ("DANSK BUTIKSDRIFT A/S FAKTURANR. 1506434668",
                 ["faktura"],
                 ["1506XXXXXX"])
            ])
    def test_blacklist(self, text, blacklist, potential):
        """Test that the presence of blacklisted words causes valid CPR numbers
        to be dismissed."""
        assert self.simplify_matches(
                CPRRule(blacklist=blacklist).match(text)) == []
        assert self.simplify_matches(
                CPRRule(blacklist=[]).match(text)) == potential

    @pytest.mark.parametrize(
            "text,whitelist,potential",
            [
                ("123456 222 444 PERSONNUMMER 444 141266-4872 997977-9777",
                 ["personnummer"],
                 ["1412XXXXXX"]),
            ])
    def test_whitelist(self, text, whitelist, potential):
        """Test that the presence of whitelisted words causes valid CPR numbers
        that would otherwise be dismissed by the context check to be candidates
        again."""
        assert self.simplify_matches(
                CPRRule().match(text)) == []
        assert self.simplify_matches(
                CPRRule(whitelist=whitelist).match(text)) == potential
