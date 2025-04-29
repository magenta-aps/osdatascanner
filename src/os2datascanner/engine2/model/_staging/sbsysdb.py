from io import BytesIO
from typing import Iterable
from functools import cached_property
import structlog
from contextlib import contextmanager

from sqlalchemy import select, MetaData, create_engine
from sqlalchemy.sql.expression import func as sql_func, text as sql_text


from os2datascanner.engine2.model.core import (
        Source, Handle, Resource, FileResource, SourceManager)
from os2datascanner.engine2.model.derived import DerivedSource
from os2datascanner.engine2.utilities.i18n import gettext as _
from os2datascanner.engine2.conversions import registry
from os2datascanner.engine2.conversions.types import OutputType

from .sbsysdb_rule import SBSYSDBRule  # noqa
from .sbsysdb_utilities import (
        exec_expr, convert_rule_to_select, resolve_complex_column_names)


logger = structlog.get_logger("engine2")


class SBSYSDBSource(Source):
    type_label = "sbsys-db"

    def __init__(
            self, server, port, db, user, password,
            *,
            reflect_tables: tuple[str, ...] | None,
            base_weblink: str | None):
        self._server = server
        self._port = port
        self._db = db
        self._user = user
        self._password = password
        self._reflect_tables = reflect_tables
        self._base_weblink = base_weblink

    @property
    def reflect_tables(self):
        return self._reflect_tables or ("Sag", "Person",)

    def censor(self):
        return SBSYSDBSource(
                self._server, self._port, self._db, None, None,
                reflect_tables=self._reflect_tables,
                base_weblink=self._base_weblink)

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
            *, rule=None) -> Iterable['SBSYSDBHandles.Case']:
        engine, tables = sm.open(self)
        Sag = tables["Sag"]

        constraint, columns = resolve_complex_column_names(
                Sag, tables, *SBSYSDBSources.Case.required_columns)
        column_labels = dict(
                zip(SBSYSDBSources.Case.required_columns, columns))
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

        for db_row in exec_expr(engine, expr, *column_labels.keys()):
            match (self._base_weblink, db_row):
                case (str() as wl, {"ID": cid}):
                    weblink = f"{wl}#/sager/{cid}"
                case _:
                    weblink = None
            yield SBSYSDBHandles.Case(
                    self,
                    db_row["Nummer"], db_row["Titel"], weblink,
                    hints={"db_row": db_row})

    def to_json_object(self):
        return super().to_json_object() | {
            "server": self._server,
            "port": self._port,
            "db": self._db,
            "user": self._user,
            "password": self._password,
            "reflect_tables": (
                    list(self._reflect_tables)
                    if self._reflect_tables
                    else None),
            "base_weblink": self._base_weblink
        }

    @Source.json_handler(type_label)
    @staticmethod
    def from_json_object(obj):
        reflect_tables = (
                tuple(rt)
                if (rt := obj.get("reflect_tables"))
                else None)
        return SBSYSDBSource(
                obj["server"], obj["port"],
                obj["db"], obj["user"], obj["password"],
                reflect_tables=reflect_tables,
                base_weblink=obj.get("base_weblink"))


class SBSYSDBHandles:
    class Case(Handle):
        _DUMMY_MIME = "application/vnd.magenta.osds.sbsys-case"

        class _Resource(Resource):
            def check(self):
                return True

            def _generate_metadata(self):
                row = registry.convert(self, OutputType.DatabaseRow)
                if upn := row.get("Behandler.UserPrincipalName"):
                    yield ("user-principal-name", upn)

            def compute_type(self):
                return SBSYSDBHandles.Case._DUMMY_MIME

        resource_type = _Resource
        type_label = "sbsys-db-case"

        def __init__(
                self,
                source: SBSYSDBSource,
                number: str,
                title: str | None,
                weblink: str | None,
                **kwargs):
            super().__init__(source, number, **kwargs)
            self._title = title
            self._weblink = weblink

        def guess_type(self):
            return self._DUMMY_MIME

        @property
        def presentation_url(self):
            return self._weblink

        @property
        def presentation_name(self):
            if not self._title:
                return _("case number {casenr}").format(casenr=self.relative_path)
            else:
                return _("case \"{title}\" (case number {casenr})").format(
                        title=self._title, casenr=self.relative_path)

        @property
        def presentation_place(self):
            return "SBSYS"

        def to_json_object(self):
            return super().to_json_object() | {
                "title": self._title,
                "hints": self._hints,
                "weblink": self._weblink,
            }

        @staticmethod
        @Handle.json_handler(type_label)
        def from_json_object(obj):
            return SBSYSDBHandles.Case(
                    Source.from_json_object(obj["source"]),
                    obj["path"], obj["title"],
                    obj.get("weblink"),
                    hints=obj["hints"])

    @Handle.stock_json_handler("sbsys-db-case-field")
    class Field(Handle):
        class _Resource(FileResource):
            def check(self):
                return True

            @cached_property
            def _val(self):
                return str(self.handle.source.fetch(self._sm)[
                        self.handle.relative_path]).encode()

            def _generate_metadata(self):
                yield from ()

            @contextmanager
            def make_stream(self):
                yield BytesIO(self._val)

            def get_size(self):
                return len(self._val)

            def compute_type(self):
                return "text/plain"

        type_label = "sbsys-db-case-field"
        resource_type = _Resource

        @property
        def presentation_name(self):
            return _("field \"{field}\" of {case}").format(
                    field=self.relative_path,
                    case=str(self.source.handle.presentation_name))

        @property
        def presentation_place(self):
            return str(self.source.handle.presentation_place)


@registry.conversion(OutputType.DatabaseRow, SBSYSDBHandles.Case._DUMMY_MIME)
def get_database_row(r):
    return r.handle.hint("db_row")


class SBSYSDBSources:
    @Source.mime_handler(SBSYSDBHandles.Case._DUMMY_MIME)
    class Case(DerivedSource):
        type_label = "sbsys-db-case"
        derived_from = SBSYSDBHandles.Case

        def fetch(self, sm: SourceManager):
            engine, tables = sm.open(self)
            Sag = tables["Sag"]

            row_hints = self.handle.hint("db_row", {})

            columns_to_select = [
                    getattr(Sag.c, col)
                    for col in self.required_columns
                    if col not in row_hints]

            db_row = None
            if columns_to_select:
                expr = select().add_columns(columns_to_select).where(
                        Sag.c.Nummer == self.handle.relative_path)

                db_row, = exec_expr(engine, expr, *columns_to_select)

            return {col: row_hints[col]
                    if col in row_hints
                    else db_row[col] for col in self.required_columns}

        required_columns = (
                "ID", "Nummer", "Titel", "Kommentar",
                "Behandler.UserPrincipalName",)

        def _generate_state(self, sm: SourceManager):
            yield sm.open(self.handle.source)

        def handles(self, sm: SourceManager):
            yield SBSYSDBHandles.Field(self, "Kommentar")
