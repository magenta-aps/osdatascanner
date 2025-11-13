from types import SimpleNamespace
import pytest
from sqlalchemy import (
        MetaData,
        Table, Column,
        UUID, Integer, String, DateTime,
        ForeignKey,
        select)
from sqlalchemy.sql.expression import func as sql_func, text as sql_text

from os2datascanner.engine2.rules import logical_operators  # noqa
from os2datascanner.engine2.model._staging import sbsysdb_rule as dbr
from os2datascanner.engine2.model._staging import sbsysdb_utilities as dbu


@pytest.fixture
def metadata():
    return MetaData()


@pytest.fixture
def municipality_table(*, metadata):
    return Table(
            "Municipality",
            metadata,
            Column("ID", UUID, primary_key=True),
            Column("Name", String),
            Column("Code", Integer),
    )


@pytest.fixture
def location_table(*, metadata, municipality_table):
    return Table(
            "Location",
            metadata,
            Column("ID", UUID, primary_key=True),
            Column("Name", String),
            Column("Address1", String),
            Column("Address2", String, nullable=True),
            Column("Address3", String, nullable=True),
            Column("PostNumber", String),
            Column("Municipality", ForeignKey("Municipality.ID")),
    )


@pytest.fixture
def user_table(*, metadata, location_table, municipality_table):
    return Table(
            "User",
            metadata,
            Column("ID", UUID, primary_key=True),
            Column("Name", String),
            Column("Email", String),
            Column("Office", ForeignKey("Location.ID")),
            Column("Municipality", ForeignKey("Municipality.ID")),
    )


@pytest.fixture
def person_table(*, metadata, location_table):
    return Table(
            "Person",
            metadata,
            Column("ID", UUID, primary_key=True),
            Column("PNR", String(10), unique=True),
            Column("Name", String),
            Column("Address", ForeignKey("Location.ID")),
    )


@pytest.fixture
def partytype_table(*, metadata):
    return Table(
            "PartyType",
            metadata,
            Column("ID", UUID, primary_key=True),
            Column("Name", String),
    )


@pytest.fixture
def partyinfo_table(*, metadata, person_table, partytype_table):
    return Table(
            "PartyInfo",
            metadata,
            Column("ID", UUID, primary_key=True),
            Column("PartyID", UUID),
            Column("PartyType", ForeignKey("PartyType.ID")),
    )


@pytest.fixture
def securityset_table(*, metadata):
    return Table(
            "SecuritySet",
            metadata,
            Column("ID", UUID, primary_key=True),
            Column("Name", String(1), nullable=True),
    )


@pytest.fixture
def case_table(*, metadata, user_table, partyinfo_table, securityset_table):
    return Table(
            "Case",
            metadata,
            Column("ID", UUID, primary_key=True),
            Column("Title", String),
            Column("Created", DateTime),
            Column("Assignee", ForeignKey("User.ID"), nullable=True),
            Column("PartyInfo", ForeignKey("PartyInfo.ID")),
            Column("SecuritySet", ForeignKey("SecuritySet.ID")),
    )


@pytest.fixture
def securitygroup_table(*, metadata):
    return Table(
            "SecurityGroup",
            metadata,
            Column("ID", UUID, primary_key=True),
            Column("Name", String),
    )


@pytest.fixture
def security_throughtable(*, metadata, securityset_table, securitygroup_table):
    return Table(
            "SecuritySet_SecurityGroup",
            metadata,
            Column("ID", UUID, primary_key=True),
            Column("SecuritySetID", ForeignKey("SecuritySet.ID")),
            Column("SecurityGroupID", ForeignKey("SecurityGroup.ID")),
    )


class TestRuleTranslation:
    # XXX: These tests examine string representations of SQL expressions, which
    # seems very brittle (what if SQLAlchemy adds or removes a newline here or
    # there?)
    def test_simple_translation_str(self, *, metadata, case_table):
        """SQL translation of simple expressions, of the form <FIELD> <OP>
        <VALUE>, is supported."""
        # Arrange
        rule = dbr.SBSYSDBRule(
                "Title",
                dbr.SBSYSDBRule.Op.CONTAINS,
                "business")

        # Act
        column_labels = {}
        sql_expr = dbu.convert_rule_to_select(
                rule,
                case_table, metadata.tables,
                select(), column_labels)

        # Assert
        assert list(column_labels.keys()) == ["Title"]

        compiled_expr = sql_expr.compile()
        assert str(compiled_expr) == (
                'SELECT "Case"."Title" \n'
                'FROM "Case" \n'
                'WHERE ("Case"."Title" LIKE \'%\' || :Title_1 || \'%\')')
        assert compiled_expr.params["Title_1"] == "business"

    def test_simple_translation_virtual_column(self, *, metadata, case_table):
        """SQL translation of simple computed expressions, of the form
        <COMPUTED FIELD> <OP> <VALUE>, is supported."""
        # Arrange
        rule = dbr.SBSYSDBRule(
                "?AgeInDays?",
                dbr.SBSYSDBRule.Op.GTE,
                365)
        virtual_columns = {
            "?AgeInDays?": sql_func.datediff(
                    sql_text("day"), case_table.c.Created, sql_func.now())
        }

        # Act
        column_labels = {}
        sql_expr = dbu.convert_rule_to_select(
                rule,
                case_table, metadata.tables,
                select(), column_labels, virtual_columns)

        # Assert
        assert list(column_labels.keys()) == ["?AgeInDays?"]

        compiled_expr = sql_expr.compile()
        assert str(compiled_expr) == (
                'SELECT datediff(day, "Case"."Created", now()) '
                'AS datediff_1 \n'
                'FROM "Case" \n'
                'WHERE datediff(day, "Case"."Created", now()) >= :datediff_2')

        assert compiled_expr.params["datediff_2"] == 365

    def test_compound_translation_int(self, *, metadata, location_table):
        """SQL translation of compound expressions (of the form <FIELD> <OP>
        <VALUE> AND <FIELD> <OP> <VALUE>) is supported."""
        # Arrange
        rule = (dbr.SBSYSDBRule("PostNumber", "gt", 1000)
                & dbr.SBSYSDBRule("PostNumber", "lte", 2000))

        # Act
        column_labels = {}
        sql_expr = dbu.convert_rule_to_select(
                rule,
                location_table, metadata.tables,
                select(), column_labels)

        # Assert
        assert list(column_labels.keys()) == ["PostNumber"]

        compiled_expr = sql_expr.compile()
        assert str(compiled_expr) == (
                'SELECT "Location"."PostNumber" \n'
                'FROM "Location" \n'
                'WHERE "Location"."PostNumber" > :PostNumber_1 '
                'AND "Location"."PostNumber" <= :PostNumber_2')
        assert compiled_expr.params["PostNumber_1"] == 1000
        assert compiled_expr.params["PostNumber_2"] == 2000

    def test_complex_name_translation_str(self, *, metadata, case_table):
        """SQL translation of complex names stretching across several tables
        (of the form <FIELD>.<OTHERTABLE_FIELD> <OP> <VALUE> is supported."""
        # Arrange
        rule = dbr.SBSYSDBRule(
                "Assignee.Office.Name",
                dbr.SBSYSDBRule.Op.EQ,
                "Municipal Headquarters")

        # Act
        column_labels = {}
        sql_expr = dbu.convert_rule_to_select(
                rule,
                case_table, metadata.tables,
                select(), column_labels)

        # Assert
        assert list(column_labels.keys()) == ["Assignee.Office.Name"]

        compiled_expr = sql_expr.compile()
        assert str(compiled_expr) == (
                'SELECT "Location"."Name" \n'
                'FROM "Location", "Case", "User" \n'
                'WHERE "Case"."Assignee" = "User"."ID" '
                'AND "User"."Office" = "Location"."ID" '
                'AND "Location"."Name" = :Name_1')

        assert compiled_expr.params["Name_1"] == "Municipal Headquarters"

    def test_complex_name_translation_str_neg(self, *, metadata, case_table):
        """Negating an OSdatascanner rule that uses the equal-to operator
        produces the same SQL as a non-negated rule that uses the not-equal
        operator."""
        # Arrange
        rule1 = ~dbr.SBSYSDBRule(
                "Assignee.Office.Name",
                dbr.SBSYSDBRule.Op.EQ,
                "Municipal Headquarters")
        rule2 = dbr.SBSYSDBRule(
                "Assignee.Office.Name",
                dbr.SBSYSDBRule.Op.NEQ,
                "Municipal Headquarters")

        # Act
        column_labels1 = {}
        sql_expr1 = dbu.convert_rule_to_select(
                rule1,
                case_table, metadata.tables,
                select(), column_labels1)
        column_labels2 = {}
        sql_expr2 = dbu.convert_rule_to_select(
                rule2,
                case_table, metadata.tables,
                select(), column_labels2)

        # Assert
        assert (list(column_labels1.keys())
                == list(column_labels2.keys())
                == ["Assignee.Office.Name"])

        compiled_expr1 = sql_expr1.compile()
        compiled_expr2 = sql_expr2.compile()
        assert str(compiled_expr1) == str(compiled_expr2) == (
                'SELECT "Location"."Name" \n'
                'FROM "Location", "Case", "User" \n'
                'WHERE "Case"."Assignee" = "User"."ID" '
                'AND "User"."Office" = "Location"."ID" '
                'AND "Location"."Name" != :Name_1')

        assert (compiled_expr1.params["Name_1"]
                == compiled_expr2.params["Name_1"]
                == "Municipal Headquarters")

    def test_complex_name_cast_translation(self, *, metadata, partyinfo_table):
        """SQL translation of complex names that also encode typing information
        (of the form <FIELD> as OtherTable.<OTHERTABLE_FIELD> <OP> <VALUE>) is
        supported."""
        # Arrange
        rule = (dbr.SBSYSDBRule("PartyType.Name", "eq", "Person")
                & dbr.SBSYSDBRule(
                        "Party as Person.Name",
                        "eq", "Jens Jensen-Jensensen"))

        # Act
        column_labels = {}
        sql_expr = dbu.convert_rule_to_select(
                rule,
                partyinfo_table, metadata.tables,
                select(), column_labels)

        # Assert
        assert list(column_labels.keys()) == [
                "PartyType.Name", "Party as Person.Name"]

        compiled_expr = sql_expr.compile()
        assert str(compiled_expr) == (
                'SELECT "PartyType"."Name", "Person"."Name" AS "Name_1" \n'
                'FROM "PartyType", "Person", "PartyInfo" \n'
                'WHERE "PartyInfo"."PartyType" = "PartyType"."ID" '
                'AND "PartyInfo"."PartyID" = "Person"."ID" '
                'AND "PartyType"."Name" = :Name_2 '
                'AND "Person"."Name" = :Name_3')

        assert compiled_expr.params["Name_2"] == 'Person'
        assert compiled_expr.params["Name_3"] == "Jens Jensen-Jensensen"

    def test_complex_name_cast_translation_ref(self, *, metadata, case_table):
        """SQL translation of references (of the form <FIELD> <OP> <FIELDREF>)
        is supported."""
        # Arrange
        rule = dbr.SBSYSDBRule(
                "PartyInfo.Party as Person.Address.Municipality",
                "neq", "&Assignee.Municipality")

        # Act
        column_labels = {}
        sql_expr = dbu.convert_rule_to_select(
                rule,
                case_table, metadata.tables,
                select(), column_labels)

        # Assert
        assert list(column_labels.keys()) == [
                "PartyInfo.Party as Person.Address.Municipality",
                "Assignee.Municipality"]

        compiled_expr = sql_expr.compile()
        assert str(compiled_expr) == (
                'SELECT "Location"."Municipality", '
                '"User"."Municipality" AS "Municipality_1" \n'
                'FROM "Location", "User", "Case", "PartyInfo", "Person" \n'
                'WHERE "Case"."PartyInfo" = "PartyInfo"."ID" '
                'AND "PartyInfo"."PartyID" = "Person"."ID" '
                'AND "Person"."Address" = "Location"."ID" '
                'AND "Case"."Assignee" = "User"."ID" '
                'AND "Location"."Municipality" != "User"."Municipality"')

        # We don't specify any values -- everything is done by the database --
        # so this dict should be empty
        assert compiled_expr.params == {}

    def test_complex_name_cast_translation_esc(self, *, metadata, case_table):
        """The interpretation of the right-hand side of a rule as a field
        reference can be disabled with an escape sequence."""
        # Arrange
        rule = dbr.SBSYSDBRule("Title", "icontains", "\\&More")

        # Act
        column_labels = {}
        sql_expr = dbu.convert_rule_to_select(
                rule,
                case_table, metadata.tables,
                select(), column_labels)

        # Assert
        assert list(column_labels.keys()) == ["Title"]

        compiled_expr = sql_expr.compile()
        assert str(compiled_expr) == (
                'SELECT "Case"."Title" \n'
                'FROM "Case" \n'
                'WHERE (lower("Case"."Title") LIKE '
                "'%' || lower(:Title_1) || '%')")

        assert compiled_expr.params["Title_1"] == "&More"

    def test_complex_name_final_component_id(
            self, *, metadata, partyinfo_table):
        """The convenience syntax that allows the "-ID" suffix to be omitted
        also works for the last component of a complex name."""
        # Arrange
        rule = dbr.SBSYSDBRule("Party", "neq", None)

        # Act
        column_labels = {}
        sql_expr = dbu.convert_rule_to_select(
                rule,
                partyinfo_table, metadata.tables,
                select(), column_labels)

        # Assert
        assert list(column_labels.keys()) == ["Party"]

        compiled_expr = sql_expr.compile()
        assert str(compiled_expr) == (
                'SELECT "PartyInfo"."PartyID" \n'
                'FROM "PartyInfo" \n'
                'WHERE "PartyInfo"."PartyID" IS NOT NULL')

    @pytest.mark.parametrize("obj,attrs,ev,raises", [
        (SimpleNamespace(dog=20, cat=40, gerbil=60),
         ["gerbil", "cat", "dog"], 60, False),
        (SimpleNamespace(cat="fluffy"),
         ["gerbil", "cat", "dog"], "fluffy", False),
        (SimpleNamespace(cat="fluffy", dog="playful"),
         ["gerbil", "dog"], "playful", False),
        (SimpleNamespace(lolcat="can haz cheeseburger??",
                         doge="such test. very robustness. wow"),
         ["dog", "cat"], None, True),
    ])
    def test_get_first_attr(self, obj, attrs, ev, raises):
        """The get_first_attr function correctly returns the first named
        attribute present on an object."""
        try:
            assert dbu.get_first_attr(obj, *attrs) == ev
            if raises:
                pytest.fail("expected AttributeError")
        except AttributeError:
            if not raises:
                pytest.fail("didn't expect this exception")

    def test_altkey_resolution_complex(
            self, *,
            metadata, case_table, security_throughtable):
        # Arrange
        rule = dbr.SBSYSDBRule(
                "SecuritySet.ID as SecuritySet_SecurityGroup"
                " on SecuritySetID.SecurityGroup.Name",
                "eq", "Everybody")

        # Act
        column_labels = {}
        sql_expr = dbu.convert_rule_to_select(
                rule,
                case_table, metadata.tables,
                select(), column_labels)

        # Assert
        assert list(column_labels.keys()) == [
                "SecuritySet.ID as SecuritySet_SecurityGroup"
                " on SecuritySetID.SecurityGroup.Name"]

        compiled_expr = sql_expr.compile()
        assert str(compiled_expr) == (
                'SELECT "SecurityGroup"."Name" \n'
                'FROM "SecurityGroup", "Case", "SecuritySet", '
                '"SecuritySet_SecurityGroup" \n'
                'WHERE "Case"."SecuritySet" = "SecuritySet"."ID" '
                'AND "SecuritySet"."ID" = "SecuritySet_SecurityGroup"."SecuritySetID" '
                'AND "SecuritySet_SecurityGroup"."SecurityGroupID" = "SecurityGroup"."ID" '
                'AND "SecurityGroup"."Name" = :Name_1')

        assert compiled_expr.params == {"Name_1": "Everybody"}

    def test_altkey_resolution_simple(
            self, *,
            metadata, case_table, security_throughtable):
        # Arrange
        rule = dbr.SBSYSDBRule(
                "SecuritySet as SecuritySet_SecurityGroup"
                " on SecuritySetID.SecurityGroup.Name",
                "eq", "Everybody")

        # Act
        column_labels = {}
        sql_expr = dbu.convert_rule_to_select(
                rule,
                case_table, metadata.tables,
                select(), column_labels)

        # Assert
        assert list(column_labels.keys()) == [
                "SecuritySet as SecuritySet_SecurityGroup"
                " on SecuritySetID.SecurityGroup.Name"]

        compiled_expr = sql_expr.compile()
        assert str(compiled_expr) == (
                'SELECT "SecurityGroup"."Name" \n'
                'FROM "SecurityGroup", "Case", '
                '"SecuritySet_SecurityGroup" \n'
                'WHERE "Case"."SecuritySet" = "SecuritySet_SecurityGroup"."SecuritySetID" '
                'AND "SecuritySet_SecurityGroup"."SecurityGroupID" = "SecurityGroup"."ID" '
                'AND "SecurityGroup"."Name" = :Name_1')

        assert compiled_expr.params == {"Name_1": "Everybody"}
