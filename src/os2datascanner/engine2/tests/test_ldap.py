import copy
import pytest

from os2datascanner.utils.ldap import RDN, LDAPNode, group_dn_selector


@pytest.fixture
def enki():
    return LDAPNode.make(
        RDN.dn_to_sequence("CN=Enki"),
        distinguishedName="CN=Enki,L=Eridu,L=Sumer",
        memberOf=[
                "CN=WhoDecree,CN=Gods,L=Sumer"
        ],
        title="Lord of the Earth")


@pytest.fixture
def ninhursag():
    return LDAPNode.make(
        RDN.dn_to_sequence("CN=Ninhursag"),
        distinguishedName="CN=Ninhursag,L=Eridu,L=Sumer",
        memberOf=[
                "CN=WhoDecree,CN=Gods,L=Sumer"
        ])


@pytest.fixture
def gilgamesh():
    return LDAPNode.make(
        RDN.dn_to_sequence("CN=Gilgamesh"),
        distinguishedName="CN=Gilgamesh,L=Uruk,L=Sumer",
        memberOf=[
                "CN=Demigods,CN=Gods,L=Sumer",
                "CN=Heroes,L=Sumer"
        ])


@pytest.fixture
def enkidu():
    return LDAPNode.make(
        RDN.dn_to_sequence("CN=Enkidu"),
        distinguishedName="CN=Enkidu,L=Uruk,L=Sumer",
        memberOf=[
                "CN=Heroes,L=Sumer"
        ])


@pytest.fixture
def sumer(enki, ninhursag, gilgamesh, enkidu):
    return LDAPNode.make(
        RDN.dn_to_sequence("L=Sumer"),
        LDAPNode.make(RDN.dn_to_sequence("L=Eridu"), enki, ninhursag),
        LDAPNode.make(RDN.dn_to_sequence("L=Uruk"), gilgamesh, enkidu))


@pytest.fixture
def sumer_groups(enki, ninhursag, gilgamesh, enkidu):
    return LDAPNode.make(
        RDN.dn_to_sequence("L=Sumer"),
        LDAPNode.make(
                RDN.dn_to_sequence("CN=Gods"),
                LDAPNode.make(
                        RDN.dn_to_sequence("CN=WhoDecree"), enki, ninhursag),
                LDAPNode.make(
                        RDN.dn_to_sequence("CN=Demigods"), gilgamesh)),
        LDAPNode.make(
                RDN.dn_to_sequence("CN=Heroes"),
                gilgamesh, enkidu))


@pytest.fixture
def sumer_iterator():
    return [
        {
            "distinguishedName": "CN=Enki,L=Eridu,L=Sumer",
            "title": "Lord of the Earth",
            "memberOf": ["CN=WhoDecree,CN=Gods,L=Sumer"]
        },
        {
            "distinguishedName": "CN=Ninhursag,L=Eridu,L=Sumer",
            "memberOf": ["CN=WhoDecree,CN=Gods,L=Sumer"]
        },
        {
            "distinguishedName": "CN=Gilgamesh,L=Uruk,L=Sumer",
            "memberOf": ["CN=Demigods,CN=Gods,L=Sumer", "CN=Heroes,L=Sumer"]
        },
        {
            "distinguishedName": "CN=Enkidu,L=Uruk,L=Sumer",
            "memberOf": ["CN=Heroes,L=Sumer"]
        },
    ]


@pytest.fixture
def post_flood(sumer):
    post_node = copy.deepcopy(sumer)
    post_node.children.append(
        LDAPNode.make(
                RDN.dn_to_sequence("L=Kish"),
                LDAPNode.make(
                        RDN.dn_to_sequence("CN=Etana"),
                        distinguishedName="CN=Etana,L=Kish,L=Sumer")))
    return post_node


@pytest.fixture
def post_epic(sumer):
    post_node = copy.deepcopy(sumer)
    del post_node.children[1].children[1]  # The death of Enkidu
    return post_node


@pytest.fixture
def keycloak_user():
    return {
        "id": "b458a8a0-ca3a-479e-bb7a-ee9be8cdc593",
        "createdTimestamp": 1619701032883,
        "username": "enkidu wildman",
        "enabled": True,
        "totp": False,
        "emailVerified": False,
        "firstName": "Enkidu",
        "lastName": "Wildman",
        "email": "ew@uruk",
        "federationLink": "67f8323e-3682-40f3-acb8-18f568b010cf",
        "attributes": {
            "LDAP_ENTRY_DN": [
                "cn=Enkidu Wildman,ou=Employees,dc=uruk"
            ],
            "modifyTimestamp": [
                "20210429124502Z"
            ],
            "createTimestamp": [
                "20210429124502Z"
            ],
            "LDAP_ID": [
                "461c6b17-9516-4513-ad50-f9185962cb4f"
            ]
        },
        "disableableCredentialTypes": [],
        "requiredActions": [],
        "notBefore": 0,
        "access": {
            "manageGroupMembership": True,
            "view": True,
            "mapRoles": True,
            "impersonate": True,
            "manage": True
        }
    }


class TestLDAP:
    def test_iterator_construction(self, sumer, sumer_iterator):
        """LDAPNode.from_iterator should be able to construct a hierarchy from
        a flat list of users."""
        assert sumer == LDAPNode.from_iterator(sumer_iterator).collapse()

    def test_iterator_construction_group(self, sumer_groups, sumer_iterator):
        """LDAPNode.from_iterator should be able to construct a hierarchy from
        the group information present in a flat list of users."""
        assert sumer_groups == LDAPNode.from_iterator(sumer_iterator,
                                                      name_selector=group_dn_selector
                                                      ).collapse()

    def test_iterator_skipping(self):
        """LDAPNode.from_iterator should skip over objects that don't have an
        identifiable distinguished name."""
        node1 = LDAPNode.from_iterator([
            {"distinguishedName": "CN=Enki"},
            {"extinguishedName": "CN=Enkidu"},
            {"distinguishedName": "CN=Ninhursag"}
        ])
        node2 = LDAPNode.make(
            (),
            LDAPNode.make(
                RDN.dn_to_sequence("CN=Enki"),
                distinguishedName="CN=Enki"),
            LDAPNode.make(
                RDN.dn_to_sequence("CN=Ninhursag"),
                distinguishedName="CN=Ninhursag")
        )
        assert node1 == node2

    def test_iterator_skipping_group(self):
        """LDAPNode.from_iterator should skip over objects that don't have at
        least one identifiable group name."""
        node1 = LDAPNode.from_iterator([
            # memberOf structurally valid but with no valid groups
            {"distinguishedName": "CN=Enki",
                "memberOf": [""]},
            # memberOf valid
            {"distinguishedName": "CN=Enkidu",
                "memberOf": ["CN=Heroes,L=Sumer"]},
            # memberOf missing
            {"distinguishedName": "CN=Ninhursag"}
        ], name_selector=group_dn_selector)
        node2 = LDAPNode.make(
            (),
            LDAPNode.make(
                    RDN.dn_to_sequence("L=Sumer"),
                    LDAPNode.make(
                            RDN.dn_to_sequence("CN=Heroes"),
                            LDAPNode.make(
                                    RDN.dn_to_sequence("CN=Enkidu"),
                                    distinguishedName="CN=Enkidu",
                                    memberOf=["CN=Heroes,L=Sumer"])))
        )
        assert node1 == node2

    def test_addition(self, sumer, post_flood):
        """LDAPNode.diff should notice when an object is added to the
        hierarchy."""
        diff = list(sumer.diff(post_flood, only_leaves=True))
        expected = [
            (
                RDN.dn_to_sequence("CN=Etana,L=Kish,L=Sumer"),
                None,
                post_flood.children[-1].children[-1]
            )
        ]
        assert diff == expected

    def test_removal(self, sumer, post_epic):
        """LDAPNode.diff should notice when an object is removed from the
        hierarchy."""
        diff = list(sumer.diff(post_epic, only_leaves=True))
        expected = [
            (
                RDN.dn_to_sequence("CN=Enkidu,L=Uruk,L=Sumer"),
                sumer.children[1].children[1],
                None
            )
        ]
        assert diff == expected

    def test_property_change(self, sumer):
        """LDAPNode.diff should notice when the properties of an object
        change."""
        s2 = copy.deepcopy(sumer)
        s2.children[0].children[0].properties["title"] = "Lord of the Waters"
        diff = list(sumer.diff(s2, only_leaves=True))
        expected = [
            (
                RDN.dn_to_sequence("CN=Enki,L=Eridu,L=Sumer"),
                sumer.children[0].children[0],
                s2.children[0].children[0]
            )
        ]
        assert diff == expected

    def test_custom_import(self, keycloak_user):
        """LDAPNode.from_iterator should be able to select distinguished names
        from Keycloak's JSON serialisation of users."""

        def select_keycloak_dn(user_dict):
            yield user_dict.get(
                    "attributes", {}).get("LDAP_ENTRY_DN", [None])[0]
        node = LDAPNode.from_iterator(
                [keycloak_user],
                name_selector=select_keycloak_dn).children[0]

        # For the moment, we don't care about the properties here -- just the
        # structure
        node.children[0].children[0].properties.clear()

        expected = LDAPNode.make(
                        RDN.dn_to_sequence("dc=uruk"),
                        LDAPNode.make(
                                RDN.dn_to_sequence("ou=Employees"),
                                LDAPNode.make(
                                        RDN.dn_to_sequence(
                                            "cn=Enkidu Wildman"))))
        assert node == expected

    def test_complicated_name(self):
        """RDN.dn_to_sequence should be able to handle Unicode characters and
        escape sequences."""
        dadi = (RDN("C", "DK"),
                RDN("L", "Ærøskøbing, Ærø"),
                RDN("ST", "Baggårde 497"),
                RDN("O", "フィクショナル・エンタープライゼズ株式会社"),
                RDN("OU", "🍪🎩"),
                RDN("CN", "Daði Ólafsson, General Manager"),)

        assert dadi == RDN.dn_to_sequence(
                        "CN=Daði Ólafsson\\, General Manager,"
                        "OU=🍪🎩,"
                        "O=フィクショナル・エンタープライゼズ株式会社,"
                        "ST=Baggårde 497,"
                        "L=Ærøskøbing\\, Ærø,"
                        "C=DK")

        assert dadi == RDN.dn_to_sequence(
                        "CN=Da\\c3\\b0i \\c3\\93lafsson\\, General Manager,OU="
                        "\\f0\\9f\\8d\\aa\\f0\\9f\\8e\\a9,O=\\e3\\83\\95\\e3\\"
                        "82\\a3\\e3\\82\\af\\e3\\82\\b7\\e3\\83\\a7\\e3\\83\\8"
                        "a\\e3\\83\\ab\\e3\\83\\bb\\e3\\82\\a8\\e3\\83\\b3\\e3"
                        "\\82\\bf\\e3\\83\\bc\\e3\\83\\97\\e3\\83\\a9\\e3\\82"
                        "\\a4\\e3\\82\\bc\\e3\\82\\ba\\e6\\a0\\aa\\e5\\bc\\8f"
                        "\\e4\\bc\\9a\\e7\\a4\\be,ST=Bagg\\c3\\a5rde 497,L=\\"
                        "c3\\86r\\c3\\b8sk\\c3\\b8bing\\, \\c3\\86r\\c3\\b8,C"
                        "=DK")

    def test_round_trip_1(self):
        """Converting a RDN sequence to and from a string representation should
        produce an equivalent RDN, even when escape sequences are involved."""

        enki = (RDN("CN", "𒀭𒂗𒆠, Enki"),
                RDN("L", "𒉣𒆠, Eridu"),
                RDN("L", "𒆠𒂗𒄀, Sumer"))
        assert enki == RDN.dn_to_sequence(RDN.sequence_to_dn(enki))

    def test_round_trip_2(self):
        """Converting a RDN sequence to and from a string representation should
        produce an equivalent RDN, even when escape sequences are involved."""
        worst_case = (RDN("CN", """ "#+\\,;<=>"""), RDN("L", "Test"))
        assert worst_case == RDN.dn_to_sequence(RDN.sequence_to_dn(worst_case))

    def test_escape_exceptions(self):
        """Converting a RDN sequence to a string representation should not
        escape more special characters than necessary."""

        assert RDN.sequence_to_dn((RDN("#CN#", " 1 2 3 4 5 "),)) == "\\#CN#=\\ 1 2 3 4 5\\ "

    def test_raw_escape(self):
        dn = RDN.sequence_to_dn(
            (
                    RDN("OU", "🍪🎩"),
                    RDN("CN", "Daði Ólafsson, General Manager"),
            ), codec=None)
        assert dn == "CN=Daði Ólafsson\\, General Manager,OU=🍪🎩"
