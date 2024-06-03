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
    SagsStatus = tables["SagsStatus"]
    Hieraki = tables["Hieraki"]

    with Session(engine) as session:
        # Populate table "SagsTilstandOpslag"
        session.execute(
            insert(SagsTilstandOpslag),
            [
                {"ID": 0, "Navn": "Aktiv"},
                {"ID": 1, "Navn": "Afsluttet"},
            ]
        )

        # Populate table "SagsStatus"
        session.execute(
            insert(SagsStatus),
            [
                {
                    "ID": 1, "Navn": "Opklaring", "Orden": 2, "SagsTilstand": 0,
                    "RequireComments": 0, "IsDeleted": 0, "SagsForklaede": 0
                },
                {
                    "ID": 2, "Navn": "Afgjort_slettet", "Orden": 3, "SagsTilstand": 0,
                    "RequireComments": 0, "IsDeleted": 1, "SagsForklaede": 0
                },
                {
                    "ID": 3, "Navn": "Afventer", "Orden": 4, "SagsTilstand": 0,
                    "RequireComments": 0, "IsDeleted": 0, "SagsForklaede": 0
                },
                {
                    "ID": 4, "Navn": "Afsluttet", "Orden": 5, "SagsTilstand": 1,
                    "RequireComments": 0, "IsDeleted": 0, "SagsForklaede": 2
                },
                {
                    "ID": 5, "Navn": "Arkiveret", "Orden": 6, "SagsTilstand": 1,
                    "RequireComments": 0, "IsDeleted": 0, "SagsForklaede": 2
                },
                {
                    "ID": 6, "Navn": "Afsluttet fra GoPro", "Orden": 7, "SagsTilstand": 1,
                    "RequireComments": 0, "IsDeleted": 0, "SagsForklaede": 2
                },
                {
                    "ID": 7, "Navn": "Endeligt_slettet", "Orden": 8, "SagsTilstand": 1,
                    "RequireComments": 0, "IsDeleted": 1, "SagsForklaede": 2
                },
                {
                    "ID": 8, "Navn": "Opstået", "Orden": 1, "SagsTilstand": 0,
                    "RequireComments": 0, "IsDeleted": 0, "SagsForklaede": 0
                },
            ]
        )

        # Populate table "Hieraki" (NOTE: "Hierarki" is misspelled in SBSYS)
        session.execute(
            insert(Hieraki),
            {"Navn": "Vejstrand Hierarki", "Beskrivelse": None, "EksternID": None}
        )

        session.commit()
