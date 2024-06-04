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
