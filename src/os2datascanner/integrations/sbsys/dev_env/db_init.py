from sqlalchemy import insert
from sqlalchemy.orm import Session

from os2datascanner.integrations.sbsys.config import get_sbsys_settings
from os2datascanner.integrations.sbsys.db import get_engine, get_tables
from os2datascanner.integrations.sbsys.dev_env.data import SAGS_TILSTAND_OPSLAG, \
    SAGS_STATUS, HIERAKI, HIERAKI_MEDLEM, ADRESSE, ARKIV_AFKLARING_STATUS, \
    ANSAETTELSESSTED, FAG_OMRAADE, BRUGER, SAG

if __name__ == "__main__":
    sbsys_settings = get_sbsys_settings()

    engine = get_engine(
        host=sbsys_settings.sbsys_host,
        port=sbsys_settings.sbsys_port,
        user=sbsys_settings.sbsys_user,
        password=sbsys_settings.sbsys_password,
        database=sbsys_settings.sbsys_database,
    )

    tables = get_tables(engine)

    # Table references for convenience
    SagsTilstandOpslag = tables["SagsTilstandOpslag"]
    SagsStatus = tables["SagsStatus"]
    Hieraki = tables["Hieraki"]
    HierakiMedlem = tables["HierakiMedlem"]
    Adresse = tables["Adresse"]
    ArkivAfklaringStatus = tables["ArkivAfklaringStatus"]
    Ansaettelsessted = tables["Ansaettelsessted"]
    FagOmraade = tables["FagOmraade"]
    Bruger = tables["Bruger"]
    Sag = tables["Sag"]

    with Session(engine) as session:
        # Populate tables
        for table, data in [
                (SagsTilstandOpslag, SAGS_TILSTAND_OPSLAG),
                (SagsStatus, SAGS_STATUS),
                (Hieraki, HIERAKI),  # NOTE misspelled in SBSYS
                (HierakiMedlem, HIERAKI_MEDLEM),  # NOTE misspelled in SBSYS
                (Adresse, ADRESSE),
                (ArkivAfklaringStatus, ARKIV_AFKLARING_STATUS),
                (Ansaettelsessted, ANSAETTELSESSTED),
                (FagOmraade, FAG_OMRAADE),
                (Bruger, BRUGER),
                (Sag, SAG)]:
            print(table.name)
            print("\t", session.execute(insert(table), data))

        session.commit()
