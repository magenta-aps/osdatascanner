# flake8: noqa
# autopep8: off

# This file was derived automatically from our SBSYS test database at
# 2026-03-06 11:01:01+0100 by the following command:
#
# sqlacodegen mssql+pymssql://sa:ub3rStr0nGpassword@localhost:7777/SbSysNetDrift --generator tables
#
# --
#
# Using this prebaked representation of the structure of the SBSYS database
# reduces the typical startup time of a SBSYS database connection with access
# to all tables to less than one one-hundredth of a second. (Using runtime
# introspection to build this structure usually takes at least a minute.)
#
# A few warnings for you:
#
# - if the target SBSYS database's structure diverges too much from these
#   definitions, OSdatascanner may make database queries that do not make
#   sense; set the "model.sbsysdb.force_reflection" setting to true to work
#   around this
# - if the SBSYS database's structure changes (for example, through updates to
#   docker/sbsys/*.sql), you /must/ regenerate this file (remember to copy and
#   update this comment block!)

from sqlalchemy import BigInteger, Boolean, CHAR, Column, DateTime, Float, ForeignKeyConstraint, Identity, Index, Integer, LargeBinary, MetaData, NCHAR, PrimaryKeyConstraint, SmallInteger, String, TEXT, Table, Unicode, Uuid, text
from sqlalchemy.dialects.mssql import DATETIME2, DATETIMEOFFSET, IMAGE, NTEXT, TIMESTAMP, TINYINT

metadata = MetaData()


t_AdministrativProfil = Table(
    'AdministrativProfil', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Kontekst', Integer, nullable=False),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_AdministrativProfil')
)

t_Adresse = Table(
    'Adresse', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Adresse1', Unicode(75, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Adresse2', Unicode(75, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Adresse3', Unicode(75, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Adresse4', Unicode(75, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Adresse5', Unicode(75, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('PostNummer', Integer),
    Column('Bynavn', Unicode(80, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('HusNummer', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Etage', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DoerBetegnelse', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('BygningsNummer', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Postboks', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('PostDistrikt', Unicode(80, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('LandeKode', Unicode(3, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ErUdlandsadresse', Boolean),
    Column('ErBeskyttet', Boolean, nullable=False, server_default=text('((0))')),
    Column('AdresseIdentity', Uuid, server_default=text('(NULL)')),
    Column('AdgangsAdresseIdentity', Uuid, server_default=text('(NULL)')),
    PrimaryKeyConstraint('ID', name='PK_tblAdresser'),
    Index('IX_Adresse', 'Adresse1', mssql_clustered=False, mssql_include=['Etage', 'DoerBetegnelse']),
    Index('IX_Adresse_Bynavn', 'Bynavn', mssql_clustered=False)
)

t_AdresseItem = Table(
    'AdresseItem', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('AdresseID', Integer, nullable=False),
    Column('AdresseItemType', TINYINT, nullable=False),
    Column('AdresseItemContext', TINYINT, nullable=False),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    PrimaryKeyConstraint('ID', name='PK_AdresseItem'),
    Index('IX_AdresseItem', 'AdresseID', mssql_clustered=True)
)

t_AmtOpslag = Table(
    'AmtOpslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Nummer', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_Amt')
)

t_AnsaettelsesstedTrustedAssembly = Table(
    'AnsaettelsesstedTrustedAssembly', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('AnsaettelsesstedID', Integer, nullable=False),
    Column('TrustedAssemblyID', Integer, nullable=False)
)

t_ArkivAfklaringStatus = Table(
    'ArkivAfklaringStatus', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    PrimaryKeyConstraint('ID', name='PK_Table1')
)

t_ArkivPeriodeStatus = Table(
    'ArkivPeriodeStatus', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_ArkivPeriodeStatus')
)

t_BeskedfordelingHandledByOpslag = Table(
    'BeskedfordelingHandledByOpslag', metadata,
    Column('Id', Integer, primary_key=True),
    Column('Navn', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('Id', name='PK__Beskedfo__3214EC07DBC04750')
)

t_BeslutningsTypeGruppe = Table(
    'BeslutningsTypeGruppe', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    PrimaryKeyConstraint('ID', name='PK_AfgoeringTypeGruppe')
)

t_BevaringOpslag = Table(
    'BevaringOpslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Kode', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Dage', Integer),
    Column('KassationsBeregning', Integer, nullable=False, server_default=text('((1))')),
    PrimaryKeyConstraint('ID', name='PK_Kassation'),
    Index('IX_Bevaring_Kode', 'Kode', mssql_clustered=False, unique=True)
)

t_Branche = Table(
    'Branche', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Nummer', Integer, nullable=False),
    Column('Navn', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_Branche'),
    Index('IX_Branche_Nummer', 'Nummer', mssql_clustered=False, unique=True)
)

t_BrugerGruppe = Table(
    'BrugerGruppe', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(75, 'SQL_Danish_Pref_CP1_CI_AS')),
    PrimaryKeyConstraint('ID', name='PK_tblBrugerGruppe')
)

t_BrugerSettingsEmailKontoRegistrering_BACKUP_20220923 = Table(
    'BrugerSettingsEmailKontoRegistrering_BACKUP_20220923', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerSettingsID', Integer, nullable=False),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('AccountName', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ServerName', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DatabaseName', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DomainName', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Password', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('BrugernavnEqualsPostkasse', Boolean),
    Column('EntryID', Unicode(600, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('StoreID', Unicode(600, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('UseSavedPassword', Boolean),
    Column('MailSystemTag', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('PasswordOnCreation', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('VistSessionNavn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('EmailKontoExchangeConfigurationId', Integer)
)

t_CivilstandOpslag = Table(
    'CivilstandOpslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Kode', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    PrimaryKeyConstraint('ID', name='PK_Civilstand')
)

t_CompatibleVersions = Table(
    'CompatibleVersions', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SbsysDatabaseVersion', String(20, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('SbsysClientVersion', String(20, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_CompatibleVersions'),
    Index('IX_CompatibleVersions_Composite', 'SbsysDatabaseVersion', 'SbsysClientVersion', mssql_clustered=False)
)

t_CprBrokerConfiguration = Table(
    'CprBrokerConfiguration', metadata,
    Column('Token', Unicode(36, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ApplicationName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False)
)

t_DagsordenpunktFeltType = Table(
    'DagsordenpunktFeltType', metadata,
    Column('ID', Integer, primary_key=True),
    Column('Navn', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_DagsordenpunktFeltType')
)

t_DagsordenpunktStandardText = Table(
    'DagsordenpunktStandardText', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Label', CHAR(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Text', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    PrimaryKeyConstraint('ID', name='PK_DagsordenpunktStandardText')
)

t_DagsordenpunktStandardTextAnsaettelsessted = Table(
    'DagsordenpunktStandardTextAnsaettelsessted', metadata,
    Column('DagsordenpunktStandardTextID', Integer, nullable=False),
    Column('AnsaettelsesstedID', Integer, nullable=False)
)

t_DagsordenpunktType = Table(
    'DagsordenpunktType', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Sortering', Integer, nullable=False),
    Column('Aktiv', Boolean, nullable=False),
    Column('Beskrivelse', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    PrimaryKeyConstraint('ID', name='PK__Dagsordenpunktty__76432E21')
)

t_DagsordenpunktsBehandlingDokumentBackup = Table(
    'DagsordenpunktsBehandlingDokumentBackup', metadata,
    Column('DagsordenpunktId', Integer),
    Column('TilbagejournaliseretDokumentID', Integer)
)

t_DelforloebTypeGruppe = Table(
    'DelforloebTypeGruppe', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_SagsTypeGruppe')
)

t_DocumentProcesseringHistorik = Table(
    'DocumentProcesseringHistorik', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('InputDokumentID', Integer, nullable=False),
    Column('InputDokumentDataInfoID', Integer, nullable=False),
    Column('OutputDokumentDataInfoID', Integer),
    Column('Action', TINYINT, nullable=False),
    Column('Queued', DateTime, nullable=False),
    Column('LastAttemptStart', DateTime),
    Column('LastAttemptEnd', DateTime),
    Column('LastAttemptDurationSeconds', BigInteger),
    Column('TotalDurationSeconds', BigInteger, nullable=False, server_default=text('((5))')),
    Column('ProcessedOnMachine', Unicode(150, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('AttemptCount', Integer, server_default=text('((1))')),
    Column('Message', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), server_default=text("('Færdig processeret')")),
    PrimaryKeyConstraint('ID', name='PK_DocumentProcesseringHistorik'),
    Index('IX_DocumentProcesseringHistorik_InputDokumentDataInfoID', 'InputDokumentDataInfoID', mssql_clustered=False),
    Index('IX_DocumentProcesseringHistorik_InputDokumentID', 'InputDokumentID', mssql_clustered=False)
)

t_DokImport = Table(
    'DokImport', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Beskrivelse', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Navn', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OprettetDato', DateTime),
    Column('OprettetAfID', String(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OprettetAfNavn', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DokumentArtNavn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DokumentArt', Integer),
    Column('DokumentType', Integer),
    Column('Modtager', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Filnavn', Unicode(1000, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('FilEkstension', Unicode(30, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ImportStiOgFilnavn', Unicode(1000, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Adresse', Unicode(400, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SagID', Integer),
    Column('AmtsSagID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DokumentGuid', String(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Laast', Boolean),
    Column('Aaben', Boolean),
    Column('YderligereMaterialeBeskrivelse', Unicode(400, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('YderligereMaterialeFindes', Boolean),
    Column('PartNo', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('JournalPostID', Integer),
    Column('Delforloeb', Unicode(254, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('PrimaryDokument', Boolean),
    Column('FilSomBlob', Boolean),
    Column('ErKladde', Boolean),
    Column('KladdeVersion', Integer),
    Column('SenestOpdateretDato', DateTime),
    Column('SenestOpdateretAfID', String(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OmfattetAfAktindsigt', Boolean),
    PrimaryKeyConstraint('ID', name='PK_DokImport'),
    Index('_dta_index_DokImport_JournalPostID2_til_konvertering', 'JournalPostID', mssql_clustered=False, mssql_include=['Filnavn', 'FilEkstension', 'DokumentGuid', 'PrimaryDokument']),
    Index('_dta_index_DokImport_JournalPostID_til_konvertering', 'JournalPostID', mssql_clustered=False, mssql_include=['Filnavn', 'PrimaryDokument'])
)

t_Dokument = Table(
    'Dokument', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DokumentArtID', Integer, nullable=False),
    Column('Beskrivelse', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OprettetAfID', Integer, nullable=False),
    Column('Oprettet', DateTime, nullable=False),
    Column('DokumentType', Integer, nullable=False),
    Column('ProcessStatus', Integer, nullable=False, server_default=text('((0))')),
    Column('YderligereMaterialeFindes', Boolean),
    Column('YderligereMaterialeBeskrivelse', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('MailID', Integer),
    Column('ParentDokumentID', Integer),
    Column('Navn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('IsImported', Boolean, nullable=False, server_default=text('((0))')),
    Column('PaaPostliste', Boolean, nullable=False, server_default=text('((0))')),
    Column('PostlisteTitel', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('PostlisteBeskrivelse', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ProcessPostAction', Integer, nullable=False, server_default=text('((0))')),
    Column('ImporteretFraKnownEksternSystemID', Integer),
    Column('EksternId', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('IsParent', Boolean, nullable=False, server_default=text('((0))')),
    Column('IsComposite', Boolean, nullable=False, server_default=text('((0))')),
    Column('PrintDate', DateTime),
    Column('PrimaryDokumentDataInfoID', Integer),
    Column('DeletedState', TINYINT, nullable=False, server_default=text('((0))')),
    Column('DeletedDate', DateTime),
    Column('DeletedByID', Integer),
    Column('DeletedReason', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DeleteConfirmed', DateTime),
    Column('DeleteConfirmedByID', Integer),
    Column('OmfattetAfAktindsigt', Boolean, nullable=False, server_default=text('((1))')),
    Column('AktindsigtKommentar', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS')),
    Column('DokumentIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    Column('StatusTekst', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('FraKladdeID', Integer),
    ForeignKeyConstraint(['DeletedByID'], ['Bruger.ID'], name='FK_Dokument_DeletedByBruger'),
    ForeignKeyConstraint(['DokumentArtID'], ['DokumentArtOpslag.ID'], name='Dokument_DokumentArt'),
    ForeignKeyConstraint(['DokumentType'], ['DokumentTypeOpslag.ID'], name='Dokument_DokumentType'),
    ForeignKeyConstraint(['MailID'], ['Mail.ID'], name='Dokument_Mail'),
    ForeignKeyConstraint(['OprettetAfID'], ['Bruger.ID'], name='Dokument_OprettetAfBruger'),
    ForeignKeyConstraint(['ParentDokumentID'], ['Dokument.ID'], name='Dokument_ParentDokument'),
    ForeignKeyConstraint(['PrimaryDokumentDataInfoID'], ['DokumentDataInfo.ID'], name='FK_Dokument_DokumentDataInfo_Primary'),
    ForeignKeyConstraint(['ProcessStatus'], ['ProcessStatusOpslag.ID'], name='FK_Dokument_ProcessStatusOpslag'),
    PrimaryKeyConstraint('ID', name='PK_Dokument'),
    Index('IX_Dokument', 'ID', 'DokumentType', mssql_clustered=True, unique=True),
    Index('IX_Dokument_EksternID', 'EksternId', mssql_clustered=False),
    Index('IX_Dokument_ParentDokumentID', 'ParentDokumentID', mssql_clustered=False, mssql_include=['ID']),
    Index('IX_Dokument_ProcessStatus', 'ProcessStatus', mssql_clustered=False),
    Index('IX_Dokument_ProcessStatus_ProcessPostAction', 'ProcessStatus', 'ProcessPostAction', mssql_clustered=False, mssql_include=['DokumentArtID', 'Beskrivelse', 'OprettetAfID', 'Oprettet', 'DokumentType', 'YderligereMaterialeFindes', 'YderligereMaterialeBeskrivelse', 'MailID', 'ParentDokumentID', 'Navn', 'IsImported', 'PaaPostliste', 'PostlisteTitel', 'PostlisteBeskrivelse', 'ImporteretFraKnownEksternSystemID', 'EksternId', 'IsParent', 'IsComposite', 'PrintDate', 'PrimaryDokumentDataInfoID', 'DeletedState', 'DeletedDate', 'DeletedByID', 'DeletedReason', 'DeleteConfirmed', 'DeleteConfirmedByID', 'OmfattetAfAktindsigt', 'AktindsigtKommentar', 'DokumentIdentity', 'StatusTekst']),
    Index('UQ__Dokument__9CA51E69C396ADD9', 'DokumentIdentity', mssql_clustered=False, unique=True)
)

t_DokumentArtOpslag = Table(
    'DokumentArtOpslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('UbeskyttetStandardMarkering', Boolean, nullable=False, server_default=text('((1))')),
    Column('MaaPubliseresPaaDagsorden', Boolean, nullable=False, server_default=text('((1))')),
    Column('UbeskyttetTilladAendring', Boolean, nullable=False, server_default=text('((1))')),
    Column('SagBeskyttetStandardMarkering', Boolean, nullable=False, server_default=text('((0))')),
    Column('SagBeskyttetTilladAendring', Boolean, nullable=False, server_default=text('((0))')),
    Column('DokumentBeskyttetStandardMarkering', Boolean, nullable=False, server_default=text('((0))')),
    Column('DokumentBeskyttetTilladAendring', Boolean, nullable=False, server_default=text('((0))')),
    Column('SagOgDokumentBeskyttetStandardMarkering', Boolean, nullable=False, server_default=text('((0))')),
    Column('SagOgDokumentBeskyttetTilladAendring', Boolean, nullable=False, server_default=text('((0))')),
    Column('DokumentArtIdentifier', Uuid, nullable=False, server_default=text('(newid())')),
    PrimaryKeyConstraint('ID', name='PK_DokumentArt'),
    Index('UQ__Dokument__5531AA63CF3383CD', 'DokumentArtIdentifier', mssql_clustered=False, unique=True)
)

t_DokumentBoksWebserviceQueue = Table(
    'DokumentBoksWebserviceQueue', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('CreatedDate', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('HandleAfterDate', DateTime, nullable=False),
    Column('QueueType', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('QueueData', IMAGE, nullable=False),
    Column('ContextSagID', Integer),
    Column('ModtagerNoegle', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('PostkasseNavn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SporGUID', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('AfsenderID', Integer, nullable=False, server_default=text('((0))')),
    PrimaryKeyConstraint('ID', name='PK_DokumentBoksWebserviceQueue')
)

t_DokumentDataInfo = Table(
    'DokumentDataInfo', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DokumentID', Integer, nullable=False),
    Column('DokumentDataType', Integer, nullable=False),
    Column('Rank', Integer),
    Column('FileName', Unicode(1000, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('FileExtension', Unicode(30, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('FilePath', Unicode(1000, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('FileSize', BigInteger, nullable=False, server_default=text('((0))')),
    Column('FileLastAccessed', DateTime),
    Column('FileCreated', DateTime),
    Column('FileAttributes', Integer),
    Column('DokumentDataInfoType', Integer, nullable=False),
    Column('Keywords', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('HasSnapshot', Boolean, nullable=False, server_default=text('((0))')),
    Column('HasThumbnail', Boolean, nullable=False, server_default=text('((0))')),
    Column('ThumbnailID', Integer),
    Column('IndexingStatus', TINYINT, nullable=False, server_default=text('((1))')),
    Column('AlternateOfID', Integer),
    Column('OCRStatus', TINYINT, nullable=False, server_default=text('((1))')),
    Column('PageFormat', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('PageDPI', Integer),
    Column('PageCount', Integer),
    Column('TextEncoding', Unicode(30, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('IsDeleted', Boolean, nullable=False, server_default=text('((0))')),
    Column('FileIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    Column('ContentID', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['AlternateOfID'], ['DokumentDataInfo.ID'], name='FK_DokumentDataInfo_AlternateOf'),
    ForeignKeyConstraint(['DokumentDataInfoType'], ['DokumentDataInfoTypeOpslag.ID'], name='DokumentDataInfo_DokumentDataInfoType'),
    ForeignKeyConstraint(['DokumentDataType'], ['DokumentDataTypeOpslag.ID'], name='DokumentDataInfo_DokumentDataType'),
    ForeignKeyConstraint(['DokumentID'], ['Dokument.ID'], name='DokumentDataInfo_Dokument'),
    ForeignKeyConstraint(['ThumbnailID'], ['DokumentThumbnail.ID'], name='FK_DokumentDataInfo_DokumentThumbnail'),
    PrimaryKeyConstraint('ID', name='PK_DokumentDataInfo'),
    Index('IX_DokumentDataInfo', 'AlternateOfID', 'DokumentDataInfoType', 'DokumentDataType', mssql_clustered=False),
    Index('IX_DokumentDataInfo_DokumentID', 'DokumentID', 'DokumentDataType', 'FileName', 'FileExtension', mssql_clustered=True),
    Index('IX_DokumentDataInfo_DokumentID_Cover', 'DokumentID', mssql_clustered=False, mssql_include=['DokumentDataType', 'FileName', 'FileExtension', 'FilePath', 'FileSize', 'FileLastAccessed', 'FileCreated', 'DokumentDataInfoType', 'HasSnapshot', 'HasThumbnail', 'IndexingStatus', 'AlternateOfID', 'PageFormat', 'TextEncoding', 'IsDeleted', 'FileIdentity', 'ContentID', 'ThumbnailID']),
    Index('IX_DokumentDataInfo_ID', 'ID', mssql_clustered=False, mssql_include=['Rank', 'FilePath', 'FileSize', 'FileLastAccessed', 'FileCreated', 'DokumentDataInfoType', 'HasSnapshot', 'HasThumbnail', 'ThumbnailID', 'IndexingStatus', 'AlternateOfID', 'OCRStatus', 'PageFormat', 'TextEncoding', 'IsDeleted', 'FileIdentity', 'ContentID']),
    Index('UQ__Dokument__7E8CC66326CFC6CC', 'FileIdentity', mssql_clustered=False, unique=True)
)

t_DokumentDataInfoTypeOpslag = Table(
    'DokumentDataInfoTypeOpslag', metadata,
    Column('ID', Integer, primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_DokumentDataInfoType')
)

t_DokumentDataTypeOpslag = Table(
    'DokumentDataTypeOpslag', metadata,
    Column('ID', Integer, primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_DokumentDataType')
)

t_DokumentKonverteringBestilling = Table(
    'DokumentKonverteringBestilling', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DokumentID', Integer),
    PrimaryKeyConstraint('ID', name='PK_DokumentKonverteringBestilling')
)

t_DokumentProcessingQueueAction = Table(
    'DokumentProcessingQueueAction', metadata,
    Column('ID', TINYINT, primary_key=True),
    Column('Name', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_DokumentProcessingQeueueAction')
)

t_DokumentProcessingQueueStatus = Table(
    'DokumentProcessingQueueStatus', metadata,
    Column('ID', TINYINT, primary_key=True),
    Column('Name', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_DokumentProcessingQueueStatus')
)

t_DokumentThumbnail = Table(
    'DokumentThumbnail', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('ThumbnailWidth', SmallInteger),
    Column('ThumbnailHeight', SmallInteger),
    Column('SnapshotWidth', SmallInteger),
    Column('SnapshotHeight', SmallInteger),
    Column('Snapshot', IMAGE),
    Column('Thumbnail', IMAGE),
    PrimaryKeyConstraint('ID', name='PK_DokumentThumbnail')
)

t_EmailKontoExchangeConfiguration = Table(
    'EmailKontoExchangeConfiguration', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Authority', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('ClientId', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('ExchangeEndpoint', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Displayname', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('ExchangeOnlineAuthenticationMethod', Integer, nullable=False, server_default=text('((0))')),
    PrimaryKeyConstraint('Id', name='PK__EmailKon__3214EC0732253953')
)

t_EmailKontoExchangeConfiguration_BACKUP_20220923 = Table(
    'EmailKontoExchangeConfiguration_BACKUP_20220923', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('Authority', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('ClientId', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('ExchangeEndpoint', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Displayname', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False)
)

t_EmneOrdOvergruppe = Table(
    'EmneOrdOvergruppe', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_EmneOrdOvergruppe')
)

t_EmnePlan = Table(
    'EmnePlan', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('MinimumDelforloeb', Integer),
    Column('MaximumDelforloeb', Integer),
    Column('AnvendDelforloeb', Boolean, nullable=False, server_default=text('((0))')),
    Column('Separator', CHAR(1, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('NummerFormat', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('NummerFormatUdenFacet', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('RequireFacet', Boolean, nullable=False, server_default=text('((0))')),
    Column('AllowChangingNummer', Boolean, nullable=False, server_default=text('((0))')),
    Column('EmnePlanNummerType', Integer, nullable=False, server_default=text('((0))')),
    Column('StandardSagsTitel', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('NySagBeskyttes', Boolean, nullable=False, server_default=text('((0))')),
    Column('Version', String(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TilladOprettlseUdFraudgaaetNummer', Boolean, nullable=False, server_default=text('((0))')),
    Column('BrugLavesteNiveau', Boolean, nullable=False, server_default=text('((0))')),
    PrimaryKeyConstraint('ID', name='PK_JournalPlanType')
)

t_FagOmraade = Table(
    'FagOmraade', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('FagomraadeIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    PrimaryKeyConstraint('ID', name='PK_tblFagOmr')
)

t_FirmaPartRolle = Table(
    'FirmaPartRolle', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    PrimaryKeyConstraint('ID', name='PK_FirmaPartRolle')
)

t_FirmaType = Table(
    'FirmaType', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(80, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_tFirmaType')
)

t_FlettetFirma = Table(
    'FlettetFirma', metadata,
    Column('ID', Integer, primary_key=True),
    Column('AdresseID', Integer),
    Column('Navn1', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Navn2', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('CVRNummer', String(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SENummer', String(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('PNummer', String(10, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Homepage', String(400, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ExternalSourceLastUpdate', DateTime),
    Column('ExternalSourceID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ExternalSourceName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('EANNummer', String(13, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KontaktForm', Integer, nullable=False),
    Column('BrancheID', Integer),
    Column('AntalAnsatte', Integer),
    Column('Note', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KommuneID', Integer),
    PrimaryKeyConstraint('ID', name='PK_FlettetFirma')
)

t_FlettetPerson = Table(
    'FlettetPerson', metadata,
    Column('ID', Integer, primary_key=True),
    Column('Initialer', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Titel', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Uddannelse', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Stilling', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Note', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('CprNummer', String(11, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Koen', TINYINT),
    Column('AdresseID', Integer),
    Column('ExternalSourceLastUpdate', DateTime),
    Column('ExternalSourceID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ExternalSourceName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Navn', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('FoedeDato', DateTime),
    Column('Ansaettelsessted', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KontaktForm', Integer, nullable=False),
    Column('CivilstandID', Integer),
    Column('AegtefaelleCPR', String(11, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('MorCPR', String(11, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('FarCPR', String(11, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KommuneID', Integer),
    PrimaryKeyConstraint('ID', name='PK_FlettetPerson')
)

t_FlettetSagspart = Table(
    'FlettetSagspart', metadata,
    Column('ID', Integer, nullable=False),
    Column('SagID', Integer, nullable=False),
    Column('PartType', Integer, nullable=False),
    Column('PartID', Integer, nullable=False),
    Column('SagsPartRolleID', Integer),
    Column('OprindeligAdresseID', Integer),
    Column('Oprettet', DateTime, nullable=False)
)

t_ForloebTypeOpslag = Table(
    'ForloebTypeOpslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(254, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KeyName', Unicode(30, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('HasIcon', Boolean),
    Column('IconName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('IsDetail', Boolean, nullable=False, server_default=text('((0))')),
    PrimaryKeyConstraint('ID', name='PK_ForloebType'),
    Index('IX_ForloebType_KeyName', 'KeyName', mssql_clustered=False, unique=True),
    Index('IX_ForloebType_KeyName_Opslag', 'KeyName', mssql_clustered=False, mssql_include=['Navn', 'Beskrivelse', 'HasIcon', 'IconName', 'IsDetail'])
)

t_GenstandTypeOpslag = Table(
    'GenstandTypeOpslag', metadata,
    Column('ID', Integer, primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_GenstandType')
)

t_GeometriFormatOpslag = Table(
    'GeometriFormatOpslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Kode', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('IsBuiltin', Boolean, nullable=False, server_default=text('((0))')),
    PrimaryKeyConstraint('ID', name='PK_ArealFormat')
)

t_Gruppering = Table(
    'Gruppering', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Tekst', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Aktiv', Boolean, nullable=False, server_default=text('((1))')),
    PrimaryKeyConstraint('ID', name='PK__Gruppering__745AE5AF')
)

t_HaendelseLog = Table(
    'HaendelseLog', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('HaendelseType', Integer, nullable=False),
    Column('TargetType', Integer),
    PrimaryKeyConstraint('ID', name='PK_HaendelseLog')
)

t_HeartbeatHistory = Table(
    'HeartbeatHistory', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Tidspunkt', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('Antal', Integer, nullable=False),
    PrimaryKeyConstraint('ID', name='PK_HeartbeatHistory')
)

t_Hieraki = Table(
    'Hieraki', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('EksternID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    PrimaryKeyConstraint('ID', name='PK_Hieraki')
)

t_JournalArkNoteOverskrift = Table(
    'JournalArkNoteOverskrift', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('Overskrift', String(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False)
)

t_JournalArkNoteOverskriftAnsaettelsessted = Table(
    'JournalArkNoteOverskriftAnsaettelsessted', metadata,
    Column('JournalArkNoteOverskriftID', Integer, nullable=False),
    Column('AnsaettelsesstedID', Integer, nullable=False)
)

t_JournalArkNoteStandardText = Table(
    'JournalArkNoteStandardText', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Label', CHAR(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Text', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    PrimaryKeyConstraint('ID', name='PK_JournalNoteStandardText')
)

t_JournalArkNoteStandardTextAnsaettelsessted = Table(
    'JournalArkNoteStandardTextAnsaettelsessted', metadata,
    Column('JournalArkNoteStandardTextID', Integer, nullable=False),
    Column('AnsaettelsesstedID', Integer, nullable=False)
)

t_JournalArkVisningsFontOpslag = Table(
    'JournalArkVisningsFontOpslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('FontStoerrelse', Integer, nullable=False),
    PrimaryKeyConstraint('ID', name='PK_JournalArkVisningsFontOpslag')
)

t_KnownEksterntSystem = Table(
    'KnownEksterntSystem', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('VistNavn', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('SystemKey', Uuid),
    Column('SystemXPathQuery', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SagstypeXPathQuery', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    PrimaryKeyConstraint('ID', name='PK_KnownEksterntSystem')
)

t_KnownFileTypeOpslag = Table(
    'KnownFileTypeOpslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Extension', Unicode(30, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('MimeType', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OpensInBrowser', Boolean, nullable=False, server_default=text('((1))')),
    Column('WatchTechnique', TINYINT, nullable=False, server_default=text('((1))')),
    Column('ChangeCheckTechnique', TINYINT, nullable=False, server_default=text('((1))')),
    Column('KanBrugesSomKladde', Boolean, nullable=False, server_default=text('((0))')),
    PrimaryKeyConstraint('ID', name='PK_KnownFileType'),
    Index('IX_KnownFileType_Extension', 'Extension', mssql_clustered=False, unique=True)
)

t_KommuneFoer2007Opslag = Table(
    'KommuneFoer2007Opslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Nummer', Integer, nullable=False),
    Column('NytNummer', Integer, nullable=False),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_KommuneFoer2007'),
    Index('IX_KommuneFoer2007_Navn', 'Navn', mssql_clustered=False, unique=True),
    Index('IX_KommuneFoer2007_Nummer', 'Nummer', mssql_clustered=False, unique=True)
)

t_KommuneOpslag = Table(
    'KommuneOpslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Nummer', Integer, nullable=False),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('RegionNummer', Integer, nullable=False),
    PrimaryKeyConstraint('ID', name='PK_Kommune'),
    Index('IX_Kommune_Nummer', 'Nummer', mssql_clustered=False, unique=True)
)

t_KontaktFormOpslag = Table(
    'KontaktFormOpslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_KontaktForm')
)

t_Kontor = Table(
    'Kontor', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Kode', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Nummer', Integer, nullable=False),
    PrimaryKeyConstraint('ID', name='PK_Kontor')
)

t_LandOpslag = Table(
    'LandOpslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Landekode', Unicode(3, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Navn', Unicode(80, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_Land'),
    Index('IX_Land_Landekode', 'Landekode', mssql_clustered=False, unique=True)
)

t_Mail = Table(
    'Mail', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('NativeID', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('FromDisplayName', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('FromEmailAddress', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Subject', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SentDate', DateTime),
    Column('ReceivedDate', DateTime),
    Column('IsSentItem', Boolean, nullable=False, server_default=text('((0))')),
    Column('AccountID', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('AccountDisplayName', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ParentFolderID', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ParentFolderDisplayName', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    Column('UniqueID', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('MailType', Integer, nullable=False, server_default=text('((0))')),
    Column('DigitalPostMaterialeType', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DigitalPostSenderPostkasse', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    PrimaryKeyConstraint('ID', name='PK_tblMail')
)

t_MatrikelArt = Table(
    'MatrikelArt', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Kode', Integer, nullable=False),
    Column('Navn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    PrimaryKeyConstraint('ID', name='PK_MatrikelArt_ID'),
    Index('IX_MatrikelArt_Kode', 'Kode', mssql_clustered=False, unique=True)
)

t_MergeData = Table(
    'MergeData', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('PartID', Integer, nullable=False),
    Column('PartType', Integer, nullable=False),
    Column('MainDokumentDataInfoID', Integer, nullable=False),
    Column('SubDokumentDataInfoID', Integer, nullable=False),
    Column('MergeDataContent', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS')),
    Index('IX_MergeData_MainDokumentDataInfoID', 'MainDokumentDataInfoID', mssql_clustered=False)
)

t_PartTypeOpslag = Table(
    'PartTypeOpslag', metadata,
    Column('ID', Integer, primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_PartTypeOpslag')
)

t_Postnummer = Table(
    'Postnummer', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Nummer', Integer, nullable=False),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_Postnummer'),
    Index('IX_Postnummer', 'Nummer', mssql_clustered=False, unique=True)
)

t_ProcessStatusOpslag = Table(
    'ProcessStatusOpslag', metadata,
    Column('ID', Integer, primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_ProcessStatus')
)

t_PropertyBagItem = Table(
    'PropertyBagItem', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BagID', Uuid, nullable=False),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Vaerdi', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OwnerID', Integer, nullable=False, server_default=text('((0))')),
    PrimaryKeyConstraint('ID', name='PK_PropertyBagValue'),
    Index('IX_PropertyBagItem', 'BagID', mssql_clustered=True)
)

t_PubliseringIndstillinger = Table(
    'PubliseringIndstillinger', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_PubliseringIndstillinger')
)

t_RegionOpslag = Table(
    'RegionOpslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Nummer', Integer, nullable=False),
    PrimaryKeyConstraint('ID', name='PK_Region'),
    Index('IX_Region_Nummer', 'Nummer', mssql_clustered=False, unique=True)
)

t_RequestLog = Table(
    'RequestLog', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Data', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS')),
    Column('Method', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('BrugerID', Integer),
    Column('URL', Unicode(400, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('URLParameters', Unicode(400, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ResponseCode', Integer),
    Column('DurationInMilliSeconds', Integer),
    Column('Logged', DATETIME2, nullable=False, server_default=text('(sysdatetime())')),
    Column('Version', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('RequestHashCode', Integer),
    Column('ClientIP', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ClientName', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ClientSession', Uuid),
    Column('CorrelationId', Uuid, nullable=False),
    PrimaryKeyConstraint('Id', name='PK__RequestL__3214EC073457C4E9')
)

t_Ressource = Table(
    'Ressource', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Identitet', Uuid, nullable=False, server_default=text('(newid())')),
    Column('Navn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Beskrivelse', Unicode(400, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Filename', Unicode(400, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('MimeType', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Data', IMAGE),
    Column('DataSize', BigInteger),
    Column('Kategori', TINYINT, nullable=False, server_default=text('((0))')),
    PrimaryKeyConstraint('ID', name='PK_Ressource')
)

t_RolleOpslag = Table(
    'RolleOpslag', metadata,
    Column('ID', BigInteger, primary_key=True),
    Column('Navn', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('IsBuiltin', Boolean, nullable=False, server_default=text('((0))')),
    PrimaryKeyConstraint('ID', name='PK__DagsordenRolle__6700EA91')
)

t_Sag = Table(
    'Sag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    Column('Nummer', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Titel', Unicode(450, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('ErBeskyttet', Boolean, nullable=False, server_default=text('((0))')),
    Column('Kommentar', Unicode(4000, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('BevaringID', Integer),
    Column('KommuneID', Integer),
    Column('BehandlerID', Integer, nullable=False),
    Column('SagsStatusID', Integer, nullable=False),
    Column('CreatedByID', Integer, nullable=False),
    Column('Created', DateTime, server_default=text('(getdate())')),
    Column('LastChangedByID', Integer),
    Column('LastChanged', DateTime, server_default=text('(getdate())')),
    Column('YderligereMaterialeFindes', Boolean),
    Column('YderligereMaterialeBeskrivelse', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('AmtID', Integer),
    Column('ErBesluttet', Boolean),
    Column('Besluttet', DateTime),
    Column('BeslutningsTypeID', Integer),
    Column('BeslutningNotat', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('BeslutningDeadline', DateTime),
    Column('BeslutningHarDeadline', Boolean),
    Column('ErSamlesag', Boolean),
    Column('FagomraadeID', Integer),
    Column('SecuritySetID', Integer),
    Column('SagsNummerID', Integer),
    Column('LastStatusChange', DateTime),
    Column('LastStatusChangeComments', Unicode(400, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Kassationsdato', DateTime),
    Column('SagsPartID', Integer),
    Column('RegionID', Integer),
    Column('KommuneFoer2007ID', Integer),
    Column('Opstaaet', DateTime),
    Column('AnsaettelsesstedID', Integer, nullable=False),
    Column('ArkivAfklaringStatusID', Integer, nullable=False, server_default=text('((1))')),
    Column('ArkivNote', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('StyringsreolHyldeID', Integer),
    Column('SkabelonID', Integer),
    Column('Sletningsdato', DateTime),
    ForeignKeyConstraint(['AmtID'], ['AmtOpslag.ID'], name='Sag_Amt'),
    ForeignKeyConstraint(['AnsaettelsesstedID'], ['Ansaettelsessted.ID'], name='FK_Sag_Ansaettelsessted'),
    ForeignKeyConstraint(['ArkivAfklaringStatusID'], ['ArkivAfklaringStatus.ID'], name='FK_Sag_ArkivStatus'),
    ForeignKeyConstraint(['BehandlerID'], ['Bruger.ID'], name='Sag_Behandler'),
    ForeignKeyConstraint(['BeslutningsTypeID'], ['BeslutningsType.ID'], name='Sag_BeslutningsType'),
    ForeignKeyConstraint(['BevaringID'], ['BevaringOpslag.ID'], name='Sag_Bevaring'),
    ForeignKeyConstraint(['CreatedByID'], ['Bruger.ID'], name='Sag_CreatedBy'),
    ForeignKeyConstraint(['FagomraadeID'], ['FagOmraade.ID'], name='Sag_FagOmraade'),
    ForeignKeyConstraint(['KommuneFoer2007ID'], ['KommuneFoer2007Opslag.ID'], name='Sag_KommuneFoer2007'),
    ForeignKeyConstraint(['KommuneID'], ['KommuneOpslag.ID'], name='Sag_Kommune'),
    ForeignKeyConstraint(['LastChangedByID'], ['Bruger.ID'], name='Sag_LastChangedBy'),
    ForeignKeyConstraint(['RegionID'], ['RegionOpslag.ID'], name='Sag_Region'),
    ForeignKeyConstraint(['SagsNummerID'], ['SagsNummer.ID'], name='Sag_SagsNummer'),
    ForeignKeyConstraint(['SagsPartID'], ['SagsPart.ID'], name='Sag_SagsPart'),
    ForeignKeyConstraint(['SagsStatusID'], ['SagsStatus.ID'], name='Sag_SagsStatus'),
    ForeignKeyConstraint(['SecuritySetID'], ['SecuritySet.ID'], name='Sag_SecuritySet'),
    ForeignKeyConstraint(['SkabelonID'], ['SagSkabelon.ID'], name='FK_Sag_SagSkabelon'),
    ForeignKeyConstraint(['StyringsreolHyldeID'], ['StyringsreolHylde.ID'], name='FK_Sag_StyringsreolHylde'),
    PrimaryKeyConstraint('ID', name='PK_Sag'),
    Index('IX_Cover_BehandlerID', 'BehandlerID', mssql_clustered=False, mssql_include=['ID', 'SagIdentity', 'Nummer', 'Titel', 'ErBeskyttet', 'Kommentar', 'BevaringID', 'KommuneID', 'SagsStatusID', 'CreatedByID', 'Created', 'LastChangedByID', 'LastChanged', 'YderligereMaterialeFindes', 'YderligereMaterialeBeskrivelse', 'AmtID', 'ErBesluttet', 'Besluttet', 'BeslutningsTypeID', 'BeslutningNotat', 'BeslutningDeadline', 'ErSamlesag', 'FagomraadeID', 'SecuritySetID', 'SagsNummerID', 'LastStatusChange', 'LastStatusChangeComments', 'Kassationsdato', 'SagsPartID', 'RegionID', 'KommuneFoer2007ID', 'Opstaaet', 'AnsaettelsesstedID', 'ArkivAfklaringStatusID', 'StyringsreolHyldeID', 'SkabelonID', 'Sletningsdato']),
    Index('IX_Gammel_Soeg_Sag', 'ID', 'ErBeskyttet', 'BehandlerID', 'SecuritySetID', mssql_clustered=False, mssql_include=['SagIdentity', 'Nummer', 'Titel', 'Created', 'LastChanged', 'LastStatusChange']),
    Index('IX_Mir_SagSecurity', 'ID', 'SecuritySetID', 'ErBeskyttet', 'BehandlerID', mssql_clustered=False),
    Index('IX_Sag_Behandler_Sag_Ansaet_Created_Status', 'BehandlerID', 'AnsaettelsesstedID', 'SagsStatusID', 'Created', mssql_clustered=False, mssql_include=['ID', 'Nummer', 'Titel', 'ErBeskyttet', 'SecuritySetID', 'Opstaaet']),
    Index('IX_Sag_Created', 'Created', mssql_clustered=False, mssql_include=['SagIdentity', 'Nummer', 'Titel', 'ErBeskyttet', 'Kommentar', 'BevaringID', 'KommuneID', 'BehandlerID', 'SagsStatusID', 'CreatedByID', 'LastChangedByID', 'LastChanged', 'YderligereMaterialeFindes', 'YderligereMaterialeBeskrivelse', 'AmtID', 'ErBesluttet', 'Besluttet', 'BeslutningsTypeID', 'BeslutningNotat', 'BeslutningDeadline', 'ErSamlesag', 'FagomraadeID', 'SecuritySetID', 'SagsNummerID', 'LastStatusChange', 'LastStatusChangeComments', 'Kassationsdato', 'SagsPartID', 'RegionID', 'KommuneFoer2007ID', 'Opstaaet', 'AnsaettelsesstedID', 'ArkivAfklaringStatusID', 'StyringsreolHyldeID', 'SkabelonID', 'Sletningsdato']),
    Index('IX_Sag_LastStatusChange', 'LastStatusChange', mssql_clustered=False),
    Index('IX_Sag_OprettetAf', 'CreatedByID', mssql_clustered=False),
    Index('IX_Sag_SagIdentity', 'SagIdentity', mssql_clustered=False, unique=True),
    Index('IX_Sag_SagsStatusID', 'SagsStatusID', mssql_clustered=False, mssql_include=['ID', 'Nummer', 'Titel', 'ErBeskyttet', 'KommuneID', 'BehandlerID', 'CreatedByID', 'Created', 'LastChangedByID', 'BeslutningDeadline', 'FagomraadeID', 'SecuritySetID', 'LastStatusChange', 'SagsPartID', 'Opstaaet', 'AnsaettelsesstedID']),
    Index('IX_Sag_Titel', 'Titel', mssql_clustered=False),
    Index('IX_SagsNummer', 'Nummer', mssql_clustered=False, unique=True)
)

t_SagSkabelonKategori = Table(
    'SagSkabelonKategori', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    PrimaryKeyConstraint('ID', name='PK_SagSkabelonKategori')
)

t_SagerOverfort = Table(
    'SagerOverfort', metadata,
    Column('id', Integer, nullable=False),
    Column('Nummer', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False)
)

t_SagerTilFilarkiv = Table(
    'SagerTilFilarkiv', metadata,
    Column('id', Integer, nullable=False),
    Column('Nummer', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False)
)

t_SagsFelt = Table(
    'SagsFelt', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Noegle', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('Id', name='PK__SagsFelt__3214EC07E255CB50'),
    Index('UQ__SagsFelt__5AE4217A0965BFF3', 'Noegle', mssql_clustered=False, unique=True)
)

t_SagsPart = Table(
    'SagsPart', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagID', Integer, nullable=False),
    Column('PartType', Integer, nullable=False),
    Column('PartID', Integer, nullable=False),
    Column('SagsPartRolleID', Integer),
    Column('OprindeligAdresseID', Integer),
    Column('Oprettet', DateTime, nullable=False, server_default=text('(getdate())')),
    ForeignKeyConstraint(['OprindeligAdresseID'], ['Adresse.ID'], name='SagsPart_OprindeligAdresse'),
    ForeignKeyConstraint(['PartType'], ['PartTypeOpslag.ID'], name='FK_SagsPart_PartTypeOpslag'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='SagsPart_Sag'),
    ForeignKeyConstraint(['SagsPartRolleID'], ['SagsPartRolle.ID'], name='SagsPart_SagsPartRolle'),
    PrimaryKeyConstraint('ID', name='PK_SagsPart'),
    Index('IX_SagsPart', 'PartType', 'PartID', mssql_clustered=False),
    Index('IX_SagsPart_Sag', 'SagID', 'PartType', 'PartID', 'SagsPartRolleID', 'OprindeligAdresseID', 'Oprettet', mssql_clustered=True),
    Index('IX_Sagspart_Ink_PartType_OprindeligAdresseid', 'PartType', 'OprindeligAdresseID', mssql_clustered=False)
)

t_SagsPartRolle = Table(
    'SagsPartRolle', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_Rolle')
)

t_SagsTilstandOpslag = Table(
    'SagsTilstandOpslag', metadata,
    Column('ID', Integer, primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_SagsTilstand')
)

t_SagsType = Table(
    'SagsType', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('Id', name='PK_SagsType'),
    Index('AK_SagsType_Navn', 'Navn', mssql_clustered=False, unique=True)
)

t_SearchLog = Table(
    'SearchLog', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SearchGuid', Uuid, nullable=False),
    Column('SearchTab', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SearchCriteria', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('LogDate', DateTime, nullable=False),
    PrimaryKeyConstraint('ID', name='PK_SearchLog')
)

t_SecuritySet = Table(
    'SecuritySet', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', String(1, 'SQL_Danish_Pref_CP1_CI_AS')),
    PrimaryKeyConstraint('ID', name='PK_SecuritySet')
)

t_Sekretariat = Table(
    'Sekretariat', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Stedbetegnelse', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Institutionsnavn', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    PrimaryKeyConstraint('ID', name='PK__Sekretariat__6518A21F')
)

t_SendBOMBesvarelseBestilling = Table(
    'SendBOMBesvarelseBestilling', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BesvarelseID', Integer, nullable=False),
    PrimaryKeyConstraint('Id', name='PK__SendBOMB__3214EC076B15EA47')
)

t_SikkerhedsbeslutningOpslag = Table(
    'SikkerhedsbeslutningOpslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Class', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(250, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Verbum', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TildelteRoller', BigInteger, nullable=False, server_default=text('((0))')),
    Column('BypassRoller', BigInteger, nullable=False, server_default=text('((0))')),
    Column('Type', Integer, server_default=text('((0))')),
    Column('Krav', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ErUdvalgsspecifik', Boolean, nullable=False, server_default=text('((0))')),
    PrimaryKeyConstraint('ID', name='PK_Sikkerhedsbeslutning'),
    Index('IX_UniktVerbum', 'Verbum', mssql_clustered=False, unique=True),
    Index('IX_UniqueClassName', 'Class', mssql_clustered=False, unique=True)
)

t_SkabelonGrundSkabelon = Table(
    'SkabelonGrundSkabelon', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('FilNavn', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('IndhentetFraFil', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SkabelonData', IMAGE),
    PrimaryKeyConstraint('ID', name='PK_tblWordSkabelon')
)

t_SkabelonTypeGruppe = Table(
    'SkabelonTypeGruppe', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    PrimaryKeyConstraint('ID', name='PK_tblSkabelontypeGruppe')
)

t_SlettetEntitet = Table(
    'SlettetEntitet', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('EntitetID', Integer, nullable=False),
    Column('EntitetIdentity', Uuid, nullable=False),
    Column('EntitetType', Integer, nullable=False),
    Column('SletTidspunkt', DATETIME2, nullable=False),
    Index('IX_SlettetEntitet_SletTidspunkt', 'SletTidspunkt', mssql_clustered=True)
)

t_StylesheetTypeOpslag = Table(
    'StylesheetTypeOpslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('FileExtension', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    PrimaryKeyConstraint('ID', name='PK_StylesheetTypeOpslag'),
    Index('IX_StylesheetTypeOpslag', 'Navn', mssql_clustered=False, unique=True)
)

t_StyringsreolSagsFelt = Table(
    'StyringsreolSagsFelt', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('InternalName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('DisplayName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('SagItemName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Abbreviation', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('IsDefault', Boolean, nullable=False),
    PrimaryKeyConstraint('ID', name='PK_StyringsreolSagsFelt')
)

t_TidsPosteringKategori = Table(
    'TidsPosteringKategori', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', NCHAR(10, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Aktiv', Boolean, nullable=False, server_default=text('((0))')),
    PrimaryKeyConstraint('Id', name='PK__TidsPost__3214EC07EA6426A3')
)

t_Udvalgsperson = Table(
    'Udvalgsperson', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Fornavn', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Efternavn', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('ErAktiv', Boolean, nullable=False, server_default=text('((1))')),
    PrimaryKeyConstraint('ID', name='PK_Udvalgsperson')
)

t_Udvalgsstruktur = Table(
    'Udvalgsstruktur', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Sortering', Integer, nullable=False, server_default=text('((-1))')),
    Column('Niveau', Integer, nullable=False),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('ParentID', Integer),
    ForeignKeyConstraint(['ParentID'], ['Udvalgsstruktur.ID'], name='FK_Udvalgsstruktur_Parent_Udvalgsstruktur'),
    PrimaryKeyConstraint('ID', name='PK__Udvalgsstruktur__782B7693')
)

t_UsageLog = Table(
    'UsageLog', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False, server_default=text('((1))')),
    Column('TargetType', Integer),
    PrimaryKeyConstraint('ID', name='PK_UsageLog')
)

t_Usagelog_20140811_09_40_19 = Table(
    'Usagelog_20140811_09_40_19', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20140811_09_40_48 = Table(
    'Usagelog_20140811_09_40_48', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20140811_09_41_14 = Table(
    'Usagelog_20140811_09_41_14', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20140811_09_41_41 = Table(
    'Usagelog_20140811_09_41_41', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20150401_00_00_00 = Table(
    'Usagelog_20150401_00_00_00', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20150501_00_00_00 = Table(
    'Usagelog_20150501_00_00_00', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20150601_00_00_00 = Table(
    'Usagelog_20150601_00_00_00', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20150901_00_00_00 = Table(
    'Usagelog_20150901_00_00_00', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20151001_00_00_01 = Table(
    'Usagelog_20151001_00_00_01', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20151201_00_00_00 = Table(
    'Usagelog_20151201_00_00_00', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20160101_00_00_00 = Table(
    'Usagelog_20160101_00_00_00', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20160201_00_00_02 = Table(
    'Usagelog_20160201_00_00_02', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20160301_00_00_03 = Table(
    'Usagelog_20160301_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20160401_00_00_04 = Table(
    'Usagelog_20160401_00_00_04', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20160501_00_01_26 = Table(
    'Usagelog_20160501_00_01_26', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20160601_00_01_20 = Table(
    'Usagelog_20160601_00_01_20', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20160701_00_01_11 = Table(
    'Usagelog_20160701_00_01_11', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20160801_00_00_51 = Table(
    'Usagelog_20160801_00_00_51', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20160901_00_01_23 = Table(
    'Usagelog_20160901_00_01_23', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20161001_00_01_05 = Table(
    'Usagelog_20161001_00_01_05', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20161101_00_00_37 = Table(
    'Usagelog_20161101_00_00_37', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20161201_00_01_55 = Table(
    'Usagelog_20161201_00_01_55', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20170101_00_01_57 = Table(
    'Usagelog_20170101_00_01_57', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20170201_00_00_56 = Table(
    'Usagelog_20170201_00_00_56', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20170301_00_01_04 = Table(
    'Usagelog_20170301_00_01_04', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20170401_00_00_08 = Table(
    'Usagelog_20170401_00_00_08', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20170501_00_00_39 = Table(
    'Usagelog_20170501_00_00_39', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20170601_00_00_45 = Table(
    'Usagelog_20170601_00_00_45', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20170701_00_00_46 = Table(
    'Usagelog_20170701_00_00_46', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20170801_00_00_44 = Table(
    'Usagelog_20170801_00_00_44', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20170901_00_00_42 = Table(
    'Usagelog_20170901_00_00_42', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20171001_00_00_45 = Table(
    'Usagelog_20171001_00_00_45', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20171101_00_00_40 = Table(
    'Usagelog_20171101_00_00_40', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20171201_00_00_47 = Table(
    'Usagelog_20171201_00_00_47', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20180101_00_00_55 = Table(
    'Usagelog_20180101_00_00_55', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20180201_00_00_36 = Table(
    'Usagelog_20180201_00_00_36', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20180301_00_00_25 = Table(
    'Usagelog_20180301_00_00_25', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20180401_00_00_06 = Table(
    'Usagelog_20180401_00_00_06', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20180501_00_00_07 = Table(
    'Usagelog_20180501_00_00_07', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20180601_00_00_03 = Table(
    'Usagelog_20180601_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20180701_00_00_04 = Table(
    'Usagelog_20180701_00_00_04', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20180801_00_00_04 = Table(
    'Usagelog_20180801_00_00_04', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20180901_00_00_08 = Table(
    'Usagelog_20180901_00_00_08', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20181001_00_00_08 = Table(
    'Usagelog_20181001_00_00_08', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20181101_00_00_03 = Table(
    'Usagelog_20181101_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20181201_00_00_07 = Table(
    'Usagelog_20181201_00_00_07', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20190101_00_00_05 = Table(
    'Usagelog_20190101_00_00_05', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20190201_00_00_09 = Table(
    'Usagelog_20190201_00_00_09', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20190301_00_00_11 = Table(
    'Usagelog_20190301_00_00_11', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20190401_00_00_05 = Table(
    'Usagelog_20190401_00_00_05', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20190501_00_00_06 = Table(
    'Usagelog_20190501_00_00_06', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20190601_00_00_16 = Table(
    'Usagelog_20190601_00_00_16', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20190701_00_00_06 = Table(
    'Usagelog_20190701_00_00_06', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20190801_00_00_04 = Table(
    'Usagelog_20190801_00_00_04', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20190901_00_00_09 = Table(
    'Usagelog_20190901_00_00_09', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20191001_00_00_04 = Table(
    'Usagelog_20191001_00_00_04', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20191101_00_00_05 = Table(
    'Usagelog_20191101_00_00_05', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20191201_00_00_06 = Table(
    'Usagelog_20191201_00_00_06', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20200101_00_00_12 = Table(
    'Usagelog_20200101_00_00_12', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20200201_00_00_08 = Table(
    'Usagelog_20200201_00_00_08', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20200301_00_00_07 = Table(
    'Usagelog_20200301_00_00_07', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20200401_00_00_05 = Table(
    'Usagelog_20200401_00_00_05', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20200501_00_00_04 = Table(
    'Usagelog_20200501_00_00_04', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20200601_00_00_03 = Table(
    'Usagelog_20200601_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20200701_00_00_03 = Table(
    'Usagelog_20200701_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20200801_00_00_03 = Table(
    'Usagelog_20200801_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20200901_00_00_02 = Table(
    'Usagelog_20200901_00_00_02', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20201001_00_00_03 = Table(
    'Usagelog_20201001_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20201101_00_00_01 = Table(
    'Usagelog_20201101_00_00_01', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20201201_00_00_03 = Table(
    'Usagelog_20201201_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20210101_00_00_02 = Table(
    'Usagelog_20210101_00_00_02', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20210201_00_00_02 = Table(
    'Usagelog_20210201_00_00_02', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20210301_00_00_03 = Table(
    'Usagelog_20210301_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20210401_00_00_03 = Table(
    'Usagelog_20210401_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20210501_00_00_04 = Table(
    'Usagelog_20210501_00_00_04', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20210601_00_00_05 = Table(
    'Usagelog_20210601_00_00_05', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20210701_00_00_04 = Table(
    'Usagelog_20210701_00_00_04', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20210801_00_00_01 = Table(
    'Usagelog_20210801_00_00_01', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20210901_00_00_01 = Table(
    'Usagelog_20210901_00_00_01', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20211001_00_00_03 = Table(
    'Usagelog_20211001_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20211101_00_00_00 = Table(
    'Usagelog_20211101_00_00_00', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20211201_00_00_02 = Table(
    'Usagelog_20211201_00_00_02', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20220101_00_00_02 = Table(
    'Usagelog_20220101_00_00_02', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20220201_00_00_03 = Table(
    'Usagelog_20220201_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20220301_00_00_03 = Table(
    'Usagelog_20220301_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20220401_00_00_01 = Table(
    'Usagelog_20220401_00_00_01', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20220501_00_00_03 = Table(
    'Usagelog_20220501_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20220601_00_00_12 = Table(
    'Usagelog_20220601_00_00_12', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20220701_00_00_09 = Table(
    'Usagelog_20220701_00_00_09', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20220801_00_00_03 = Table(
    'Usagelog_20220801_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20220901_00_00_08 = Table(
    'Usagelog_20220901_00_00_08', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20221001_00_00_02 = Table(
    'Usagelog_20221001_00_00_02', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20221101_00_00_01 = Table(
    'Usagelog_20221101_00_00_01', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20221201_00_00_02 = Table(
    'Usagelog_20221201_00_00_02', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20230101_00_00_03 = Table(
    'Usagelog_20230101_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20230201_00_00_02 = Table(
    'Usagelog_20230201_00_00_02', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20230301_00_00_06 = Table(
    'Usagelog_20230301_00_00_06', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20230401_00_00_04 = Table(
    'Usagelog_20230401_00_00_04', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20230501_00_00_04 = Table(
    'Usagelog_20230501_00_00_04', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20230601_00_00_08 = Table(
    'Usagelog_20230601_00_00_08', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20230701_00_00_03 = Table(
    'Usagelog_20230701_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20230801_00_00_03 = Table(
    'Usagelog_20230801_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20230901_00_00_03 = Table(
    'Usagelog_20230901_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20231001_00_00_05 = Table(
    'Usagelog_20231001_00_00_05', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20231101_00_00_03 = Table(
    'Usagelog_20231101_00_00_03', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20231201_00_00_04 = Table(
    'Usagelog_20231201_00_00_04', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20240101_00_00_05 = Table(
    'Usagelog_20240101_00_00_05', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20240201_00_00_07 = Table(
    'Usagelog_20240201_00_00_07', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20240301_00_00_06 = Table(
    'Usagelog_20240301_00_00_06', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20240401_00_00_07 = Table(
    'Usagelog_20240401_00_00_07', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_Usagelog_20240501_00_00_16 = Table(
    'Usagelog_20240501_00_00_16', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('LogDate', DateTime, nullable=False),
    Column('Event', String(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Details', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TargetID', Integer),
    Column('DelforloebID', Integer),
    Column('SagID', Integer),
    Column('UsageType', Integer, nullable=False),
    Column('TargetType', Integer)
)

t_WebApiAppAccess = Table(
    'WebApiAppAccess', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('ClientId', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('ClientSecret', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Uri', Unicode(1000, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('AllowAuthorizationCodeGrant', Boolean, nullable=False, server_default=text('((0))')),
    Column('AllowImplicitCodeGrant', Boolean, nullable=False, server_default=text('((0))')),
    Column('AllowResourceOwnerCredentialsGrant', Boolean, nullable=False, server_default=text('((0))')),
    Column('AllowClientCredentialsGrant', Boolean, nullable=False, server_default=text('((0))')),
    Column('RefreshTokenExpiration', Integer, nullable=False, server_default=text('((14))')),
    PrimaryKeyConstraint('ID', name='PK_WebApiAppAccess'),
    Index('IX_WebApiAppAccess_ClientId', 'ClientId', mssql_clustered=False, unique=True),
    Index('IX_WebApiAppAccess_Uri', 'Uri', mssql_clustered=False)
)

t_WebApiRefreshToken = Table(
    'WebApiRefreshToken', metadata,
    Column('Id', NCHAR(160, 'SQL_Danish_Pref_CP1_CI_AS'), primary_key=True),
    Column('SerializedTicket', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('IssuedUtc', DATETIMEOFFSET, nullable=False),
    Column('ExpiresUtc', DATETIMEOFFSET, nullable=False),
    Column('ClientId', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Revoked', Boolean, nullable=False, server_default=text('((0))')),
    PrimaryKeyConstraint('Id', name='PK__WebApiRe__3214EC07FABF00CA')
)

t_WebWidget = Table(
    'WebWidget', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(1024, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Titel', Unicode(1024, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Url', Unicode(1024, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Aktiv', Boolean, nullable=False),
    Column('Indlejret', Boolean, nullable=False, server_default=text('((1))')),
    Column('Placering', Integer),
    Column('Icon', LargeBinary),
    Column('Regel', Integer),
    Column('SortIndex', Integer, nullable=False),
    Column('KonfigurationID', Uuid, nullable=False),
    Column('ErBU', Boolean, nullable=False, server_default=text('((0))')),
    PrimaryKeyConstraint('ID', name='PK__WebWidge__3214EC274ED1BA8C')
)

t_backup_SecuritySet = Table(
    'backup_SecuritySet', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('Navn', String(1, 'SQL_Danish_Pref_CP1_CI_AS'))
)

t_backup_SecuritySetBrugere = Table(
    'backup_SecuritySetBrugere', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('SecuritySetID', Integer, nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('ErPermanent', Boolean, nullable=False)
)

t_backup_SecuritySetSikkerhedsgrupper = Table(
    'backup_SecuritySetSikkerhedsgrupper', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('SecuritySetID', Integer, nullable=False),
    Column('SikkerhedsgruppeID', Integer, nullable=False)
)

t_tmp_CasesToUpdateWithPermissions = Table(
    'tmp_CasesToUpdateWithPermissions', metadata,
    Column('nummer', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Titel', Unicode(450, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('sikkerhedsgruppe', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('id', Integer, nullable=False),
    Column('skabelon', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False)
)

t_tmp_CasesToUpdateWithPermissions2 = Table(
    'tmp_CasesToUpdateWithPermissions2', metadata,
    Column('nummer', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False)
)

t_AdministrativProfilRettigheder = Table(
    'AdministrativProfilRettigheder', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('AdministrativProfilID', Integer, nullable=False),
    Column('SikkerhedsbeslutningID', Integer, nullable=False),
    ForeignKeyConstraint(['AdministrativProfilID'], ['AdministrativProfil.ID'], name='FK_AdministrativProfil_Rettighed'),
    ForeignKeyConstraint(['SikkerhedsbeslutningID'], ['SikkerhedsbeslutningOpslag.ID'], name='FK_AdministrativProfil_rettigheder_sikkerhedsopslag'),
    PrimaryKeyConstraint('ID', name='PK_adminprol_rettigheder')
)

t_BeslutningsType = Table(
    'BeslutningsType', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('BeslutningsTypeGruppeID', Integer, nullable=False),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    ForeignKeyConstraint(['BeslutningsTypeGruppeID'], ['BeslutningsTypeGruppe.ID'], name='BeslutningsType_BeslutningsTypeGruppe'),
    PrimaryKeyConstraint('ID', name='PK_AfgoeringType')
)

t_Bygning = Table(
    'Bygning', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('KommuneID', Integer, nullable=False),
    Column('Beskrivelse', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Oprettet', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('BygningsNummer', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('BbrIndikator', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('EjendomsNummer', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Anvendelse', Unicode(75, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ExternalSourceLastUpdate', DateTime),
    Column('ExternalSourceID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ExternalSourceName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Beliggenhed', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Historisk', Boolean, nullable=False, server_default=text('((0))')),
    Column('BygningIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    ForeignKeyConstraint(['KommuneID'], ['KommuneOpslag.ID'], name='FK_Bygning_Kommune'),
    PrimaryKeyConstraint('ID', name='PK_Bygning'),
    Index('IX_Bygning_BygningIdentity', 'BygningIdentity', mssql_clustered=False, unique=True),
    Index('UQ__Bygning__211C0CA61E7D4425', 'BygningIdentity', mssql_clustered=False, unique=True)
)

t_DagsordenpunktFelt = Table(
    'DagsordenpunktFelt', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SkabelonHtmlTekst', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('ErIndtastningFelt', Boolean, server_default=text('((0))')),
    Column('DagsordenpunktFeltTypeId', Integer),
    Column('EksterntId', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['DagsordenpunktFeltTypeId'], ['DagsordenpunktFeltType.ID'], name='FK_DagsordenpunktFelt_DagsordenpunktFeltType'),
    PrimaryKeyConstraint('ID', name='PK_DagsordenpunktFelt')
)

t_DelforloebType = Table(
    'DelforloebType', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('DelforloebTypeGruppeID', Integer, nullable=False),
    ForeignKeyConstraint(['DelforloebTypeGruppeID'], ['DelforloebTypeGruppe.ID'], name='DelforloebType_DelforloebTypeGruppe'),
    PrimaryKeyConstraint('ID', name='PK_DelforloebType')
)

t_DokumentBoksHistorik = Table(
    'DokumentBoksHistorik', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('Sent', DateTime),
    Column('SagID', Integer, nullable=False),
    Column('Modtagertype', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('AfsenderId', Integer, nullable=False, server_default=text('((-1))')),
    Column('Materiale', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Postkasse', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ForsoegtSendt', DateTime),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='FK__DokumentB__SagID__5728DECD')
)

t_DokumentMetaData = Table(
    'DokumentMetaData', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DokumentID', Integer, nullable=False),
    Column('KeyName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Value', Unicode(400, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['DokumentID'], ['Dokument.ID'], name='FK_DokumentMetaData_Dokument'),
    PrimaryKeyConstraint('ID', name='PK_DokumentMetaData'),
    Index('IX_DokumentMetaData', 'DokumentID', mssql_clustered=True)
)

t_DokumentPart = Table(
    'DokumentPart', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DokumentID', Integer, nullable=False),
    Column('PartID', Integer, nullable=False),
    Column('PartType', Integer, nullable=False),
    Column('KontaktForm', Integer, nullable=False),
    Column('AnvendtAdresse', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['DokumentID'], ['Dokument.ID'], name='DokumentPart_Dokument'),
    ForeignKeyConstraint(['KontaktForm'], ['KontaktFormOpslag.ID'], name='DokumentPart_KontaktForm'),
    PrimaryKeyConstraint('ID', name='PK_DokumentPart'),
    Index('IX_DokumentPart_DokumentID', 'DokumentID', mssql_clustered=False, mssql_include=['PartID', 'PartType', 'KontaktForm', 'AnvendtAdresse'])
)

t_DokumentProcessingQueue = Table(
    'DokumentProcessingQueue', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('InputDokumentID', Integer, nullable=False),
    Column('InputDokumentDataInfoID', Integer, nullable=False),
    Column('OutputDokumentDataInfoID', Integer),
    Column('Action', TINYINT, nullable=False, server_default=text('((0))')),
    Column('Queued', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('LastAttemptStart', DateTime),
    Column('LastAttemptEnd', DateTime),
    Column('LastAttemptDurationSeconds', BigInteger),
    Column('NextAttempt', DateTime),
    Column('AttemptCount', Integer, nullable=False, server_default=text('((0))')),
    Column('Log', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Status', TINYINT, nullable=False, server_default=text('((0))')),
    Column('Message', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TotalDurationSeconds', BigInteger, nullable=False, server_default=text('((0))')),
    Column('TimeoutSeconds', Integer, nullable=False, server_default=text('((10))')),
    Column('ProcessedOnMachine', Unicode(150, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['Action'], ['DokumentProcessingQueueAction.ID'], name='FK_DokumentProcessingQueue_DokumentProcessingQeueueAction'),
    ForeignKeyConstraint(['InputDokumentDataInfoID'], ['DokumentDataInfo.ID'], name='FK_DokumentProcessingQueue_DokumentDataInfo_Input'),
    ForeignKeyConstraint(['InputDokumentID'], ['Dokument.ID'], name='FK_DokumentProcessingQueue_Dokument'),
    ForeignKeyConstraint(['OutputDokumentDataInfoID'], ['DokumentDataInfo.ID'], name='FK_DokumentProcessingQueue_DokumentDataInfo_Output'),
    ForeignKeyConstraint(['Status'], ['DokumentProcessingQueueStatus.ID'], name='FK_DokumentProcessingQueue_DokumentProcessingQueueStatus'),
    PrimaryKeyConstraint('ID', name='PK_DokumentProcessingQueue'),
    Index('IX_DokumentProcessingQueue', 'InputDokumentDataInfoID', 'Action', mssql_clustered=False),
    Index('IX_DokumentProcessingQueue_InputDokument', 'ID', 'InputDokumentID', mssql_clustered=True)
)

t_DokumentTypeOpslag = Table(
    'DokumentTypeOpslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('DefaultDokumentArtID', Integer),
    ForeignKeyConstraint(['DefaultDokumentArtID'], ['DokumentArtOpslag.ID'], name='DokumentType_DokumentArt'),
    PrimaryKeyConstraint('ID', name='PK_tDokumentType_1')
)

t_Ejendom = Table(
    'Ejendom', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('KommuneID', Integer, nullable=False),
    Column('Beskrivelse', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Oprettet', DateTime, nullable=False),
    Column('EjendomsNummer', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('ExternalSourceLastUpdate', DateTime),
    Column('ExternalSourceID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ExternalSourceName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Beliggenhed', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Historisk', Boolean, nullable=False, server_default=text('((0))')),
    Column('BeliggenhedAdresseID', Integer),
    Column('Vejkode', Integer),
    Column('EjendomIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    Column('BFENummer', BigInteger, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['KommuneID'], ['KommuneOpslag.ID'], name='FK_Ejendom_Kommune'),
    PrimaryKeyConstraint('ID', name='PK_Ejendom'),
    Index('UQ__Ejendom__5F56C031E70861B2', 'EjendomIdentity', mssql_clustered=False, unique=True)
)

t_EmneOrdGruppe = Table(
    'EmneOrdGruppe', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('EmneordOvergruppeID', Integer, nullable=False),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('ErAktiv', Boolean),
    ForeignKeyConstraint(['EmneordOvergruppeID'], ['EmneOrdOvergruppe.ID'], name='EmneOrdGruppe_EmneOrdOvergruppe'),
    PrimaryKeyConstraint('ID', name='PK_tblEmneordGruppe')
)

t_EmnePlanLovGrundlag = Table(
    'EmnePlanLovGrundlag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('VedroererEmnePlanNummer', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Paragraf', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Lovtitel', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('RetsinfoLink', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('RetsinfoLinkParagraf', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('EmnePlanID', Integer),
    ForeignKeyConstraint(['EmnePlanID'], ['EmnePlan.ID'], name='FK_EmnePlanLovGrundlag_EmnePlan'),
    PrimaryKeyConstraint('ID', name='PK_LovUpdate')
)

t_EmnePlanNummer = Table(
    'EmnePlanNummer', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('EmnePlanID', Integer, nullable=False),
    Column('Nummer', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Navn', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Niveau', Integer),
    Column('BevaringID', Integer),
    Column('Oprettet', DateTime),
    Column('Rettet', DateTime),
    Column('Udgaaet', DateTime),
    Column('ErUdgaaet', Boolean),
    ForeignKeyConstraint(['BevaringID'], ['BevaringOpslag.ID'], name='EmnePlanNummer_Bevaring'),
    ForeignKeyConstraint(['EmnePlanID'], ['EmnePlan.ID'], name='FK_EmnePlanNummer_EmnePlan'),
    PrimaryKeyConstraint('ID', name='PK_EmnePlan'),
    Index('IX_EmnePlanNummer', 'EmnePlanID', 'Nummer', 'Niveau', mssql_clustered=True, unique=True)
)

t_EmnePlanStikord = Table(
    'EmnePlanStikord', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('EmnePlanID', Integer, nullable=False),
    Column('ForeslaaNummer', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ForeslaaFacetKode', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('EmneOrd', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['EmnePlanID'], ['EmnePlan.ID'], name='EmnePlanStikord_EmnePlan'),
    PrimaryKeyConstraint('ID', name='PK_EmnePlanStikord')
)

t_EmneplanOpdatering = Table(
    'EmneplanOpdatering', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('EmneplanID', Integer, nullable=False),
    Column('SendMail', Boolean),
    Column('Opretnyhed', Boolean),
    Column('SmtpServer', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SSL', Boolean),
    Column('Brugerkonto', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Adgangskode', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('EmneplanUrl', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('StikordUrl', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('FacetUrl', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TjekInterval', Integer, server_default=text('((30))')),
    Column('SidsteTjek', DateTime),
    Column('Aktiv', Boolean, nullable=False, server_default=text('((0))')),
    Column('Mail', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['EmneplanID'], ['EmnePlan.ID'], name='FK_EmneplanOpdatering_EmnePlan'),
    PrimaryKeyConstraint('ID', name='PK_EmneplanOpdatering')
)

t_FacetType = Table(
    'FacetType', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(75, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(3900, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Boolean),
    Column('EmnePlanID', Integer, nullable=False),
    Column('Oprettet', DateTime),
    Column('Rettet', DateTime),
    Column('Udgaaet', DateTime),
    Column('FacetTypeKode', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['EmnePlanID'], ['EmnePlan.ID'], name='FK_FacetType_EmnePlan'),
    PrimaryKeyConstraint('ID', name='PK_tblInstitutionsType'),
    Index('IX_FacetType_Emneplan', 'EmnePlanID', mssql_clustered=True)
)

t_Firma = Table(
    'Firma', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('AdresseID', Integer),
    Column('Navn1', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Navn2', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('CVRNummer', String(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SENummer', String(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('PNummer', String(10, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Homepage', String(400, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ExternalSourceLastUpdate', DateTime),
    Column('ExternalSourceID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ExternalSourceName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('EANNummer', String(13, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KontaktForm', Integer, nullable=False, server_default=text('((1))')),
    Column('BrancheID', Integer),
    Column('AntalAnsatte', Integer),
    Column('Note', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KommuneID', Integer),
    Column('PartOprydningsKeyCheckSum', Integer),
    Column('ErJuridiskEnhed', Boolean, server_default=text('((0))')),
    Column('JuridiskEnhedAdresseID', Integer),
    Column('TilmeldtDigitalPost', Boolean, nullable=False, server_default=text('((0))')),
    Column('FirmaIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    ForeignKeyConstraint(['AdresseID'], ['Adresse.ID'], name='Firma_Adresse'),
    ForeignKeyConstraint(['BrancheID'], ['Branche.ID'], name='FK_Firma_Branche'),
    ForeignKeyConstraint(['KommuneID'], ['KommuneOpslag.ID'], name='FK_Firma_KommuneOpslag'),
    ForeignKeyConstraint(['KontaktForm'], ['KontaktFormOpslag.ID'], name='Firma_KontaktForm'),
    PrimaryKeyConstraint('ID', name='PK_tFirma'),
    Index('IX_Firma_AdresseId', 'AdresseID', mssql_clustered=False),
    Index('IX_Firma_CvrNummer', 'CVRNummer', mssql_clustered=False),
    Index('IX_Firma_PNummer', 'PNummer', mssql_clustered=False),
    Index('UQ__Firma__CBAB490AEC1BF8AA', 'FirmaIdentity', mssql_clustered=False, unique=True)
)

t_GenstandRegistrering = Table(
    'GenstandRegistrering', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagID', Integer, nullable=False),
    Column('GenstandType', Integer, nullable=False),
    Column('GenstandID', Integer, nullable=False),
    ForeignKeyConstraint(['GenstandType'], ['GenstandTypeOpslag.ID'], name='GenstandRegistrering_GenstandType'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='GenstandRegistrering_Sag'),
    PrimaryKeyConstraint('ID', name='PK_GenstandRegistrering')
)

t_Geometri = Table(
    'Geometri', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Oprettet', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('GeometriFormatID', Integer, nullable=False),
    Column('Data', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['GeometriFormatID'], ['GeometriFormatOpslag.ID'], name='FK_Geometri_GeometriFormat'),
    PrimaryKeyConstraint('ID', name='PK_Areal')
)

t_HierakiMedlem = Table(
    'HierakiMedlem', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('HierakiID', Integer, nullable=False),
    Column('ParentID', Integer),
    Column('EksternID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SortIndex', Integer),
    ForeignKeyConstraint(['HierakiID'], ['Hieraki.ID'], name='FK_HierakiMedlem_Hieraki'),
    ForeignKeyConstraint(['ParentID'], ['HierakiMedlem.ID'], name='FK_HierakiMedlem_HierakiMedlem'),
    PrimaryKeyConstraint('ID', name='PK_HierakiMedlem')
)

t_JournalArk = Table(
    'JournalArk', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagID', Integer, nullable=False),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='FK_JournalArk_Sag'),
    PrimaryKeyConstraint('ID', name='PK_JournalArk'),
    Index('IX_Journalark_SagID', 'SagID', mssql_clustered=False)
)

t_Lokation = Table(
    'Lokation', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('KommuneID', Integer, nullable=False),
    Column('Beskrivelse', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Oprettet', DateTime, nullable=False),
    Column('VejNavn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('HusNummer', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('PostNummerID', Integer, nullable=False),
    Column('ExternalSourceLastUpdate', DateTime),
    Column('ExternalSourceID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ExternalSourceName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Beliggenhed', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Historisk', Boolean, nullable=False, server_default=text('((0))')),
    Column('LokationIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    ForeignKeyConstraint(['KommuneID'], ['KommuneOpslag.ID'], name='FK_Lokation_KommuneOpslag'),
    ForeignKeyConstraint(['PostNummerID'], ['Postnummer.ID'], name='FK_Lokation_PostnummerOpslag'),
    PrimaryKeyConstraint('ID', name='PK_Lokation'),
    Index('IX_Lokation_LokationIdentity', 'LokationIdentity', mssql_clustered=False, unique=True),
    Index('UQ__Lokation__E0E2904AF48CD2E9', 'LokationIdentity', mssql_clustered=False, unique=True)
)

t_MailRecipient = Table(
    'MailRecipient', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('MailID', Integer, nullable=False),
    Column('Navn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Adresse', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('MailRecipientType', Integer),
    Column('CPR', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('CVR', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Pnummer', Unicode(30, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ContextSagID', Integer, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['MailID'], ['Mail.ID'], name='FK_MailRecipient_Mail'),
    PrimaryKeyConstraint('ID', name='PK_MailRecipient'),
    Index('IX_MailRecipient_MailID', 'MailID', mssql_clustered=False, mssql_include=['Navn', 'Adresse', 'MailRecipientType', 'CPR', 'CVR', 'Pnummer', 'ContextSagID'])
)

t_Matrikel = Table(
    'Matrikel', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Beskrivelse', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Oprettet', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('MatrikelNummer', Unicode(15, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('KommuneID', Integer, nullable=False),
    Column('Ejerlav', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('EjerlavKode', Integer),
    Column('ExternalSourceLastUpdate', DateTime),
    Column('ExternalSourceID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ExternalSourceName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Beliggenhed', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('LandsEjerlav', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('LandsEjerlavKode', Integer),
    Column('Historisk', Boolean, nullable=False, server_default=text('((0))')),
    Column('ArtID', Integer, nullable=False, server_default=text('((1))')),
    Column('Parcelnummer', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Ejerlejlighedsnummer', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('BeliggenhedAdresseID', Integer),
    Column('EjendomsNummer', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('MatrikelIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    Column('BFENummer', BigInteger, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['ArtID'], ['MatrikelArt.ID'], name='FK_Matrikel_MatrikelArt'),
    ForeignKeyConstraint(['BeliggenhedAdresseID'], ['Adresse.ID'], name='Matrikel_BeliggenhedAdresse'),
    ForeignKeyConstraint(['KommuneID'], ['KommuneOpslag.ID'], name='FK_Matrikel_Kommune'),
    PrimaryKeyConstraint('ID', name='PK_Matrikel'),
    Index('IX_Matrikel_Lookup', 'KommuneID', 'ArtID', 'LandsEjerlavKode', 'MatrikelNummer', 'Ejerlejlighedsnummer', 'Parcelnummer', mssql_clustered=False),
    Index('IX_Matrikel_Nummer', 'MatrikelNummer', 'LandsEjerlavKode', mssql_clustered=False, mssql_include=['Beskrivelse', 'Oprettet', 'KommuneID', 'Ejerlav', 'EjerlavKode', 'ExternalSourceLastUpdate', 'ExternalSourceID', 'ExternalSourceName', 'Beliggenhed', 'LandsEjerlav', 'Historisk', 'ArtID', 'Parcelnummer', 'Ejerlejlighedsnummer', 'BeliggenhedAdresseID', 'EjendomsNummer', 'MatrikelIdentity']),
    Index('UQ__Matrikel__08330CE19008BFA2', 'MatrikelIdentity', mssql_clustered=False, unique=True)
)

t_Person = Table(
    'Person', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Initialer', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Titel', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Uddannelse', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Stilling', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Note', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('CprNummer', String(11, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Koen', TINYINT, nullable=False),
    Column('AdresseID', Integer),
    Column('ExternalSourceLastUpdate', DateTime),
    Column('ExternalSourceID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ExternalSourceName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Navn', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('FoedeDato', DateTime),
    Column('Ansaettelsessted', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KontaktForm', Integer, nullable=False, server_default=text('((1))')),
    Column('CivilstandID', Integer),
    Column('AegtefaelleCPR', String(11, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('MorCPR', String(11, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('FarCPR', String(11, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KommuneID', Integer),
    Column('PartOprydningsKeyCheckSum', Integer),
    Column('TilmeldtDigitalPost', Boolean, nullable=False, server_default=text('((0))')),
    Column('PersonIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    ForeignKeyConstraint(['AdresseID'], ['Adresse.ID'], name='Person_Adresse'),
    ForeignKeyConstraint(['CivilstandID'], ['CivilstandOpslag.ID'], name='FK_Person_CivilstandOpslag'),
    ForeignKeyConstraint(['KommuneID'], ['KommuneOpslag.ID'], name='FK_Person_KommuneOpslag'),
    ForeignKeyConstraint(['KontaktForm'], ['KontaktFormOpslag.ID'], name='Person_KontaktForm'),
    PrimaryKeyConstraint('ID', name='PK_Person'),
    Index('IX_Mir_Person_FarCPR', 'FarCPR', mssql_clustered=False),
    Index('IX_Mir_Person_MorCPR', 'MorCPR', mssql_clustered=False),
    Index('IX_Person', 'CprNummer', mssql_clustered=False),
    Index('IX_Person_AdresseId', 'AdresseID', mssql_clustered=False),
    Index('IX_Person_Navn', 'Navn', mssql_clustered=False),
    Index('UQ__Person__90EA71019499C9E3', 'PersonIdentity', mssql_clustered=False, unique=True)
)

t_PostnummerKommune = Table(
    'PostnummerKommune', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('PostnummerID', Integer, nullable=False),
    Column('KommuneID', Integer, nullable=False),
    ForeignKeyConstraint(['KommuneID'], ['KommuneOpslag.ID'], name='FK_PostnummerKommune_KommuneOpslag'),
    ForeignKeyConstraint(['PostnummerID'], ['Postnummer.ID'], name='FK_PostnummerKommune_Postnummer'),
    PrimaryKeyConstraint('ID', name='PK_PostnummerKommune'),
    Index('IX_PostnummerKommune', 'PostnummerID', 'KommuneID', mssql_clustered=True)
)

t_RelateretSag = Table(
    'RelateretSag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('RelateretFraSagID', Integer, nullable=False),
    Column('RelateretSagID', Integer, nullable=False),
    ForeignKeyConstraint(['RelateretFraSagID'], ['Sag.ID'], name='RelateretSag_FraSag'),
    ForeignKeyConstraint(['RelateretSagID'], ['Sag.ID'], name='RelateretSag_TilSag'),
    PrimaryKeyConstraint('ID', name='PK_JournalUnderjournaler')
)

t_SagEksternIdentitet = Table(
    'SagEksternIdentitet', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagID', Integer, nullable=False),
    Column('Oprettet', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('EksternSystemID', Integer, nullable=False),
    Column('EksternIdentitet', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Status', TINYINT, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['EksternSystemID'], ['KnownEksterntSystem.ID'], name='FK_SagEksternIdentitet_KnownEksterntSystem'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='FK_SagEksternIdentitet_Sag'),
    PrimaryKeyConstraint('ID', name='PK_SagEksternIdentitet'),
    Index('IX_SagEksternIdentitet_SagID', 'SagID', mssql_clustered=False)
)

t_SagMetaData = Table(
    'SagMetaData', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagID', Integer, nullable=False),
    Column('KeyName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Value', Unicode(400, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='FK_SagMetaData_Sag'),
    PrimaryKeyConstraint('ID', name='PK_SagMetaData'),
    Index('IX_SagMetaData', 'SagID', mssql_clustered=True)
)

t_SagSagsType = Table(
    'SagSagsType', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagId', Integer, nullable=False),
    Column('SagsTypeId', Integer, nullable=False),
    ForeignKeyConstraint(['SagId'], ['Sag.ID'], name='FK_SagSagsType_Sag'),
    ForeignKeyConstraint(['SagsTypeId'], ['SagsType.Id'], name='FK_SagSagsType_SagsType'),
    PrimaryKeyConstraint('Id', name='PK__SagSagsT__3214EC07ADBA8576'),
    Index('UQ_Sag_SagsType', 'SagId', 'SagsTypeId', mssql_clustered=False, unique=True)
)

t_SagsHenvisning = Table(
    'SagsHenvisning', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('HenvisningFraID', Integer, nullable=False),
    Column('HenvisningTilID', Integer, nullable=False),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    ForeignKeyConstraint(['HenvisningFraID'], ['Sag.ID'], name='SagHenvisning_SagFra'),
    ForeignKeyConstraint(['HenvisningTilID'], ['Sag.ID'], name='SagHenvisning_SagTil'),
    PrimaryKeyConstraint('ID', name='PK_JournalHenvisning')
)

t_SagsStatus = Table(
    'SagsStatus', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Orden', Integer, nullable=False),
    Column('SagsTilstand', Integer, nullable=False),
    Column('RequireComments', Boolean, nullable=False, server_default=text('((0))')),
    Column('IsDeleted', Boolean, nullable=False, server_default=text('((0))')),
    Column('SagsForklaede', Integer, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['SagsTilstand'], ['SagsTilstandOpslag.ID'], name='SagsStatus_SagsTilstand'),
    PrimaryKeyConstraint('ID', name='PK_SagsStgatus')
)

t_SagsfeltIndhold = Table(
    'SagsfeltIndhold', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagID', Integer, nullable=False),
    Column('SagsfeltID', Integer, nullable=False),
    Column('Vaerdi', Unicode(1024, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='FK_SagsfeltVaerdi_Sag'),
    ForeignKeyConstraint(['SagsfeltID'], ['SagsFelt.Id'], name='FK_SagsfeltVaerdi_Sagsfelt'),
    PrimaryKeyConstraint('ID', name='PK_SagsfeltIndhold_Id'),
    Index('AK_SagsfeltIndhold_SagID_SagsfeltID', 'SagsfeltID', 'SagID', mssql_clustered=False, unique=True)
)

t_SkabelonType = Table(
    'SkabelonType', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SkabelonTypeGruppeID', Integer, nullable=False, server_default=text('((0))')),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    Column('GrundSkabelonID', Integer),
    ForeignKeyConstraint(['GrundSkabelonID'], ['SkabelonGrundSkabelon.ID'], name='FK_SkabelonType_SkabelonGrundSkabelon'),
    ForeignKeyConstraint(['SkabelonTypeGruppeID'], ['SkabelonTypeGruppe.ID'], name='Skabelontype_SkabelonTypeGruppe'),
    PrimaryKeyConstraint('ID', name='PK_tblSkabelontype'),
    Index('IX_SkabelonType', 'SkabelonTypeGruppeID', mssql_clustered=True)
)

t_Stylesheet = Table(
    'Stylesheet', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Data', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('StylesheetTypeID', Integer, nullable=False),
    Column('Gruppering', Integer, nullable=False, server_default=text('((1))')),
    ForeignKeyConstraint(['StylesheetTypeID'], ['StylesheetTypeOpslag.ID'], name='FK_Stylesheets_StylesheetTypeOpslag'),
    PrimaryKeyConstraint('ID', name='PK_Stylesheets')
)

t_TidsPostering = Table(
    'TidsPostering', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('TidsPosteringKategoriID', Integer, nullable=False),
    Column('Tekst', String(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Oprettet', DateTime, nullable=False),
    Column('PosteringsDato', DateTime, nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('ContextSagID', Integer),
    Column('ContextDelforloebID', Integer),
    Column('ContextErindringID', Integer),
    ForeignKeyConstraint(['TidsPosteringKategoriID'], ['TidsPosteringKategori.Id'], name='FK_TidsPostering_TidsPosteringKategori'),
    PrimaryKeyConstraint('Id', name='PK__TidsPost__3214EC07C73335D6'),
    Index('IX_TidsPostering_Column', 'ContextSagID', mssql_clustered=False)
)

t_Vej = Table(
    'Vej', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('VejNummer', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Oprettet', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('KilometerFra', Float(53)),
    Column('KilometerTil', Float(53)),
    Column('Position', Unicode(30, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KommuneID', Integer, nullable=False),
    Column('ExternalSourceLastUpdate', DateTime),
    Column('ExternalSourceID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ExternalSourceName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Beliggenhed', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Historisk', Boolean, nullable=False, server_default=text('((0))')),
    Column('VejIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    ForeignKeyConstraint(['KommuneID'], ['KommuneOpslag.ID'], name='Vej_Kommune'),
    PrimaryKeyConstraint('ID', name='PK_Vej'),
    Index('IX_Vej_VejIdentity', 'VejIdentity', mssql_clustered=False, unique=True),
    Index('UQ__Vej__A30BABC0620C61C4', 'VejIdentity', mssql_clustered=False, unique=True)
)

t_WebWidgetSagstype = Table(
    'WebWidgetSagstype', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagstypeID', Integer),
    Column('WebWidgetId', Integer),
    ForeignKeyConstraint(['SagstypeID'], ['SagsType.Id'], name='FK__WebWidget__Sagst__11DF9047'),
    ForeignKeyConstraint(['WebWidgetId'], ['WebWidget.ID'], name='FK__WebWidget__WebWi__12D3B480'),
    PrimaryKeyConstraint('ID', name='PK__WebWidge__3214EC27AC5F4322')
)

t_AdresseGenstand = Table(
    'AdresseGenstand', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Uuid', Uuid, nullable=False),
    Column('Status', Integer, nullable=False),
    Column('FoerstOprettet', DateTime, nullable=False),
    Column('SidstAendret', DateTime, nullable=False),
    Column('Vejkode', Unicode(4, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Vejnavn', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('AdresseringsVejnavn', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('HusNummer', Unicode(4, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Etage', Unicode(2, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Doer', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SupplerendeBynavn', Unicode(34, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('PostNummer', Unicode(5, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('PostNummerNavn', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('StormodtagerPostNummer', Unicode(5, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('StormodtagerPostNummerNavn', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KommuneKode', Integer, nullable=False),
    Column('KommuneNavn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('EsrEjendomsNummer', Integer),
    Column('Etrs89KoordinatEast', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Etrs89KoordinatNorth', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Wgs84KoordinatLatitude', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Wgs84KoordinatLongtitude', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Noejagtighed', Unicode(1, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Kilde', Integer),
    Column('TeknikStandard', Unicode(2, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Tekstretning', Unicode(6, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DdknM100', Unicode(15, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DdknKm1', Unicode(12, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DdknKm10', Unicode(11, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('AdressepunktAendringsDato', DateTime),
    Column('AdgangsadresseUuid', Uuid, nullable=False),
    Column('AdgangsadresseStatus', Integer, nullable=False),
    Column('AdgangsadresseOprettet', DateTime),
    Column('AdgangsadresseAendret', DateTime),
    Column('AdgangsadresseKvh', Unicode(12, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('RegionsKode', Unicode(4, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('RegionsNavn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Kvhx', Unicode(19, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('SogneKode', Unicode(4, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SogneNavn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('PolitikredsKode', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('PolitikredsNavn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('RetskredsKode', Unicode(4, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('RetskredsNavn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OpstillingskredsKode', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OpstillingskredsNavn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Zone', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('JordstykkeEjerlavkode', Unicode(7, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('JordstykkeEjerlavNavn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('JordstykkeMatrikelNummer', Unicode(7, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('JordstykkeEsrEjendomsNummer', Integer),
    Column('EjendomID', Integer),
    Column('KommuneID', Integer, nullable=False),
    Column('Beskrivelse', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Oprettet', DateTime, nullable=False),
    Column('Beliggenhed', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Historisk', Boolean, nullable=False),
    Column('AdresseIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    Column('ExternalSourceLastUpdate', DateTime),
    Column('ExternalSourceID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ExternalSourceName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['EjendomID'], ['Ejendom.ID'], name='FK_AdresseGenstand_Ejendom'),
    ForeignKeyConstraint(['KommuneID'], ['KommuneOpslag.ID'], name='FK_AdresseGenstand_KommuneOpslag'),
    PrimaryKeyConstraint('ID', name='PK__AdresseG__3214EC276A7F4E13'),
    Index('IX_AdresseGenstand_EsrEjendomsNummer', 'EsrEjendomsNummer', mssql_clustered=False),
    Index('UQ__AdresseG__ACE2A91F523E0269', 'AdresseIdentity', mssql_clustered=False, unique=True)
)

t_Ansaettelsessted = Table(
    'Ansaettelsessted', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('CustomAdID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Beskrivelse', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('PostAdresseID', Integer, nullable=False),
    Column('FysiskAdresseID', Integer, nullable=False),
    Column('Aabningstider', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('EanNummer', Unicode(15, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Leder', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('CvrNummer', Unicode(12, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('PNummer', Unicode(12, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Fritekst1', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Fritekst2', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('FagomraadeID', Integer),
    Column('Indjournaliseringsfolder', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DefaultEmneplanID', Integer),
    Column('HierakiMedlemID', Integer, nullable=False),
    Column('Webside', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DefaultSagSecuritySetID', Integer),
    Column('VisAdgangsListeVedOpretSag', Boolean, server_default=text('((0))')),
    Column('TilladBrugerAtSkiftePassword', Boolean, nullable=False, server_default=text('((1))')),
    Column('TilladPublicering', Boolean, nullable=False, server_default=text('((1))')),
    Column('EksterneAdviseringer', Integer, nullable=False, server_default=text('((0))')),
    Column('AutomatiskErindringVedJournalisering', Boolean, nullable=False, server_default=text('((1))')),
    Column('StandardAktindsigtVedJournalisering', Boolean, nullable=False, server_default=text('((1))')),
    Column('VisCPR', Boolean, nullable=False, server_default=text('((1))')),
    Column('AnsaettelsesstedIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    Column('VisCVR', Boolean, nullable=False, server_default=text('((1))')),
    ForeignKeyConstraint(['DefaultEmneplanID'], ['EmnePlan.ID'], name='FK_Ansaettelsessted_EmnePlan'),
    ForeignKeyConstraint(['DefaultSagSecuritySetID'], ['SecuritySet.ID'], name='FK_Ansaettelsessted_DefaultSecuritySet'),
    ForeignKeyConstraint(['FagomraadeID'], ['FagOmraade.ID'], name='FK_Ansaettelsessted_FagOmraade'),
    ForeignKeyConstraint(['FysiskAdresseID'], ['Adresse.ID'], name='FK_Ansaettelsessted_FysiskAdresse'),
    ForeignKeyConstraint(['HierakiMedlemID'], ['HierakiMedlem.ID'], name='FK_Ansaettelsessted_HierakiMedlem'),
    ForeignKeyConstraint(['PostAdresseID'], ['Adresse.ID'], name='FK_Ansaettelsessted_Adresse'),
    PrimaryKeyConstraint('ID', name='PK_Ansaettelsessted'),
    Index('UQ__Ansaette__85CA8426E6BAA778', 'AnsaettelsesstedIdentity', mssql_clustered=False, unique=True)
)

t_CprBrokerPersonReference = Table(
    'CprBrokerPersonReference', metadata,
    Column('PersonId', Integer, primary_key=True),
    Column('CprBrokerUuid', Uuid, primary_key=True),
    ForeignKeyConstraint(['PersonId'], ['Person.ID'], ondelete='CASCADE', name='FK__CprBroker__Perso__174363E2'),
    PrimaryKeyConstraint('PersonId', 'CprBrokerUuid', name='PK__CprBroke__B196D940BD822C9E')
)

t_DagsordenpunktFeltIndhold = Table(
    'DagsordenpunktFeltIndhold', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DagsordenpunktFeltId', Integer, nullable=False),
    Column('Html', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('Tekst', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('FeltIndholdIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    Column('TilknyttetStjernehoering', Boolean, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['DagsordenpunktFeltId'], ['DagsordenpunktFelt.ID'], name='FK_DagsordenpunktFeltIndhold_DagsordenpunktFeltTypeId'),
    PrimaryKeyConstraint('Id', name='PK_DagsordenpunktFeltIndhold'),
    Index('UQ__Dagsorde__FC17B0B15FCA4EC3', 'FeltIndholdIdentity', mssql_clustered=False, unique=True)
)

t_DagsordenpunktTypeDagsordenpunktFelt = Table(
    'DagsordenpunktTypeDagsordenpunktFelt', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DagsordenpunktFeltId', Integer, nullable=False),
    Column('Sortering', Integer, nullable=False),
    Column('DagsordenpunkttypeID', Integer, nullable=False),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    Column('IsBuiltin', Boolean, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['DagsordenpunktFeltId'], ['DagsordenpunktFelt.ID'], name='FK_DagsordenpunktTypeDagsordenpunktFelt_DagsordenpunktFelt'),
    ForeignKeyConstraint(['DagsordenpunkttypeID'], ['DagsordenpunktType.ID'], name='FK_DagsordenpunktTypeDagsordenpunktFelt_DagsordenpunktType'),
    PrimaryKeyConstraint('ID', name='PK_DagsordenpunktTypeDagsordenpunktFeltID'),
    Index('AK_DagsordenpunktTypeDagsordenpunktFelt_DagsordenpunktFeltId_DagsordenpunkttypeID', 'DagsordenpunktFeltId', 'DagsordenpunkttypeID', mssql_clustered=False, unique=True),
    Index('AK_DagsordenpunktTypeDagsordenpunktFelt_Sortering_DagsordenpunkttypeID', 'Sortering', 'DagsordenpunkttypeID', mssql_clustered=False, unique=True)
)

t_EmneOrd = Table(
    'EmneOrd', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('EmneOrdGruppeID', Integer, nullable=False),
    Column('ErAktiv', Boolean, server_default=text('((1))')),
    ForeignKeyConstraint(['EmneOrdGruppeID'], ['EmneOrdGruppe.ID'], name='EmneOrd_EmneOrdGruppe'),
    PrimaryKeyConstraint('ID', name='PK_tblEmneOrd')
)

t_EmneplanNummerAfloeserNummer = Table(
    'EmneplanNummerAfloeserNummer', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('OprindeligEmnePlanNummerID', Integer, nullable=False),
    Column('AfloserEmnePlanNummerID', Integer, nullable=False),
    ForeignKeyConstraint(['AfloserEmnePlanNummerID'], ['EmnePlanNummer.ID'], name='FK_OprindeligEmnePlanNummer_EmnePlanNummer'),
    ForeignKeyConstraint(['OprindeligEmnePlanNummerID'], ['EmnePlanNummer.ID'], name='FK_EmneplanNummerAfloeserNummer_EmnePlanNummer'),
    PrimaryKeyConstraint('ID', name='PK_EmneplanNummerAfloeserNummer')
)

t_ErindringTypeOpslag = Table(
    'ErindringTypeOpslag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('KeyName', Unicode(30, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    Column('SynlighedIDage', Integer),
    Column('DeadlineIDage', Integer),
    Column('HierakiMedlemID', Integer),
    Column('SkjulErindring', Boolean, nullable=False, server_default=text('((0))')),
    Column('TilladKunSystemhaandtering', Boolean, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['HierakiMedlemID'], ['HierakiMedlem.ID'], name='FK_ErindringTypeOpslag_HierakiMedlem'),
    PrimaryKeyConstraint('ID', name='PK_ErindringType')
)

t_Facet = Table(
    'Facet', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Nummer', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('FacetTypeID', Integer, nullable=False),
    Column('Navn', Unicode(150, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ErBrugerDefineret', Boolean),
    Column('BevaringID', Integer),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Boolean),
    Column('Oprettet', DateTime),
    Column('Rettet', DateTime),
    Column('Udgaaet', DateTime),
    ForeignKeyConstraint(['BevaringID'], ['BevaringOpslag.ID'], name='Facet_Bevaring'),
    ForeignKeyConstraint(['FacetTypeID'], ['FacetType.ID'], name='Facet_FacetType'),
    PrimaryKeyConstraint('ID', name='PK_tblInstitution'),
    Index('IX_Facet_FacetType', 'FacetTypeID', mssql_clustered=True)
)

t_FirmaAttentionPerson = Table(
    'FirmaAttentionPerson', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('FirmaID', Integer, nullable=False),
    Column('Navn', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('AdresseID', Integer, nullable=False),
    Column('Telefonnummer', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('EmailAdresse', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Afdeling', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['AdresseID'], ['Adresse.ID'], name='FK_FirmaAttentionPerson_Adresse'),
    ForeignKeyConstraint(['FirmaID'], ['Firma.ID'], name='FK_FirmaAttentionPerson_Firma'),
    PrimaryKeyConstraint('ID', name='PK_FirmaAttentionPerson'),
    Index('IX_FirmaAttentionPerson', 'FirmaID', mssql_clustered=True)
)

t_FirmaPart = Table(
    'FirmaPart', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('FirmaID', Integer, nullable=False),
    Column('PartType', Integer, nullable=False),
    Column('PartID', Integer, nullable=False),
    Column('FirmaPartRolleID', Integer),
    Column('OprindeligAdresseID', Integer),
    Column('Oprettet', DateTime, nullable=False, server_default=text('(getdate())')),
    ForeignKeyConstraint(['FirmaID'], ['Firma.ID'], name='PersonFirma_Firma'),
    ForeignKeyConstraint(['FirmaPartRolleID'], ['FirmaPartRolle.ID'], name='FirmaPart_FirmaPartRolle'),
    ForeignKeyConstraint(['OprindeligAdresseID'], ['Adresse.ID'], name='FirmaPart_OprindeligAdresse'),
    ForeignKeyConstraint(['PartType'], ['PartTypeOpslag.ID'], name='FK_FirmaPart_PartTypeOpslag'),
    PrimaryKeyConstraint('ID', name='PK_PersonFirma')
)

t_FkOrgHierarkiMedlemReference = Table(
    'FkOrgHierarkiMedlemReference', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('HierarkiMedlemID', Integer, nullable=False),
    Column('FkOrgUuid', Uuid, nullable=False),
    ForeignKeyConstraint(['HierarkiMedlemID'], ['HierakiMedlem.ID'], name='FK_FkorgHierarkimedlemreference_Hierarkimedlem')
)

t_KnownEksterntSystemStylesheetMap = Table(
    'KnownEksterntSystemStylesheetMap', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('KnownEksternSystemID', Integer, nullable=False),
    Column('Notat', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SagstypeVaerdi', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('StylesheetID', Integer, nullable=False),
    ForeignKeyConstraint(['KnownEksternSystemID'], ['KnownEksterntSystem.ID'], name='FK_KnownEksterntSystemStylesheetMap_KnownEksterntSystemOpslag'),
    ForeignKeyConstraint(['StylesheetID'], ['Stylesheet.ID'], name='FK_KnownEksterntSystemStylesheetMap_Stylesheet'),
    PrimaryKeyConstraint('ID', name='PK_KnownEksterntSystemStylesheetMap')
)

t_MatrikelEjendom = Table(
    'MatrikelEjendom', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('MatrikelID', Integer, nullable=False),
    Column('EjendomID', Integer, nullable=False),
    ForeignKeyConstraint(['EjendomID'], ['Ejendom.ID'], name='FK_MatrikelEjendom_Ejendom'),
    ForeignKeyConstraint(['MatrikelID'], ['Matrikel.ID'], name='FK_MatrikelEjendom_Matrikel'),
    PrimaryKeyConstraint('ID', name='PK_MatrikelEjendom')
)

t_PubliseringTarget = Table(
    'PubliseringTarget', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('PubliseringIndstillingerID', Integer, nullable=False),
    Column('OutputPath', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OutputFileNameWithoutExtension', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('XslStylesheetID', Integer, nullable=False),
    Column('CssStylesheetID', Integer, nullable=False),
    Column('FileOutputBehavior', TINYINT, nullable=False, server_default=text('((0))')),
    Column('FolderNameBehavior', TINYINT, nullable=False, server_default=text('((0))')),
    Column('FolderNamePattern', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('FileOutputRule', TINYINT, nullable=False, server_default=text('((0))')),
    Column('PrepareRule', TINYINT, nullable=False, server_default=text('((2))')),
    ForeignKeyConstraint(['CssStylesheetID'], ['Stylesheet.ID'], name='FK_PubliseringTarget_Stylesheet1'),
    ForeignKeyConstraint(['PubliseringIndstillingerID'], ['PubliseringIndstillinger.ID'], name='FK_PubliseringTarget_PubliseringIndstillinger'),
    ForeignKeyConstraint(['XslStylesheetID'], ['Stylesheet.ID'], name='FK_PubliseringTarget_Stylesheet'),
    PrimaryKeyConstraint('ID', name='PK_PubliseringTarget')
)

t_SagSkabelon = Table(
    'SagSkabelon', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('XmlData', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('XmlSchema', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('SchemaVersion', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('SagSkabelonKategoriID', Integer),
    Column('SagsTitel', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ErBeskyttet', Boolean, nullable=False),
    Column('ForudFyldSagsbehandler', Boolean, nullable=False),
    Column('SecuritySetID', Integer),
    Column('EmnePlanNummerID', Integer),
    Column('FacetID', Integer),
    Column('BrugerID', Integer),
    Column('AnsaettelsesstedID', Integer),
    Column('FagomraadeID', Integer),
    Column('StyringsreolHyldeID', Integer),
    Column('AnvendSikkerhedFraAnsaettelssted', Boolean, nullable=False),
    Column('Hierakimedlem', Integer),
    Column('PartForlangAltid', Boolean, nullable=False, server_default=text('((0))')),
    Column('PartForlangAltidPrimaer', Boolean, nullable=False, server_default=text('((0))')),
    Column('PartAnvendIkke', Boolean, nullable=False, server_default=text('((0))')),
    Column('GenstandForlangAltid', Boolean, nullable=False, server_default=text('((0))')),
    Column('Aktiv', Boolean, nullable=False, server_default=text('((1))')),
    Column('SagSkabelonIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    Column('SagsTypeId', Integer, nullable=False, server_default=text('((1))')),
    Column('SagsTitelKanAendresFoerOprettelse', Boolean, nullable=False, server_default=text('((1))')),
    Column('SagsTitelKanAendresEfterOprettelse', Boolean, nullable=False, server_default=text('((1))')),
    Column('AnsaettelsesstedKanAendresFoerOprettelse', Boolean, nullable=False, server_default=text('((1))')),
    Column('AnsaettelsesstedKanAendresEfterOprettelse', Boolean, nullable=False, server_default=text('((1))')),
    Column('StyringsreolKanAendresFoerOprettelse', Boolean, nullable=False, server_default=text('((1))')),
    Column('StyringsreolKanAendresEfterOprettelse', Boolean, nullable=False, server_default=text('((1))')),
    Column('DelforloebKanTilfoejesFoerOprettelse', Boolean, nullable=False, server_default=text('((1))')),
    Column('DelforloebKanTilfoejesEfterOprettelse', Boolean, nullable=False, server_default=text('((1))')),
    Column('DelforloebKanFjernesFoerOprettelse', Boolean, nullable=False, server_default=text('((1))')),
    Column('DelforloebKanFjernesEfterOprettelse', Boolean, nullable=False, server_default=text('((1))')),
    Column('ErBeskyttetKanAendresFoerOprettelse', Boolean, nullable=False, server_default=text('((1))')),
    Column('ErBeskyttetKanAendresEfterOprettelse', Boolean, nullable=False, server_default=text('((1))')),
    Column('AdgangslisteKanAendresFoerOprettelse', Boolean, nullable=False, server_default=text('((1))')),
    Column('AdgangslisteKanAendresEfterOprettelse', Boolean, nullable=False, server_default=text('((1))')),
    Column('EmneplanNummerOgFacetKanAendresFoerOprettelse', Boolean, nullable=False, server_default=text('((1))')),
    Column('EmneplanNummerOgFacetKanAendresEfterOprettelse', Boolean, nullable=False, server_default=text('((1))')),
    ForeignKeyConstraint(['Hierakimedlem'], ['HierakiMedlem.ID'], name='FK_SagSkabelon_Hierakimedlem'),
    ForeignKeyConstraint(['SagSkabelonKategoriID'], ['SagSkabelonKategori.ID'], name='FK_SagSkabelon_SagSkabelonKategori'),
    ForeignKeyConstraint(['SagsTypeId'], ['SagsType.Id'], name='FK_SagSkabelon_SagsType'),
    PrimaryKeyConstraint('ID', name='PK_SagSkabelon'),
    Index('UQ__SagSkabe__593A23081D7A5543', 'SagSkabelonIdentity', mssql_clustered=False, unique=True)
)

t_SagSkabelonPart = Table(
    'SagSkabelonPart', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('SagSkabelonID', Integer, nullable=False),
    Column('FirmaID', Integer),
    Column('PersonID', Integer),
    Column('PartTypeID', Integer, nullable=False),
    Column('Primaer', Boolean, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['FirmaID'], ['Firma.ID'], name='FK_SagSkabelonPart_Firma'),
    ForeignKeyConstraint(['PartTypeID'], ['PartTypeOpslag.ID'], name='FK_SagSkabelonPart_PartTypeOpslag'),
    ForeignKeyConstraint(['PersonID'], ['Person.ID'], name='FK_SagSkabelonPart_Part'),
    Index('CK_SagSkabelonPart_TilladIkkeSammePartToGange', 'FirmaID', 'SagSkabelonID', 'PersonID', mssql_clustered=False, unique=True)
)

t_Sikkerhedsgruppe = Table(
    'Sikkerhedsgruppe', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('HierakiMedlemID', Integer, nullable=False),
    Column('EksternID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ObjectSid', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['HierakiMedlemID'], ['HierakiMedlem.ID'], name='FK_Sikkerhedsgruppe_HierakiMedlem'),
    PrimaryKeyConstraint('ID', name='PK_tblOrganisationsEnhed'),
    Index('IX_Sikkerhedsgruppe', 'HierakiMedlemID', mssql_clustered=True),
    Index('IX_Sikkerhedsgruppe_ID', 'ID', mssql_clustered=False, mssql_include=['Navn', 'EksternID', 'ObjectSid'])
)

t_AdministrativProfilAnsaettelsessteder = Table(
    'AdministrativProfilAnsaettelsessteder', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('AdministrativProfilID', Integer, nullable=False),
    Column('AnsaettelsesstedID', Integer, nullable=False),
    ForeignKeyConstraint(['AdministrativProfilID'], ['AdministrativProfil.ID'], name='FK_AdministrativProfil_Profil'),
    ForeignKeyConstraint(['AnsaettelsesstedID'], ['Ansaettelsessted.ID'], name='GK_AdministrativProfil_Ansaettelessted'),
    PrimaryKeyConstraint('ID', name='PK_AdministrativProfilAnsaettelsessteder')
)

t_AnsaettelsesstedEksternMapning = Table(
    'AnsaettelsesstedEksternMapning', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('EksternID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('AnsaettelsesstedID', Integer, nullable=False),
    Column('DefaultSikkerhedsGruppeID', Integer),
    Column('PassivSikkerhedsGruppeID', Integer),
    Column('PassivAnsaettelsesstedID', Integer),
    Column('EksternSystemID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), server_default=text("(N'BSK')")),
    ForeignKeyConstraint(['AnsaettelsesstedID'], ['Ansaettelsessted.ID'], name='FK_AnsaettelsesstedEksternMapning_Ansaettelsessted'),
    ForeignKeyConstraint(['DefaultSikkerhedsGruppeID'], ['Sikkerhedsgruppe.ID'], name='FK_AnsaettelsesstedEksternMapning_DefaultSikkerhdsGruppe'),
    ForeignKeyConstraint(['PassivAnsaettelsesstedID'], ['Ansaettelsessted.ID'], name='FK_AnsaettelsesstedEksternMapning_Ansaettelsessted_Passiv'),
    ForeignKeyConstraint(['PassivSikkerhedsGruppeID'], ['Sikkerhedsgruppe.ID'], name='FK_AnsaettelsesstedEksternMapning_Sikkerhedsgruppe_passiv'),
    PrimaryKeyConstraint('ID', name='PK_AnsaettelsesstedEksternMapning')
)

t_AnsaettelsesstedStandardSikkerhedsGrupper = Table(
    'AnsaettelsesstedStandardSikkerhedsGrupper', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('AnsaettelsesstedID', Integer, nullable=False),
    Column('SikkerhedsgruppeID', Integer, nullable=False),
    ForeignKeyConstraint(['AnsaettelsesstedID'], ['Ansaettelsessted.ID'], name='FK_AnsaettelsesstedStandardSikkerhedsGrupper_Ansaettelsessted'),
    ForeignKeyConstraint(['SikkerhedsgruppeID'], ['Sikkerhedsgruppe.ID'], name='FK_AnsaettelsesstedStandardSikkerhedsGrupper_Sikkerhedsgruppe'),
    PrimaryKeyConstraint('ID', name='PK_AnsaettelsesstedStandardSikkerhedsGrupper')
)

t_Bruger = Table(
    'Bruger', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('LogonID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('LogonPassword', Unicode(88, 'SQL_Danish_Pref_CP1_CI_AS'), server_default=text("(N'd41d8cd98f00b204e9800998ecf8427e')")),
    Column('LogonSalt', Unicode(88, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('LogonAlgorithm', Unicode(6, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False, server_default=text("('MD5')")),
    Column('LogonIterations', Integer),
    Column('LogonFailedAttemptCount', Integer, nullable=False, server_default=text('((0))')),
    Column('LogonTemporaryLockedExpiration', DateTime),
    Column('Navn', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Titel', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Stilling', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KontorID', Integer, server_default=text('((0))')),
    Column('FagomraadeID', Integer, nullable=False),
    Column('Lokale', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('AdresseID', Integer),
    Column('AnsaettelsesstedID', Integer, nullable=False),
    Column('Status', Integer, nullable=False, server_default=text('((0))')),
    Column('EksternID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ObjectSid', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('UserPrincipalName', Unicode(254, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('BrugerIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    Column('ErSystembruger', Boolean, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['AdresseID'], ['Adresse.ID'], name='Bruger_Adresse'),
    ForeignKeyConstraint(['AnsaettelsesstedID'], ['Ansaettelsessted.ID'], name='FK_Bruger_Ansaettelsessted'),
    ForeignKeyConstraint(['FagomraadeID'], ['FagOmraade.ID'], name='Bruger_FagOmraade'),
    ForeignKeyConstraint(['KontorID'], ['Kontor.ID'], name='Bruger_Kontor'),
    PrimaryKeyConstraint('ID', name='PK_Bruger'),
    Index('IX_Bruger_BrugerIdentity', 'BrugerIdentity', mssql_clustered=False, unique=True),
    Index('IX_Bruger_LoginID', 'LogonID', mssql_clustered=False, unique=True),
    Index('IX_Bruger_Logon', 'LogonID', 'LogonPassword', mssql_clustered=False, unique=True),
    Index('UQ__Bruger__52471EC1E2CFACDD', 'BrugerIdentity', mssql_clustered=False, unique=True)
)

t_EmneordOvergruppeEmnePlanNummer = Table(
    'EmneordOvergruppeEmnePlanNummer', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('EmneordOvergruppeID', Integer, nullable=False),
    Column('FacetID', Integer, nullable=False),
    Column('EmnePlanNummerID', Integer, nullable=False),
    ForeignKeyConstraint(['EmnePlanNummerID'], ['EmnePlanNummer.ID'], name='FK_EmneordOvergruppeEmnePlanNummer_EmnePlanNummer'),
    ForeignKeyConstraint(['EmneordOvergruppeID'], ['EmneOrdOvergruppe.ID'], name='FK_EmneordOvergruppeEmnePlanNummer_EmneordOvergruppe'),
    ForeignKeyConstraint(['FacetID'], ['Facet.ID'], name='FK_EmneordOvergruppeEmnePlanNummer_Facet'),
    PrimaryKeyConstraint('Id', name='PK__EmneordO__3214EC070E8BF235')
)

t_ErindringRegel = Table(
    'ErindringRegel', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('Alder', Integer, nullable=False),
    Column('AntalDage', Integer, nullable=False),
    Column('BeforeOrAfter', Boolean, nullable=False),
    Column('SagSkabelonID', Integer, nullable=False),
    ForeignKeyConstraint(['SagSkabelonID'], ['SagSkabelon.ID'], name='FK_ErindringRegel_SagSkabelon')
)

t_FkOrgAnsaettelsesstedReference = Table(
    'FkOrgAnsaettelsesstedReference', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('AnsaettelsesstedID', Integer, nullable=False),
    Column('FkOrgUuid', Uuid, nullable=False),
    ForeignKeyConstraint(['AnsaettelsesstedID'], ['Ansaettelsessted.ID'], name='FK_FkorgAnsaettelsesstedreference_Ansaettelsessted')
)

t_FlowSkabelon = Table(
    'FlowSkabelon', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('FlowForloeb', Integer, nullable=False),
    Column('AnsaettelsesstedID', Integer, nullable=False),
    ForeignKeyConstraint(['AnsaettelsesstedID'], ['Ansaettelsessted.ID'], name='FK_FlowSkabelon_Ansaettelsessted'),
    PrimaryKeyConstraint('ID', name='PK__FlowSkab__3214EC27F20B6AE6')
)

t_MapNemJournaliseringSagSkabelon = Table(
    'MapNemJournaliseringSagSkabelon', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Blanket', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS')),
    Column('KLE', Unicode(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SagSkabelonID', Integer),
    Column('Aktiv', Boolean, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['SagSkabelonID'], ['SagSkabelon.ID'], name='FK_MapNemJournalisering_SagSkabelon'),
    PrimaryKeyConstraint('Id', name='PK_MapNemJournaliseringSagSkabelon')
)

t_SagEmneOrd = Table(
    'SagEmneOrd', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagID', Integer, nullable=False),
    Column('EmneOrdID', Integer, nullable=False),
    ForeignKeyConstraint(['EmneOrdID'], ['EmneOrd.ID'], name='SagEmneOrd_EmneOrd'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='SagEmneOrd_Sag'),
    PrimaryKeyConstraint('ID', name='PK_SagEmneOrd'),
    Index('IX_SagEmneOrd_Sag', 'SagID', mssql_clustered=False)
)

t_SagSkabelonEmneord = Table(
    'SagSkabelonEmneord', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('SagSkabelonID', Integer, nullable=False),
    Column('EmneordID', Integer, nullable=False),
    ForeignKeyConstraint(['EmneordID'], ['EmneOrd.ID'], name='FK_SagSkabelonEmneord_Emneord'),
    ForeignKeyConstraint(['SagSkabelonID'], ['SagSkabelon.ID'], name='FK_SagSkabelonEmneord_SagSkabelon'),
    Index('CK_SagSkabelonEmneord_Unique', 'SagSkabelonID', 'EmneordID', mssql_clustered=False, unique=True)
)

t_SagSkabelonTilknyttetSagSkabelon = Table(
    'SagSkabelonTilknyttetSagSkabelon', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagSkabelonID', Integer, nullable=False),
    Column('SagSkabelonTilknyttetSagSkabelonID', Integer, nullable=False),
    ForeignKeyConstraint(['SagSkabelonID'], ['SagSkabelon.ID'], name='FK_SagSkabelonTilknyttetSagSkabelon_SagSkabelon'),
    ForeignKeyConstraint(['SagSkabelonTilknyttetSagSkabelonID'], ['SagSkabelon.ID'], name='FK_SagSkabelonTilknyttetSagSkabelon_TilknyttetSagSkabelon'),
    PrimaryKeyConstraint('ID', name='PK_SagSkabelonTilknyttetSagSkabelon')
)

t_SagSkabelonTitler = Table(
    'SagSkabelonTitler', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('Titel', String(1000, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('SagSkabelonID', Integer, nullable=False),
    ForeignKeyConstraint(['SagSkabelonID'], ['SagSkabelon.ID'], name='FK_SagSkabelonTitler_SagSkabelon')
)

t_SagsFeltSagSkabelon = Table(
    'SagsFeltSagSkabelon', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagsFeltId', Integer, nullable=False),
    Column('SagSkabelonId', Integer, nullable=False),
    ForeignKeyConstraint(['SagSkabelonId'], ['SagSkabelon.ID'], name='FK_SagsFeltSagSkabelon_SagSkabelon'),
    ForeignKeyConstraint(['SagsFeltId'], ['SagsFelt.Id'], name='FK_SagsFeltSagSkabelon_SagsFelt'),
    PrimaryKeyConstraint('Id', name='PK__SagsFelt__3214EC07E4516156'),
    Index('AK_SagsFeltSagSkabelon_SagsFeltId_SagSkabelonId', 'SagsFeltId', 'SagSkabelonId', mssql_clustered=False, unique=True)
)

t_SagsNummer = Table(
    'SagsNummer', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('EmnePlanID', Integer, nullable=False),
    Column('EmnePlanNummerID', Integer, nullable=False),
    Column('FacetID', Integer),
    Column('SekvensNummer', Integer, nullable=False, server_default=text('((1))')),
    Column('Aarstal', Integer, nullable=False, server_default=text('(datepart(year,getdate()))')),
    ForeignKeyConstraint(['EmnePlanID'], ['EmnePlan.ID'], name='SagsNummer_EmnePlan'),
    ForeignKeyConstraint(['EmnePlanNummerID'], ['EmnePlanNummer.ID'], name='SagsNummer_EmnePlanNummer'),
    ForeignKeyConstraint(['FacetID'], ['Facet.ID'], name='SagsNummer_Facet'),
    PrimaryKeyConstraint('ID', name='PK_SagsNummer'),
    Index('Unikt_sagsnummer', 'EmnePlanNummerID', 'SekvensNummer', 'Aarstal', mssql_clustered=False)
)

t_SecuritySetSikkerhedsgrupper = Table(
    'SecuritySetSikkerhedsgrupper', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SecuritySetID', Integer, nullable=False),
    Column('SikkerhedsgruppeID', Integer, nullable=False),
    ForeignKeyConstraint(['SecuritySetID'], ['SecuritySet.ID'], name='SecuritySetOrganisationsEnheder_SecuritySet'),
    ForeignKeyConstraint(['SikkerhedsgruppeID'], ['Sikkerhedsgruppe.ID'], name='SecuritySetOrganisationsEnheder_OrganisationsEnhed'),
    PrimaryKeyConstraint('ID', name='PK_SecuritySetOrganisationsEnheder'),
    Index('IX_SecuritySetOrganisationsEnheder', 'SecuritySetID', 'SikkerhedsgruppeID', mssql_clustered=True, unique=True),
    Index('IX_SecuritySetSikkerhedsgrupper_SikkerhedsgruppeID', 'SikkerhedsgruppeID', mssql_clustered=False, mssql_include=['SecuritySetID'])
)

t_Styringsreol = Table(
    'Styringsreol', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', String(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('AnsaettelsesstedID', Integer, nullable=False),
    Column('FjernFraSoegReolEfterAntalDage', Integer, nullable=False),
    Column('EksterntMapped', Boolean, nullable=False, server_default=text('((0))')),
    Column('ReadOnly', Boolean, nullable=False, server_default=text('((0))')),
    Column('GUID', Uuid),
    ForeignKeyConstraint(['AnsaettelsesstedID'], ['Ansaettelsessted.ID'], name='FK_Styringsreol_Ansaettelsessted'),
    PrimaryKeyConstraint('ID', name='PK_Styringsreol')
)

t_SystemDefaults = Table(
    'SystemDefaults', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('ErindringTypeRingTilID', Integer, nullable=False, server_default=text('((1))')),
    Column('ErindringTypeBemaerkID', Integer, nullable=False, server_default=text('((2))')),
    Column('ErindringTypeLaesID', Integer, nullable=False, server_default=text('((3))')),
    Column('ErindringTypeOpfoelgID', Integer, nullable=False, server_default=text('((4))')),
    Column('DokumentArtJournaliserFilID', Integer, nullable=False, server_default=text('((6))')),
    Column('DokumentArtDefaultID', Integer, nullable=False, server_default=text('((6))')),
    Column('DokumentArtJournaliserSendtMailID', Integer, nullable=False, server_default=text('((2))')),
    Column('DokumentArtJournaliserModtagetMailID', Integer, nullable=False, server_default=text('((1))')),
    Column('DokumentArtJournaliserPapirID', Integer, nullable=False, server_default=text('((6))')),
    Column('DokumentArtJournaliserScanningID', Integer, nullable=False, server_default=text('((1))')),
    Column('DokumentArtJournaliserNotatID', Integer, nullable=False, server_default=text('((5))')),
    Column('DokumentArtJournaliserInterntID', Integer, nullable=False, server_default=text('((3))')),
    Column('DokumentArtJournaliserTelefonID', Integer, nullable=False, server_default=text('((6))')),
    Column('SagsStatusID', Integer, nullable=False, server_default=text('((0))')),
    Column('EmneplanID', Integer, nullable=False, server_default=text('((1))')),
    Column('PubliceringXslStylesheetID', Integer, nullable=False),
    Column('PubliceringCssStylesheetID', Integer, nullable=False),
    Column('AnsaettelsesstedID', Integer, nullable=False),
    Column('FagomraadeID', Integer, nullable=False),
    Column('DokumentArtAvanceretFletID', Integer, nullable=False),
    Column('DokumentArtJournaliserTilbageJournaliserDOP', Integer, nullable=False, server_default=text('((4))')),
    Column('GrundskabelonID', Integer, nullable=False),
    Column('KnownEksterntSystemID', Integer, nullable=False),
    Column('DelforloebTypeID', Integer, nullable=False),
    Column('ArkivAfklaringStatusID', Integer, nullable=False, server_default=text('((1))')),
    Column('DagsordenXslStylesheetID', Integer, nullable=False),
    Column('DagsordenCssStylesheetID', Integer, nullable=False),
    Column('DagsordenGenereringRessourceID', Integer, nullable=False),
    Column('DagsordenTilbagejournaliseringRessourceID', Integer, nullable=False),
    Column('CivilstandNyPersonID', Integer, nullable=False),
    Column('SekretariatID', Integer, nullable=False),
    ForeignKeyConstraint(['AnsaettelsesstedID'], ['Ansaettelsessted.ID'], name='FK_SystemDefaults_Ansaettelsessted'),
    ForeignKeyConstraint(['ArkivAfklaringStatusID'], ['ArkivAfklaringStatus.ID'], name='FK_SystemDefaults_ArkivStatus'),
    ForeignKeyConstraint(['CivilstandNyPersonID'], ['CivilstandOpslag.ID'], name='FK_SystemDefaults_CivilstandNyPerson'),
    ForeignKeyConstraint(['DagsordenCssStylesheetID'], ['Stylesheet.ID'], name='FK_SystemDefaults_DagsordenCssStylesheet'),
    ForeignKeyConstraint(['DagsordenGenereringRessourceID'], ['Ressource.ID'], name='FK_SystemDefaults_DagsordenGenereringRessource'),
    ForeignKeyConstraint(['DagsordenTilbagejournaliseringRessourceID'], ['Ressource.ID'], name='FK_SystemDefaults_DagsordenTilbagejournaliseringRessource'),
    ForeignKeyConstraint(['DagsordenXslStylesheetID'], ['Stylesheet.ID'], name='FK_SystemDefaults_DagsordenXslStylesheet'),
    ForeignKeyConstraint(['DelforloebTypeID'], ['DelforloebType.ID'], name='FK_SystemDefaults_DelforloebType'),
    ForeignKeyConstraint(['DokumentArtAvanceretFletID'], ['DokumentArtOpslag.ID'], name='FK_SystemDefaults_DokumentArtOpslag'),
    ForeignKeyConstraint(['DokumentArtDefaultID'], ['DokumentArtOpslag.ID'], name='FK_SystemDefaults_DokumentArt_Default'),
    ForeignKeyConstraint(['DokumentArtJournaliserFilID'], ['DokumentArtOpslag.ID'], name='FK_SystemDefaults_DokumentArt_JournaliserFil'),
    ForeignKeyConstraint(['DokumentArtJournaliserInterntID'], ['DokumentArtOpslag.ID'], name='FK_SystemDefaults_DokumentArt_JournaliserInternt'),
    ForeignKeyConstraint(['DokumentArtJournaliserModtagetMailID'], ['DokumentArtOpslag.ID'], name='FK_SystemDefaults_DokumentArt_JournaliserModtagetMail'),
    ForeignKeyConstraint(['DokumentArtJournaliserNotatID'], ['DokumentArtOpslag.ID'], name='FK_SystemDefaults_DokumentArt_JournaliserNotat'),
    ForeignKeyConstraint(['DokumentArtJournaliserPapirID'], ['DokumentArtOpslag.ID'], name='FK_SystemDefaults_DokumentArt_Papir'),
    ForeignKeyConstraint(['DokumentArtJournaliserScanningID'], ['DokumentArtOpslag.ID'], name='FK_SystemDefaults_DokumentArt_Scanning'),
    ForeignKeyConstraint(['DokumentArtJournaliserSendtMailID'], ['DokumentArtOpslag.ID'], name='FK_SystemDefaults_DokumentArt_JournaliserSendtMail'),
    ForeignKeyConstraint(['DokumentArtJournaliserTelefonID'], ['DokumentArtOpslag.ID'], name='FK_SystemDefaults_DokumentArt_JournaliserTelefon'),
    ForeignKeyConstraint(['EmneplanID'], ['EmnePlan.ID'], name='FK_SystemDefaults_EmnePlan'),
    ForeignKeyConstraint(['ErindringTypeBemaerkID'], ['ErindringTypeOpslag.ID'], name='FK_SystemDefaults_ErindringType_Bemaerk'),
    ForeignKeyConstraint(['ErindringTypeLaesID'], ['ErindringTypeOpslag.ID'], name='FK_SystemDefaults_ErindringType_Laes'),
    ForeignKeyConstraint(['ErindringTypeOpfoelgID'], ['ErindringTypeOpslag.ID'], name='FK_SystemDefaults_ErindringType_Opfoelg'),
    ForeignKeyConstraint(['ErindringTypeRingTilID'], ['ErindringTypeOpslag.ID'], name='FK_SystemDefaults_ErindringType_RingTil'),
    ForeignKeyConstraint(['FagomraadeID'], ['FagOmraade.ID'], name='FK_SystemDefaults_Fagomraade'),
    ForeignKeyConstraint(['GrundskabelonID'], ['SkabelonGrundSkabelon.ID'], name='FK_SystemDefaults_SkabelonGrundSkabelon'),
    ForeignKeyConstraint(['KnownEksterntSystemID'], ['KnownEksterntSystem.ID'], name='FK_SystemDefaults_KnownEksterntSystem'),
    ForeignKeyConstraint(['PubliceringCssStylesheetID'], ['Stylesheet.ID'], name='FK_SystemDefaults_Stylesheet1'),
    ForeignKeyConstraint(['PubliceringXslStylesheetID'], ['Stylesheet.ID'], name='FK_SystemDefaults_Stylesheet'),
    ForeignKeyConstraint(['SagsStatusID'], ['SagsStatus.ID'], name='FK_SystemDefaults_SagsStatus'),
    ForeignKeyConstraint(['SekretariatID'], ['Sekretariat.ID'], name='FK_SystemDefaults_Sekretariat'),
    PrimaryKeyConstraint('ID', name='PK_SystemDefaults')
)

t_WebWidgetSagSkabelon = Table(
    'WebWidgetSagSkabelon', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagskabelonId', Integer),
    Column('WebWidgetId', Integer),
    ForeignKeyConstraint(['SagskabelonId'], ['SagSkabelon.ID'], name='FK__WebWidget__Sagsk__0FF747D5'),
    ForeignKeyConstraint(['WebWidgetId'], ['WebWidget.ID'], name='FK__WebWidget__WebWi__10EB6C0E'),
    PrimaryKeyConstraint('ID', name='PK__WebWidge__3214EC27799AE82A')
)

t_AdministrativProfilBruger = Table(
    'AdministrativProfilBruger', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('AdministrativProfilID', Integer, nullable=False),
    Column('BrugerID', Integer, nullable=False),
    ForeignKeyConstraint(['AdministrativProfilID'], ['AdministrativProfil.ID'], name='FK_AdminProfilBruger_profil'),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='FK_AdministrativProfilBruger_Bruger'),
    PrimaryKeyConstraint('ID', name='PK_AdministrativProfilBruger')
)

t_AktindsigtSaves = Table(
    'AktindsigtSaves', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Oprettet', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('BrugerId', Integer, nullable=False),
    Column('SavedProgress', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['BrugerId'], ['Bruger.ID'], name='FK_AktindsigtSaves_ToTable'),
    PrimaryKeyConstraint('Id', name='PK_AktindsigtSaves'),
    Index('IX_Aktindsigt', 'Id', mssql_clustered=False, mssql_include=['Oprettet', 'BrugerId', 'SavedProgress'], unique=True)
)

t_ArkivPeriode = Table(
    'ArkivPeriode', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('CreatedByID', Integer, nullable=False),
    Column('Created', DateTime, server_default=text('(getdate())')),
    Column('LastChangedByID', Integer),
    Column('LastChanged', DateTime, server_default=text('(getdate())')),
    Column('PeriodeStart', DateTime, nullable=False),
    Column('PeriodeSlut', DateTime, nullable=False),
    Column('OverlapningsperiodeSlut', DateTime, nullable=False),
    Column('ArkivPeriodeStatusID', Integer, nullable=False),
    Column('ArkivPeriodeIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    ForeignKeyConstraint(['ArkivPeriodeStatusID'], ['ArkivPeriodeStatus.ID'], name='FK_ArkivPeriode_ArkivPeriodeStatus'),
    ForeignKeyConstraint(['CreatedByID'], ['Bruger.ID'], name='FK_ArkivPeriode_CreatedByBruger'),
    ForeignKeyConstraint(['LastChangedByID'], ['Bruger.ID'], name='FK_ArkivPeriode_LastChangedBruger'),
    PrimaryKeyConstraint('ID', name='PK_ArkivPeriode'),
    Index('IX_ArkivPeriode_ArkivPeriodeIdentity', 'ArkivPeriodeIdentity', mssql_clustered=False, unique=True),
    Index('IX_ArkivPeriode_PeriodeStart', 'PeriodeStart', mssql_clustered=False, unique=True),
    Index('UQ__ArkivPer__DE03889CB6D075BC', 'ArkivPeriodeIdentity', mssql_clustered=False, unique=True)
)

t_BrugerGruppeBruger = Table(
    'BrugerGruppeBruger', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerGruppeID', Integer, nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    ForeignKeyConstraint(['BrugerGruppeID'], ['BrugerGruppe.ID'], name='BrugerGruppeBrugere_BrugerGruppe'),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='BrugerGruppeBruger_Bruger'),
    PrimaryKeyConstraint('ID', name='PK_tblBrugerGruppe_Brugere_Link'),
    Index('IX_tblBrugerGruppe_Brugere_Link', 'BrugerGruppeID', mssql_clustered=False),
    Index('IX_tblBrugerGruppe_Brugere_Link_1', 'BrugerID', mssql_clustered=False)
)

t_BrugerLogonLog = Table(
    'BrugerLogonLog', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerID', Integer),
    Column('SbsysLogonID', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('SbsysLogonPassword', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Occured', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('Action', TINYINT, nullable=False, server_default=text('((0))')),
    Column('Message', Unicode(400, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('WindowsLogonName', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('WindowsDomainName', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('MachineName', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('MachineAddress', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Session', Uuid, nullable=False),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='FK_BrugerLogonLog_Bruger'),
    PrimaryKeyConstraint('ID', name='PK_BrugerLogonLog')
)

t_BrugerSettings = Table(
    'BrugerSettings', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerID', Integer, nullable=False),
    Column('MaxOpenSager', Integer),
    Column('MaxSenesteSager', Integer, nullable=False, server_default=text('((30))')),
    Column('CheckOutFolderRoot', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TemporaryFolderRoot', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('VisDelforloeb', Boolean),
    Column('VisErindringer', Boolean),
    Column('VisDokumenter', Boolean),
    Column('VisForloeb', Boolean),
    Column('VisKladder', Boolean),
    Column('VisSager', Boolean),
    Column('AabenDokumentPaaFaneblad', Boolean),
    Column('VisKladdeCheckinVedAfslut', Boolean),
    Column('VisListeKriterieSektion', Boolean),
    Column('UdfyldDelforloebFaneblad', Boolean, nullable=False, server_default=text('((1))')),
    Column('UdfyldErindringerFaneblad', Boolean, nullable=False, server_default=text('((1))')),
    Column('UdfyldDokumenterFaneblad', Boolean, nullable=False, server_default=text('((1))')),
    Column('UdfyldForloebFaneblad', Boolean, nullable=False, server_default=text('((1))')),
    Column('UdfyldKladderFaneblad', Boolean, nullable=False, server_default=text('((1))')),
    Column('MaxMailItemsReturned', Integer),
    Column('VisPanel', Boolean, nullable=False, server_default=text('((0))')),
    Column('UserFolderName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('VisPluginWarnings', Boolean),
    Column('VisSagsTitelPaaFaneblad', Boolean),
    Column('VisBeskedEfterSagGem', Boolean, nullable=False, server_default=text('((0))')),
    Column('ErindringPopupStaySec', Integer),
    Column('MaxSagItemsReturned', Integer),
    Column('VisListeFiltrering', Boolean),
    Column('VisListeGruppering', Boolean),
    Column('VisPdfVersionHvisForefindes', Boolean),
    Column('LaeseLayoutPaaSag', Boolean),
    Column('VisDokumentReadonlyAdvarsel', Boolean),
    Column('VisScannedeDokumenter', Boolean),
    Column('StartOn', Integer),
    Column('DefaultClientTab', Unicode(30, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('LastClientTab', Unicode(30, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('GenaabenSager', Boolean),
    Column('VisDagsordensystem', Boolean, server_default=text('((1))')),
    Column('VisPartSoegning', Boolean),
    Column('DefaultSagSecuritySetID', Integer),
    Column('DefaultKommuneVedSagsoprettelseID', Integer),
    Column('VisPreviewPaaDokumentOgKladdeLister', Boolean, nullable=False, server_default=text('((1))')),
    Column('VisDokumentTabBlock', Boolean, nullable=False, server_default=text('((1))')),
    Column('DokumentLaesningsLayout', Boolean, nullable=False, server_default=text('((0))')),
    Column('ErStandardForNyeBrugere', Boolean, nullable=False, server_default=text('((0))')),
    Column('SplitterDistancePercentage', Integer, nullable=False, server_default=text('((0))')),
    Column('AutoArkiverKladder', Boolean, nullable=False, server_default=text('((1))')),
    Column('AutoFortrydUaendredeKladder', Boolean, nullable=False, server_default=text('((1))')),
    Column('DefaultRegionVedSagsoprettelseID', Integer),
    Column('DefaultAmtVedSagsoprettelseID', Integer),
    Column('PubliseringFolderRoot', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('WorkFolderRoot', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('LastUsedTekstbehandlerName', Unicode(60, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('MailSignatur', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS')),
    Column('VisKladdeProcessInfo', Boolean, nullable=False, server_default=text('((1))')),
    Column('VisGenstandSoegning', Boolean),
    Column('DagsordenPubliseringIndstilling', Integer, nullable=False, server_default=text('((3))')),
    Column('AnvendDokumentNavnTilAttachment', Boolean, nullable=False, server_default=text('((0))')),
    Column('PostlisteIndstilling', Integer, nullable=False, server_default=text('((3))')),
    Column('VisPostlister', Boolean, nullable=False, server_default=text('((0))')),
    Column('VisSbsysIdag', Boolean, nullable=False, server_default=text('((1))')),
    Column('DagsordenpunktSoegningType', Integer, nullable=False, server_default=text('((0))')),
    Column('VisDagsordenpunktSoegning', Boolean, nullable=False, server_default=text('((1))')),
    Column('VisJournalArkSogning', Boolean, nullable=False, server_default=text('((1))')),
    Column('JournalarkVisningsFontID', Integer),
    Column('VisJournalNoterSomOversigt', Boolean),
    Column('VisJournalNoteTabBlock', Boolean, server_default=text('((1))')),
    Column('AnvendDokumenterSomJournalNote', Boolean, server_default=text('((1))')),
    Column('SenestePubliceringIndstillingerID', Integer),
    Column('SendFejl', Boolean, nullable=False, server_default=text('((0))')),
    Column('FlashQueueBell', Boolean, nullable=False, server_default=text('((1))')),
    Column('AutomaticallyExecuteCommandsQueue', Boolean, nullable=False, server_default=text('((1))')),
    Column('VerificerProgramLukning', Boolean, nullable=False, server_default=text('((0))')),
    Column('MailSignaturVedSvarVideresend', Boolean, nullable=False, server_default=text('((0))')),
    Column('VisInaktiveBrugere', Boolean, nullable=False, server_default=text('((1))')),
    Column('SagStartView', Integer, nullable=False, server_default=text('((-1))')),
    Column('VisDokumentReadonlyAdvarselVedEksternAabning', Boolean, nullable=False, server_default=text('((1))')),
    Column('AnvendSagspartSomStartvisningVedSoegSag', Boolean, nullable=False, server_default=text('((0))')),
    Column('ModtagErindringSomMail', Boolean, nullable=False, server_default=text('((1))')),
    Column('VisNewsPopUpSidstFravalgtDato', DateTime),
    Column('ShowAllCprCvr', Boolean, nullable=False, server_default=text('((0))')),
    Column('ObfuscateAllCprCvr', Boolean, nullable=False, server_default=text('((0))')),
    Column('ObfuscateLastCharactersInCpr', Boolean, nullable=False, server_default=text('((0))')),
    Column('ObfuscateCvr', Boolean, nullable=False, server_default=text('((0))')),
    Column('VisIkkeLukkedePunkter', Boolean, nullable=False, server_default=text('((0))')),
    Column('AnvendSenesteKladdeVedOpretKladde', Boolean, nullable=False, server_default=text('((1))')),
    Column('StandardErindringRetur', Boolean, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='FK_BrugerSettings_Bruger'),
    ForeignKeyConstraint(['DefaultAmtVedSagsoprettelseID'], ['AmtOpslag.ID'], name='FK_BrugerSettings_AmtOpslag'),
    ForeignKeyConstraint(['DefaultKommuneVedSagsoprettelseID'], ['KommuneOpslag.ID'], name='FK_BrugerSettings_KommuneOpslag'),
    ForeignKeyConstraint(['DefaultRegionVedSagsoprettelseID'], ['RegionOpslag.ID'], name='FK_BrugerSettings_RegionOpslag'),
    ForeignKeyConstraint(['DefaultSagSecuritySetID'], ['SecuritySet.ID'], name='FK_BrugerSettings_DefaultSagSecuritySet'),
    ForeignKeyConstraint(['SenestePubliceringIndstillingerID'], ['PubliseringIndstillinger.ID'], name='FK_BrugerSettings_PubliseringIndstillinger'),
    PrimaryKeyConstraint('ID', name='PK_BrugerSettings'),
    Index('IX_BrugerSettings', 'BrugerID', mssql_clustered=False, unique=True),
    Index('IX_BrugerSettings_UserFolderName', 'UserFolderName', mssql_clustered=False, unique=True)
)

t_Delforloeb = Table(
    'Delforloeb', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagID', Integer, nullable=False),
    Column('DelforloebTypeID', Integer, nullable=False),
    Column('BehandlerID', Integer, nullable=False),
    Column('BevaringID', Integer),
    Column('KommuneID', Integer),
    Column('KontorID', Integer),
    Column('BeslutningsTypeID', Integer),
    Column('Titel', Unicode(254, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('AfsendtFraSagsPart', DateTime),
    Column('Modtaget', DateTime),
    Column('ErBesluttet', Boolean),
    Column('Besluttet', DateTime),
    Column('BeslutningNotat', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ErTinglyst', Boolean),
    Column('ErMoedeSag', Boolean),
    Column('BeslutningHarDeadline', Boolean),
    Column('BeslutningDeadline', DateTime),
    Column('Created', DateTime),
    Column('CreatedByID', Integer),
    Column('LastChanged', DateTime),
    Column('LastChangedByID', Integer),
    Column('SagspartID', Integer),
    Column('SagspartRolleID', Integer),
    Column('FagomraadeID', Integer),
    Column('Orden', Integer),
    Column('KommuneFoer2007ID', Integer),
    ForeignKeyConstraint(['BehandlerID'], ['Bruger.ID'], name='Delforloeb_Behandler'),
    ForeignKeyConstraint(['BeslutningsTypeID'], ['BeslutningsType.ID'], name='Delforloeb_BeslutningsType'),
    ForeignKeyConstraint(['BevaringID'], ['BevaringOpslag.ID'], name='Delforloeb_Bevaring'),
    ForeignKeyConstraint(['CreatedByID'], ['Bruger.ID'], name='Delforloeb_CreatedBy'),
    ForeignKeyConstraint(['DelforloebTypeID'], ['DelforloebType.ID'], name='Delforloeb_DelforloebType'),
    ForeignKeyConstraint(['FagomraadeID'], ['FagOmraade.ID'], name='Delforloeb_FagOmraade'),
    ForeignKeyConstraint(['KommuneFoer2007ID'], ['KommuneFoer2007Opslag.ID'], name='Delforloeb_KommuneFoer2007'),
    ForeignKeyConstraint(['KommuneID'], ['KommuneOpslag.ID'], name='Delforloeb_Kommune'),
    ForeignKeyConstraint(['KontorID'], ['Kontor.ID'], name='Delforloeb_Kontor'),
    ForeignKeyConstraint(['LastChangedByID'], ['Bruger.ID'], name='Delforloeb_LastChangedBy'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='Delforloeb_Sag'),
    ForeignKeyConstraint(['SagspartID'], ['SagsPart.ID'], name='Delforloeb_Sagspart'),
    ForeignKeyConstraint(['SagspartRolleID'], ['SagsPartRolle.ID'], name='Delforloeb_SagsPartRolle'),
    PrimaryKeyConstraint('ID', name='PK_Delforloeb'),
    Index('IX_Delforloeb_DelforloebType', 'DelforloebTypeID', mssql_clustered=False),
    Index('IX_Delforloeb_ID', 'ID', mssql_clustered=False, mssql_include=['Titel']),
    Index('IX_JournalDelforloeb_Journal', 'SagID', mssql_clustered=True)
)

t_DokumentRegistrering = Table(
    'DokumentRegistrering', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagID', Integer, nullable=False),
    Column('DokumentID', Integer, nullable=False),
    Column('SagspartID', Integer),
    Column('OprindeligSagspartAdresse', Unicode(400, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ErBeskyttet', Boolean, nullable=False, server_default=text('((0))')),
    Column('Registreret', DateTime, nullable=False),
    Column('RegistreretAfID', Integer, nullable=False),
    Column('Beskrivelse', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SecuritySetID', Integer),
    Column('Navn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('DeletedState', TINYINT, nullable=False, server_default=text('((0))')),
    Column('DeletedDate', DateTime),
    Column('DeletedByID', Integer),
    Column('DeletedReason', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DeleteConfirmed', DateTime),
    Column('DeleteConfirmedByID', Integer),
    Column('DokumentRegistreringIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    ForeignKeyConstraint(['DokumentID'], ['Dokument.ID'], name='DokumentRegistrering_Dokument'),
    ForeignKeyConstraint(['RegistreretAfID'], ['Bruger.ID'], name='FK_DokumentRegistrering_Bruger'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='DokumentRegistrering_Sag'),
    ForeignKeyConstraint(['SagspartID'], ['SagsPart.ID'], name='DokumentRegistrering_SagsPart'),
    ForeignKeyConstraint(['SecuritySetID'], ['SecuritySet.ID'], name='DokumentRegistrering_SecuritySet'),
    PrimaryKeyConstraint('ID', name='PK_DokumentRegistrering'),
    Index('IX_DokumentRegistrering_Dokument', 'DokumentID', mssql_clustered=False, mssql_include=['ID', 'SagspartID', 'OprindeligSagspartAdresse', 'ErBeskyttet', 'Registreret', 'RegistreretAfID', 'Beskrivelse', 'SecuritySetID', 'Navn', 'DeletedState', 'DeletedDate', 'DeletedByID', 'DeletedReason', 'DeleteConfirmed', 'DeleteConfirmedByID', 'DokumentRegistreringIdentity']),
    Index('IX_DokumentRegistrering_ID', 'ID', mssql_clustered=False, mssql_include=['DokumentID', 'ErBeskyttet', 'RegistreretAfID', 'SecuritySetID']),
    Index('IX_DokumentRegistrering_Registreret', 'Registreret', mssql_clustered=False),
    Index('IX_DokumentRegistrering_RegistreretAf', 'RegistreretAfID', mssql_clustered=False),
    Index('IX_DokumentRegistrering_Sag', 'SagID', mssql_clustered=True),
    Index('IX_DokumentRegistrering_SagsPart', 'SagspartID', mssql_clustered=False),
    Index('UQ__Dokument__ECDBF0625F2D2DB6', 'DokumentRegistreringIdentity', mssql_clustered=False, unique=True)
)

t_ErindringSkabelon = Table(
    'ErindringSkabelon', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ErindringTypeID', Integer, nullable=False),
    Column('AnsvarligBrugerID', Integer),
    Column('Normtid', Integer, nullable=False, server_default=text('((0))')),
    Column('HierakiMedlemID', Integer),
    ForeignKeyConstraint(['AnsvarligBrugerID'], ['Bruger.ID'], name='FK_ErindringSkabelon_Bruger'),
    ForeignKeyConstraint(['ErindringTypeID'], ['ErindringTypeOpslag.ID'], name='ErindringSkabelon_ErindringType'),
    ForeignKeyConstraint(['HierakiMedlemID'], ['HierakiMedlem.ID'], name='FK_ErindringSkabelon_HierakiMedlem'),
    PrimaryKeyConstraint('ID', name='pk_ErindringSkabelon')
)

t_ErindringSomMail = Table(
    'ErindringSomMail', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerID', Integer),
    Column('AnsaettelsesstedID', Integer),
    ForeignKeyConstraint(['AnsaettelsesstedID'], ['Ansaettelsessted.ID'], name='FK_ErindringSomMail_Ansaettelsessted'),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='FK_ErindringSomMail_Bruger'),
    PrimaryKeyConstraint('ID', name='PK_ErindringSomMail'),
    Index('IX_ErindringSomMail_2', 'AnsaettelsesstedID', 'BrugerID', mssql_clustered=False, unique=True)
)

t_FkOrgBrugerReference = Table(
    'FkOrgBrugerReference', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('FkOrgUuid', Uuid, nullable=False),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='FK_FkorgBrugerreference_Bruger')
)

t_FlowSkabelonModtager = Table(
    'FlowSkabelonModtager', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('FlowSkabelonID', Integer, nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('Opgave', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Bemaerkninger', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS')),
    Column('TidsfristDage', Integer, nullable=False),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], ondelete='CASCADE', name='FK_FlowSkabelonModtager_Bruger'),
    ForeignKeyConstraint(['FlowSkabelonID'], ['FlowSkabelon.ID'], ondelete='CASCADE', name='FK_FlowSkabelonModtager_FlowSkabelon'),
    PrimaryKeyConstraint('ID', name='PK__FlowSkab__3214EC275A33B697')
)

t_GridLayout = Table(
    'GridLayout', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerID', Integer, nullable=False),
    Column('Context', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Layout', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SplitterPercent', Integer),
    Column('SplitterHorizontal', Boolean, nullable=False, server_default=text('((1))')),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='FK_GridLayout_Bruger'),
    PrimaryKeyConstraint('ID', name='PK_GridLayout')
)

t_Heartbeat = Table(
    'Heartbeat', metadata,
    Column('BrugerID', Integer, nullable=False),
    Column('BrugerLogonID', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('MachineName', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('LastHeartbeat', DateTime, nullable=False),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='FK_Heartbeat_Bruger'),
    Index('IX_Heartbeat', 'BrugerID', mssql_clustered=True, unique=True)
)

t_JournalArkNote = Table(
    'JournalArkNote', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('JournalArkID', Integer, nullable=False),
    Column('OprettetAf', Integer, nullable=False),
    Column('Oprettet', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('KontaktTidspunkt', DateTime, nullable=False),
    Column('Overskrift', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Note', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OmfattetAfAktindsigt', Boolean, nullable=False, server_default=text('((1))')),
    Column('SlettetDato', DateTime),
    Column('SlettetAfBrugerID', Integer),
    Column('JournalArkNoteIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    Column('AktindsigtBeskrivelse', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['JournalArkID'], ['JournalArk.ID'], name='FK_JournalArkNote_JournalArk'),
    ForeignKeyConstraint(['OprettetAf'], ['Bruger.ID'], name='FK_JournalArkNote_Bruger'),
    PrimaryKeyConstraint('ID', name='PK_JournalArkNote'),
    Index('IX_JournalarkNote', 'ID', 'JournalArkID', 'OprettetAf', 'SlettetAfBrugerID', mssql_clustered=False),
    Index('IX_Support_Cluster_JournalarkNote', 'JournalArkID', mssql_clustered=False, mssql_include=['OprettetAf', 'SlettetAfBrugerID'])
)

t_Kladde = Table(
    'Kladde', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Beskrivelse', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Emne', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Created', DateTime),
    Column('CreatedByID', Integer),
    Column('LastChanged', DateTime),
    Column('LastChangedByID', Integer),
    Column('FileName', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('FileExtension', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('IsCheckedOut', Boolean),
    Column('IsArchived', Boolean),
    Column('CheckedOutFileName', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('CheckedOutFilePath', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('CheckedOutByID', Integer),
    Column('CheckedOut', DateTime),
    Column('CheckedOutMachineName', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('CheckedOutMachineAddress', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('CheckedOutUserName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('LastCheckedInByID', Integer),
    Column('LastCheckedIn', DateTime),
    Column('CurrentVersion', Integer, nullable=False),
    Column('Navn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('MergeData', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('MergeDataFileName', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KeepCheckedOut', Boolean, nullable=False, server_default=text('((0))')),
    Column('MailBody', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('MailSubject', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('PrinterName', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KladdeFletteStrategi', Integer, nullable=False, server_default=text('((1))')),
    Column('KladdeRedigeringGenoptaget', Boolean, nullable=False, server_default=text('((0))')),
    Column('DeletedState', TINYINT, nullable=False, server_default=text('((0))')),
    Column('DeletedDate', DateTime),
    Column('DeletedByID', Integer),
    Column('DeletedReason', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DeleteConfirmed', DateTime),
    Column('DeleteConfirmedByID', Integer),
    Column('MaterialeType', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('IndexingStatus', TINYINT, nullable=False, server_default=text('((1))')),
    Column('Keywords', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('FileSize', BigInteger),
    Column('ImporteretFraKnownEksternSystemID', Integer),
    Column('EksternID', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KladdeArt', Unicode(30, 'SQL_Danish_Pref_CP1_CI_AS'), server_default=text('(NULL)')),
    ForeignKeyConstraint(['CheckedOutByID'], ['Bruger.ID'], name='Kladde_CheckedOutByBruger'),
    ForeignKeyConstraint(['CreatedByID'], ['Bruger.ID'], name='Kladde_CreatedByBruger'),
    ForeignKeyConstraint(['DeletedByID'], ['Bruger.ID'], name='FK_Kladde_DeletedByBruger'),
    ForeignKeyConstraint(['LastChangedByID'], ['Bruger.ID'], name='FK_Kladde_Bruger_LastChangedBy'),
    ForeignKeyConstraint(['LastCheckedInByID'], ['Bruger.ID'], name='Kladde_LastCheckedInByBruger'),
    PrimaryKeyConstraint('ID', name='PK_tblBreve'),
    Index('IX_Kladde_Created', 'CreatedByID', mssql_clustered=False),
    Index('IX_Kladde_ID_CreatedByID', 'CreatedByID', 'ID', mssql_clustered=False, mssql_include=['Beskrivelse', 'Emne', 'Created', 'LastChanged', 'LastChangedByID', 'FileName', 'FileExtension', 'IsCheckedOut', 'IsArchived', 'CheckedOutFileName', 'CheckedOutFilePath', 'CheckedOutByID', 'CheckedOut', 'CheckedOutMachineName', 'CheckedOutMachineAddress', 'CheckedOutUserName', 'LastCheckedInByID', 'LastCheckedIn', 'CurrentVersion', 'Navn', 'MergeDataFileName', 'KeepCheckedOut', 'MailSubject', 'PrinterName', 'KladdeFletteStrategi', 'KladdeRedigeringGenoptaget', 'DeletedState', 'DeletedDate', 'DeletedByID', 'DeletedReason', 'DeleteConfirmed', 'DeleteConfirmedByID', 'MaterialeType', 'IndexingStatus', 'FileSize', 'ImporteretFraKnownEksternSystemID', 'EksternID', 'KladdeArt']),
    Index('IX_Kladde_IsCheckedOut', 'IsCheckedOut', mssql_clustered=False, mssql_include=['ID'])
)

t_Log = Table(
    'Log', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerID', Integer, nullable=False),
    Column('Comments', Unicode(400, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Type', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Severity', Integer),
    Column('ProductVersion', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ProductName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Logged', DateTime, nullable=False),
    Column('Category', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Message', Unicode(1024, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Source', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SqlCommand', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('StackTrace', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('InnerException', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OSUserName', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OSRegionalSettings', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OSMachineName', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OSVersion', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('NetRuntimeVersion', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ReviewComments', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ReviewedBy', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ReviewDate', DateTime),
    Column('ReviewIgnore', Boolean),
    Column('IsSolved', Boolean),
    Column('ExceptionType', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('RuntimeLog', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Occurences', Integer, nullable=False, server_default=text('((1))')),
    Column('BuildLabel', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='Log_Bruger'),
    PrimaryKeyConstraint('ID', name='PK_Log')
)

t_MapSag = Table(
    'MapSag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Kode', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Titel', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('EmneplanID', Integer, nullable=False),
    Column('EmneplanNummerID', Integer, nullable=False),
    Column('FacetID', Integer),
    Column('MaxSagsnummerLaengde', Integer, nullable=False, server_default=text('((0))')),
    Column('SagsbehandlerID', Integer),
    Column('SaetSagspartSomPrimaer', Boolean, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['SagsbehandlerID'], ['Bruger.ID'], name='FK_MapSag_Sagsbehandler'),
    PrimaryKeyConstraint('ID', name='PK_MapSag')
)

t_MostRecentInfo = Table(
    'MostRecentInfo', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Text', Unicode(450, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('GroupName', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('ItemID', Integer, nullable=False),
    Column('Created', DateTime, nullable=False),
    Column('OwnerID', Integer, nullable=False),
    Column('ClassName', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['OwnerID'], ['Bruger.ID'], name='FK_MostRecentInfo_Bruger'),
    PrimaryKeyConstraint('ID', name='PK_MostRecentInfo'),
    Index('IX_MOSTRECENT_OwnerID_GroupName_Created', 'OwnerID', 'GroupName', 'Created', mssql_clustered=False, mssql_include=['ID', 'Text', 'ItemID', 'ClassName']),
    Index('IX_MostRecentInfo', 'OwnerID', 'GroupName', 'ItemID', mssql_clustered=False, unique=True)
)

t_Nyhed = Table(
    'Nyhed', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('OprettetDato', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('OprettetAfID', Integer, nullable=False),
    Column('Indhold', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('ErUdgaaet', Boolean, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['OprettetAfID'], ['Bruger.ID'], name='FK_Nyhed_OprettetAfBruger'),
    PrimaryKeyConstraint('ID', name='PK_Nyhed')
)

t_PessimisticLockInfo = Table(
    'PessimisticLockInfo', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('TargetID', Integer, nullable=False),
    Column('TargetName', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('LockedByID', Integer, nullable=False),
    Column('Locked', DateTime, nullable=False),
    Column('LockType', Integer, nullable=False, server_default=text('((1))')),
    Column('UnLockedByID', Integer),
    Column('UnLocked', DateTime),
    ForeignKeyConstraint(['LockedByID'], ['Bruger.ID'], name='FK_PessimisticLockInfo_Bruger'),
    ForeignKeyConstraint(['UnLockedByID'], ['Bruger.ID'], name='FK_PessimisticLockInfo_UnlockedByBruger'),
    PrimaryKeyConstraint('ID', name='PK_PessimisticLockInfo'),
    Index('IX_PessimisticLockInfo_Target', 'TargetID', 'TargetName', 'LockedByID', mssql_clustered=True, unique=True)
)

t_Publisering = Table(
    'Publisering', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Oprettet', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('OprettetAfID', Integer, nullable=False),
    Column('Publiseres', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('ErPubliseret', Boolean, nullable=False, server_default=text('((0))')),
    Column('ErPrivatPublisering', Boolean, nullable=False, server_default=text('((0))')),
    Column('Publiseret', DateTime),
    Column('SidsteStatement', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['OprettetAfID'], ['Bruger.ID'], name='FK_Publicering_Bruger'),
    PrimaryKeyConstraint('ID', name='PK_Publicering'),
    Index('IX_Publicering_Navn_Unique', 'Navn', mssql_clustered=False, unique=True)
)

t_QueryProfil = Table(
    'QueryProfil', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('CreatedByID', Integer),
    Column('Query', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('LastChanged', DateTime),
    Column('Context', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['CreatedByID'], ['Bruger.ID'], name='FK_QueryProfil_Bruger'),
    PrimaryKeyConstraint('ID', name='PK_QueryProfil')
)

t_QueueCommand = Table(
    'QueueCommand', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Oprettet', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('BrugerID', Integer, nullable=False),
    Column('Status', Integer, nullable=False, server_default=text('((1))')),
    Column('Navn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('XML', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Error', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OriginalLocation', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Behavior', Integer, nullable=False, server_default=text('((1))')),
    Column('GUID', Uuid),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='FK_Que_Bruger'),
    PrimaryKeyConstraint('ID', name='PK_Que'),
    Index('IX_QueueCommand_', 'BrugerID', 'Status', mssql_clustered=True)
)

t_SagHistorikStatus = Table(
    'SagHistorikStatus', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagID', Integer, nullable=False),
    Column('RegistreretAfID', Integer, nullable=False),
    Column('FraSagsStatusID', Integer),
    Column('TilSagsStatusID', Integer, nullable=False),
    Column('Kommentar', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Note', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Tidspunkt', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('VarighedsMinuter', BigInteger),
    ForeignKeyConstraint(['FraSagsStatusID'], ['SagsStatus.ID'], name='FK_SagHistorikStatus_SagsStatus'),
    ForeignKeyConstraint(['RegistreretAfID'], ['Bruger.ID'], name='FK_SagHistorikStatus_Bruger'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='FK_SagHistorikStatus_Sag'),
    ForeignKeyConstraint(['TilSagsStatusID'], ['SagsStatus.ID'], name='FK_SagHistorikStatus_SagsStatus1'),
    PrimaryKeyConstraint('ID', name='PK_SagHistorikStatus')
)

t_SagsVisit = Table(
    'SagsVisit', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagID', Integer, nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('Tidspunkt', DateTime, nullable=False, server_default=text('(getdate())')),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='SagVisit_Bruger'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='SagVisit_Sag'),
    PrimaryKeyConstraint('ID', name='PK_tblJournalVisit'),
    Index('IX_Sagsvisit_SagId', 'SagID', 'Tidspunkt', mssql_clustered=False)
)

t_SecuritySetBrugere = Table(
    'SecuritySetBrugere', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SecuritySetID', Integer, nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('ErPermanent', Boolean, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='SecuritySetBrugere_Bruger'),
    ForeignKeyConstraint(['SecuritySetID'], ['SecuritySet.ID'], name='SecuritySetBrugere_SecuritySet'),
    PrimaryKeyConstraint('ID', name='PK_SecuritySetBrugere'),
    Index('IX_SecuritySetBrugere_SecuritySetID', 'BrugerID', mssql_clustered=False, mssql_include=['SecuritySetID']),
    Index('IX_SecuritySetBrugere_SecuritySetOgBruger', 'SecuritySetID', 'BrugerID', mssql_clustered=True, unique=True)
)

t_SikkerhedsgruppeBrugere = Table(
    'SikkerhedsgruppeBrugere', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerID', Integer, nullable=False),
    Column('SikkerhedsgruppeID', Integer, nullable=False),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='BrugerOrganisationsEnheder_Bruger'),
    ForeignKeyConstraint(['SikkerhedsgruppeID'], ['Sikkerhedsgruppe.ID'], name='BrugerOrganisationsenheder_OrganisationsEnhed'),
    PrimaryKeyConstraint('ID', name='PK_BrugerOrganisationsenhed'),
    Index('IX_BrugerOrganisationsEnheder_Unique', 'BrugerID', 'SikkerhedsgruppeID', mssql_clustered=False, unique=True),
    Index('IX_BrugerOrganisationsenhed_Bruger', 'BrugerID', mssql_clustered=True),
    Index('IX_BrugerOrganisationsenhed_OrganisationsEnhed', 'SikkerhedsgruppeID', mssql_clustered=False),
    Index('IX_SikkerhedsgruppeBrugere', 'SikkerhedsgruppeID', mssql_clustered=False, mssql_include=['ID']),
    Index('IX_Sikkerhedsgruppe_BrugerID', 'SikkerhedsgruppeID', mssql_clustered=False, mssql_include=['ID', 'BrugerID'])
)

t_Skabelon = Table(
    'Skabelon', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Redigeret', DateTime),
    Column('RedigeretAfID', Integer),
    Column('GrundSkabelonID', Integer),
    Column('VisTekstblokvaelger', Boolean, nullable=False, server_default=text("('False')")),
    ForeignKeyConstraint(['GrundSkabelonID'], ['SkabelonGrundSkabelon.ID'], name='Skabelon_SkabelonGrundSkabelon'),
    ForeignKeyConstraint(['RedigeretAfID'], ['Bruger.ID'], name='FK_Skabelon_Bruger'),
    PrimaryKeyConstraint('ID', name='PK_tblSkabelon')
)

t_SkabelonTekstblok = Table(
    'SkabelonTekstblok', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('TekstRtf', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('IsCheckedOut', Boolean),
    Column('CheckOutpath', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('BrugerID', Integer),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    Column('IsDefault', Boolean),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='SkabelonTekstblok_Bruger'),
    PrimaryKeyConstraint('ID', name='PK_tblTekstBlok')
)

t_StyringsreolHylde = Table(
    'StyringsreolHylde', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('SagsstatusID', Integer, nullable=False),
    Column('StyringsreolID', Integer, nullable=False),
    Column('Normtidstype', Integer, nullable=False, server_default=text('((1))')),
    Column('SorteringsIndex', Integer),
    Column('Skjult', Boolean, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['SagsstatusID'], ['SagsStatus.ID'], name='FK_StyringsreolStatus_SagsStatus'),
    ForeignKeyConstraint(['StyringsreolID'], ['Styringsreol.ID'], name='FK_StyringsreolHylde_Styringsreol'),
    PrimaryKeyConstraint('ID', name='PK_StyringsreolHylde')
)

t_SystemConfiguration = Table(
    'SystemConfiguration', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('VisRedigerMedWordKnapPaaDagsordenpunkt', Boolean, server_default=text('((0))')),
    Column('DefaultTemporaryFolderPath', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS'), server_default=text("(N'[MyDocuments]\\SBSYS\\Temp')")),
    Column('DefaultCheckoutFolderPath', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS'), server_default=text("(N'[MyDocuments]\\SBSYS\\Kladder')")),
    Column('ForceTemporaryFolderPath', Boolean),
    Column('ForceCheckoutFolderPath', Boolean),
    Column('RequireErindringConclusion', Boolean),
    Column('SbsysDatabaseVersion', String(20, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('AllowBlankPassword', Boolean),
    Column('BulkJournaliseringsSti', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DagsordenSystemAktivt', Boolean, nullable=False, server_default=text('((1))')),
    Column('JournaliseringMaxFilesize', Integer, nullable=False, server_default=text('((50))')),
    Column('Timestamp', TIMESTAMP, nullable=False),
    Column('KontrollerCheckOutTilSammeMaskineVedKladeJournalisering', Boolean, nullable=False, server_default=text('((1))')),
    Column('HelpSystemUrl', Unicode(1000, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False, server_default=text("(N'http://www.sbsys.dk/Hjaelp/Show.aspx?N={0}&V={1}&I={2}')")),
    Column('Kommune', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TrustedADDomains', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KraevetGruppemedlemsskab', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TilladAutomatiskLogon', Boolean, nullable=False, server_default=text('((0))')),
    Column('SynkroniserADEgenskaber', Boolean, nullable=False, server_default=text('((1))')),
    Column('SynkroniserADGrupperMedRoller', Boolean, nullable=False, server_default=text('((0))')),
    Column('IntegreretBrugerID', Integer, nullable=False),
    Column('DefaultWorkFolderPath', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS'), server_default=text("(N'[MyDocuments]\\SBSYS\\Work')")),
    Column('ForceWorkFolderPath', Boolean),
    Column('PostlisteQuery', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False, server_default=text("('select distinct DokumentRegistrering.ID from Dokument inner join DokumentRegistrering on DokumentRegistrering.DokumentID = Dokument.ID where PaaPostliste = 1 and datediff(Day, Oprettet, getdate()) = 0')")),
    Column('TilladAfslutUdenKladdeArkivering', Boolean, nullable=False, server_default=text('((0))')),
    Column('TilladFletningVhaTekstbehandler', Boolean, nullable=False, server_default=text('((0))')),
    Column('PaaSagStartView', Integer, nullable=False, server_default=text('((4))')),
    Column('GrupperFaneblade', Boolean, nullable=False, server_default=text('((0))')),
    Column('DagsordenWebGeneratorInternetRootPath', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DagsordenWebGeneratorIntranetRootPath', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DefaultPubliseringFolderRoot', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ForcePubliseringFolderRoot', Boolean, nullable=False, server_default=text('((0))')),
    Column('AnvendGenstande', Boolean, nullable=False, server_default=text('((1))')),
    Column('VisOrdetÅbenIDagsordenOverskrift', Boolean, nullable=False, server_default=text('((1))')),
    Column('DefaultDagsordenerVedMødeoprettelse', Integer, nullable=False, server_default=text('((15))')),
    Column('KanPublicereDagsordenerMedKladdeBilag', Boolean, nullable=False, server_default=text('((0))')),
    Column('BiholdUdvalgsMedlemmerPaaAdgangsliste', Boolean, nullable=False, server_default=text('((0))')),
    Column('JournalNoteRedigeringsPeriode', Integer, nullable=False, server_default=text('((36))')),
    Column('AnvendDokumentGalleri', Boolean, nullable=False, server_default=text('((0))')),
    Column('JournalArkCss', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('JournalArkLogo', IMAGE),
    Column('JournalArkLogoFilename', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ServiceDatabaseConnectionString', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TvingKommentarVedLogfejl', Boolean, nullable=False, server_default=text('((0))')),
    Column('SendErindringTilSagsBehandlerVedJournalisering', Boolean, nullable=False, server_default=text('((1))')),
    Column('InstallationIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    Column('VisJournalNoterSomOversigt', Boolean),
    Column('DagsordenPubliceringEmbedXml', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SendFejlUrl', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False, server_default=text("(N'mailto:support@ditmer.dk?subject=Fejl i Sbsys.Net version {0}&body={1}')")),
    Column('JournalarkHyperlink', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SendErindringTilNySagsBehandlerVedSkiftSagsbehandler', Boolean, nullable=False, server_default=text('((1))')),
    Column('AnvendMaxLaengdePaaDagsordenBilag', Boolean, nullable=False, server_default=text('((0))')),
    Column('MaxLaengdePaaDagsordenBilag', Integer, nullable=False, server_default=text('((40))')),
    Column('AnvendDagsordenpunktVersioner', Boolean, nullable=False, server_default=text('((0))')),
    Column('FastholdUdvalgOverskrift', Boolean, nullable=False, server_default=text('((0))')),
    Column('SamlePDFUrl', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DffForsendelsesType', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['IntegreretBrugerID'], ['Bruger.ID'], name='FK_SystemConfiguration_Bruger'),
    PrimaryKeyConstraint('ID', name='PK_SystemConfiguration')
)

t_Udvalg = Table(
    'Udvalg', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('UdvalgIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Sortering', Integer, nullable=False, server_default=text('((-1))')),
    Column('Oprettet', DateTime),
    Column('Nedlagt', DateTime),
    Column('WebUndermappe', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('KanBeslutteAllePunkter', Boolean, nullable=False),
    Column('PunktnummereringStart', Integer, nullable=False),
    Column('FortloebendePunktnummerering', Boolean, nullable=False),
    Column('Created', DateTime, nullable=False),
    Column('CreatedBy', Integer, nullable=False),
    Column('LastChanged', DateTime, nullable=False),
    Column('LastChangedBy', Integer, nullable=False),
    Column('SekretariatID', Integer, nullable=False),
    Column('UdvalgsstrukturID', Integer, nullable=False),
    Column('PubliceringCss', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('IndstillingStandardTekst', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False, server_default=text("(N'Direktionen indstiller,')")),
    Column('StedStandardTekst', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False, server_default=text("(N'Ikke angivet')")),
    Column('MoedetidspunktStandard', DateTime),
    Column('RydIndstillingVedKopiering', Boolean, nullable=False, server_default=text('((1))')),
    Column('EksternSikkerhedsgruppe', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TekstForBesluttendeUdvalg', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False, server_default=text("(N'Udvalget har beslutningskompetence for punkter markeret med *.')")),
    Column('DefaultSagId', Integer),
    Column('Klarmeldingsfrist', Integer),
    Column('IndstillingSkalKopieresTilFeltID', Integer),
    Column('BeslutningSkalKopieresTilFeltID', Integer),
    Column('Forkortelse', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False, server_default=text("(N'NYFORK')")),
    ForeignKeyConstraint(['BeslutningSkalKopieresTilFeltID'], ['DagsordenpunktFelt.ID'], name='FK_Udvalg_DagsordenpunktFelt_beslutning'),
    ForeignKeyConstraint(['CreatedBy'], ['Bruger.ID'], name='FK_Udvalg_Bruger_CreatedBy'),
    ForeignKeyConstraint(['IndstillingSkalKopieresTilFeltID'], ['DagsordenpunktFelt.ID'], name='FK_Udvalg_DagsordenpunktFelt_Indstilling'),
    ForeignKeyConstraint(['LastChangedBy'], ['Bruger.ID'], name='FK_Udvalg_Bruger_LastChangedBy'),
    ForeignKeyConstraint(['SekretariatID'], ['Sekretariat.ID'], name='FK_Udvalg_Sekretariat_Sekretariat'),
    ForeignKeyConstraint(['UdvalgsstrukturID'], ['Udvalgsstruktur.ID'], name='FK_Udvalg_Udvalg_Udvalgsstruktur'),
    PrimaryKeyConstraint('ID', name='PK__Udvalg__7A13BF05'),
    Index('IX_Udvalg_Mappe', 'UdvalgsstrukturID', mssql_clustered=False),
    Index('UQ__Udvalg__19B50C825E73EEB1', 'UdvalgIdentity', mssql_clustered=False, unique=True)
)

t_WebWidgetBruger = Table(
    'WebWidgetBruger', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerId', Integer),
    Column('WebWidgetId', Integer),
    ForeignKeyConstraint(['BrugerId'], ['Bruger.ID'], name='FK__WebWidget__Bruge__0E0EFF63'),
    ForeignKeyConstraint(['WebWidgetId'], ['WebWidget.ID'], name='FK__WebWidget__WebWi__0F03239C'),
    PrimaryKeyConstraint('ID', name='PK__WebWidge__3214EC27778A033C')
)

t_BrugerGruppeEjer = Table(
    'BrugerGruppeEjer', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerGruppeID', Integer, nullable=False),
    Column('BrugerSettingsID', Integer, nullable=False),
    ForeignKeyConstraint(['BrugerGruppeID'], ['BrugerGruppe.ID'], name='BrugerGruppeEjer_BrugerGruppe'),
    ForeignKeyConstraint(['BrugerSettingsID'], ['BrugerSettings.ID'], name='BrugerGruppeEjer_Bruger'),
    Index('IX_BrugerGruppeEjer', 'BrugerGruppeID', 'BrugerSettingsID', mssql_clustered=False, unique=True)
)

t_BrugerSettingsAnsaettelsessted = Table(
    'BrugerSettingsAnsaettelsessted', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerSettingsID', Integer, nullable=False),
    Column('AnsaettelsesstedID', Integer, nullable=False),
    ForeignKeyConstraint(['AnsaettelsesstedID'], ['Ansaettelsessted.ID'], name='FK_BrugerSettingsAnsaettelsessteder_Ansaettelsessted'),
    ForeignKeyConstraint(['BrugerSettingsID'], ['BrugerSettings.ID'], name='FK_BrugerSettingsAnsaettelsessteder_BrugerSettings'),
    PrimaryKeyConstraint('ID', name='PK_BrugerSettingsAnsaettelsessteder'),
    Index('IX_BrugerSettingsAnsaettelsessteder', 'BrugerSettingsID', mssql_clustered=True)
)

t_BrugerSettingsAnvendteEmailAdresser = Table(
    'BrugerSettingsAnvendteEmailAdresser', metadata,
    Column('BrugerSettingsID', Integer, nullable=False),
    Column('EmailAdresse', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    ForeignKeyConstraint(['BrugerSettingsID'], ['BrugerSettings.ID'], name='FK_BrugerSettingsAnvendteEmailAdresser_BrugerSettings'),
    PrimaryKeyConstraint('ID', name='PK_BrugerSettingsAnvendteEmailAdresser')
)

t_BrugerSettingsDropFolderConfiguration = Table(
    'BrugerSettingsDropFolderConfiguration', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerSettingsID', Integer, nullable=False),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DropFolderSti', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Enabled', Boolean, nullable=False, server_default=text('((1))')),
    Column('Notificer', Integer, nullable=False, server_default=text('((1))')),
    Column('InkluderUnderFoldere', Boolean, nullable=False, server_default=text('((0))')),
    Column('ErJournaliseringskoe', Boolean, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['BrugerSettingsID'], ['BrugerSettings.ID'], name='BrugerSettingsDropFolderConfiguration_BrugerSettings'),
    PrimaryKeyConstraint('ID', name='PK_BrugerSettingsDropFolderConfiguration'),
    Index('IX_BrugerSettingsDropFolderConfiguration_BrugersettingsID', 'BrugerSettingsID', mssql_clustered=False, mssql_include=['Navn', 'Beskrivelse', 'DropFolderSti', 'Enabled', 'InkluderUnderFoldere'])
)

t_BrugerSettingsEmailKontoRegistrering = Table(
    'BrugerSettingsEmailKontoRegistrering', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerSettingsID', Integer, nullable=False),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('AccountName', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ServerName', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DatabaseName', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DomainName', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Password', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('BrugernavnEqualsPostkasse', Boolean),
    Column('EntryID', Unicode(600, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('StoreID', Unicode(600, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('UseSavedPassword', Boolean),
    Column('MailSystemTag', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('PasswordOnCreation', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('VistSessionNavn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('EmailKontoExchangeConfigurationId', Integer),
    ForeignKeyConstraint(['BrugerSettingsID'], ['BrugerSettings.ID'], name='MailSystemSessionInfo_BrugerSettings'),
    ForeignKeyConstraint(['EmailKontoExchangeConfigurationId'], ['EmailKontoExchangeConfiguration.Id'], name='FK__BrugerSet__Email__08F5448B'),
    PrimaryKeyConstraint('ID', name='PK_MailSystemSessionInfo'),
    Index('IX_MailSystemSessionInfo_BrugerSettings', 'BrugerSettingsID', mssql_clustered=False)
)

t_BrugerSettingsFavoritSag = Table(
    'BrugerSettingsFavoritSag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerSettingsID', Integer, nullable=False),
    Column('SagID', Integer),
    Column('Order', Integer, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['BrugerSettingsID'], ['BrugerSettings.ID'], name='BrugerSettingsFavoritSag_BrugerSettings'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='BrugerSettingsFavoritSag_Sag'),
    PrimaryKeyConstraint('ID', name='PK_BrugerSettingsFavoriteJournal'),
    Index('IX_BrugerSettingsFavoritSag_BrugerSettingsID', 'BrugerSettingsID', mssql_clustered=False, mssql_include=['SagID'])
)

t_BrugerSettingsFavoritSagSkabelon = Table(
    'BrugerSettingsFavoritSagSkabelon', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerSettingsID', Integer, nullable=False),
    Column('SagSkabelonID', Integer),
    ForeignKeyConstraint(['BrugerSettingsID'], ['BrugerSettings.ID'], name='FK_BrugerSettingsFavoritSagSkabelon_BrugerSettings'),
    ForeignKeyConstraint(['SagSkabelonID'], ['SagSkabelon.ID'], name='FK_BrugerSettingsFavoritSagSkabelon_SagSkabelon'),
    PrimaryKeyConstraint('Id', name='PK_BrugerSettingsFavoritSagSkabelon')
)

t_BrugerSettingsFavoritSkabelon = Table(
    'BrugerSettingsFavoritSkabelon', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerSettingsID', Integer, nullable=False),
    Column('SkabelonID', Integer),
    ForeignKeyConstraint(['BrugerSettingsID'], ['BrugerSettings.ID'], name='FK_BrugerSettingsFavoritSkabelon_BrugerSettings'),
    ForeignKeyConstraint(['SkabelonID'], ['Skabelon.ID'], name='FK_BrugerSettingsFavoritSkabelon_Skabelon'),
    PrimaryKeyConstraint('ID', name='PK_BrugersettingsFavoritSkabelon')
)

t_BrugerSettingsSagsType = Table(
    'BrugerSettingsSagsType', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerSettingsID', Integer, nullable=False),
    Column('SagsTypeID', Integer, nullable=False),
    ForeignKeyConstraint(['BrugerSettingsID'], ['BrugerSettings.ID'], name='FK_BrugerSettingsSagsType_BrugerSettings'),
    ForeignKeyConstraint(['SagsTypeID'], ['SagsType.Id'], name='FK_BrugerSettingsSagsType_SagsType'),
    PrimaryKeyConstraint('Id', name='PK__BrugerSe__3214EC07A0FFF94D')
)

t_BrugerSettingsSagsstatus = Table(
    'BrugerSettingsSagsstatus', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BrugerSettingsID', Integer, nullable=False),
    Column('SagsstatusID', Integer, nullable=False),
    ForeignKeyConstraint(['BrugerSettingsID'], ['BrugerSettings.ID'], name='FK_BrugerSettingsSagsstatus_BrugerSettings'),
    ForeignKeyConstraint(['SagsstatusID'], ['SagsStatus.ID'], name='FK_BrugerSettingsSagsstatus_Sagsstatus'),
    PrimaryKeyConstraint('ID', name='PK_BrugerSettingsSagsstatus')
)

t_BrugerSettingsStyringsreolSagsfelt = Table(
    'BrugerSettingsStyringsreolSagsfelt', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('BrugerSettingsID', Integer, nullable=False),
    Column('StyringsreolSagsfeltID', Integer, nullable=False),
    ForeignKeyConstraint(['BrugerSettingsID'], ['BrugerSettings.ID'], name='FK_BrugerSettingsStyringsreolsagsfelt_BrugerSettings'),
    ForeignKeyConstraint(['StyringsreolSagsfeltID'], ['StyringsreolSagsFelt.ID'], name='FK_BrugerSettingsStyringsreolsagsfelt_Styringsreolsagsfelt')
)

t_Dagsordenpunkt = Table(
    'Dagsordenpunkt', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DagsordenpunktTypeID', Integer, nullable=False),
    Column('AktivitetsLog', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Created', DateTime, nullable=False),
    Column('CreatedBy', Integer, nullable=False),
    Column('SagID', Integer, nullable=False),
    Column('BesluttendeUdvalgID', Integer),
    Column('RedigeresLigeNuAfID', Integer),
    Column('Timestamp', TIMESTAMP, nullable=False),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    Column('Beskrivelse', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DagsordenpunktIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    ForeignKeyConstraint(['BesluttendeUdvalgID'], ['Udvalg.ID'], name='FK_Dagsordenpunkt_BesluttendeUdvalg_Udvalg'),
    ForeignKeyConstraint(['CreatedBy'], ['Bruger.ID'], name='FK_Dagsordenpunkt_Bruger_CreatedBy'),
    ForeignKeyConstraint(['DagsordenpunktTypeID'], ['DagsordenpunktType.ID'], name='FK_Dagsordenpunkt_Dagsordenpunkttype'),
    ForeignKeyConstraint(['RedigeresLigeNuAfID'], ['Bruger.ID'], name='FK_Dagsordenpunkt_RedigresAfBruger'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='FK_Dagsordenpunkt_Sag'),
    PrimaryKeyConstraint('ID', name='PK__Dagsordenpunkt__72729D3D'),
    Index('IX_Dagsordenpunkt_SagID', 'SagID', mssql_clustered=False),
    Index('UQ__Dagsorde__984DA92CC8921714', 'DagsordenpunktIdentity', mssql_clustered=False, unique=True)
)

t_DagsordenpunktVersion = Table(
    'DagsordenpunktVersion', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('VersionNummer', Integer, nullable=False),
    Column('VersionCreated', DateTime, nullable=False),
    Column('DagsordenpunktID', Integer, nullable=False),
    Column('Offentlig', Boolean, nullable=False),
    Column('Note', Unicode(2000, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Overskrift', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('OffentligOverskriftVedIkkeOffentlig', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Gruppering', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DagsordenpunktTypeID', Integer, nullable=False),
    Column('AktivitetsLog', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Created', DateTime, nullable=False),
    Column('CreatedBy', Integer, nullable=False),
    Column('LastChanged', DateTime, nullable=False),
    Column('LastChangedBy', Integer, nullable=False),
    Column('IndstillingOverskrift', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SagID', Integer, nullable=False),
    Column('AnsvarligID', Integer, nullable=False),
    Column('BesluttendeUdvalgID', Integer),
    Column('RedigeresLigeNuAfID', Integer),
    Column('Timestamp', TIMESTAMP, nullable=False),
    Column('YderligereSagsNumre', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Version', Integer, nullable=False, server_default=text('((1))')),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    Column('HarBeslutning', Boolean, nullable=False),
    Column('Beskrivelse', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['AnsvarligID'], ['Bruger.ID'], name='FK_DagsordenpunktVersion_Bruger_AnsvarligID'),
    ForeignKeyConstraint(['BesluttendeUdvalgID'], ['Udvalg.ID'], name='FK_DagsordenpunktVersion_BesluttendeUdvalg_Udvalg'),
    ForeignKeyConstraint(['CreatedBy'], ['Bruger.ID'], name='FK_DagsordenpunktVersion_Bruger_CreatedBy'),
    ForeignKeyConstraint(['DagsordenpunktTypeID'], ['DagsordenpunktType.ID'], name='FK_DagsordenpunktVersion_Dagsordenpunkttype'),
    ForeignKeyConstraint(['LastChangedBy'], ['Bruger.ID'], name='FK_DagsordenpunktVersion_Bruger_LastChangedBy'),
    ForeignKeyConstraint(['RedigeresLigeNuAfID'], ['Bruger.ID'], name='FK_DagsordenpunktVersion_RedigresAfBruger'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='FK_DagsordenpunktVersion_Sag'),
    PrimaryKeyConstraint('ID', name='PK_DagsordenpunktVersion'),
    Index('IX_DagsordenpunktVersion', 'VersionNummer', 'DagsordenpunktID', mssql_clustered=True, unique=True)
)

t_DagsordenpunkttypeIUdvalg = Table(
    'DagsordenpunkttypeIUdvalg', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DagsordenpunkttypeID', Integer, nullable=False),
    Column('UdvalgID', Integer, nullable=False),
    Column('Sortering', Integer, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['DagsordenpunkttypeID'], ['DagsordenpunktType.ID'], name='FK_DagsordenpunkttypeIUdvalg_Dagsordenpunkttype'),
    ForeignKeyConstraint(['UdvalgID'], ['Udvalg.ID'], name='FK_DagsordenpunkttypeIUdvalg_Udvalg'),
    PrimaryKeyConstraint('ID', name='PK_DagsordenpunkttypeIUdvalg')
)

t_DelforloebDokumentRegistrering = Table(
    'DelforloebDokumentRegistrering', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DelforloebID', Integer, nullable=False),
    Column('DokumentRegistreringID', Integer, nullable=False),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    ForeignKeyConstraint(['DelforloebID'], ['Delforloeb.ID'], name='DelforloebDokumentRegistrering_Delforloeb'),
    ForeignKeyConstraint(['DokumentRegistreringID'], ['DokumentRegistrering.ID'], name='DelforloebDokumentRegistrering_DokumentRegistrering'),
    PrimaryKeyConstraint('ID', name='PK_DelforloebDokumentRegistreringer'),
    Index('IX_DelforloebDokumentRegistrering_Delforloeb', 'DokumentRegistreringID', mssql_clustered=False, mssql_include=['DelforloebID']),
    Index('IX_DelforloebDokumentRegistrering_DelforloebID', 'DelforloebID', mssql_clustered=False),
    Index('UNIQUE_DELFORLOEB_DOKUMENTREG', 'DelforloebID', 'DokumentRegistreringID', mssql_clustered=False, unique=True)
)

t_DelforloebEksternIdentitet = Table(
    'DelforloebEksternIdentitet', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DelforloebID', Integer, nullable=False),
    Column('Oprettet', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('EksternSystemID', Integer, nullable=False),
    Column('EksternIdentitet', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Status', TINYINT, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['DelforloebID'], ['Delforloeb.ID'], name='FK_DelforloebEksternIdentitet_Delforloeb'),
    ForeignKeyConstraint(['EksternSystemID'], ['KnownEksterntSystem.ID'], name='FK_DelforloebEksternIdentitet_KnownEksterntSystem'),
    PrimaryKeyConstraint('ID', name='PK_DelforloebEksternIdentitet')
)

t_DelforloebEmneOrd = Table(
    'DelforloebEmneOrd', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DelforloebID', Integer, nullable=False),
    Column('EmneOrdID', Integer, nullable=False),
    ForeignKeyConstraint(['DelforloebID'], ['Delforloeb.ID'], name='DelforloebEmneOrd_Delforloeb'),
    ForeignKeyConstraint(['EmneOrdID'], ['EmneOrd.ID'], name='DelforloebEmneOrd_EmneOrd'),
    PrimaryKeyConstraint('ID', name='PK_DelforloebEmneOrd')
)

t_DokumentRegistreringSletning = Table(
    'DokumentRegistreringSletning', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DokumentRegistreringID', Integer, nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('Aarsag', String(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('TimeStamp', DateTime, server_default=text('(getdate())')),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='FK_DokumentRegistreringSletning_Bruger'),
    ForeignKeyConstraint(['DokumentRegistreringID'], ['DokumentRegistrering.ID'], name='FK_DokumentRegistreringSletning_DokumentRegistrering'),
    PrimaryKeyConstraint('ID', name='PK_DokumentRegistreringSletning')
)

t_Flow = Table(
    'Flow', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DokumentID', Integer),
    Column('KladdeID', Integer),
    Column('FlowForloeb', Integer, nullable=False),
    Column('Navn', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Oprettet', DateTime, nullable=False),
    Column('OprettetAf', Integer, nullable=False),
    Column('NextFristDato', DateTime),
    Column('Status', Integer, nullable=False),
    Column('Discriminator', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    ForeignKeyConstraint(['DokumentID'], ['Dokument.ID'], name='FK_Flow_Dokument'),
    ForeignKeyConstraint(['KladdeID'], ['Kladde.ID'], name='FK_Flow_Kladde'),
    ForeignKeyConstraint(['OprettetAf'], ['Bruger.ID'], name='FK_Flow_Bruger'),
    PrimaryKeyConstraint('ID', name='PK__Flow__3214EC272D05FF8D')
)

t_Handling = Table(
    'Handling', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('ErindringSkabelonID', Integer),
    Column('SkabelonID', Integer),
    Column('SkabelonTypeID', Integer),
    Column('SagSkabelonID', Integer),
    Column('AnvendErindringSkabelonID', Integer),
    Column('JournalNotatOverskrift', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('JournalNotatNote', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['AnvendErindringSkabelonID'], ['ErindringSkabelon.ID'], name='FK_Handling_AnvendErindringSkabelon'),
    ForeignKeyConstraint(['ErindringSkabelonID'], ['ErindringSkabelon.ID'], name='FK_Handling_ErindringSkabelon'),
    ForeignKeyConstraint(['SagSkabelonID'], ['SagSkabelon.ID'], name='FK_Handling_SagSkabelon'),
    ForeignKeyConstraint(['SkabelonID'], ['Skabelon.ID'], name='FK_Handling_Skabelon'),
    ForeignKeyConstraint(['SkabelonTypeID'], ['SkabelonType.ID'], name='FK_Handling_SkabelonType'),
    PrimaryKeyConstraint('ID', name='pk_Handling')
)

t_JournalArkNoteVedrPart = Table(
    'JournalArkNoteVedrPart', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('JournalArkNoteID', Integer, nullable=False),
    Column('SagspartID', Integer, nullable=False),
    ForeignKeyConstraint(['JournalArkNoteID'], ['JournalArkNote.ID'], name='FK_JournalArkNoteVedrPart_JournalArkNote'),
    ForeignKeyConstraint(['SagspartID'], ['SagsPart.ID'], name='FK_JournalArkNoteVedrPart_SagsPart'),
    PrimaryKeyConstraint('ID', name='PK_JournalArkNoteVedrPart'),
    Index('IX_JournalarkNoteID', 'JournalArkNoteID', mssql_clustered=False, mssql_include=['SagspartID']),
    Index('IX_Sagspart_JournalArkNote', 'SagspartID', mssql_clustered=False, mssql_include=['JournalArkNoteID'])
)

t_KladdePart = Table(
    'KladdePart', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('KladdeID', Integer, nullable=False),
    Column('PartID', Integer, nullable=False),
    Column('PartType', Integer, nullable=False),
    Column('KontaktForm', Integer, nullable=False),
    Column('AnvendtAdresse', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SekundaerPart', Boolean, nullable=False),
    Column('Markeret', Boolean, nullable=False),
    Column('MergeData', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('FirmaAttentionPersonID', Integer),
    Column('Status', TINYINT, nullable=False, server_default=text('((0))')),
    Column('StatusInfo', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('StatusTidspunkt', DateTime),
    ForeignKeyConstraint(['FirmaAttentionPersonID'], ['FirmaAttentionPerson.ID'], name='FK_KladdePart_FirmaAttentionPerson'),
    ForeignKeyConstraint(['KladdeID'], ['Kladde.ID'], name='KladdePart_Kladde'),
    ForeignKeyConstraint(['KontaktForm'], ['KontaktFormOpslag.ID'], name='KladdePart_KontaktForm'),
    PrimaryKeyConstraint('ID', name='PK_KladdePart'),
    Index('IX_KladdePart_KladdeID', 'KladdeID', mssql_clustered=False),
    Index('UNIQUE_KLADDEPART', 'KladdeID', 'PartID', 'PartType', mssql_clustered=False, unique=True)
)

t_KladdeRegistrering = Table(
    'KladdeRegistrering', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagID', Integer, nullable=False),
    Column('KladdeID', Integer, nullable=False),
    Column('ErBeskyttet', Boolean, nullable=False, server_default=text('((0))')),
    Column('SecuritySetID', Integer),
    Column('RegistreretAfID', Integer, nullable=False),
    Column('Registreret', DateTime, nullable=False),
    Column('Beskrivelse', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('SagsPartID', Integer),
    Column('Navn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('DeletedState', TINYINT, nullable=False, server_default=text('((0))')),
    Column('DeletedDate', DateTime),
    Column('DeletedByID', Integer),
    Column('DeletedReason', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DeleteConfirmed', DateTime),
    Column('DeleteConfirmedByID', Integer),
    ForeignKeyConstraint(['KladdeID'], ['Kladde.ID'], name='KladdeRegistrering_Kladde'),
    ForeignKeyConstraint(['RegistreretAfID'], ['Bruger.ID'], name='KladdeRegistrering_Bruger'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='KladdeRegistrering_Sag'),
    ForeignKeyConstraint(['SagsPartID'], ['SagsPart.ID'], name='KladdeRegistrering_SagsPart'),
    ForeignKeyConstraint(['SecuritySetID'], ['SecuritySet.ID'], name='KladdeRegistrering_SecuritySet'),
    PrimaryKeyConstraint('ID', name='PK_SagKladde'),
    Index('IX_KladdeRegistrering_KladdeID', 'KladdeID', mssql_clustered=False),
    Index('IX_KladdeRegistrering_Sag', 'SagID', mssql_clustered=True)
)

t_MapDelforloeb = Table(
    'MapDelforloeb', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('MapSagID', Integer, nullable=False),
    Column('Kode', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Titel', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['MapSagID'], ['MapSag.ID'], name='FK_MapDelforloeb_MapSag'),
    PrimaryKeyConstraint('ID', name='PK_MapDelforloeb')
)

t_Memo = Table(
    'Memo', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Message', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Scheme', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Version', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('DokumentRegistreringID', Integer, nullable=False),
    Column('Modtaget', Boolean, nullable=False),
    ForeignKeyConstraint(['DokumentRegistreringID'], ['DokumentRegistrering.ID'], name='FK_Memo_DokumentRegistrering'),
    PrimaryKeyConstraint('ID', name='PK_Memo'),
    Index('IX_Memo_DokumentRegistreringID', 'DokumentRegistreringID', mssql_clustered=False)
)

t_Moede = Table(
    'Moede', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('MoedeIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    Column('Dato', DateTime, nullable=False),
    Column('Sted', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Aktiv', Boolean, nullable=False),
    Column('PunktnummereringStart', Integer, nullable=False),
    Column('FortloebendePunktnummerering', Boolean, nullable=False),
    Column('Afsluttet', Boolean, nullable=False),
    Column('FoerstAfsluttet', DateTime),
    Column('Created', DateTime, nullable=False),
    Column('CreatedBy', Integer, nullable=False),
    Column('LastChanged', DateTime, nullable=False),
    Column('LastChangedBy', Integer, nullable=False),
    Column('UdvalgID', Integer),
    Column('ErSkabelon', Boolean, nullable=False, server_default=text('((0))')),
    Column('SkabelonNavn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Klarmeldingsfrist', DateTime),
    Column('Sluttidspunkt', DateTime),
    ForeignKeyConstraint(['CreatedBy'], ['Bruger.ID'], name='FK_Moede_Bruger_CreatedBy'),
    ForeignKeyConstraint(['LastChangedBy'], ['Bruger.ID'], name='FK_Moede_Bruger_LastChangedBy'),
    ForeignKeyConstraint(['UdvalgID'], ['Udvalg.ID'], name='FK_Moede_Moeder_Udvalg'),
    PrimaryKeyConstraint('ID', name='PK__Moede__6CB9C3E7'),
    Index('IX_Moede_Udvalg', 'UdvalgID', mssql_clustered=False),
    Index('UQ__Moede__A34F60B8B7F05FCE', 'MoedeIdentity', mssql_clustered=False, unique=True)
)

t_PubliseringDokument = Table(
    'PubliseringDokument', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('PubliseringID', Integer, nullable=False),
    Column('DokumentRegistreringID', Integer, nullable=False),
    Column('Navn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ErPubliseretFoer', Boolean, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['DokumentRegistreringID'], ['DokumentRegistrering.ID'], name='FK_PubliseringDokument_DokumentRegistrering'),
    ForeignKeyConstraint(['PubliseringID'], ['Publisering.ID'], name='FK_PubliceringDokument_Publicering'),
    PrimaryKeyConstraint('ID', name='PK_PubliceringDokument'),
    Index('IX_PubliceringDokument', 'PubliseringID', 'DokumentRegistreringID', mssql_clustered=False, unique=True)
)

t_PubliseringPlan = Table(
    'PubliseringPlan', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('AgentIdentity', Uuid, nullable=False),
    Column('Aktiv', Boolean, nullable=False, server_default=text('((1))')),
    Column('PubliseringIndstillingerID', Integer, nullable=False),
    Column('PubliseringNavn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Opfoersel', TINYINT),
    Column('SidstePubliseringID', Integer),
    Column('SidsteKoersel', DateTime),
    Column('Statement', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['PubliseringIndstillingerID'], ['PubliseringIndstillinger.ID'], name='FK_PubliseringPlan_PubliseringIndstillinger'),
    ForeignKeyConstraint(['SidstePubliseringID'], ['Publisering.ID'], name='FK_PubliseringPlan_Publisering'),
    PrimaryKeyConstraint('ID', name='PK_PubliseringPlan')
)

t_QueueCommandFile = Table(
    'QueueCommandFile', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('QueueCommandID', Integer, nullable=False),
    Column('Data', IMAGE),
    Column('Filename', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('OriginalLocation', Unicode(400, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('Length', BigInteger, nullable=False),
    Column('Sortering', Integer, nullable=False, server_default=text('((0))')),
    Column('MetaName', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['QueueCommandID'], ['QueueCommand.ID'], name='FK_CommandQueueFile_CommandQueue'),
    PrimaryKeyConstraint('ID', name='PK_QueBlob')
)

t_RolleTildeling = Table(
    'RolleTildeling', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('UdvalgID', Integer),
    Column('BrugerID', Integer),
    Column('Roller', BigInteger, nullable=False, server_default=text('((0))')),
    Column('SikkerhedsgruppeID', Integer),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='FK_RolleTildeling_Bruger'),
    ForeignKeyConstraint(['SikkerhedsgruppeID'], ['Sikkerhedsgruppe.ID'], name='FK_RolleTildeling_Sikkerhedsgruppe'),
    ForeignKeyConstraint(['UdvalgID'], ['Udvalg.ID'], name='FK_RolleIUdvalg_Udvalg_Udvalg'),
    PrimaryKeyConstraint('ID', name='PK__RolleIUdvalg__6EA20C59')
)

t_SagHistorikStyringsreolStatus = Table(
    'SagHistorikStyringsreolStatus', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('FraHyldeID', Integer),
    Column('TilHyldeID', Integer),
    Column('BrugerID', Integer, nullable=False),
    Column('Dato', DateTime, nullable=False),
    Column('SagID', Integer, nullable=False),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='FK_SagHistorikStyringsreolStatus_Bruger'),
    ForeignKeyConstraint(['FraHyldeID'], ['StyringsreolHylde.ID'], name='FK_SagHistorikStyringsreolStatus_StyringsreolHylde_Fra'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='FK_SagHistorikStyringsreolStatus_Sag'),
    ForeignKeyConstraint(['TilHyldeID'], ['StyringsreolHylde.ID'], name='FK_SagHistorikStyringsreolStatus_StyringsreolHylde_Til'),
    PrimaryKeyConstraint('ID', name='PK_SagHistorikReolStatus')
)

t_SagSkabelonErindringSkabelon = Table(
    'SagSkabelonErindringSkabelon', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagSkabelonID', Integer, nullable=False),
    Column('ErindringSkabelonID', Integer, nullable=False),
    Column('Trin', Integer),
    ForeignKeyConstraint(['ErindringSkabelonID'], ['ErindringSkabelon.ID'], name='FK_SagSkabelonErindringSkabelon_ErindringSkabelon'),
    ForeignKeyConstraint(['SagSkabelonID'], ['SagSkabelon.ID'], name='FK_SagSkabelonErindringSkabelon_SagSkabelon'),
    PrimaryKeyConstraint('ID', name='PK_SagSkabelonErindringSkabelon')
)

t_SkabelonKladde = Table(
    'SkabelonKladde', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SkabelonID', Integer, nullable=False),
    Column('KladdeID', Integer, nullable=False),
    Column('SkabelonGrundskabelonID', Integer, nullable=False),
    ForeignKeyConstraint(['KladdeID'], ['Kladde.ID'], name='SkabelonKladde_Kladde'),
    ForeignKeyConstraint(['SkabelonGrundskabelonID'], ['SkabelonGrundSkabelon.ID'], name='FK_SkabelonKladde_SkabelonGrundSkabelon'),
    ForeignKeyConstraint(['SkabelonID'], ['Skabelon.ID'], name='SkabelonKladde_Skabelon'),
    PrimaryKeyConstraint('ID', name='PK_SkabelonKladde'),
    Index('IX_SkabelonKladde', 'KladdeID', mssql_clustered=False, mssql_include=['SkabelonID', 'SkabelonGrundskabelonID']),
    Index('IX_SkabelonKladde_Unique', 'SkabelonID', 'KladdeID', mssql_clustered=False, unique=True)
)

t_SkabelonTrin = Table(
    'SkabelonTrin', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SkabelonID', Integer, nullable=False),
    Column('SkabelonTekstBlokID', Integer, nullable=False),
    Column('Trin', Integer, nullable=False),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    ForeignKeyConstraint(['SkabelonID'], ['Skabelon.ID'], name='SkabelonTrin_Skabelon'),
    ForeignKeyConstraint(['SkabelonTekstBlokID'], ['SkabelonTekstblok.ID'], name='SkabelonTrin_SkabelonTekstblok'),
    PrimaryKeyConstraint('ID', name='PK_SkabelonTrin')
)

t_SkabelonTypeSkabelon = Table(
    'SkabelonTypeSkabelon', metadata,
    Column('SkabelonID', Integer, nullable=False),
    Column('SkabelonTypeID', Integer, nullable=False),
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    ForeignKeyConstraint(['SkabelonID'], ['Skabelon.ID'], name='SkabelonType_Skabelon'),
    ForeignKeyConstraint(['SkabelonTypeID'], ['SkabelonType.ID'], name='SkabelonType_SkabelonType'),
    PrimaryKeyConstraint('ID', name='PK_SkabelontypeSkabelon'),
    Index('IX_SkabelonTypeSkabelon', 'SkabelonID', 'SkabelonTypeID', mssql_clustered=True)
)

t_Stedfaestelse = Table(
    'Stedfaestelse', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Noegle', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('StedfaestetAfID', Integer, nullable=False),
    Column('SystemId', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Oprettet', DateTime, nullable=False),
    Column('StedfaestetType', Integer, nullable=False),
    Column('StedfaestetTypeId', Integer, nullable=False),
    Column('Status', Integer, nullable=False),
    Column('GeometriID', Integer),
    Column('SagID', Integer, nullable=False),
    Column('DokumentRegistreringID', Integer),
    Column('OprettetAutomatisk', Boolean, nullable=False),
    Column('Redigeret', DateTime),
    ForeignKeyConstraint(['DokumentRegistreringID'], ['DokumentRegistrering.ID'], name='FK_Stedfaestelse_DokumentRegistrering'),
    ForeignKeyConstraint(['GeometriID'], ['Geometri.ID'], name='FK_Stedfaestelse_Geometri'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='FK_Stedfaestelse_Sag'),
    ForeignKeyConstraint(['StedfaestetAfID'], ['Bruger.ID'], name='FK_Stedfaestelse_Bruger'),
    PrimaryKeyConstraint('ID', name='PK_Stedfaestelse'),
    Index('IX_Stedfaestelse_Status', 'SagID', 'Status', mssql_clustered=False)
)

t_StyringsreolHyldeErindringSkabelon = Table(
    'StyringsreolHyldeErindringSkabelon', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('StyringsreolHyldeID', Integer, nullable=False),
    Column('ErindringSkabelonID', Integer, nullable=False),
    ForeignKeyConstraint(['ErindringSkabelonID'], ['ErindringSkabelon.ID'], name='fk_StyringsreolHyldeErindringSkabelon_ErindringSkabelon'),
    ForeignKeyConstraint(['StyringsreolHyldeID'], ['StyringsreolHylde.ID'], name='fk_StyringsreolHyldeErindringSkabelon_StyringsreolHylde'),
    PrimaryKeyConstraint('ID', name='pk_StyringsreolHyldeErindringSkabelon')
)

t_StyringsreolHyldeFag = Table(
    'StyringsreolHyldeFag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('FarveIndex', Integer, nullable=False),
    Column('NormtidDage', Integer),
    Column('StyringsreolHyldeID', Integer, nullable=False),
    Column('NormtidDato', DateTime),
    Column('SorteringsIndex', Integer),
    ForeignKeyConstraint(['StyringsreolHyldeID'], ['StyringsreolHylde.ID'], name='FK_StyringsreolHyldeFag_StyringsreolHylde'),
    PrimaryKeyConstraint('ID', name='PK_StyringsreolFag')
)

t_TrustedAssembly = Table(
    'TrustedAssembly', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SystemConfigurationID', Integer, nullable=False),
    Column('AssemblyFileName', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('AssemblyGuid', Uuid, nullable=False),
    Column('Enabled', Boolean, nullable=False, server_default=text('((0))')),
    Column('Navn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    ForeignKeyConstraint(['SystemConfigurationID'], ['SystemConfiguration.ID'], name='TrustedAssembly_SystemConfiguration'),
    PrimaryKeyConstraint('ID', name='PK_TrustedAssemblies'),
    Index('IX_TrustedAssembly', 'AssemblyGuid', mssql_clustered=False, unique=True)
)

t_Udvalgsmedlem = Table(
    'Udvalgsmedlem', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Suppleant', Boolean, nullable=False),
    Column('UdvaelgspersonID', Integer, nullable=False),
    Column('UdvalgID', Integer, nullable=False),
    Column('Sortering', Integer, nullable=False, server_default=text('((-1))')),
    ForeignKeyConstraint(['UdvaelgspersonID'], ['Udvalgsperson.ID'], name='FK_Udvalgsmedlem_Udvalgsperson'),
    ForeignKeyConstraint(['UdvalgID'], ['Udvalg.ID'], name='FK_Udvaelgsmedlem_Udvaelgsmedlemmer_Udvalg'),
    PrimaryKeyConstraint('ID', name='PK__Udvaelgsmedlem__7DE44FE9')
)

t_WordGeneratorUdvalgExtension = Table(
    'WordGeneratorUdvalgExtension', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('UdvalgID', Integer, nullable=False),
    Column('WordTemplateGenerering', IMAGE),
    Column('WordTemplateTilbagejournalisering', IMAGE),
    Column('TvungenSideskiftEfterPunkt', Boolean, nullable=False, server_default=text('((1))')),
    Column('UdrykPunktnummer', Boolean, nullable=False, server_default=text('((0))')),
    Column('FjernLinks', Boolean, nullable=False, server_default=text('((0))')),
    Column('WordTemplateGenereringFilename', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('WordTemplateTilbagejournaliseringFilename', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['UdvalgID'], ['Udvalg.ID'], name='FK_WordGeneratorUdvalgExtension_Udvalg'),
    PrimaryKeyConstraint('ID', name='PK_WordGeneratorUdvalgExtension'),
    Index('IX_WordGeneratorUdvalgExtension', 'UdvalgID', mssql_clustered=False, unique=True)
)

t_Beslutningsvej = Table(
    'Beslutningsvej', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DagsordenpunktID', Integer, nullable=False),
    Column('MoedeID', Integer, nullable=False),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    ForeignKeyConstraint(['DagsordenpunktID'], ['Dagsordenpunkt.ID'], name='FK_Beslutningsvej_Dagsordenpunkt'),
    ForeignKeyConstraint(['MoedeID'], ['Moede.ID'], name='FK_Beslutningsvej_Moede'),
    PrimaryKeyConstraint('ID', name='PK_Beslutningsvej')
)

t_Bilag = Table(
    'Bilag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Sortering', Integer, nullable=False),
    Column('DokumentRegistreringID', Integer),
    Column('KladdeRegistreringID', Integer),
    Column('MaaPubliceres', Boolean, nullable=False, server_default=text('((0))')),
    Column('ReferenceNummer', Integer, nullable=False),
    Column('LinkTekst', Unicode(300, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('FilnavnUdenExtension', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Aktiv', Boolean, nullable=False),
    Column('BilagIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    ForeignKeyConstraint(['DokumentRegistreringID'], ['DokumentRegistrering.ID'], name='FK_Bilag_DokumentRegistrering'),
    ForeignKeyConstraint(['KladdeRegistreringID'], ['KladdeRegistrering.ID'], name='FK_Bilag_KladdeRegistrering'),
    PrimaryKeyConstraint('ID', name='PK__Bilag__708A54CB'),
    Index('IX_KladdeRegistrering_Aktiv_Dokumentregistrering', 'KladdeRegistreringID', 'Aktiv', 'DokumentRegistreringID', mssql_clustered=False, mssql_include=['ID']),
    Index('UQ__Bilag__CBC12088D525635C', 'BilagIdentity', mssql_clustered=False, unique=True)
)

t_Dagsorden = Table(
    'Dagsorden', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DagsordenIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    Column('Sortering', Integer, nullable=False, server_default=text('((32767))')),
    Column('PunktnummereringStart', Integer, nullable=False),
    Column('Offentlig', Boolean, nullable=False),
    Column('Tillaegsdagsorden', Boolean, nullable=False),
    Column('SidenummereringStart', Integer, nullable=False),
    Column('ValgfriForsidetekstHtml', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('LukketForTilgang', Boolean, nullable=False),
    Column('Publiceret', Boolean, nullable=False),
    Column('Created', DateTime, nullable=False),
    Column('CreatedBy', Integer, nullable=False),
    Column('LastChanged', DateTime, nullable=False),
    Column('LastChangedBy', Integer, nullable=False),
    Column('MoedeID', Integer, nullable=False),
    Column('Historik', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('ErSkabelon', Boolean, nullable=False, server_default=text('((0))')),
    Column('SkabelonNavn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['CreatedBy'], ['Bruger.ID'], name='FK_Dagsorden_Bruger_CreatedBy'),
    ForeignKeyConstraint(['LastChangedBy'], ['Bruger.ID'], name='FK_Dagsorden_Bruger_LastChangedBy'),
    ForeignKeyConstraint(['MoedeID'], ['Moede.ID'], name='FK_Dagsorden_Dagsordener_Moede'),
    PrimaryKeyConstraint('ID', name='PK__Dagsorden__68E93303'),
    Index('IX_Dagsorden_Moede', 'MoedeID', mssql_clustered=False),
    Index('UQ__Dagsorde__44B20D2A23D58E09', 'DagsordenIdentity', mssql_clustered=False, unique=True)
)

t_DagsordenpunktRessource = Table(
    'DagsordenpunktRessource', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DagsordenpunktID', Integer, nullable=False),
    Column('RessourceID', Integer, nullable=False),
    ForeignKeyConstraint(['DagsordenpunktID'], ['Dagsordenpunkt.ID'], name='FK_DagsordenpunktRessource_Dagsordenpunkt'),
    ForeignKeyConstraint(['RessourceID'], ['Ressource.ID'], name='FK_DagsordenpunktRessource_Ressource'),
    PrimaryKeyConstraint('ID', name='PK_DagsordenpunktRessource'),
    Index('IX_DagsordenpunktRessource', 'DagsordenpunktID', mssql_clustered=True)
)

t_DagsordenpunktVersionFeltIndhold = Table(
    'DagsordenpunktVersionFeltIndhold', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DagsordenpunktFeltIndholdId', Integer, nullable=False),
    Column('DagsordenpunktVersionId', Integer, nullable=False),
    Column('Redigerbar', Boolean, nullable=False, server_default=text('((1))')),
    ForeignKeyConstraint(['DagsordenpunktFeltIndholdId'], ['DagsordenpunktFeltIndhold.Id'], name='FK_DagsordenpunktVersionFeltIndhold_DagsordenpunktFeltIndhold'),
    ForeignKeyConstraint(['DagsordenpunktVersionId'], ['DagsordenpunktVersion.ID'], name='FK_DagsordenpunktVersionFeltIndhold_DagsordenpunktsVersion'),
    PrimaryKeyConstraint('Id', name='PK_DagsordenpunktVersionFeltIndhold'),
    Index('AK_DagsordenpunktVersionFeltIndhold_FeltId_BehandlingId', 'DagsordenpunktFeltIndholdId', 'DagsordenpunktVersionId', mssql_clustered=False, unique=True)
)

t_DelforloebDagsordenpunkt = Table(
    'DelforloebDagsordenpunkt', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DelforloebID', Integer, nullable=False),
    Column('DagsordenpunktID', Integer, nullable=False),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    ForeignKeyConstraint(['DagsordenpunktID'], ['Dagsordenpunkt.ID'], name='FK_DelforloebDagsordenpunkt_Dagsordenpunkt'),
    ForeignKeyConstraint(['DelforloebID'], ['Delforloeb.ID'], name='FK_DelforloebDagsordenpunkt_Delforloeb'),
    PrimaryKeyConstraint('ID', name='PK_DelforloebDagsordenpunkt')
)

t_DelforloebKladdeRegistrering = Table(
    'DelforloebKladdeRegistrering', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DelforloebID', Integer, nullable=False),
    Column('KladdeRegistreringID', Integer, nullable=False),
    Column('OrgPK_ID', Integer),
    Column('IsImportedField', Integer),
    ForeignKeyConstraint(['DelforloebID'], ['Delforloeb.ID'], name='DelforloebKladdeRegistrering_Delforloeb'),
    ForeignKeyConstraint(['KladdeRegistreringID'], ['KladdeRegistrering.ID'], name='DelforloebKladdeRegistrering_KladdeRegistrering'),
    PrimaryKeyConstraint('ID', name='PK_DelforloebKladdeRegistrering'),
    Index('IX_Delforloeb_KladdeRegistrering', 'DelforloebID', 'KladdeRegistreringID', mssql_clustered=False),
    Index('UNIQUE_DELFORLOEB_KLADDEREG', 'DelforloebID', 'KladdeRegistreringID', mssql_clustered=False, unique=True)
)

t_FlowModtager = Table(
    'FlowModtager', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('FlowID', Integer, nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('Opgave', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Bemaerkninger', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS')),
    Column('Tidsfrist', DateTime, nullable=False),
    Column('ErindringID', Integer),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='FK_FlowModtager_Bruger'),
    ForeignKeyConstraint(['FlowID'], ['Flow.ID'], name='FK_FlowModtager_Flow'),
    PrimaryKeyConstraint('ID', name='PK__FlowModt__3214EC27EBB4D623')
)

t_Fravaer = Table(
    'Fravaer', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('UdvalgspersonId', Integer, nullable=False),
    Column('MoedeId', Integer, nullable=False),
    ForeignKeyConstraint(['MoedeId'], ['Moede.ID'], name='FK_Fravaer_Moede'),
    ForeignKeyConstraint(['UdvalgspersonId'], ['Udvalgsperson.ID'], name='FK_Fravaer_Udvalgsperson'),
    PrimaryKeyConstraint('Id', name='PK__Fravaer__3214EC07255C3522'),
    Index('IX_Fravaer_MoedeId_UdvalgspersonId', 'MoedeId', 'UdvalgspersonId', mssql_clustered=False, unique=True)
)

t_KladdePartDokument = Table(
    'KladdePartDokument', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('KladdeID', Integer, nullable=False),
    Column('KladdePartID', Integer),
    Column('DokumentID', Integer, nullable=False),
    ForeignKeyConstraint(['DokumentID'], ['Dokument.ID'], name='FK_KladdePartDokument_Dokument'),
    ForeignKeyConstraint(['KladdePartID'], ['KladdePart.ID'], name='FK_KladdePartDokument_KladdePart'),
    PrimaryKeyConstraint('ID', name='PK_KladdePartDokument'),
    Index('IX_KladdePartDokument', 'KladdeID', 'KladdePartID', 'DokumentID', mssql_clustered=True, unique=True)
)

t_MapDelforloebDokument = Table(
    'MapDelforloebDokument', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('MapDelforloebID', Integer, nullable=False),
    Column('Kode', Unicode(50, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Titel', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['MapDelforloebID'], ['MapDelforloeb.ID'], name='FK_MapDelforloebDokument_MapDelforloeb'),
    PrimaryKeyConstraint('ID', name='PK_MapDelforloebDokument')
)

t_PluginConfigurationSecuritySet = Table(
    'PluginConfigurationSecuritySet', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('TrustedAssemblyID', Integer, nullable=False),
    Column('SecuritySetID', Integer, nullable=False),
    ForeignKeyConstraint(['SecuritySetID'], ['SecuritySet.ID'], name='FK_SecuritySet_TrustedAssembly'),
    ForeignKeyConstraint(['TrustedAssemblyID'], ['TrustedAssembly.ID'], name='FK_TrustedAssembly_SecuritySet')
)

t_StyringsreolHistorik = Table(
    'StyringsreolHistorik', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Tidspunkt', DateTime, nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('AnsaettelsesstedID', Integer, nullable=False),
    Column('ReolID', Integer, nullable=False),
    Column('ReolNavn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('HyldeID', Integer, nullable=False),
    Column('HyldeNavn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('HyldeSagsstatusID', Integer, nullable=False),
    Column('HyldeNormtidstype', Integer, nullable=False),
    Column('FagID', Integer, nullable=False),
    Column('FagNormtidDage', Integer),
    Column('FagNormtidDato', DateTime),
    ForeignKeyConstraint(['AnsaettelsesstedID'], ['Ansaettelsessted.ID'], name='FK_StyringsreolHistorik_Ansaettelsessted'),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='FK_StyringsreolHistorik_Bruger'),
    ForeignKeyConstraint(['FagID'], ['StyringsreolHyldeFag.ID'], name='FK_StyringsreolHistorik_StyringsreolHyldeFag'),
    ForeignKeyConstraint(['HyldeID'], ['StyringsreolHylde.ID'], name='FK_StyringsreolHistorik_StyringsreolHylde'),
    ForeignKeyConstraint(['HyldeSagsstatusID'], ['SagsStatus.ID'], name='FK_StyringsreolHistorik_SagsStatus'),
    ForeignKeyConstraint(['ReolID'], ['Styringsreol.ID'], name='FK_StyringsreolHistorik_Styringsreol'),
    PrimaryKeyConstraint('ID', name='PK_StyringsreolHistorik')
)

t_DagsordenpunktsBehandling = Table(
    'DagsordenpunktsBehandling', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DagsordenId', Integer, nullable=False),
    Column('DagsordenpunktId', Integer, nullable=False),
    Column('DagsordenRaekkefoelge', Integer, nullable=False, server_default=text('((1))')),
    Column('BehandlingRaekkefoelge', Integer, nullable=False, server_default=text('((1))')),
    Column('DagsordenpunktStatus', Integer, nullable=False),
    Column('Laast', Boolean, nullable=False, server_default=text('((0))')),
    Column('TilbagejournaliseretDokumentID', Integer),
    Column('Aabent', Boolean, nullable=False, server_default=text('((0))')),
    Column('AnsvarligID', Integer, nullable=False, server_default=text('((0))')),
    Column('Note', Unicode(2000, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('HarBeslutning', Boolean, nullable=False, server_default=text('((0))')),
    Column('Overskrift', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False, server_default=text("('')")),
    Column('OffentligOverskriftVedIkkeOffentlig', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('YderligereSagsNumre', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS')),
    Column('IndstillingOverskrift', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS')),
    Column('Gruppering', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('LastChanged', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('LastChangedBy', Integer, nullable=False, server_default=text('((0))')),
    Column('DagsordenpunktsBehandlingIdentity', Uuid, nullable=False, server_default=text('(newid())')),
    Column('IsStjernehoering', Boolean, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['AnsvarligID'], ['Bruger.ID'], name='FK_DagsordenpunktsBehandling_Bruger_AnsvarligID'),
    ForeignKeyConstraint(['DagsordenId'], ['Dagsorden.ID'], name='FK_DagsordenpunktsBehandling_Dagsorden'),
    ForeignKeyConstraint(['DagsordenpunktId'], ['Dagsordenpunkt.ID'], name='FK_DagsordenpunktsBehandling_Dagsordenpunkt'),
    ForeignKeyConstraint(['LastChangedBy'], ['Bruger.ID'], name='FK_DagsordenpunktsBehandling_Bruger_LastChangedBy'),
    ForeignKeyConstraint(['TilbagejournaliseretDokumentID'], ['Dokument.ID'], name='FK_DagsordenpunktsBehandling_Dokument'),
    PrimaryKeyConstraint('Id', name='PK_DagsordenpunktsBehandling'),
    Index('AK_DagsordenpunktsBehandling_DagsordenId_DagsprdenpunktId', 'DagsordenId', 'DagsordenpunktId', mssql_clustered=False, unique=True),
    Index('IX_DagsordenpunktsBehandling_DagsordenId', 'DagsordenId', mssql_clustered=False),
    Index('IX_DagsordenpunktsBehandling_DagsordenpunktId', 'DagsordenpunktId', mssql_clustered=False),
    Index('UQ__Dagsorde__8E5E014F70C99E18', 'DagsordenpunktsBehandlingIdentity', mssql_clustered=False, unique=True)
)

t_FlowModtagerSvar = Table(
    'FlowModtagerSvar', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('FlowModtagerID', Integer, nullable=False),
    Column('BrugerID', Integer, nullable=False),
    Column('SvarDato', DateTime, nullable=False),
    Column('Kommentar', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS')),
    Column('Svar', Integer, nullable=False),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='FK_FlowModtagerSvar_Bruger'),
    ForeignKeyConstraint(['FlowModtagerID'], ['FlowModtager.ID'], name='FK_FlowModtagerSvar_FlowModtager'),
    PrimaryKeyConstraint('ID', name='PK__FlowModt__3214EC2768CD9D7C')
)

t_FravaerDagsorden = Table(
    'FravaerDagsorden', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('FravaerId', Integer, nullable=False),
    Column('DagsordenId', Integer, nullable=False),
    ForeignKeyConstraint(['DagsordenId'], ['Dagsorden.ID'], name='FK_FravaerDagsorden_Dagsorden'),
    ForeignKeyConstraint(['FravaerId'], ['Fravaer.Id'], name='FK_FravaerDagsorden_Fravaer'),
    PrimaryKeyConstraint('Id', name='PK__FravaerD__3214EC07DF40A188'),
    Index('IX_FravaerDagsorden_FravaerId_DagsordenId', 'FravaerId', 'DagsordenId', mssql_clustered=False, unique=True)
)

t_GeneratorIndstillinger = Table(
    'GeneratorIndstillinger', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('InkluderLukkedePunkterIFuldVersion', Boolean, nullable=False),
    Column('TilladKunBilagSomPDF', Boolean, nullable=False),
    Column('TilladBilagSomIkkeOffentligtDokument', Boolean, nullable=False),
    Column('TilladBilagSomScanningUdenPDF', Boolean, nullable=False),
    Column('OpdelIAabneOgLukkedePunkter', Boolean, nullable=False),
    Column('AnvendGruppering', Boolean, nullable=False),
    Column('Tilbagejournalisering', Boolean, nullable=False, server_default=text('((0))')),
    Column('Bilagsliste', Boolean, nullable=False),
    Column('Indkaldelse', Boolean, nullable=False),
    Column('Underskriftsark', Boolean, nullable=False),
    Column('Forside', Boolean, nullable=False),
    Column('Indholdsfortegnelse', Boolean, nullable=False),
    Column('Created', DateTime),
    Column('CreatedBy', Integer),
    Column('LastChanged', DateTime),
    Column('LastChangedBy', Integer),
    Column('DagsordenID', Integer),
    Column('BrugerID', Integer),
    Column('UdvalgID', Integer),
    Column('SidstGenereredeDagsordenSti', Unicode(512, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('DagsordenType', Unicode(100, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('VisBeslutningsvejUnderBeslutning', Boolean, nullable=False, server_default=text('((0))')),
    Column('Bilagstegn', Unicode(10, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('BilagslistePlacering', Integer, nullable=False, server_default=text('((0))')),
    Column('OmgivIndstillingslinjerMedTabel', Boolean, nullable=False, server_default=text('((1))')),
    Column('MedtagTommeFelter', Boolean, nullable=False, server_default=text('((0))')),
    Column('MedtagTomtBeslutningsfelt', Boolean, nullable=False, server_default=text('((0))')),
    ForeignKeyConstraint(['BrugerID'], ['Bruger.ID'], name='FK_GeneratorIndstillinger_Bruger_Bruger'),
    ForeignKeyConstraint(['CreatedBy'], ['Bruger.ID'], name='FK_GeneratorIndstillinger_Bruger_CreatedBy'),
    ForeignKeyConstraint(['DagsordenID'], ['Dagsorden.ID'], name='FK_GeneratorIndstillinger_Dagsorden_Dagsorden'),
    ForeignKeyConstraint(['LastChangedBy'], ['Bruger.ID'], name='FK_GeneratorIndstillinger_Bruger_LastChangedBy'),
    ForeignKeyConstraint(['UdvalgID'], ['Udvalg.ID'], name='FK_GeneratorIndstillinger_Udvalg'),
    PrimaryKeyConstraint('ID', name='PK__GeneratorIndstil__7F3866D5')
)

t_WordGeneratorDagsordenExtension = Table(
    'WordGeneratorDagsordenExtension', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DagsordenID', Integer, nullable=False),
    Column('Forsidetekst', NTEXT(8, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('TvungenSideskiftEfterPunkt', Boolean, nullable=False, server_default=text('((1))')),
    ForeignKeyConstraint(['DagsordenID'], ['Dagsorden.ID'], name='FK_WordGeneratorDagsordenExtension_Dagsorden'),
    PrimaryKeyConstraint('ID', name='PK_WordGeneratorDagsordenExtension'),
    Index('IX_WordGeneratorDagsordenExtension', 'DagsordenID', mssql_clustered=False, unique=True)
)

t_DagsordenPunktBehandlingBilag = Table(
    'DagsordenPunktBehandlingBilag', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('BilagID', Integer, nullable=False),
    Column('BehandlingID', Integer, nullable=False),
    ForeignKeyConstraint(['BehandlingID'], ['DagsordenpunktsBehandling.Id'], name='FK_DagsordenPunktBehandlingBilag_DagsordenpunktsBehandling'),
    ForeignKeyConstraint(['BilagID'], ['Bilag.ID'], name='FK_DagsordenPunktBehandlingBilag_Bilag'),
    PrimaryKeyConstraint('ID', name='PK_DagsordenBehandlingBilag'),
    Index('AK_DagsordenBehandlingBilag_BilagId_BehandlingId', 'BilagID', 'BehandlingID', mssql_clustered=False, unique=True),
    Index('IX_DagsordenpunktBehandlingBilag_BehandlingID', 'BehandlingID', mssql_clustered=False, mssql_include=['BilagID'])
)

t_DagsordenpunktBehandlingFeltIndhold = Table(
    'DagsordenpunktBehandlingFeltIndhold', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('DagsordenpunktFeltIndholdId', Integer, nullable=False),
    Column('DagsordenpunktsBehandlingId', Integer, nullable=False),
    ForeignKeyConstraint(['DagsordenpunktFeltIndholdId'], ['DagsordenpunktFeltIndhold.Id'], name='FK_DagsordenpunktBehandlingFeltIndhold_DagsordenpunktFeltIndhold'),
    ForeignKeyConstraint(['DagsordenpunktsBehandlingId'], ['DagsordenpunktsBehandling.Id'], name='FK_DagsordenpunktBehandlingFeltIndhold_DagsordenpunktsBehandling'),
    PrimaryKeyConstraint('Id', name='PK_DagsordenpunkBehandlingFeltIndhold'),
    Index('AK_DagsordenpunkBehandlingFeltIndhold_FeltId_BehandlingId', 'DagsordenpunktFeltIndholdId', 'DagsordenpunktsBehandlingId', mssql_clustered=False, unique=True),
    Index('IX_DagsordenpunktbehanldingID', 'DagsordenpunktsBehandlingId', mssql_clustered=False, mssql_include=['DagsordenpunktFeltIndholdId'])
)

t_Erindring = Table(
    'Erindring', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('Navn', Unicode(200, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Beskrivelse', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('ErindringTypeID', Integer, nullable=False),
    Column('CreatedByID', Integer),
    Column('Created', DateTime),
    Column('LastChangedByID', Integer),
    Column('LastChanged', DateTime),
    Column('OpretterID', Integer, nullable=False),
    Column('AnsvarligID', Integer, nullable=False),
    Column('Uddelegeret', DateTime),
    Column('ErAfsluttet', Boolean, nullable=False, server_default=text('((0))')),
    Column('AfsluttetAfID', Integer),
    Column('Afsluttet', DateTime),
    Column('ErAnnulleret', Boolean, nullable=False, server_default=text('((0))')),
    Column('AnnulleretAfID', Integer),
    Column('Annulleret', DateTime),
    Column('SagID', Integer, nullable=False),
    Column('DelforloebID', Integer),
    Column('DokumentRegistreringID', Integer),
    Column('KladdeRegistreringID', Integer),
    Column('HarDeadline', Boolean),
    Column('Deadline', DateTime),
    Column('AfsluttetNotat', Unicode(500, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('PopupStatus', Integer, nullable=False, server_default=text('((0))')),
    Column('SagsPartID', Integer),
    Column('DagsordenpunktsBehandlingID', Integer),
    Column('KopierEfterUdfoerelse', Boolean, nullable=False, server_default=text('((0))')),
    Column('KopierTilID', Integer),
    Column('ReturEfterUdfoerelse', Boolean, nullable=False, server_default=text('((0))')),
    Column('JournalArkNoteID', Integer),
    Column('ProcessPostAction', Integer, nullable=False, server_default=text('((0))')),
    Column('SynligFra', DateTime),
    Column('SendSomMailRetryCount', Integer),
    ForeignKeyConstraint(['AfsluttetAfID'], ['Bruger.ID'], name='Erindring_AfsluttetAfBruger'),
    ForeignKeyConstraint(['AnnulleretAfID'], ['Bruger.ID'], name='FK_Erindring_AnnulleretAf'),
    ForeignKeyConstraint(['AnsvarligID'], ['Bruger.ID'], name='Erindring_Ansvarlig'),
    ForeignKeyConstraint(['CreatedByID'], ['Bruger.ID'], name='Erindring_OprettetAfBruger'),
    ForeignKeyConstraint(['DagsordenpunktsBehandlingID'], ['DagsordenpunktsBehandling.Id'], name='FK_Erindring_DagsordenpunktsBehandling'),
    ForeignKeyConstraint(['DelforloebID'], ['Delforloeb.ID'], name='Erindring_Delforloeb'),
    ForeignKeyConstraint(['DokumentRegistreringID'], ['DokumentRegistrering.ID'], name='Erindring_DokumentRegistrering'),
    ForeignKeyConstraint(['ErindringTypeID'], ['ErindringTypeOpslag.ID'], name='Erindring_ErindringType'),
    ForeignKeyConstraint(['JournalArkNoteID'], ['JournalArkNote.ID'], name='FK_Erindring_JournalArkNote'),
    ForeignKeyConstraint(['KladdeRegistreringID'], ['KladdeRegistrering.ID'], name='Erindring_KladdeRegistrering'),
    ForeignKeyConstraint(['KopierTilID'], ['Bruger.ID'], name='FK_Erindring_Bruger'),
    ForeignKeyConstraint(['LastChangedByID'], ['Bruger.ID'], name='Erindring_SidstRettetAfBruger'),
    ForeignKeyConstraint(['OpretterID'], ['Bruger.ID'], name='FK_Erindring_Bruger_OprettetAf'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='Erindring_Sag'),
    ForeignKeyConstraint(['SagsPartID'], ['SagsPart.ID'], name='Erindring_SagsPart'),
    PrimaryKeyConstraint('ID', name='PK_Erindring'),
    Index('IX_Erindring_AnsvarligID_ProcessPostAction', 'AnsvarligID', 'ProcessPostAction', mssql_clustered=False, mssql_include=['ID', 'Navn', 'Beskrivelse', 'ErindringTypeID', 'CreatedByID', 'Created', 'LastChangedByID', 'LastChanged', 'OpretterID', 'Uddelegeret', 'ErAfsluttet', 'AfsluttetAfID', 'Afsluttet', 'ErAnnulleret', 'AnnulleretAfID', 'Annulleret', 'SagID', 'DelforloebID', 'DokumentRegistreringID', 'KladdeRegistreringID', 'HarDeadline', 'Deadline', 'AfsluttetNotat', 'PopupStatus', 'SagsPartID', 'DagsordenpunktsBehandlingID', 'KopierEfterUdfoerelse', 'KopierTilID', 'ReturEfterUdfoerelse', 'JournalArkNoteID', 'SynligFra', 'SendSomMailRetryCount']),
    Index('IX_Erindring_Cover', 'KladdeRegistreringID', 'DokumentRegistreringID', 'DagsordenpunktsBehandlingID', 'ErindringTypeID', 'SagsPartID', 'AnsvarligID', 'CreatedByID', 'SagID', mssql_clustered=False, mssql_include=['ID', 'SynligFra', 'JournalArkNoteID', 'ErAfsluttet', 'ErAnnulleret', 'OpretterID', 'LastChanged', 'Created', 'Uddelegeret', 'AfsluttetAfID', 'AnnulleretAfID', 'DelforloebID', 'HarDeadline', 'Deadline', 'PopupStatus', 'KopierEfterUdfoerelse', 'KopierTilID', 'ReturEfterUdfoerelse']),
    Index('IX_Erindring_DelforloebID_ErAfsluttet', 'DelforloebID', 'ErAfsluttet', mssql_clustered=False),
    Index('IX_Erindring_Popup', 'PopupStatus', 'AnsvarligID', mssql_clustered=False),
    Index('IX_Erindring_Sag', 'SagID', mssql_clustered=True)
)

t_FravaerDagsordenpunktsBehandling = Table(
    'FravaerDagsordenpunktsBehandling', metadata,
    Column('Id', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('FravaerId', Integer, nullable=False),
    Column('DagsordenpunktsBehandlingId', Integer, nullable=False),
    ForeignKeyConstraint(['DagsordenpunktsBehandlingId'], ['DagsordenpunktsBehandling.Id'], name='FK_FravaerDagsordenpunktsBehandling_DagsordenPunktsBehandling'),
    ForeignKeyConstraint(['FravaerId'], ['Fravaer.Id'], name='FK_FravaerDagsordenpunktsBehandling_Fravaer'),
    PrimaryKeyConstraint('Id', name='PK__FravaerD__3214EC0797D8D7DA'),
    Index('IX_FravaerDagsordenpunktsBehandling_FravaerId_DagsordenpunktsBehandlingId', 'FravaerId', 'DagsordenpunktsBehandlingId', mssql_clustered=False)
)

t_GeneratorIndstillingerFeltRegistrering = Table(
    'GeneratorIndstillingerFeltRegistrering', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('GeneratorIndstillingerID', Integer, nullable=False),
    Column('DagsordenpunktFeltID', Integer, nullable=False),
    ForeignKeyConstraint(['DagsordenpunktFeltID'], ['DagsordenpunktFelt.ID'], name='FK_GeneratorIndstillingerFeltRegistrering_DagsordenpunktFelt'),
    ForeignKeyConstraint(['GeneratorIndstillingerID'], ['GeneratorIndstillinger.ID'], name='FK_GeneratorIndstillingerFeltRegistrering_GeneratorIndstillinger'),
    PrimaryKeyConstraint('ID', name='PK_GeneratorIndstillingerFeltRegistrering'),
    Index('IX_GeneratorIndstillingerFeltRegistrering', 'DagsordenpunktFeltID', mssql_clustered=False, mssql_include=['GeneratorIndstillingerID'])
)

t_ErindringDataRegistrering = Table(
    'ErindringDataRegistrering', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('ErindringID', Integer, nullable=False),
    Column('DataRegistreringType', Integer, nullable=False),
    Column('RegistreringID', Integer, nullable=False),
    ForeignKeyConstraint(['ErindringID'], ['Erindring.ID'], name='FK_ErindringDataRegistrering_ErindringID'),
    PrimaryKeyConstraint('ID', name='PK_ErindringDataRegistrering'),
    Index('IX_ErindringDataRegistrering_Erindring', 'ErindringID', mssql_clustered=False, mssql_include=['DataRegistreringType', 'RegistreringID'])
)

t_ErindringHandling = Table(
    'ErindringHandling', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('ErindringID', Integer, nullable=False),
    Column('HandlingID', Integer, nullable=False),
    ForeignKeyConstraint(['ErindringID'], ['Erindring.ID'], name='FK_ErindringHandling_Erindring'),
    ForeignKeyConstraint(['HandlingID'], ['Handling.ID'], name='FK_ErindringHandling_Handling'),
    PrimaryKeyConstraint('ID', name='pk_ErindringHandling')
)

t_ErindringTrin = Table(
    'ErindringTrin', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('SagID', Integer, nullable=False),
    Column('ErindringID', Integer, nullable=False),
    Column('TrinID', Integer, nullable=False),
    ForeignKeyConstraint(['ErindringID'], ['Erindring.ID'], name='FK_ErindringTrin_Erindring'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='FK_ErindringTrin_Sag'),
    PrimaryKeyConstraint('ID', name='PK_ErindringTrin')
)

t_Forloeb = Table(
    'Forloeb', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('ForloebTypeID', Integer, nullable=False),
    Column('Beskrivelse', Unicode(255, 'SQL_Danish_Pref_CP1_CI_AS'), nullable=False),
    Column('Note', TEXT(16, 'SQL_Danish_Pref_CP1_CI_AS')),
    Column('RegistreretAfID', Integer, nullable=False),
    Column('SagID', Integer, nullable=False),
    Column('DelforloebID', Integer),
    Column('Tidspunkt', DateTime, nullable=False, server_default=text('(getdate())')),
    Column('TargetType', Integer, nullable=False),
    Column('TargetID', Integer, nullable=False),
    Column('ErindringID', Integer),
    Column('ForloebData', Unicode(collation='SQL_Danish_Pref_CP1_CI_AS')),
    ForeignKeyConstraint(['DelforloebID'], ['Delforloeb.ID'], name='Forloeb_Delforloeb'),
    ForeignKeyConstraint(['ErindringID'], ['Erindring.ID'], name='FK_Forloeb_Erindring'),
    ForeignKeyConstraint(['ForloebTypeID'], ['ForloebTypeOpslag.ID'], name='Forloeb_ForloebType'),
    ForeignKeyConstraint(['RegistreretAfID'], ['Bruger.ID'], name='Forloeb_Bruger'),
    ForeignKeyConstraint(['SagID'], ['Sag.ID'], name='Forloeb_Sag'),
    PrimaryKeyConstraint('ID', name='PK_Forloeb'),
    Index('IX_Forloeb_Delforloeb', 'DelforloebID', mssql_clustered=False),
    Index('IX_Forloeb_Erindring', 'ID', 'ErindringID', mssql_clustered=False),
    Index('IX_Forloeb_Erindring_sag', 'ErindringID', mssql_clustered=False, mssql_include=['SagID']),
    Index('IX_Forloeb_RegistreretAf', 'RegistreretAfID', mssql_clustered=False),
    Index('IX_Forloeb_Sag', 'SagID', mssql_clustered=True),
    Index('IX_Forloeb_Target', 'TargetType', 'TargetID', mssql_clustered=False)
)

t_Beskedfordeling = Table(
    'Beskedfordeling', metadata,
    Column('ID', Integer, Identity(start=1, increment=1), primary_key=True),
    Column('ForloebId', Integer, server_default=text('(NULL)')),
    Column('UsageLogId', Integer, server_default=text('(NULL)')),
    Column('AfsendtTilBeskedfordeler', DateTime),
    Column('Error', String(100, 'SQL_Danish_Pref_CP1_CI_AS'), server_default=text('(NULL)')),
    Column('ForsoegtGensendt', Integer, server_default=text('((0))')),
    Column('DokumentKonverteringBestillingId', Integer, server_default=text('(NULL)')),
    Column('HandledBy', Integer, server_default=text('(NULL)')),
    Column('SendBOMBesvarelseBestillingId', Integer, server_default=text('(NULL)')),
    ForeignKeyConstraint(['DokumentKonverteringBestillingId'], ['DokumentKonverteringBestilling.ID'], ondelete='CASCADE', name='FK_Beskedfordeling_DokumentKonverteringBestilling'),
    ForeignKeyConstraint(['ForloebId'], ['Forloeb.ID'], ondelete='CASCADE', name='FK_Beskedfordeling_ForloebId'),
    ForeignKeyConstraint(['SendBOMBesvarelseBestillingId'], ['SendBOMBesvarelseBestilling.Id'], ondelete='CASCADE', name='FK_Beskedfordeling_SendBOMBesvarelseBestilling'),
    ForeignKeyConstraint(['UsageLogId'], ['UsageLog.ID'], ondelete='CASCADE', name='FK_Beskedfordeling_UsageLog'),
    PrimaryKeyConstraint('ID', name='PK_Beskedfordeling'),
    Index('IX_BeskedFordeling_ForloebId', 'HandledBy', 'ForloebId', mssql_clustered=False),
    Index('IX_Beskedfordeling_DokumentKonverteringBestillingId', 'HandledBy', 'DokumentKonverteringBestillingId', mssql_clustered=False),
    Index('IX_Beskedfordeling_UsageLogId', 'HandledBy', 'UsageLogId', mssql_clustered=False)
)
