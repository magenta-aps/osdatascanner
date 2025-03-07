from datetime import datetime


databases = {
    "SbSysNetDrift": {
        "tables": {}
    },
}
SbSysNetDrift = databases["SbSysNetDrift"]["tables"]


SbSysNetDrift["SagsTilstandOpslag"] = [
    {
        "ID": 0,
        "Navn": "Aktiv"
    },
    {
        "ID": 1,
        "Navn": "Afsluttet"
    },
]

SbSysNetDrift["SagsStatus"] = [
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

_HIERAKI_BASE = {
    "Navn": None,
    "Beskrivelse": None,
    "EksternID": None
}

# Misspelled in SBSYS
SbSysNetDrift["Hieraki"] = [
    _HIERAKI_BASE | {
        "Navn": "Vejstrand Hierarki",
    }
]

_HIERAKI_MEDLEM_BASE = {
    "Navn": None,
    "HierakiID": None,
    "ParentID": None,
    "EksternID": None,
    "SortIndex": None,
}

SbSysNetDrift["HierakiMedlem"] = [
    _HIERAKI_MEDLEM_BASE | {
        "Navn": "Vejstrand Hieraki Medlem",
        "HierakiID": 1,
    }
]

_ADRESSE_BASE = {
    "Adresse1": None,
    "Adresse2": None,
    "Adresse3": None,
    "Adresse4": None,
    "Adresse5": None,
    "PostNummer": None,
    "HusNummer": None,
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


SbSysNetDrift["Adresse"] = [
    _ADRESSE_BASE | {
        "Adresse1": "Paradisæblevej",
        "PostNummer": 1000,
        "HusNummer": 13,
    },
    _ADRESSE_BASE | {
        "Adresse1": "Shaolin Temple",
        "Adresse2": "Dengfeng Boulevard",
        "Adresse3": "Zhengzhou",
        "Adresse4": "Henan",
        "Landekode": "CN",
        "PostNummer": 471925,
        "HusNummer": 1,
    },
]


SbSysNetDrift["ArkivAfklaringStatus"] = [
    {
        "ID": 1,
        "Navn": "Mangler bekræftelse",
    },
    {
        "ID": 2,
        "Navn": "Skal arkiveres",
    },
]

_ANSAETTELSESSTED_BASE = {
    "Navn": None,
    "CustomAdID": None,
    "Beskrivelse": None,
    "PostAdresseID": None,
    "FysiskAdresseID": None,
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
    "HierakiMedlemID": None,
    "Webside": None,
    "DefaultSagSecuritySetID": None,
    "VisAdgangsListeVedOpretSag": None,
    "TilladBrugerAtSkiftePassword": 1,
    "TilladPublicering": 1,
    "EksterneAdviseringer": 0,
    "AutomatiskErindringVedJournalisering": 1,
    "StandardAktindsigtVedJournalisering": 1,
    "VisCPR": 1,
    "AnsaettelsesstedIdentity": None,
    "VisCVR": 1,
}

SbSysNetDrift["Ansaettelsessted"] = [
    _ANSAETTELSESSTED_BASE | {
        "Navn": "Vejstrand vej-afdeling",
        "PostAdresseID": 1,
        "FysiskAdresseID": 1,
        "HierakiMedlemID": 1,
        "AnsaettelsesstedIdentity": "DB05212B-15FA-4C02-8001-A05D0D45FED8",
    }
]

_FAG_OMRAADE_BASE = {
    "Navn": None,
    "FagomraadeIdentity": None,
}

SbSysNetDrift["FagOmraade"] = [
    _FAG_OMRAADE_BASE | {
        "Navn": "Veje og strande",
        "FagomraadeIdentity": "B14BD0FE-C6E1-450E-942F-80CD8B6DCEE0",
    }
]

_BRUGER_BASE = {
    "LogonID": None,
    "LogonPassword": None,
    "LogonSalt": None,
    "LogonAlgorithm": "MD5",
    "LogonIterations": None,
    "LogonFailedAttemptCount": 0,
    "LogonTemporaryLockedExpiration": None,
    "Navn": None,
    "Titel": None,
    "Stilling": None,
    "KontorID": None,
    "FagomraadeID": None,
    "Lokale": None,
    "AdresseID": None,
    "AnsaettelsesstedID": None,
    "Status": None,
    "EksternID": None,
    "ObjectSid": None,
    "UserPrincipalName": None,
    "BrugerIdentity": None,
    "ErSystembruger": 0,
}

SbSysNetDrift["Bruger"] = [
    _BRUGER_BASE | {
        "LogonID": 1,
        "Navn": "Bruce Lee",
        "FagomraadeID": 1,
        "AdresseID": 2,
        "AnsaettelsesstedID": 1,
        "Status": 1,
        "ObjectSid": "S-DIG",
        "UserPrincipalName": "bruce@kungfu.org",
        "BrugerIdentity": "5F079C97-1E85-4205-8489-EC64FA99F81D",
    },
    _BRUGER_BASE | {
        "LogonID": 2,
        "Navn": "Jan Kowalski",
        "FagomraadeID": 1,
        "AdresseID": 1,
        "AnsaettelsesstedID": 1,
        "Status": 1,
        "ObjectSID": "S-CYF",
        "UserPrincipalName": "jkowalski@vstkom.internal",
        "BrugerIdentity": "69131057-FA37-4EE0-A79F-D8A5EF879CB6",
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

SbSysNetDrift["Sag"] = [
    _SAG_BASE | {
        "SagIdentity": "2B37AF33-BDFC-4C9B-B332-CAE56310E963",
        "Nummer": "06.13.01-K02-3-13",
        "Titel": "Opsætning af skilte: Skabet til Narnia",
        "ErBeskyttet": 1,
        "BehandlerID": 1,  # Reference to the "Bruger" table
        "Kommentar": "Flere borgere er forvirret over, at rådhusets garderobe"
                     " huser en magisk portal til en anden verden -- nogen er"
                     " endda kommet til skade derinde. Den Hvide Heks på"
                     " portalens anden side er også mistænkt for flere"
                     " databrud samt læk af personfølsomme informationer. Vi "
                     " skal derfor få skiltet fænomenet for at undgå bøde.",
        "SagsStatusID": 8,
        "CreatedByID": 1,
        "Created": datetime(2013, 9, 11),
        "LastChangedByID": 1,
        "LastChanged": datetime(2023, 9, 11),
        "AnsaettelsesstedID": 1,
        "ArkivAfklaringStatusID": 1,
    },
    _SAG_BASE | {
        "SagIdentity": "EE5BF8A0-D44F-4780-A76A-6E625EF312DA",
        "Nummer": "07.13.01-K02-3-13",
        "Titel": "Eiffel Tower",
        "ErBeskyttet": 1,
        "BehandlerID": 1,  # Reference to the "Bruger" table
        "Kommentar": "En lille fransk kommune har fået kontakt til os og"
                     " spørger, om vi kunne være interesseret i at erhverve et"
                     " ældgammelt industrielt kunstværk fra 1880'erne.",
        "SagsStatusID": 5,
        "CreatedByID": 1,
        "Created": datetime(2013, 9, 11),
        "LastChangedByID": 1,
        "LastChanged": datetime(2022, 9, 11),
        "AnsaettelsesstedID": 1,
        "ArkivAfklaringStatusID": 1,
    },
    _SAG_BASE | {
        "SagIdentity": "5A766711-7E0C-4085-8A8B-158ACE9EE087",
        "Nummer": "05.13.01-K02-3-13",
        "Titel": "Den Grimme Ælling",
        "ErBeskyttet": 1,
        "BehandlerID": 1,  # Reference to the "Bruger" table
        "Kommentar": "En ikke-menneskelig borger har ansøgt om at få penge "
                     "til plastikkirurgi fra kommunens pulje til borgernes "
                     " almene trivsel.",
        "SagsStatusID": 8,
        "CreatedByID": 1,
        "Created": datetime(2013, 9, 11),
        "LastChangedByID": 1,
        "LastChanged": datetime(2022, 9, 11),
        "AnsaettelsesstedID": 1,
        "ArkivAfklaringStatusID": 1,
    },
    _SAG_BASE | {
        "SagIdentity": "6DB35330-CDC3-41E9-A498-67127B205BCF",
        "Nummer": "22.13.01-K02-3-13",
        "Titel": "Personfølsomme Informationer",
        "ErBeskyttet": 1,
        "BehandlerID": 1,  # Reference to the "Bruger" table
        "Kommentar": "Borgeren Rebecca Testsen har bedt os om at opbevare sit"
                     " CPR-nummer (111111-1118) på sikker vis.",
        "SagsStatusID": 8,
        "CreatedByID": 1,
        "Created": datetime(2015, 4, 21),
        "LastChangedByID": 1,
        "LastChanged": datetime(2015, 4, 22),
        "AnsaettelsesstedID": 1,
        "ArkivAfklaringStatusID": 1,
    },
]

# --

databases["SbSysNetDriftDokument0000"] = (_dr := {"tables": {}})
SbSysNetDriftDokument0000 = _dr["tables"]

with open("1111111118.pdf", "rb") as fp:
    SbSysNetDriftDokument0000["DokumentData"] = [
        {
            "ID": 16240,
            "DokumentID": 1274,
            "DokumentDataInfoID": 1331,
            "Data": fp.read()
        }
    ]


SbSysNetDrift["DokumentDataInfoTypeOpslag"] = [
    # Taken from the production environment
    {
        "ID": 0,
        "Navn": "Attachment"
    },
    {
        "ID": 1,
        "Navn": "Mail body"
    },
    {
        "ID": 2,
        "Navn": "Unspecified"
    },
    {
        "ID": 3,
        "Navn": "Alternate"
    },
    {
        "ID": 4,
        "Navn": "Mailbody resource"
    },
    {
        "ID": 5,
        "Navn": "UnspecifiedSubDocument"
    },
    {
        "ID": 6,
        "Navn": "Email"
    }
]


SbSysNetDrift["DokumentDataTypeOpslag"] = [
    # Taken from the production environment
    {
        "ID": 0,
        "Navn": "Ukendt"
    },
    {
        "ID": 1,
        "Navn": "Microsoft Word"
    },
    {
        "ID": 2,
        "Navn": "Microsoft Excel"
    },
    {
        "ID": 3,
        "Navn": "Microsoft PowerPoint"
    },
    {
        "ID": 4,
        "Navn": "Tekst"
    },
    {
        "ID": 5,
        "Navn": "RTF"
    },
    {
        "ID": 6,
        "Navn": "PDF"
    },
    {
        "ID": 7,
        "Navn": "Billede"
    },
    {
        "ID": 8,
        "Navn": "Film Klip"
    },
    {
        "ID": 9,
        "Navn": "Lyd"
    },
    {
        "ID": 10,
        "Navn": "HTML"
    },
    {
        "ID": 11,
        "Navn": "Email"
    }
]


SbSysNetDrift["DokumentArtOpslag"] = [
    # Taken from the production environment
    {
        "ID": 1,
        "Navn": "Indg\u00e5ende",
        "UbeskyttetStandardMarkering": True,
        "MaaPubliseresPaaDagsorden": True,
        "UbeskyttetTilladAendring": True,
        "SagBeskyttetStandardMarkering": False,
        "SagBeskyttetTilladAendring": False,
        "DokumentBeskyttetStandardMarkering": False,
        "DokumentBeskyttetTilladAendring": False,
        "SagOgDokumentBeskyttetStandardMarkering": False,
        "SagOgDokumentBeskyttetTilladAendring": False,
        "DokumentArtIdentifier": "0fd9387b-a0ed-4340-b466-5f0451bd67bc"
    },
    {
        "ID": 2,
        "Navn": "Udg\u00e5ende",
        "UbeskyttetStandardMarkering": True,
        "MaaPubliseresPaaDagsorden": True,
        "UbeskyttetTilladAendring": True,
        "SagBeskyttetStandardMarkering": False,
        "SagBeskyttetTilladAendring": False,
        "DokumentBeskyttetStandardMarkering": False,
        "DokumentBeskyttetTilladAendring": False,
        "SagOgDokumentBeskyttetStandardMarkering": False,
        "SagOgDokumentBeskyttetTilladAendring": False,
        "DokumentArtIdentifier": "6744e1ff-c166-4e61-a1db-ab7b6dbf0f35"
    },
    {
        "ID": 3,
        "Navn": "Internt",
        "UbeskyttetStandardMarkering": False,
        "MaaPubliseresPaaDagsorden": True,
        "UbeskyttetTilladAendring": True,
        "SagBeskyttetStandardMarkering": False,
        "SagBeskyttetTilladAendring": False,
        "DokumentBeskyttetStandardMarkering": True,
        "DokumentBeskyttetTilladAendring": False,
        "SagOgDokumentBeskyttetStandardMarkering": False,
        "SagOgDokumentBeskyttetTilladAendring": False,
        "DokumentArtIdentifier": "4f1403a3-c55f-4d9f-bc1e-1e14dfd32bce"
    },
    {
        "ID": 5,
        "Navn": "Notat",
        "UbeskyttetStandardMarkering": True,
        "MaaPubliseresPaaDagsorden": True,
        "UbeskyttetTilladAendring": True,
        "SagBeskyttetStandardMarkering": False,
        "SagBeskyttetTilladAendring": False,
        "DokumentBeskyttetStandardMarkering": False,
        "DokumentBeskyttetTilladAendring": False,
        "SagOgDokumentBeskyttetStandardMarkering": False,
        "SagOgDokumentBeskyttetTilladAendring": False,
        "DokumentArtIdentifier": "6ddc6599-2e94-44cd-814e-4a4974ad7c98"
    },
    {
        "ID": 6,
        "Navn": "Andet",
        "UbeskyttetStandardMarkering": True,
        "MaaPubliseresPaaDagsorden": True,
        "UbeskyttetTilladAendring": True,
        "SagBeskyttetStandardMarkering": False,
        "SagBeskyttetTilladAendring": False,
        "DokumentBeskyttetStandardMarkering": False,
        "DokumentBeskyttetTilladAendring": False,
        "SagOgDokumentBeskyttetStandardMarkering": False,
        "SagOgDokumentBeskyttetTilladAendring": False,
        "DokumentArtIdentifier": "ef9ebdb7-fd93-4d86-a3c4-edc9fc93ecf5"
    },
    {
        "ID": 7,
        "Navn": "Dagsordenpunkt",
        "UbeskyttetStandardMarkering": True,
        "MaaPubliseresPaaDagsorden": True,
        "UbeskyttetTilladAendring": True,
        "SagBeskyttetStandardMarkering": False,
        "SagBeskyttetTilladAendring": False,
        "DokumentBeskyttetStandardMarkering": False,
        "DokumentBeskyttetTilladAendring": False,
        "SagOgDokumentBeskyttetStandardMarkering": False,
        "SagOgDokumentBeskyttetTilladAendring": False,
        "DokumentArtIdentifier": "60e72338-db2b-4409-8a5a-a5551c740f94"
    },
    {
        "ID": 8,
        "Navn": "Skema",
        "UbeskyttetStandardMarkering": True,
        "MaaPubliseresPaaDagsorden": True,
        "UbeskyttetTilladAendring": True,
        "SagBeskyttetStandardMarkering": False,
        "SagBeskyttetTilladAendring": False,
        "DokumentBeskyttetStandardMarkering": False,
        "DokumentBeskyttetTilladAendring": False,
        "SagOgDokumentBeskyttetStandardMarkering": False,
        "SagOgDokumentBeskyttetTilladAendring": False,
        "DokumentArtIdentifier": "af5803d3-59e6-43ae-ba05-688df08a50e1"
    },
    {
        "ID": 9,
        "Navn": "Rapport",
        "UbeskyttetStandardMarkering": True,
        "MaaPubliseresPaaDagsorden": True,
        "UbeskyttetTilladAendring": True,
        "SagBeskyttetStandardMarkering": False,
        "SagBeskyttetTilladAendring": False,
        "DokumentBeskyttetStandardMarkering": False,
        "DokumentBeskyttetTilladAendring": False,
        "SagOgDokumentBeskyttetStandardMarkering": False,
        "SagOgDokumentBeskyttetTilladAendring": False,
        "DokumentArtIdentifier": "cd91e596-e834-4ce7-b0f7-c9d27d06cf09"
    },
    {
        "ID": 10,
        "Navn": "Kontrakt",
        "UbeskyttetStandardMarkering": True,
        "MaaPubliseresPaaDagsorden": True,
        "UbeskyttetTilladAendring": True,
        "SagBeskyttetStandardMarkering": False,
        "SagBeskyttetTilladAendring": False,
        "DokumentBeskyttetStandardMarkering": False,
        "DokumentBeskyttetTilladAendring": False,
        "SagOgDokumentBeskyttetStandardMarkering": False,
        "SagOgDokumentBeskyttetTilladAendring": False,
        "DokumentArtIdentifier": "8176c171-3344-4201-80c6-344f8dd50901"
    },
    {
        "ID": 11,
        "Navn": "Dagsorden",
        "UbeskyttetStandardMarkering": True,
        "MaaPubliseresPaaDagsorden": True,
        "UbeskyttetTilladAendring": True,
        "SagBeskyttetStandardMarkering": False,
        "SagBeskyttetTilladAendring": False,
        "DokumentBeskyttetStandardMarkering": False,
        "DokumentBeskyttetTilladAendring": False,
        "SagOgDokumentBeskyttetStandardMarkering": False,
        "SagOgDokumentBeskyttetTilladAendring": False,
        "DokumentArtIdentifier": "4b5dbc1a-b0ee-4f5b-839e-140ac588c8a4"
    },
    {
        "ID": 12,
        "Navn": "Referat",
        "UbeskyttetStandardMarkering": True,
        "MaaPubliseresPaaDagsorden": True,
        "UbeskyttetTilladAendring": True,
        "SagBeskyttetStandardMarkering": False,
        "SagBeskyttetTilladAendring": False,
        "DokumentBeskyttetStandardMarkering": False,
        "DokumentBeskyttetTilladAendring": False,
        "SagOgDokumentBeskyttetStandardMarkering": False,
        "SagOgDokumentBeskyttetTilladAendring": False,
        "DokumentArtIdentifier": "4287cfcf-4e8f-4432-b88a-ade5618fca2c"
    },
    {
        "ID": 13,
        "Navn": "Brev",
        "UbeskyttetStandardMarkering": True,
        "MaaPubliseresPaaDagsorden": True,
        "UbeskyttetTilladAendring": True,
        "SagBeskyttetStandardMarkering": False,
        "SagBeskyttetTilladAendring": False,
        "DokumentBeskyttetStandardMarkering": False,
        "DokumentBeskyttetTilladAendring": False,
        "SagOgDokumentBeskyttetStandardMarkering": False,
        "SagOgDokumentBeskyttetTilladAendring": False,
        "DokumentArtIdentifier": "3ae1a8e9-d47d-43f1-a643-ae95e4f74243"
    },
    {
        "ID": 15,
        "Navn": "Foto",
        "UbeskyttetStandardMarkering": True,
        "MaaPubliseresPaaDagsorden": True,
        "UbeskyttetTilladAendring": True,
        "SagBeskyttetStandardMarkering": False,
        "SagBeskyttetTilladAendring": False,
        "DokumentBeskyttetStandardMarkering": False,
        "DokumentBeskyttetTilladAendring": False,
        "SagOgDokumentBeskyttetStandardMarkering": False,
        "SagOgDokumentBeskyttetTilladAendring": False,
        "DokumentArtIdentifier": "cacb925c-be6f-4480-bd53-9e29369b7eae"
    }
]


SbSysNetDrift["DokumentTypeOpslag"] = [
    # Taken from the production environment
    {
        "ID": 0,
        "Navn": "Uspecificeret",
        "DefaultDokumentArtID": 6
    },
    {
        "ID": 1,
        "Navn": "Sbsys.Net dokument",
        "DefaultDokumentArtID": 6
    },
    {
        "ID": 2,
        "Navn": "Journaliseret via scanner",
        "DefaultDokumentArtID": 6
    },
    {
        "ID": 3,
        "Navn": "Journaliseret fra fil",
        "DefaultDokumentArtID": 6
    },
    {
        "ID": 4,
        "Navn": "Papir dokument",
        "DefaultDokumentArtID": 6
    },
    {
        "ID": 5,
        "Navn": "Journaliseret email",
        "DefaultDokumentArtID": 1
    },
    {
        "ID": 6,
        "Navn": "Notat",
        "DefaultDokumentArtID": 5
    },
    {
        "ID": 7,
        "Navn": "Journaliseret digitalpost",
        "DefaultDokumentArtID": 1
    }
]


SbSysNetDrift["ProcessStatusOpslag"] = [
    # Taken from the production environment
    {
        "ID": 0,
        "Navn": "Skal ikke konverteres"
    },
    {
        "ID": 1,
        "Navn": "Skal konverteres"
    },
    {
        "ID": 2,
        "Navn": "Konvertering færdig"
    },
    {
        "ID": 3,
        "Navn": "Konvertering fejlede"
    },
    {
        "ID": 4,
        "Navn": "Konverteres lige nu"
    },
    {
        "ID": 5,
        "Navn": "Skal genkonverteres"
    },
    {
        "ID": 6,
        "Navn": "Genprocesseres"
    }
]
