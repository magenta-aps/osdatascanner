from enum import Enum
from typing import Iterable
import operator
import structlog

from sqlalchemy import (
        and_, or_, not_, true, false,
        select, Table, Column, MetaData, create_engine)
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import (
        Select, func as sql_func, text as sql_text)


from os2datascanner.engine2.model.core import (
        Source, Handle, Resource, SourceManager)
from os2datascanner.engine2.rules import logical
from os2datascanner.engine2.rules.rule import Rule, SimpleRule


logger = structlog.get_logger("engine2")


DUMMY_CASE_MIME = "application/vnd.magenta.osds.sbsys-case"


class SBSYSDBRule(SimpleRule):
    class Op(Enum):
        EQ = ("eq", operator.eq)
        NEQ = ("neq", operator.ne)
        LT = ("lt", operator.lt)
        LTE = ("lte", operator.le)
        GT = ("gt", operator.gt)
        GTE = ("gte", operator.ge)

        CONTAINS = (
                "contains",
                lambda haystack, needle: needle in haystack,
                lambda column, value: column.contains(value))
        ICONTAINS = (
                "icontains",
                lambda haystack, needle: (
                        needle.casefold() in haystack.casefold()),
                lambda column, value: column.icontains(value))

        def __new__(cls, value, func_py, func_db=None):
            obj = object.__new__(cls)
            obj._value_ = value
            obj.func_py = func_py
            obj.func_db = func_db or func_py
            return obj

        def __call__(self, *args, **kwargs):
            return self.func_py(*args, **kwargs)

    type_label = "sbsys-db-fieldrule"
    operates_on = None

    __match_args__ = ("_field", "_op", "_value")

    def __init__(self, field: str, op: Op, value, *args, **kwargs):
        self._field = field
        self._op = op
        self._value = value

    @property
    def presentation_raw(self):
        return ":D"

    def match(self, db_row):
        if self._op(db_row[self._field], self._value):
            yield {
                "match": db_row[self._field]
            }

    def to_json_object(self):
        return NotImplemented


def resolve_complex_column_name(
        start: Table, col_name: str) -> (Select, Column):
    """Given a Table at which to start and a complex column name that may
    traverse several tables (for example,
    "Creator.ContactInfo.Address.Postcode"), returns the conjunction of all the
    extra constraints required by the traversal and a reference to the column
    that was eventually selected."""
    here = start
    *field_path, last = col_name.split(".")

    # Worked example: starting at Sag and trying to get to
    # Behandler.Adresse.Landekode...

    links = []

    for part in field_path:
        # ... we first select the "BehandlerID" column...
        try:
            link_column = getattr(here.c, part + "ID")
        except AttributeError:
            # Handle foreign key reference columns that don't use the "ID"
            # name suffix convention
            link_column = getattr(here.c, part)

        # ... then we follow the foreign key to get a reference to the Bruger
        # table on the other side...
        fk, = link_column.foreign_keys
        other_table = fk.column.table

        # ... then we (implicitly) join the Bruger table into our query...
        links.append(link_column == other_table.c.ID)
        # ... and continue following the chain at Bruger, where we do the
        # same trick again for "Adresse" -> AdresseID -> <table Adresse>
        here = other_table

    # Finally, we take the last part of the column name ("Landekode") and look
    # it up in the table we've ended up at
    return and_(*links), getattr(here.c, last)


def convert_rule_to_select(
        rule: Rule, table: Table,
        initial_select: Select, column_labels: dict[str, Column],
        virtual_columns: dict[str, object] = None) -> Select:
    """Converts an OSdatascanner Rule containing SBSYSDBRule objects into a
    corresponding SQLAlchemy Select expression.

    The resulting expression is guaranteed to select columns in the same order
    as the keys of the column_labels dict. (One useful consequence of this is
    that you can make a mapping from field names to results by just zipping
    the keys together with a result tuple.)"""

    def rule_to_constraints(r):
        """Recursively converts an OSdatascanner Rule into a SQLAlchemy
        constraint.

        This function updates the column_labels dictionary with each new column
        required by the expression, labelled with its name from the Rule; this
        information will eventually be required to turn the constraint into a
        complete Select expression."""
        match r:
            case logical.AndRule():
                return and_(
                        true(),
                        *(rule_to_constraints(c) for c in r.components))

            case logical.OrRule():
                return or_(
                        false(),
                        *(rule_to_constraints(c) for c in r.components))

            case logical.NotRule():
                return not_(rule_to_constraints(r._rule))

            case SBSYSDBRule(field_name, op, value) \
                    if virtual_columns and field_name in virtual_columns:
                virtual_column = virtual_columns.get(field_name)
                if field_name not in column_labels:
                    column_labels[field_name] = virtual_column
                return op.func_db(virtual_column, value)

            case SBSYSDBRule(field_name, op, value):
                extra_constraints, column = resolve_complex_column_name(
                        table, field_name)
                if field_name not in column_labels:
                    column_labels[field_name] = column
                return and_(extra_constraints, op.func_db(column, value))

            case _:
                # For now, we assume that any other OSdatascanner rule plays no
                # part in the SQL query
                return true()

    constraints = rule_to_constraints(rule) if rule else true()
    # To turn our constraint object into a valid Select expression, we need to
    # make sure we actually select the columns required by the constraints.
    # Luckily rule_to_constraints stashes those away in the column_labels dict
    return initial_select.add_columns(
            *column_labels.values()).where(constraints)


class SBSYSDBSource(Source):
    type_label = "sbsys-db"

    def __init__(self, server, port, db, user, password):
        self._server = server
        self._port = port
        self._db = db
        self._user = user
        self._password = password

    def censor(self):
        return SBSYSDBSource(
                self._server, self._port, self._db, None, None)

    def _generate_state(self, sm: SourceManager):
        engine = create_engine(
                "mssql+pymssql://"
                f"{self._user}:{self._password}"
                f"@{self._server}:{self._port}/{self._db}")

        metadata_obj = MetaData()
        metadata_obj.reflect(bind=engine, only=("Sag",))

        yield engine, metadata_obj.tables

    def handles(
            self, sm: SourceManager,
            *, rule=None) -> Iterable['SBSYSDBCaseHandle']:
        engine, tables = sm.open(self)
        Sag = tables["Sag"]

        column_labels = {"Nummer": Sag.c.Nummer, "Titel": Sag.c.Titel}
        expr = convert_rule_to_select(
                rule, Sag, select(), column_labels,
                virtual_columns={
                    # Subtracting two datetimes in SQL Server utterly
                    # bafflingly gives you /a third datetime/ (2024-01-01 -
                    # 2020-01-01 = 1904-01-02), so let's not do that. Instead
                    # we use the DATEDIFF() function, which computes the
                    # difference between the start date and the end date in
                    # terms of the unit you request
                    "?Age?": sql_func.datediff(
                            sql_text("day"), Sag.c.LastChanged, sql_func.now())
                })
        breakpoint()

        with Session(engine) as session:
            logger.debug(
                    "executing SBSYS database query",
                    query=str(expr), params=expr.compile().params)

            # Simulate Django's iterator() (with its default page size of 2000)
            # to avoid allocating too much memory
            for db_row_ in session.execute(
                    expr, execution_options={
                        "yield_per": 2000
                    }):
                db_row = dict(zip(column_labels.keys(), db_row_))
                yield SBSYSDBCaseHandle(
                        self,
                        db_row["Nummer"], db_row["Titel"],
                        hints={"db_row": db_row})

    def to_json_object(self):
        return {
            "server": self._server,
            "port": self._port,
            "db": self._db,
            "user": self._user,
            "password": self._password
        }


class SBSYSDBCaseResource(Resource):
    def check(self):
        return True

    def compute_type(self):
        return DUMMY_CASE_MIME


class SBSYSDBCaseHandle(Handle):
    type_label = "sbsys-db-case"
    resource_type = SBSYSDBCaseResource

    def __init__(
            self, source, path, title, **kwargs):
        super().__init__(source, path, **kwargs)
        self._title = title

    def guess_type(self):
        return DUMMY_CASE_MIME

    @property
    def presentation_name(self):
        rv = f"case {self.relative_path}"
        return rv if not self._title else f"\"{self._title}\" ({rv})"

    @property
    def presentation_place(self):
        return "SBSYS"
