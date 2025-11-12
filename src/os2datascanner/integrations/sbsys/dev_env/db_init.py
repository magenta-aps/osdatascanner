from functools import partial
from sqlalchemy import insert, Connection
from sqlalchemy.sql.expression import text as sql_text
from contextlib import contextmanager

from os2datascanner.integrations.sbsys.config import get_sbsys_settings
from os2datascanner.integrations.sbsys.db import get_engine, get_tables
from os2datascanner.integrations.sbsys.dev_env.data import databases


@contextmanager
def defer_constraints(conn: Connection):
    """Emulates the optional SQL command "SET CONSTRAINTS ALL DEFERRED" in the
    deranged world of Transact-SQL by rewriting every table to ignore all
    constraints at the start of the context, and rewriting them to switch them
    back on and check them again at the end.

    (No, really, you have to do that. I promise I'm not making this up...)"""
    try:
        conn.execute(sql_text(
                # sp_MSforeachtable is an undocumented stored proceedure that
                # evaluates a SQL command for every table in the database
                "EXEC sp_MSforeachtable '"
                # "?" is the magic placeholder that refers to each table
                "ALTER TABLE ? "
                # "NOCHECK CONSTRAINT" switches the named constraint(s) off
                "NOCHECK CONSTRAINT all"
                "';"))
        yield
    except BaseException:
        # The transaction is doomed. Give up immediately and let the exception
        # bubble up
        raise
    else:
        # The transaction is not doomed. Put the constraints back
        conn.execute(sql_text(
                "EXEC sp_MSforeachtable 'ALTER TABLE ? "
                # If you don't specify "WITH CHECK" then changes made while
                # the constraint was switched off aren't actually constrained
                # (... what)
                "WITH CHECK CHECK CONSTRAINT all';"))


if __name__ == "__main__":
    sbsys_settings = get_sbsys_settings()
    make_engine = partial(
            get_engine,
            host=sbsys_settings.sbsys_host,
            port=sbsys_settings.sbsys_port,
            user=sbsys_settings.sbsys_user,
            password=sbsys_settings.sbsys_password)

    for database_name, database_obj in databases.items():
        tables = database_obj["tables"]
        print(database_name)
        engine = make_engine(database=database_name)
        table_map = get_tables(engine, only=tuple(tables.keys()))

        with engine.begin() as conn, defer_constraints(conn):
            for table_name, items in tables.items():
                table = table_map[table_name]
                batches = []
                while "flush" in items:
                    flush_at = items.index("flush")
                    batches.append(items[:flush_at])
                    items = items[flush_at + 1:]
                batches.append(items)
                print("\t", table.name, "\t", f"{len(batches)} batches")
                for batch in batches:
                    result = conn.execute(insert(table), batch)
                    print("\t", "\t", f"inserted {result.rowcount} rows")
