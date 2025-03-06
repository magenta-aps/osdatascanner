from typing import Iterable
import structlog

from sqlalchemy import select, MetaData, create_engine
from sqlalchemy.sql.expression import func as sql_func, text as sql_text


from os2datascanner.engine2.model.core import (
        Source, Handle, Resource, SourceManager)
from os2datascanner.engine2.model.derived import DerivedSource
from os2datascanner.engine2.utilities.i18n import gettext as _

from .sbsysdb_utilities import convert_rule_to_select, exec_expr


logger = structlog.get_logger("engine2")


class SBSYSDBSource(Source):
    type_label = "sbsys-db"

    def __init__(
            self, server, port, db, user, password,
            *,
            reflect_tables=None):
        self._server = server
        self._port = port
        self._db = db
        self._user = user
        self._password = password
        self._reflect_tables = reflect_tables

    @property
    def reflect_tables(self):
        return self._reflect_tables or ("Sag", "Person",)

    def censor(self):
        return SBSYSDBSource(
                self._server, self._port, self._db, None, None)

    def _generate_state(self, sm: SourceManager):
        engine = create_engine(
                "mssql+pymssql://"
                f"{self._user}:{self._password}"
                f"@{self._server}:{self._port}/{self._db}")

        metadata_obj = MetaData()
        metadata_obj.reflect(bind=engine, only=self.reflect_tables)

        yield engine, metadata_obj.tables

    def handles(
            self, sm: SourceManager,
            *, rule=None) -> Iterable['SBSYSDBCaseHandle']:
        engine, tables = sm.open(self)
        Sag = tables["Sag"]

        column_labels = {"Nummer": Sag.c.Nummer, "Titel": Sag.c.Titel}
        expr = convert_rule_to_select(
                rule,
                Sag, tables,
                select(), column_labels,
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
