from sqlalchemy import insert
from sqlalchemy.orm import Session

from os2datascanner.engine2.sbsys.config import get_sbsys_settings
from os2datascanner.engine2.sbsys.db import get_engine, get_tables


if __name__ == "__main__":
    sbsys_settings = get_sbsys_settings()

    engine = get_engine(
        host=sbsys_settings.host,
        port=sbsys_settings.port,
        user=sbsys_settings.user,
        password=sbsys_settings.password,
        database=sbsys_settings.database,
    )

    tables = get_tables(engine)

    # Table references for convenience
    SagsTilstandOpslag = tables["SagsTilstandOpslag"]

    with Session(engine) as session:
        # Populate table "SagsTilstandOpslag"
        session.execute(
            insert(SagsTilstandOpslag),
            [
                {"ID": 0, "Navn": "Aktiv"},
                {"ID": 1, "Navn": "Afsluttet"},
            ]
        )

        session.commit()
