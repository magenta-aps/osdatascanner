from functools import partial
from sqlalchemy import insert
from sqlalchemy.orm import Session

from os2datascanner.integrations.sbsys.config import get_sbsys_settings
from os2datascanner.integrations.sbsys.db import get_engine, get_tables
from os2datascanner.integrations.sbsys.dev_env.data import databases


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

        with Session(engine) as session:
            for table_name, items in tables.items():
                table = table_map[table_name]
                print("\t", table.name, "\t", f"{len(items)} rows")
                print("\t", "\t", str(session.execute(insert(table), items)))

            session.commit()
