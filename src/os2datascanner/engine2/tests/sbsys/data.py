from copy import copy
from datetime import datetime
from typing import Any


def _update_base_obj(
    base_obj: dict[str, Any],
    updates: dict[str, Any],
) -> dict[str, Any]:
    """
    Update a base table object dict with values new values, e.g.
    we can update the _SAG_BASE dict to a proper SAG dict.

    Args:
        base_obj: the base object to update, e.g. _SAG_BASE
        updates: the values to update
    """

    updated_obj = copy(base_obj)
    updated_obj.update(updates)
    return updated_obj


SAGS_TILSTAND_OPSLAG = [
    {
        "ID": 0,
        "Navn": "Aktiv"
    },
    {
        "ID": 1,
        "Navn": "Afsluttet"
    },
]

SAGS_STATUS = [
    {
        "ID": 1,
        "Navn": "Opklaring",
        "Orden": 2,
        "SagsTilstand": 0,
        "RequireComments": 0,
        "IsDeleted": 0,
        "SagsForklaede": 0
    },
    {
        "ID": 2,
        "Navn": "Afgjort_slettet",
        "Orden": 3,
        "SagsTilstand": 0,
        "RequireComments": 0,
        "IsDeleted": 1,
        "SagsForklaede": 0
    },
    {
        "ID": 3,
        "Navn": "Afventer",
        "Orden": 4,
        "SagsTilstand": 0,
        "RequireComments": 0,
        "IsDeleted": 0,
        "SagsForklaede": 0
    },
    {
        "ID": 4,
        "Navn": "Afsluttet",
        "Orden": 5,
        "SagsTilstand": 1,
        "RequireComments": 0,
        "IsDeleted": 0,
        "SagsForklaede": 2
    },
    {
        "ID": 5,
        "Navn": "Arkiveret",
        "Orden": 6,
        "SagsTilstand": 1,
        "RequireComments": 0,
        "IsDeleted": 0,
        "SagsForklaede": 2
    },
    {
        "ID": 6,
        "Navn": "Afsluttet fra GoPro",
        "Orden": 7,
        "SagsTilstand": 1,
        "RequireComments": 0,
        "IsDeleted": 0,
        "SagsForklaede": 2
    },
    {
        "ID": 7,
        "Navn": "Endeligt_slettet",
        "Orden": 8,
        "SagsTilstand": 1,
        "RequireComments": 0,
        "IsDeleted": 1,
        "SagsForklaede": 2
    },
    {
        "ID": 8,
        "Navn": "Opstået",
        "Orden": 1,
        "SagsTilstand": 0,
        "RequireComments": 0,
        "IsDeleted": 0,
        "SagsForklaede": 0
    },
]

# Misspelled in SBSYS
HIERAKI = [
    {
        "Navn": "Vejstrand Hierarki",
        "Beskrivelse": None,
        "EksternID": None
    }
]

HIERAKI_MEDLEM = [
    {
        "Navn": "Vejstrand Hieraki Medlem",
        "HierakiID": 1,
        "ParentID": None,
        "EksternID": None,
        "SortIndex": None,
    }
]

ADRESSE = [
    {
        "Adresse1": "Paradisæblevej",
        "Adresse2": None,
        "Adresse3": None,
        "Adresse4": None,
        "Adresse5": None,
        "PostNummer": 1000,
        "HusNummer": 13,
        "Etage": None,
        "DoerBetegnelse": None,
        "PostBoks": None,
        "PostDistrikt": None,
        "LandeKode": "DK",
        "ErUdlandsadresse": 0,
        "ErBeskyttet": 0,
        "AdresseIdentity": None,
        "AdgangsAdresseIdentity": None,
    }
]

ARKIV_AFKLARING_STATUS = [
    {
        "ID": 1,
        "Navn": "Mangler bekræftelse",
    },
    {
        "ID": 2,
        "Navn": "Skal arkiveres",
    },
]

ANSAETTELSESSTED = [
    {
        "Navn": "Vejstrand vej-afdeling",
        "CustomAdID": None,
        "Beskrivelse": None,
        "PostAdresseID": 1,
        "FysiskAdresseID": 1,
        "Aabningstider": None,
        "EanNummer": None,
        "Leder": None,
        "CvrNummer": None,
        "PNummer": None,
        "Fritekst1": None,
        "Fritekst2": None,
        "FagomraadeID": None,
        "Indjournaliseringsfolder": None,
        "DefaultEmneplanID": None,
        "HierakiMedlemID": 1,
        "Webside": None,
        "DefaultSagSecuritySetID": None,
        "VisAdgangsListeVedOpretSag": None,
        "TilladBrugerAtSkiftePassword": 1,
        "TilladPublicering": 1,
        "EksterneAdviseringer": 0,
        "AutomatiskErindringVedJournalisering": 1,
        "StandardAktindsigtVedJournalisering": 1,
        "VisCPR": 1,
        "AnsaettelsesstedIdentity": "DB05212B-15FA-4C02-8001-A05D0D45FED8",
        "VisCVR": 1,
    }
]

FAG_OMRAADE = [
    {
        "Navn": "Veje og strande",
        "FagomraadeIdentity": "B14BD0FE-C6E1-450E-942F-80CD8B6DCEE0",
    }
]

BRUGER = [
    {
        "LogonID": 1,
        "LogonPassword": None,
        "LogonSalt": None,
        "LogonAlgorithm": "MD5",
        "LogonIterations": None,
        "LogonFailedAttemptCount": 0,
        "LogonTemporaryLockedExpiration": None,
        "Navn": "Bruce Lee",
        "Titel": None,
        "Stilling": None,
        "KontorID": None,
        "FagomraadeID": 1,
        "Lokale": None,
        "AdresseID": None,
        "AnsaettelsesstedID": 1,
        "Status": 1,
        "EksternID": None,
        "ObjectSid": "S-DIG",
        "UserPrincipalName": "bruce@kungfu.org",
        "BrugerIdentity": "5F079C97-1E85-4205-8489-EC64FA99F81D",
        "ErSystembruger": 0,
    }
]

_SAG_BASE = {
    "SagIdentity": None,
    "Nummer": None,
    "Titel": None,
    "ErBeskyttet": None,
    "Kommentar": None,
    "BevaringID": None,
    "KommuneID": None,
    "BehandlerID": None,
    "SagsStatusID": None,
    "CreatedByID": None,
    "Created": None,
    "LastChangedByID": None,
    "LastChanged": None,
    "YderligereMaterialeFindes": None,
    "YderligereMaterialeBeskrivelse": None,
    "AmtID": None,
    "ErBesluttet": None,
    "Besluttet": None,
    "BeslutningsTypeID": None,
    "BeslutningNotat": None,
    "BeslutningDeadline": None,
    "BeslutningHarDeadline": None,
    "ErSamlesag": None,
    "FagomraadeID": None,
    "SecuritySetID": None,
    "SagsNummerID": None,
    "LastStatusChange": None,
    "LastStatusChangeComments": None,
    "Kassationsdato": None,
    "SagsPartID": None,
    "RegionID": None,
    "KommuneFoer2007ID": None,
    "Opstaaet": None,
    "AnsaettelsesstedID": None,
    "ArkivAfklaringStatusID": None,
    "ArkivNote": None,
    "StyringsreolHyldeID": None,
    "SkabelonID": None,
    "Sletningsdato": None,
}

SAG = [
    _update_base_obj(
        _SAG_BASE,
        {
            "SagIdentity": "2B37AF33-BDFC-4C9B-B332-CAE56310E963",
            "Nummer": "06.13.01-K02-3-13",
            "Titel": "Opsætning af skilte: Skabet til Narnia",
            "ErBeskyttet": 1,
            "BehandlerID": 1,  # Reference to the "Bruger" table
            "SagsStatusID": 8,
            "CreatedByID": 1,
            "Created": datetime(2013, 9, 11),
            "LastChangedByID": 1,
            "LastChanged": datetime(2023, 9, 11),
            "AnsaettelsesstedID": 1,
            "ArkivAfklaringStatusID": 1,
        }
    ),
    _update_base_obj(
        _SAG_BASE,
        {
            "SagIdentity": "EE5BF8A0-D44F-4780-A76A-6E625EF312DA",
            "Nummer": "07.13.01-K02-3-13",
            "Titel": "Eiffel Tower",
            "ErBeskyttet": 1,
            "BehandlerID": 1,  # Reference to the "Bruger" table
            "SagsStatusID": 5,
            "CreatedByID": 1,
            "Created": datetime(2013, 9, 11),
            "LastChangedByID": 1,
            "LastChanged": datetime(2022, 9, 11),
            "AnsaettelsesstedID": 1,
            "ArkivAfklaringStatusID": 1,
        }
    ),
    _update_base_obj(
        _SAG_BASE,
        {
            "SagIdentity": "5A766711-7E0C-4085-8A8B-158ACE9EE087",
            "Nummer": "05.13.01-K02-3-13",
            "Titel": "Den Grimme Ælling",
            "ErBeskyttet": 1,
            "BehandlerID": 1,  # Reference to the "Bruger" table
            "SagsStatusID": 8,
            "CreatedByID": 1,
            "Created": datetime(2013, 9, 11),
            "LastChangedByID": 1,
            "LastChanged": datetime(2022, 9, 11),
            "AnsaettelsesstedID": 1,
            "ArkivAfklaringStatusID": 1,
        }
    ),
]
