from sqlalchemy import insert
from sqlalchemy.orm import Session

from os2datascanner.engine2.sbsys.config import get_sbsys_settings
from os2datascanner.engine2.sbsys.db import get_engine, get_tables
from os2datascanner.engine2.tests.sbsys.data import SAGS_TILSTAND_OPSLAG, \
    SAGS_STATUS, HIERAKI, HIERAKI_MEDLEM, ADRESSE, ARKIV_AFKLARINGS_STATUS

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
    HierakiMedlem = tables["HierakiMedlem"]
    Adresse = tables["Adresse"]
    ArkivAfklaringsStatus = tables["ArkivAfklaringsStatus"]

    with Session(engine) as session:
        # Populate table "SagsTilstandOpslag"
        session.execute(
            insert(SagsTilstandOpslag),
            SAGS_TILSTAND_OPSLAG,
        )

        # Populate table "SagsStatus"
        session.execute(
            insert(SagsStatus),
            SAGS_STATUS,
        )

        # Populate table "Hieraki" (NOTE: "Hierarki" is misspelled in SBSYS)
        session.execute(
            insert(Hieraki),
            HIERAKI,
        )

        # Polulate table "HierakiMedlem" (NOTE: table name is misspelled in SBSYS)
        session.execute(
            insert(HierakiMedlem),
            HIERAKI_MEDLEM,
        )

        # Populate table "Adresse"
        session.execute(
            insert(Adresse),
            ADRESSE,
        )

        # Populate table "ArkivAfklaringsStatus"
        session.execute(
            insert(ArkivAfklaringsStatus),
            ARKIV_AFKLARINGS_STATUS,
        )

        session.commit()
