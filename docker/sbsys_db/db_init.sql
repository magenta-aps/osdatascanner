CREATE DATABASE [SbSysNetDrift]
GO

USE [SbSysNetDrift]
GO
/****** Object:  Table [dbo].[AdministrativProfil]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AdministrativProfil](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Kontekst] [int] NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
 CONSTRAINT [PK_AdministrativProfil] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AdministrativProfilAnsaettelsessteder]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AdministrativProfilAnsaettelsessteder](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[AdministrativProfilID] [int] NOT NULL,
	[AnsaettelsesstedID] [int] NOT NULL,
 CONSTRAINT [PK_AdministrativProfilAnsaettelsessteder] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AdministrativProfilBruger]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AdministrativProfilBruger](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[AdministrativProfilID] [int] NOT NULL,
	[BrugerID] [int] NOT NULL,
 CONSTRAINT [PK_AdministrativProfilBruger] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AdministrativProfilRettigheder]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AdministrativProfilRettigheder](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[AdministrativProfilID] [int] NOT NULL,
	[SikkerhedsbeslutningID] [int] NOT NULL,
 CONSTRAINT [PK_adminprol_rettigheder] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Adresse]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Adresse](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Adresse1] [nvarchar](75) NULL,
	[Adresse2] [nvarchar](75) NULL,
	[Adresse3] [nvarchar](75) NULL,
	[Adresse4] [nvarchar](75) NULL,
	[Adresse5] [nvarchar](75) NULL,
	[PostNummer] [int] NULL,
	[Bynavn] [nvarchar](80) NULL,
	[HusNummer] [nvarchar](20) NULL,
	[Etage] [nvarchar](10) NULL,
	[DoerBetegnelse] [nvarchar](20) NULL,
	[BygningsNummer] [nvarchar](20) NULL,
	[Postboks] [nvarchar](10) NULL,
	[PostDistrikt] [nvarchar](80) NULL,
	[LandeKode] [nvarchar](3) NULL,
	[ErUdlandsadresse] [bit] NULL,
	[ErBeskyttet] [bit] NOT NULL,
	[AdresseIdentity] [uniqueidentifier] NULL,
	[AdgangsAdresseIdentity] [uniqueidentifier] NULL,
 CONSTRAINT [PK_tblAdresser] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 90) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AdresseGenstand]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AdresseGenstand](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Uuid] [uniqueidentifier] NOT NULL,
	[Status] [int] NOT NULL,
	[FoerstOprettet] [datetime] NOT NULL,
	[SidstAendret] [datetime] NOT NULL,
	[Vejkode] [nvarchar](4) NOT NULL,
	[Vejnavn] [nvarchar](500) NOT NULL,
	[AdresseringsVejnavn] [nvarchar](20) NULL,
	[HusNummer] [nvarchar](4) NULL,
	[Etage] [nvarchar](2) NULL,
	[Doer] [nvarchar](10) NULL,
	[SupplerendeBynavn] [nvarchar](34) NULL,
	[PostNummer] [nvarchar](5) NULL,
	[PostNummerNavn] [nvarchar](20) NULL,
	[StormodtagerPostNummer] [nvarchar](5) NULL,
	[StormodtagerPostNummerNavn] [nvarchar](20) NULL,
	[KommuneKode] [int] NOT NULL,
	[KommuneNavn] [nvarchar](100) NULL,
	[EsrEjendomsNummer] [int] NULL,
	[Etrs89KoordinatEast] [nvarchar](20) NULL,
	[Etrs89KoordinatNorth] [nvarchar](20) NULL,
	[Wgs84KoordinatLatitude] [nvarchar](20) NULL,
	[Wgs84KoordinatLongtitude] [nvarchar](20) NULL,
	[Noejagtighed] [nvarchar](1) NOT NULL,
	[Kilde] [int] NULL,
	[TeknikStandard] [nvarchar](2) NULL,
	[Tekstretning] [nvarchar](6) NULL,
	[DdknM100] [nvarchar](15) NULL,
	[DdknKm1] [nvarchar](12) NULL,
	[DdknKm10] [nvarchar](11) NULL,
	[AdressepunktAendringsDato] [datetime] NULL,
	[AdgangsadresseUuid] [uniqueidentifier] NOT NULL,
	[AdgangsadresseStatus] [int] NOT NULL,
	[AdgangsadresseOprettet] [datetime] NULL,
	[AdgangsadresseAendret] [datetime] NULL,
	[AdgangsadresseKvh] [nvarchar](12) NOT NULL,
	[RegionsKode] [nvarchar](4) NULL,
	[RegionsNavn] [nvarchar](100) NULL,
	[Kvhx] [nvarchar](19) NOT NULL,
	[SogneKode] [nvarchar](4) NULL,
	[SogneNavn] [nvarchar](100) NULL,
	[PolitikredsKode] [nvarchar](100) NULL,
	[PolitikredsNavn] [nvarchar](100) NULL,
	[RetskredsKode] [nvarchar](4) NULL,
	[RetskredsNavn] [nvarchar](100) NULL,
	[OpstillingskredsKode] [nvarchar](100) NULL,
	[OpstillingskredsNavn] [nvarchar](100) NULL,
	[Zone] [nvarchar](100) NOT NULL,
	[JordstykkeEjerlavkode] [nvarchar](7) NULL,
	[JordstykkeEjerlavNavn] [nvarchar](100) NULL,
	[JordstykkeMatrikelNummer] [nvarchar](7) NULL,
	[JordstykkeEsrEjendomsNummer] [int] NULL,
	[EjendomID] [int] NULL,
	[KommuneID] [int] NOT NULL,
	[Beskrivelse] [nvarchar](500) NULL,
	[Oprettet] [datetime] NOT NULL,
	[Beliggenhed] [nvarchar](500) NULL,
	[Historisk] [bit] NOT NULL,
	[AdresseIdentity] [uniqueidentifier] NOT NULL,
	[ExternalSourceLastUpdate] [datetime] NULL,
	[ExternalSourceID] [nvarchar](50) NULL,
	[ExternalSourceName] [nvarchar](50) NULL,
PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[AdresseIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AdresseItem]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AdresseItem](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[AdresseID] [int] NOT NULL,
	[AdresseItemType] [tinyint] NOT NULL,
	[AdresseItemContext] [tinyint] NOT NULL,
	[Navn] [nvarchar](100) NULL,
 CONSTRAINT [PK_AdresseItem] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_AdresseItem]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_AdresseItem] ON [dbo].[AdresseItem]
(
	[AdresseID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AktindsigtSaves]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AktindsigtSaves](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Oprettet] [datetime] NOT NULL,
	[BrugerId] [int] NOT NULL,
	[SavedProgress] [nvarchar](max) NULL,
 CONSTRAINT [PK_AktindsigtSaves] PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AmtOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AmtOpslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[Nummer] [nvarchar](50) NOT NULL,
 CONSTRAINT [PK_Amt] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Ansaettelsessted]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Ansaettelsessted](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[CustomAdID] [nvarchar](50) NULL,
	[Beskrivelse] [nvarchar](300) NULL,
	[PostAdresseID] [int] NOT NULL,
	[FysiskAdresseID] [int] NOT NULL,
	[Aabningstider] [nvarchar](200) NULL,
	[EanNummer] [nvarchar](15) NULL,
	[Leder] [nvarchar](100) NULL,
	[CvrNummer] [nvarchar](12) NULL,
	[PNummer] [nvarchar](12) NULL,
	[Fritekst1] [nvarchar](200) NULL,
	[Fritekst2] [nvarchar](200) NULL,
	[FagomraadeID] [int] NULL,
	[Indjournaliseringsfolder] [nvarchar](300) NULL,
	[DefaultEmneplanID] [int] NULL,
	[HierakiMedlemID] [int] NOT NULL,
	[Webside] [nvarchar](300) NULL,
	[DefaultSagSecuritySetID] [int] NULL,
	[VisAdgangsListeVedOpretSag] [bit] NULL,
	[TilladBrugerAtSkiftePassword] [bit] NOT NULL,
	[TilladPublicering] [bit] NOT NULL,
	[EksterneAdviseringer] [int] NOT NULL,
	[AutomatiskErindringVedJournalisering] [bit] NOT NULL,
	[StandardAktindsigtVedJournalisering] [bit] NOT NULL,
	[VisCPR] [bit] NOT NULL,
	[AnsaettelsesstedIdentity] [uniqueidentifier] NOT NULL,
	[VisCVR] [bit] NOT NULL,
 CONSTRAINT [PK_Ansaettelsessted] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[AnsaettelsesstedIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AnsaettelsesstedEksternMapning]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AnsaettelsesstedEksternMapning](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[EksternID] [nvarchar](50) NULL,
	[AnsaettelsesstedID] [int] NOT NULL,
	[DefaultSikkerhedsGruppeID] [int] NULL,
	[PassivSikkerhedsGruppeID] [int] NULL,
	[PassivAnsaettelsesstedID] [int] NULL,
	[EksternSystemID] [nvarchar](50) NULL,
 CONSTRAINT [PK_AnsaettelsesstedEksternMapning] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AnsaettelsesstedStandardSikkerhedsGrupper]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AnsaettelsesstedStandardSikkerhedsGrupper](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[AnsaettelsesstedID] [int] NOT NULL,
	[SikkerhedsgruppeID] [int] NOT NULL,
 CONSTRAINT [PK_AnsaettelsesstedStandardSikkerhedsGrupper] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AnsaettelsesstedTrustedAssembly]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AnsaettelsesstedTrustedAssembly](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[AnsaettelsesstedID] [int] NOT NULL,
	[TrustedAssemblyID] [int] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ArkivAfklaringStatus]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ArkivAfklaringStatus](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](200) NULL,
 CONSTRAINT [PK_Table1] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ArkivPeriode]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ArkivPeriode](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[CreatedByID] [int] NOT NULL,
	[Created] [datetime] NULL,
	[LastChangedByID] [int] NULL,
	[LastChanged] [datetime] NULL,
	[PeriodeStart] [datetime] NOT NULL,
	[PeriodeSlut] [datetime] NOT NULL,
	[OverlapningsperiodeSlut] [datetime] NOT NULL,
	[ArkivPeriodeStatusID] [int] NOT NULL,
	[ArkivPeriodeIdentity] [uniqueidentifier] NOT NULL,
 CONSTRAINT [PK_ArkivPeriode] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_ArkivPeriode_PeriodeStart] UNIQUE NONCLUSTERED
(
	[PeriodeStart] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[ArkivPeriodeIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ArkivPeriodeStatus]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ArkivPeriodeStatus](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](200) NOT NULL,
 CONSTRAINT [PK_ArkivPeriodeStatus] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[backup_SecuritySet]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[backup_SecuritySet](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [varchar](1) NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[backup_SecuritySetBrugere]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[backup_SecuritySetBrugere](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SecuritySetID] [int] NOT NULL,
	[BrugerID] [int] NOT NULL,
	[ErPermanent] [bit] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[backup_SecuritySetSikkerhedsgrupper]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[backup_SecuritySetSikkerhedsgrupper](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SecuritySetID] [int] NOT NULL,
	[SikkerhedsgruppeID] [int] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Beskedfordeling]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Beskedfordeling](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[ForloebId] [int] NULL,
	[UsageLogId] [int] NULL,
	[AfsendtTilBeskedfordeler] [datetime] NULL,
	[Error] [varchar](100) NULL,
	[ForsoegtGensendt] [int] NULL,
	[DokumentKonverteringBestillingId] [int] NULL,
	[HandledBy] [int] NULL,
	[SendBOMBesvarelseBestillingId] [int] NULL,
 CONSTRAINT [PK_Beskedfordeling] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BeskedfordelingHandledByOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BeskedfordelingHandledByOpslag](
	[Id] [int] NOT NULL,
	[Navn] [nvarchar](255) NOT NULL,
PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BeslutningsType]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BeslutningsType](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[BeslutningsTypeGruppeID] [int] NOT NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
 CONSTRAINT [PK_AfgoeringType] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BeslutningsTypeGruppe]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BeslutningsTypeGruppe](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
 CONSTRAINT [PK_AfgoeringTypeGruppe] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Beslutningsvej]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Beslutningsvej](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DagsordenpunktID] [int] NOT NULL,
	[MoedeID] [int] NOT NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
 CONSTRAINT [PK_Beslutningsvej] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BevaringOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BevaringOpslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[Beskrivelse] [nvarchar](200) NULL,
	[Kode] [nvarchar](50) NOT NULL,
	[Dage] [int] NULL,
	[KassationsBeregning] [int] NOT NULL,
 CONSTRAINT [PK_Kassation] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_Bevaring_Kode] UNIQUE NONCLUSTERED
(
	[Kode] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Bilag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Bilag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Sortering] [int] NOT NULL,
	[DokumentRegistreringID] [int] NULL,
	[KladdeRegistreringID] [int] NULL,
	[MaaPubliceres] [bit] NOT NULL,
	[ReferenceNummer] [int] NOT NULL,
	[LinkTekst] [nvarchar](300) NOT NULL,
	[FilnavnUdenExtension] [nvarchar](200) NOT NULL,
	[Aktiv] [bit] NOT NULL,
	[BilagIdentity] [uniqueidentifier] NOT NULL,
 CONSTRAINT [PK__Bilag__708A54CB] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[BilagIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Branche]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Branche](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Nummer] [int] NOT NULL,
	[Navn] [nvarchar](300) NOT NULL,
 CONSTRAINT [PK_Branche] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_Branche_Nummer] UNIQUE NONCLUSTERED
(
	[Nummer] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Bruger]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Bruger](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[LogonID] [nvarchar](50) NOT NULL,
	[LogonPassword] [nvarchar](88) NULL,
	[LogonSalt] [nvarchar](88) NULL,
	[LogonAlgorithm] [nvarchar](6) NOT NULL,
	[LogonIterations] [int] NULL,
	[LogonFailedAttemptCount] [int] NOT NULL,
	[LogonTemporaryLockedExpiration] [datetime] NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[Titel] [nvarchar](50) NULL,
	[Stilling] [nvarchar](50) NULL,
	[KontorID] [int] NULL,
	[FagomraadeID] [int] NOT NULL,
	[Lokale] [nvarchar](50) NULL,
	[AdresseID] [int] NULL,
	[AnsaettelsesstedID] [int] NOT NULL,
	[Status] [int] NOT NULL,
	[EksternID] [nvarchar](50) NULL,
	[ObjectSid] [nvarchar](50) NULL,
	[UserPrincipalName] [nvarchar](254) NULL,
	[BrugerIdentity] [uniqueidentifier] NOT NULL,
	[ErSystembruger] [bit] NOT NULL,
 CONSTRAINT [PK_Bruger] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[BrugerIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BrugerGruppe]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BrugerGruppe](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](75) NULL,
 CONSTRAINT [PK_tblBrugerGruppe] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BrugerGruppeBruger]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BrugerGruppeBruger](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerGruppeID] [int] NOT NULL,
	[BrugerID] [int] NOT NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
 CONSTRAINT [PK_tblBrugerGruppe_Brugere_Link] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BrugerGruppeEjer]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BrugerGruppeEjer](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerGruppeID] [int] NOT NULL,
	[BrugerSettingsID] [int] NOT NULL,
 CONSTRAINT [IX_BrugerGruppeEjer] UNIQUE NONCLUSTERED
(
	[BrugerGruppeID] ASC,
	[BrugerSettingsID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BrugerLogonLog]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BrugerLogonLog](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NULL,
	[SbsysLogonID] [nvarchar](100) NOT NULL,
	[SbsysLogonPassword] [nvarchar](200) NULL,
	[Occured] [datetime] NOT NULL,
	[Action] [tinyint] NOT NULL,
	[Message] [nvarchar](400) NOT NULL,
	[WindowsLogonName] [nvarchar](100) NOT NULL,
	[WindowsDomainName] [nvarchar](100) NOT NULL,
	[MachineName] [nvarchar](100) NOT NULL,
	[MachineAddress] [nvarchar](100) NOT NULL,
	[Session] [uniqueidentifier] NOT NULL,
 CONSTRAINT [PK_BrugerLogonLog] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BrugerSettings]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BrugerSettings](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[MaxOpenSager] [int] NULL,
	[MaxSenesteSager] [int] NOT NULL,
	[CheckOutFolderRoot] [nvarchar](300) NULL,
	[TemporaryFolderRoot] [nvarchar](300) NULL,
	[VisDelforloeb] [bit] NULL,
	[VisErindringer] [bit] NULL,
	[VisDokumenter] [bit] NULL,
	[VisForloeb] [bit] NULL,
	[VisKladder] [bit] NULL,
	[VisSager] [bit] NULL,
	[AabenDokumentPaaFaneblad] [bit] NULL,
	[VisKladdeCheckinVedAfslut] [bit] NULL,
	[VisListeKriterieSektion] [bit] NULL,
	[UdfyldDelforloebFaneblad] [bit] NOT NULL,
	[UdfyldErindringerFaneblad] [bit] NOT NULL,
	[UdfyldDokumenterFaneblad] [bit] NOT NULL,
	[UdfyldForloebFaneblad] [bit] NOT NULL,
	[UdfyldKladderFaneblad] [bit] NOT NULL,
	[MaxMailItemsReturned] [int] NULL,
	[VisPanel] [bit] NOT NULL,
	[UserFolderName] [nvarchar](50) NULL,
	[VisPluginWarnings] [bit] NULL,
	[VisSagsTitelPaaFaneblad] [bit] NULL,
	[VisBeskedEfterSagGem] [bit] NOT NULL,
	[ErindringPopupStaySec] [int] NULL,
	[MaxSagItemsReturned] [int] NULL,
	[VisListeFiltrering] [bit] NULL,
	[VisListeGruppering] [bit] NULL,
	[VisPdfVersionHvisForefindes] [bit] NULL,
	[LaeseLayoutPaaSag] [bit] NULL,
	[VisDokumentReadonlyAdvarsel] [bit] NULL,
	[VisScannedeDokumenter] [bit] NULL,
	[StartOn] [int] NULL,
	[DefaultClientTab] [nvarchar](30) NULL,
	[LastClientTab] [nvarchar](30) NULL,
	[GenaabenSager] [bit] NULL,
	[VisDagsordensystem] [bit] NULL,
	[VisPartSoegning] [bit] NULL,
	[DefaultSagSecuritySetID] [int] NULL,
	[DefaultKommuneVedSagsoprettelseID] [int] NULL,
	[VisPreviewPaaDokumentOgKladdeLister] [bit] NOT NULL,
	[VisDokumentTabBlock] [bit] NOT NULL,
	[DokumentLaesningsLayout] [bit] NOT NULL,
	[ErStandardForNyeBrugere] [bit] NOT NULL,
	[SplitterDistancePercentage] [int] NOT NULL,
	[AutoArkiverKladder] [bit] NOT NULL,
	[AutoFortrydUaendredeKladder] [bit] NOT NULL,
	[DefaultRegionVedSagsoprettelseID] [int] NULL,
	[DefaultAmtVedSagsoprettelseID] [int] NULL,
	[PubliseringFolderRoot] [nvarchar](300) NULL,
	[WorkFolderRoot] [nvarchar](300) NULL,
	[LastUsedTekstbehandlerName] [nvarchar](60) NULL,
	[MailSignatur] [nvarchar](max) NULL,
	[VisKladdeProcessInfo] [bit] NOT NULL,
	[VisGenstandSoegning] [bit] NULL,
	[DagsordenPubliseringIndstilling] [int] NOT NULL,
	[AnvendDokumentNavnTilAttachment] [bit] NOT NULL,
	[PostlisteIndstilling] [int] NOT NULL,
	[VisPostlister] [bit] NOT NULL,
	[VisSbsysIdag] [bit] NOT NULL,
	[DagsordenpunktSoegningType] [int] NOT NULL,
	[VisDagsordenpunktSoegning] [bit] NOT NULL,
	[VisJournalArkSogning] [bit] NOT NULL,
	[JournalarkVisningsFontID] [int] NULL,
	[VisJournalNoterSomOversigt] [bit] NULL,
	[VisJournalNoteTabBlock] [bit] NULL,
	[AnvendDokumenterSomJournalNote] [bit] NULL,
	[SenestePubliceringIndstillingerID] [int] NULL,
	[SendFejl] [bit] NOT NULL,
	[FlashQueueBell] [bit] NOT NULL,
	[AutomaticallyExecuteCommandsQueue] [bit] NOT NULL,
	[VerificerProgramLukning] [bit] NOT NULL,
	[MailSignaturVedSvarVideresend] [bit] NOT NULL,
	[VisInaktiveBrugere] [bit] NOT NULL,
	[SagStartView] [int] NOT NULL,
	[VisDokumentReadonlyAdvarselVedEksternAabning] [bit] NOT NULL,
	[AnvendSagspartSomStartvisningVedSoegSag] [bit] NOT NULL,
	[ModtagErindringSomMail] [bit] NOT NULL,
	[VisNewsPopUpSidstFravalgtDato] [datetime] NULL,
	[ShowAllCprCvr] [bit] NOT NULL,
	[ObfuscateAllCprCvr] [bit] NOT NULL,
	[ObfuscateLastCharactersInCpr] [bit] NOT NULL,
	[ObfuscateCvr] [bit] NOT NULL,
	[VisIkkeLukkedePunkter] [bit] NOT NULL,
	[AnvendSenesteKladdeVedOpretKladde] [bit] NOT NULL,
	[StandardErindringRetur] [bit] NOT NULL,
 CONSTRAINT [PK_BrugerSettings] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_BrugerSettings] UNIQUE NONCLUSTERED
(
	[BrugerID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_BrugerSettings_UserFolderName] UNIQUE NONCLUSTERED
(
	[UserFolderName] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BrugerSettingsAnsaettelsessted]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BrugerSettingsAnsaettelsessted](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerSettingsID] [int] NOT NULL,
	[AnsaettelsesstedID] [int] NOT NULL,
 CONSTRAINT [PK_BrugerSettingsAnsaettelsessteder] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_BrugerSettingsAnsaettelsessteder]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_BrugerSettingsAnsaettelsessteder] ON [dbo].[BrugerSettingsAnsaettelsessted]
(
	[BrugerSettingsID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BrugerSettingsAnvendteEmailAdresser]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BrugerSettingsAnvendteEmailAdresser](
	[BrugerSettingsID] [int] NOT NULL,
	[EmailAdresse] [nvarchar](300) NOT NULL,
	[ID] [int] IDENTITY(1,1) NOT NULL,
 CONSTRAINT [PK_BrugerSettingsAnvendteEmailAdresser] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BrugerSettingsDropFolderConfiguration]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BrugerSettingsDropFolderConfiguration](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerSettingsID] [int] NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[Beskrivelse] [nvarchar](300) NULL,
	[DropFolderSti] [nvarchar](500) NULL,
	[Enabled] [bit] NOT NULL,
	[Notificer] [int] NOT NULL,
	[InkluderUnderFoldere] [bit] NOT NULL,
	[ErJournaliseringskoe] [bit] NOT NULL,
 CONSTRAINT [PK_BrugerSettingsDropFolderConfiguration] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BrugerSettingsEmailKontoRegistrering]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BrugerSettingsEmailKontoRegistrering](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerSettingsID] [int] NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[Beskrivelse] [nvarchar](300) NULL,
	[AccountName] [nvarchar](100) NULL,
	[ServerName] [nvarchar](100) NULL,
	[DatabaseName] [nvarchar](100) NULL,
	[DomainName] [nvarchar](100) NULL,
	[Password] [nvarchar](100) NULL,
	[BrugernavnEqualsPostkasse] [bit] NULL,
	[EntryID] [nvarchar](600) NULL,
	[StoreID] [nvarchar](600) NULL,
	[UseSavedPassword] [bit] NULL,
	[MailSystemTag] [nvarchar](50) NOT NULL,
	[PasswordOnCreation] [nvarchar](100) NULL,
	[VistSessionNavn] [nvarchar](100) NULL,
	[EmailKontoExchangeConfigurationId] [int] NULL,
 CONSTRAINT [PK_MailSystemSessionInfo] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BrugerSettingsEmailKontoRegistrering_BACKUP_20220923]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BrugerSettingsEmailKontoRegistrering_BACKUP_20220923](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerSettingsID] [int] NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[Beskrivelse] [nvarchar](300) NULL,
	[AccountName] [nvarchar](100) NULL,
	[ServerName] [nvarchar](100) NULL,
	[DatabaseName] [nvarchar](100) NULL,
	[DomainName] [nvarchar](100) NULL,
	[Password] [nvarchar](100) NULL,
	[BrugernavnEqualsPostkasse] [bit] NULL,
	[EntryID] [nvarchar](600) NULL,
	[StoreID] [nvarchar](600) NULL,
	[UseSavedPassword] [bit] NULL,
	[MailSystemTag] [nvarchar](50) NOT NULL,
	[PasswordOnCreation] [nvarchar](100) NULL,
	[VistSessionNavn] [nvarchar](100) NULL,
	[EmailKontoExchangeConfigurationId] [int] NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BrugerSettingsFavoritSag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BrugerSettingsFavoritSag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerSettingsID] [int] NOT NULL,
	[SagID] [int] NULL,
	[Order] [int] NOT NULL,
 CONSTRAINT [PK_BrugerSettingsFavoriteJournal] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BrugerSettingsFavoritSagSkabelon]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BrugerSettingsFavoritSagSkabelon](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[BrugerSettingsID] [int] NOT NULL,
	[SagSkabelonID] [int] NULL,
 CONSTRAINT [PK_BrugerSettingsFavoritSagSkabelon] PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BrugerSettingsFavoritSkabelon]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BrugerSettingsFavoritSkabelon](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerSettingsID] [int] NOT NULL,
	[SkabelonID] [int] NULL,
 CONSTRAINT [PK_BrugersettingsFavoritSkabelon] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BrugerSettingsSagsstatus]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BrugerSettingsSagsstatus](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerSettingsID] [int] NOT NULL,
	[SagsstatusID] [int] NOT NULL,
 CONSTRAINT [PK_BrugerSettingsSagsstatus] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BrugerSettingsSagsType]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BrugerSettingsSagsType](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[BrugerSettingsID] [int] NOT NULL,
	[SagsTypeID] [int] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[BrugerSettingsStyringsreolSagsfelt]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BrugerSettingsStyringsreolSagsfelt](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerSettingsID] [int] NOT NULL,
	[StyringsreolSagsfeltID] [int] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Bygning]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Bygning](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[KommuneID] [int] NOT NULL,
	[Beskrivelse] [nvarchar](500) NULL,
	[Oprettet] [datetime] NOT NULL,
	[BygningsNummer] [nvarchar](20) NOT NULL,
	[BbrIndikator] [nvarchar](50) NULL,
	[EjendomsNummer] [nvarchar](20) NULL,
	[Anvendelse] [nvarchar](75) NULL,
	[ExternalSourceLastUpdate] [datetime] NULL,
	[ExternalSourceID] [nvarchar](50) NULL,
	[ExternalSourceName] [nvarchar](50) NULL,
	[Beliggenhed] [nvarchar](500) NULL,
	[Historisk] [bit] NOT NULL,
	[BygningIdentity] [uniqueidentifier] NOT NULL,
 CONSTRAINT [PK_Bygning] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[BygningIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[CivilstandOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[CivilstandOpslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Kode] [nvarchar](10) NULL,
	[Navn] [nvarchar](100) NULL,
 CONSTRAINT [PK_Civilstand] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[CompatibleVersions]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[CompatibleVersions](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SbsysDatabaseVersion] [varchar](20) NOT NULL,
	[SbsysClientVersion] [varchar](20) NOT NULL,
 CONSTRAINT [PK_CompatibleVersions] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[CprBrokerConfiguration]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[CprBrokerConfiguration](
	[Token] [nvarchar](36) NULL,
	[ApplicationName] [nvarchar](50) NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[CprBrokerPersonReference]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[CprBrokerPersonReference](
	[PersonId] [int] NOT NULL,
	[CprBrokerUuid] [uniqueidentifier] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[PersonId] ASC,
	[CprBrokerUuid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Dagsorden]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Dagsorden](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DagsordenIdentity] [uniqueidentifier] NOT NULL,
	[Sortering] [int] NOT NULL,
	[PunktnummereringStart] [int] NOT NULL,
	[Offentlig] [bit] NOT NULL,
	[Tillaegsdagsorden] [bit] NOT NULL,
	[SidenummereringStart] [int] NOT NULL,
	[ValgfriForsidetekstHtml] [ntext] NULL,
	[LukketForTilgang] [bit] NOT NULL,
	[Publiceret] [bit] NOT NULL,
	[Created] [datetime] NOT NULL,
	[CreatedBy] [int] NOT NULL,
	[LastChanged] [datetime] NOT NULL,
	[LastChangedBy] [int] NOT NULL,
	[MoedeID] [int] NOT NULL,
	[Historik] [ntext] NOT NULL,
	[ErSkabelon] [bit] NOT NULL,
	[SkabelonNavn] [nvarchar](200) NULL,
 CONSTRAINT [PK__Dagsorden__68E93303] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[DagsordenIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Dagsordenpunkt]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Dagsordenpunkt](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DagsordenpunktTypeID] [int] NOT NULL,
	[AktivitetsLog] [ntext] NULL,
	[Created] [datetime] NOT NULL,
	[CreatedBy] [int] NOT NULL,
	[SagID] [int] NOT NULL,
	[BesluttendeUdvalgID] [int] NULL,
	[RedigeresLigeNuAfID] [int] NULL,
	[Timestamp] [timestamp] NOT NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
	[Beskrivelse] [ntext] NULL,
	[DagsordenpunktIdentity] [uniqueidentifier] NOT NULL,
 CONSTRAINT [PK__Dagsordenpunkt__72729D3D] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[DagsordenpunktIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DagsordenPunktBehandlingBilag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DagsordenPunktBehandlingBilag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BilagID] [int] NOT NULL,
	[BehandlingID] [int] NOT NULL,
 CONSTRAINT [PK_DagsordenBehandlingBilag] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [AK_DagsordenBehandlingBilag_BilagId_BehandlingId] UNIQUE NONCLUSTERED
(
	[BilagID] ASC,
	[BehandlingID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DagsordenpunktBehandlingFeltIndhold]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DagsordenpunktBehandlingFeltIndhold](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[DagsordenpunktFeltIndholdId] [int] NOT NULL,
	[DagsordenpunktsBehandlingId] [int] NOT NULL,
 CONSTRAINT [PK_DagsordenpunkBehandlingFeltIndhold] PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [AK_DagsordenpunkBehandlingFeltIndhold_FeltId_BehandlingId] UNIQUE NONCLUSTERED
(
	[DagsordenpunktFeltIndholdId] ASC,
	[DagsordenpunktsBehandlingId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DagsordenpunktFelt]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DagsordenpunktFelt](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[Beskrivelse] [ntext] NULL,
	[SkabelonHtmlTekst] [ntext] NOT NULL,
	[ErIndtastningFelt] [bit] NULL,
	[DagsordenpunktFeltTypeId] [int] NULL,
	[EksterntId] [nvarchar](100) NULL,
 CONSTRAINT [PK_DagsordenpunktFelt] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DagsordenpunktFeltIndhold]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DagsordenpunktFeltIndhold](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[DagsordenpunktFeltId] [int] NOT NULL,
	[Html] [ntext] NOT NULL,
	[Tekst] [ntext] NOT NULL,
	[FeltIndholdIdentity] [uniqueidentifier] NOT NULL,
	[TilknyttetStjernehoering] [bit] NOT NULL,
 CONSTRAINT [PK_DagsordenpunktFeltIndhold] PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[FeltIndholdIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DagsordenpunktFeltType]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DagsordenpunktFeltType](
	[ID] [int] NOT NULL,
	[Navn] [nvarchar](255) NOT NULL,
 CONSTRAINT [PK_DagsordenpunktFeltType] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DagsordenpunktRessource]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DagsordenpunktRessource](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DagsordenpunktID] [int] NOT NULL,
	[RessourceID] [int] NOT NULL,
 CONSTRAINT [PK_DagsordenpunktRessource] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_DagsordenpunktRessource]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_DagsordenpunktRessource] ON [dbo].[DagsordenpunktRessource]
(
	[DagsordenpunktID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DagsordenpunktsBehandling]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DagsordenpunktsBehandling](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[DagsordenId] [int] NOT NULL,
	[DagsordenpunktId] [int] NOT NULL,
	[DagsordenRaekkefoelge] [int] NOT NULL,
	[BehandlingRaekkefoelge] [int] NOT NULL,
	[DagsordenpunktStatus] [int] NOT NULL,
	[Laast] [bit] NOT NULL,
	[TilbagejournaliseretDokumentID] [int] NULL,
	[Aabent] [bit] NOT NULL,
	[AnsvarligID] [int] NOT NULL,
	[Note] [nvarchar](2000) NULL,
	[HarBeslutning] [bit] NOT NULL,
	[Overskrift] [nvarchar](255) NOT NULL,
	[OffentligOverskriftVedIkkeOffentlig] [nvarchar](255) NULL,
	[YderligereSagsNumre] [nvarchar](max) NULL,
	[IndstillingOverskrift] [nvarchar](max) NULL,
	[Gruppering] [nvarchar](255) NULL,
	[LastChanged] [datetime] NOT NULL,
	[LastChangedBy] [int] NOT NULL,
	[DagsordenpunktsBehandlingIdentity] [uniqueidentifier] NOT NULL,
	[IsStjernehoering] [bit] NOT NULL,
 CONSTRAINT [PK_DagsordenpunktsBehandling] PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [AK_DagsordenpunktsBehandling_DagsordenId_DagsprdenpunktId] UNIQUE NONCLUSTERED
(
	[DagsordenId] ASC,
	[DagsordenpunktId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[DagsordenpunktsBehandlingIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DagsordenpunktsBehandlingDokumentBackup]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DagsordenpunktsBehandlingDokumentBackup](
	[DagsordenpunktId] [int] NULL,
	[TilbagejournaliseretDokumentID] [int] NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DagsordenpunktStandardText]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DagsordenpunktStandardText](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Label] [char](50) NOT NULL,
	[Text] [ntext] NULL,
 CONSTRAINT [PK_DagsordenpunktStandardText] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DagsordenpunktStandardTextAnsaettelsessted]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DagsordenpunktStandardTextAnsaettelsessted](
	[DagsordenpunktStandardTextID] [int] NOT NULL,
	[AnsaettelsesstedID] [int] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DagsordenpunktType]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DagsordenpunktType](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](255) NOT NULL,
	[Sortering] [int] NOT NULL,
	[Aktiv] [bit] NOT NULL,
	[Beskrivelse] [ntext] NULL,
 CONSTRAINT [PK__Dagsordenpunktty__76432E21] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DagsordenpunktTypeDagsordenpunktFelt]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DagsordenpunktTypeDagsordenpunktFelt](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DagsordenpunktFeltId] [int] NOT NULL,
	[Sortering] [int] NOT NULL,
	[DagsordenpunkttypeID] [int] NOT NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
	[IsBuiltin] [bit] NOT NULL,
 CONSTRAINT [PK_DagsordenpunktTypeDagsordenpunktFeltID] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [AK_DagsordenpunktTypeDagsordenpunktFelt_DagsordenpunktFeltId_DagsordenpunkttypeID] UNIQUE NONCLUSTERED
(
	[DagsordenpunktFeltId] ASC,
	[DagsordenpunkttypeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [AK_DagsordenpunktTypeDagsordenpunktFelt_Sortering_DagsordenpunkttypeID] UNIQUE NONCLUSTERED
(
	[Sortering] ASC,
	[DagsordenpunkttypeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DagsordenpunkttypeIUdvalg]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DagsordenpunkttypeIUdvalg](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DagsordenpunkttypeID] [int] NOT NULL,
	[UdvalgID] [int] NOT NULL,
	[Sortering] [int] NOT NULL,
 CONSTRAINT [PK_DagsordenpunkttypeIUdvalg] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DagsordenpunktVersion]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DagsordenpunktVersion](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[VersionNummer] [int] NOT NULL,
	[VersionCreated] [datetime] NOT NULL,
	[DagsordenpunktID] [int] NOT NULL,
	[Offentlig] [bit] NOT NULL,
	[Note] [nvarchar](2000) NULL,
	[Overskrift] [nvarchar](255) NOT NULL,
	[OffentligOverskriftVedIkkeOffentlig] [nvarchar](255) NULL,
	[Gruppering] [nvarchar](255) NULL,
	[DagsordenpunktTypeID] [int] NOT NULL,
	[AktivitetsLog] [ntext] NULL,
	[Created] [datetime] NOT NULL,
	[CreatedBy] [int] NOT NULL,
	[LastChanged] [datetime] NOT NULL,
	[LastChangedBy] [int] NOT NULL,
	[IndstillingOverskrift] [ntext] NULL,
	[SagID] [int] NOT NULL,
	[AnsvarligID] [int] NOT NULL,
	[BesluttendeUdvalgID] [int] NULL,
	[RedigeresLigeNuAfID] [int] NULL,
	[Timestamp] [timestamp] NOT NULL,
	[YderligereSagsNumre] [ntext] NULL,
	[Version] [int] NOT NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
	[HarBeslutning] [bit] NOT NULL,
	[Beskrivelse] [ntext] NULL,
 CONSTRAINT [PK_DagsordenpunktVersion] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Index [IX_DagsordenpunktVersion]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE CLUSTERED INDEX [IX_DagsordenpunktVersion] ON [dbo].[DagsordenpunktVersion]
(
	[DagsordenpunktID] ASC,
	[VersionNummer] DESC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DagsordenpunktVersionFeltIndhold]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DagsordenpunktVersionFeltIndhold](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[DagsordenpunktFeltIndholdId] [int] NOT NULL,
	[DagsordenpunktVersionId] [int] NOT NULL,
	[Redigerbar] [bit] NOT NULL,
 CONSTRAINT [PK_DagsordenpunktVersionFeltIndhold] PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [AK_DagsordenpunktVersionFeltIndhold_FeltId_BehandlingId] UNIQUE NONCLUSTERED
(
	[DagsordenpunktFeltIndholdId] ASC,
	[DagsordenpunktVersionId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Delforloeb]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Delforloeb](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagID] [int] NOT NULL,
	[DelforloebTypeID] [int] NOT NULL,
	[BehandlerID] [int] NOT NULL,
	[BevaringID] [int] NULL,
	[KommuneID] [int] NULL,
	[KontorID] [int] NULL,
	[BeslutningsTypeID] [int] NULL,
	[Titel] [nvarchar](254) NOT NULL,
	[AfsendtFraSagsPart] [datetime] NULL,
	[Modtaget] [datetime] NULL,
	[ErBesluttet] [bit] NULL,
	[Besluttet] [datetime] NULL,
	[BeslutningNotat] [nvarchar](200) NULL,
	[ErTinglyst] [bit] NULL,
	[ErMoedeSag] [bit] NULL,
	[BeslutningHarDeadline] [bit] NULL,
	[BeslutningDeadline] [datetime] NULL,
	[Created] [datetime] NULL,
	[CreatedByID] [int] NULL,
	[LastChanged] [datetime] NULL,
	[LastChangedByID] [int] NULL,
	[SagspartID] [int] NULL,
	[SagspartRolleID] [int] NULL,
	[FagomraadeID] [int] NULL,
	[Orden] [int] NULL,
	[KommuneFoer2007ID] [int] NULL,
 CONSTRAINT [PK_Delforloeb] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_JournalDelforloeb_Journal]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_JournalDelforloeb_Journal] ON [dbo].[Delforloeb]
(
	[SagID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DelforloebDagsordenpunkt]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DelforloebDagsordenpunkt](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DelforloebID] [int] NOT NULL,
	[DagsordenpunktID] [int] NOT NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
 CONSTRAINT [PK_DelforloebDagsordenpunkt] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DelforloebDokumentRegistrering]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DelforloebDokumentRegistrering](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DelforloebID] [int] NOT NULL,
	[DokumentRegistreringID] [int] NOT NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
 CONSTRAINT [PK_DelforloebDokumentRegistreringer] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UNIQUE_DELFORLOEB_DOKUMENTREG] UNIQUE NONCLUSTERED
(
	[DelforloebID] ASC,
	[DokumentRegistreringID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DelforloebEksternIdentitet]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DelforloebEksternIdentitet](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DelforloebID] [int] NOT NULL,
	[Oprettet] [datetime] NOT NULL,
	[EksternSystemID] [int] NOT NULL,
	[EksternIdentitet] [nvarchar](300) NOT NULL,
	[Status] [tinyint] NOT NULL,
 CONSTRAINT [PK_DelforloebEksternIdentitet] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DelforloebEmneOrd]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DelforloebEmneOrd](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DelforloebID] [int] NOT NULL,
	[EmneOrdID] [int] NOT NULL,
 CONSTRAINT [PK_DelforloebEmneOrd] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DelforloebKladdeRegistrering]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DelforloebKladdeRegistrering](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DelforloebID] [int] NOT NULL,
	[KladdeRegistreringID] [int] NOT NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
 CONSTRAINT [PK_DelforloebKladdeRegistrering] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UNIQUE_DELFORLOEB_KLADDEREG] UNIQUE NONCLUSTERED
(
	[DelforloebID] ASC,
	[KladdeRegistreringID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DelforloebType]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DelforloebType](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[DelforloebTypeGruppeID] [int] NOT NULL,
 CONSTRAINT [PK_DelforloebType] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DelforloebTypeGruppe]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DelforloebTypeGruppe](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
 CONSTRAINT [PK_SagsTypeGruppe] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DocumentProcesseringHistorik]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DocumentProcesseringHistorik](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[InputDokumentID] [int] NOT NULL,
	[InputDokumentDataInfoID] [int] NOT NULL,
	[OutputDokumentDataInfoID] [int] NULL,
	[Action] [tinyint] NOT NULL,
	[Queued] [datetime] NOT NULL,
	[LastAttemptStart] [datetime] NULL,
	[LastAttemptEnd] [datetime] NULL,
	[LastAttemptDurationSeconds] [bigint] NULL,
	[TotalDurationSeconds] [bigint] NOT NULL,
	[ProcessedOnMachine] [nvarchar](150) NULL,
	[AttemptCount] [int] NULL,
	[Message] [nvarchar](200) NULL,
 CONSTRAINT [PK_DocumentProcesseringHistorik] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokImport]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokImport](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Beskrivelse] [nvarchar](255) NULL,
	[Navn] [nvarchar](255) NULL,
	[OprettetDato] [datetime] NULL,
	[OprettetAfID] [varchar](20) NULL,
	[OprettetAfNavn] [nvarchar](255) NULL,
	[DokumentArtNavn] [nvarchar](50) NULL,
	[DokumentArt] [int] NULL,
	[DokumentType] [int] NULL,
	[Modtager] [nvarchar](300) NULL,
	[Filnavn] [nvarchar](1000) NULL,
	[FilEkstension] [nvarchar](30) NULL,
	[ImportStiOgFilnavn] [nvarchar](1000) NULL,
	[Adresse] [nvarchar](400) NULL,
	[SagID] [int] NULL,
	[AmtsSagID] [nvarchar](50) NULL,
	[DokumentGuid] [varchar](50) NULL,
	[Laast] [bit] NULL,
	[Aaben] [bit] NULL,
	[YderligereMaterialeBeskrivelse] [nvarchar](400) NULL,
	[YderligereMaterialeFindes] [bit] NULL,
	[PartNo] [nvarchar](50) NULL,
	[JournalPostID] [int] NULL,
	[Delforloeb] [nvarchar](254) NULL,
	[PrimaryDokument] [bit] NULL,
	[FilSomBlob] [bit] NULL,
	[ErKladde] [bit] NULL,
	[KladdeVersion] [int] NULL,
	[SenestOpdateretDato] [datetime] NULL,
	[SenestOpdateretAfID] [varchar](20) NULL,
	[OmfattetAfAktindsigt] [bit] NULL,
 CONSTRAINT [PK_DokImport] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Dokument]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Dokument](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DokumentArtID] [int] NOT NULL,
	[Beskrivelse] [nvarchar](255) NULL,
	[OprettetAfID] [int] NOT NULL,
	[Oprettet] [datetime] NOT NULL,
	[DokumentType] [int] NOT NULL,
	[ProcessStatus] [int] NOT NULL,
	[YderligereMaterialeFindes] [bit] NULL,
	[YderligereMaterialeBeskrivelse] [nvarchar](255) NULL,
	[MailID] [int] NULL,
	[ParentDokumentID] [int] NULL,
	[Navn] [nvarchar](200) NOT NULL,
	[IsImported] [bit] NOT NULL,
	[PaaPostliste] [bit] NOT NULL,
	[PostlisteTitel] [nvarchar](200) NULL,
	[PostlisteBeskrivelse] [nvarchar](255) NULL,
	[ProcessPostAction] [int] NOT NULL,
	[ImporteretFraKnownEksternSystemID] [int] NULL,
	[EksternId] [nvarchar](50) NULL,
	[IsParent] [bit] NOT NULL,
	[IsComposite] [bit] NOT NULL,
	[PrintDate] [datetime] NULL,
	[PrimaryDokumentDataInfoID] [int] NULL,
	[DeletedState] [tinyint] NOT NULL,
	[DeletedDate] [datetime] NULL,
	[DeletedByID] [int] NULL,
	[DeletedReason] [nvarchar](100) NULL,
	[DeleteConfirmed] [datetime] NULL,
	[DeleteConfirmedByID] [int] NULL,
	[OmfattetAfAktindsigt] [bit] NOT NULL,
	[AktindsigtKommentar] [nvarchar](max) NULL,
	[DokumentIdentity] [uniqueidentifier] NOT NULL,
	[StatusTekst] [nvarchar](200) NULL,
	[FraKladdeID] [int] NULL,
 CONSTRAINT [PK_Dokument] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 90) ON [PRIMARY],
 CONSTRAINT [IX_Dokument] UNIQUE CLUSTERED
(
	[ID] ASC,
	[DokumentType] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[DokumentIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokumentArtOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokumentArtOpslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[UbeskyttetStandardMarkering] [bit] NOT NULL,
	[MaaPubliseresPaaDagsorden] [bit] NOT NULL,
	[UbeskyttetTilladAendring] [bit] NOT NULL,
	[SagBeskyttetStandardMarkering] [bit] NOT NULL,
	[SagBeskyttetTilladAendring] [bit] NOT NULL,
	[DokumentBeskyttetStandardMarkering] [bit] NOT NULL,
	[DokumentBeskyttetTilladAendring] [bit] NOT NULL,
	[SagOgDokumentBeskyttetStandardMarkering] [bit] NOT NULL,
	[SagOgDokumentBeskyttetTilladAendring] [bit] NOT NULL,
	[DokumentArtIdentifier] [uniqueidentifier] NOT NULL,
 CONSTRAINT [PK_DokumentArt] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[DokumentArtIdentifier] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokumentBoksHistorik]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokumentBoksHistorik](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Sent] [datetime] NULL,
	[SagID] [int] NOT NULL,
	[Modtagertype] [nvarchar](50) NOT NULL,
	[AfsenderId] [int] NOT NULL,
	[Materiale] [nvarchar](200) NULL,
	[Postkasse] [nvarchar](200) NULL,
	[ForsoegtSendt] [datetime] NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokumentBoksWebserviceQueue]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokumentBoksWebserviceQueue](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[CreatedDate] [datetime] NOT NULL,
	[HandleAfterDate] [datetime] NOT NULL,
	[QueueType] [nvarchar](100) NOT NULL,
	[QueueData] [image] NOT NULL,
	[ContextSagID] [int] NULL,
	[ModtagerNoegle] [nvarchar](100) NULL,
	[PostkasseNavn] [nvarchar](100) NULL,
	[SporGUID] [nvarchar](100) NULL,
	[AfsenderID] [int] NOT NULL,
 CONSTRAINT [PK_DokumentBoksWebserviceQueue] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokumentDataInfo]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokumentDataInfo](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DokumentID] [int] NOT NULL,
	[DokumentDataType] [int] NOT NULL,
	[Rank] [int] NULL,
	[FileName] [nvarchar](1000) NULL,
	[FileExtension] [nvarchar](30) NULL,
	[FilePath] [nvarchar](1000) NULL,
	[FileSize] [bigint] NOT NULL,
	[FileLastAccessed] [datetime] NULL,
	[FileCreated] [datetime] NULL,
	[FileAttributes] [int] NULL,
	[DokumentDataInfoType] [int] NOT NULL,
	[Keywords] [ntext] NULL,
	[HasSnapshot] [bit] NOT NULL,
	[HasThumbnail] [bit] NOT NULL,
	[ThumbnailID] [int] NULL,
	[IndexingStatus] [tinyint] NOT NULL,
	[AlternateOfID] [int] NULL,
	[OCRStatus] [tinyint] NOT NULL,
	[PageFormat] [nvarchar](10) NULL,
	[PageDPI] [int] NULL,
	[PageCount] [int] NULL,
	[TextEncoding] [nvarchar](30) NULL,
	[IsDeleted] [bit] NOT NULL,
	[FileIdentity] [uniqueidentifier] NOT NULL,
	[ContentID] [nvarchar](500) NULL,
 CONSTRAINT [PK_DokumentDataInfo] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[FileIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_DokumentDataInfo_DokumentID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_DokumentDataInfo_DokumentID] ON [dbo].[DokumentDataInfo]
(
	[DokumentID] ASC,
	[DokumentDataType] ASC,
	[FileName] ASC,
	[FileExtension] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokumentDataInfoTypeOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokumentDataInfoTypeOpslag](
	[ID] [int] NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
 CONSTRAINT [PK_DokumentDataInfoType] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokumentDataTypeOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokumentDataTypeOpslag](
	[ID] [int] NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
 CONSTRAINT [PK_DokumentDataType] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokumentKonverteringBestilling]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokumentKonverteringBestilling](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DokumentID] [int] NULL,
 CONSTRAINT [PK_DokumentKonverteringBestilling] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokumentMetaData]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokumentMetaData](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DokumentID] [int] NOT NULL,
	[KeyName] [nvarchar](50) NOT NULL,
	[Value] [nvarchar](400) NULL,
 CONSTRAINT [PK_DokumentMetaData] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_DokumentMetaData]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_DokumentMetaData] ON [dbo].[DokumentMetaData]
(
	[DokumentID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokumentPart]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokumentPart](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DokumentID] [int] NOT NULL,
	[PartID] [int] NOT NULL,
	[PartType] [int] NOT NULL,
	[KontaktForm] [int] NOT NULL,
	[AnvendtAdresse] [nvarchar](300) NULL,
 CONSTRAINT [PK_DokumentPart] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokumentProcessingQueue]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokumentProcessingQueue](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[InputDokumentID] [int] NOT NULL,
	[InputDokumentDataInfoID] [int] NOT NULL,
	[OutputDokumentDataInfoID] [int] NULL,
	[Action] [tinyint] NOT NULL,
	[Queued] [datetime] NOT NULL,
	[LastAttemptStart] [datetime] NULL,
	[LastAttemptEnd] [datetime] NULL,
	[LastAttemptDurationSeconds] [bigint] NULL,
	[NextAttempt] [datetime] NULL,
	[AttemptCount] [int] NOT NULL,
	[Log] [nvarchar](max) NOT NULL,
	[Status] [tinyint] NOT NULL,
	[Message] [nvarchar](200) NULL,
	[TotalDurationSeconds] [bigint] NOT NULL,
	[TimeoutSeconds] [int] NOT NULL,
	[ProcessedOnMachine] [nvarchar](150) NULL,
 CONSTRAINT [PK_DokumentProcessingQueue] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Index [IX_DokumentProcessingQueue_InputDokument]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_DokumentProcessingQueue_InputDokument] ON [dbo].[DokumentProcessingQueue]
(
	[ID] ASC,
	[InputDokumentID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokumentProcessingQueueAction]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokumentProcessingQueueAction](
	[ID] [tinyint] NOT NULL,
	[Name] [nvarchar](100) NOT NULL,
 CONSTRAINT [PK_DokumentProcessingQeueueAction] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokumentProcessingQueueStatus]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokumentProcessingQueueStatus](
	[ID] [tinyint] NOT NULL,
	[Name] [nvarchar](100) NOT NULL,
 CONSTRAINT [PK_DokumentProcessingQueueStatus] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokumentRegistrering]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokumentRegistrering](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagID] [int] NOT NULL,
	[DokumentID] [int] NOT NULL,
	[SagspartID] [int] NULL,
	[OprindeligSagspartAdresse] [nvarchar](400) NULL,
	[ErBeskyttet] [bit] NOT NULL,
	[Registreret] [datetime] NOT NULL,
	[RegistreretAfID] [int] NOT NULL,
	[Beskrivelse] [nvarchar](255) NULL,
	[SecuritySetID] [int] NULL,
	[Navn] [nvarchar](200) NOT NULL,
	[DeletedState] [tinyint] NOT NULL,
	[DeletedDate] [datetime] NULL,
	[DeletedByID] [int] NULL,
	[DeletedReason] [nvarchar](100) NULL,
	[DeleteConfirmed] [datetime] NULL,
	[DeleteConfirmedByID] [int] NULL,
	[DokumentRegistreringIdentity] [uniqueidentifier] NOT NULL,
 CONSTRAINT [PK_DokumentRegistrering] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[DokumentRegistreringIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_DokumentRegistrering_Sag]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_DokumentRegistrering_Sag] ON [dbo].[DokumentRegistrering]
(
	[SagID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokumentRegistreringSletning]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokumentRegistreringSletning](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DokumentRegistreringID] [int] NOT NULL,
	[BrugerID] [int] NOT NULL,
	[Aarsag] [varchar](200) NOT NULL,
	[TimeStamp] [datetime] NULL,
 CONSTRAINT [PK_DokumentRegistreringSletning] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokumentThumbnail]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokumentThumbnail](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[ThumbnailWidth] [smallint] NULL,
	[ThumbnailHeight] [smallint] NULL,
	[SnapshotWidth] [smallint] NULL,
	[SnapshotHeight] [smallint] NULL,
	[Snapshot] [image] NULL,
	[Thumbnail] [image] NULL,
 CONSTRAINT [PK_DokumentThumbnail] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[DokumentTypeOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DokumentTypeOpslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[DefaultDokumentArtID] [int] NULL,
 CONSTRAINT [PK_tDokumentType_1] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Ejendom]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Ejendom](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[KommuneID] [int] NOT NULL,
	[Beskrivelse] [nvarchar](500) NULL,
	[Oprettet] [datetime] NOT NULL,
	[EjendomsNummer] [nvarchar](20) NOT NULL,
	[ExternalSourceLastUpdate] [datetime] NULL,
	[ExternalSourceID] [nvarchar](50) NULL,
	[ExternalSourceName] [nvarchar](50) NULL,
	[Beliggenhed] [nvarchar](500) NULL,
	[Historisk] [bit] NOT NULL,
	[BeliggenhedAdresseID] [int] NULL,
	[Vejkode] [int] NULL,
	[EjendomIdentity] [uniqueidentifier] NOT NULL,
	[BFENummer] [bigint] NOT NULL,
 CONSTRAINT [PK_Ejendom] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[EjendomIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[EmailKontoExchangeConfiguration]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EmailKontoExchangeConfiguration](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Authority] [nvarchar](100) NOT NULL,
	[ClientId] [nvarchar](100) NOT NULL,
	[ExchangeEndpoint] [nvarchar](100) NOT NULL,
	[Displayname] [nvarchar](50) NOT NULL,
	[ExchangeOnlineAuthenticationMethod] [int] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[EmailKontoExchangeConfiguration_BACKUP_20220923]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EmailKontoExchangeConfiguration_BACKUP_20220923](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Authority] [nvarchar](100) NOT NULL,
	[ClientId] [nvarchar](100) NOT NULL,
	[ExchangeEndpoint] [nvarchar](100) NOT NULL,
	[Displayname] [nvarchar](50) NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[EmneOrd]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EmneOrd](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[EmneOrdGruppeID] [int] NOT NULL,
	[ErAktiv] [bit] NULL,
 CONSTRAINT [PK_tblEmneOrd] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[EmneOrdGruppe]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EmneOrdGruppe](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[EmneordOvergruppeID] [int] NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[ErAktiv] [bit] NULL,
 CONSTRAINT [PK_tblEmneordGruppe] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[EmneOrdOvergruppe]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EmneOrdOvergruppe](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
 CONSTRAINT [PK_EmneOrdOvergruppe] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[EmneordOvergruppeEmnePlanNummer]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EmneordOvergruppeEmnePlanNummer](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[EmneordOvergruppeID] [int] NOT NULL,
	[FacetID] [int] NOT NULL,
	[EmnePlanNummerID] [int] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[EmnePlan]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EmnePlan](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[Beskrivelse] [nvarchar](200) NULL,
	[MinimumDelforloeb] [int] NULL,
	[MaximumDelforloeb] [int] NULL,
	[AnvendDelforloeb] [bit] NOT NULL,
	[Separator] [char](1) NULL,
	[NummerFormat] [nvarchar](100) NOT NULL,
	[NummerFormatUdenFacet] [nvarchar](100) NOT NULL,
	[RequireFacet] [bit] NOT NULL,
	[AllowChangingNummer] [bit] NOT NULL,
	[EmnePlanNummerType] [int] NOT NULL,
	[StandardSagsTitel] [nvarchar](200) NOT NULL,
	[NySagBeskyttes] [bit] NOT NULL,
	[Version] [varchar](50) NULL,
	[TilladOprettlseUdFraudgaaetNummer] [bit] NOT NULL,
	[BrugLavesteNiveau] [bit] NOT NULL,
 CONSTRAINT [PK_JournalPlanType] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[EmnePlanLovGrundlag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EmnePlanLovGrundlag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[VedroererEmnePlanNummer] [nvarchar](50) NOT NULL,
	[Paragraf] [nvarchar](100) NULL,
	[Lovtitel] [nvarchar](200) NOT NULL,
	[RetsinfoLink] [nvarchar](200) NULL,
	[RetsinfoLinkParagraf] [nvarchar](20) NULL,
	[EmnePlanID] [int] NULL,
 CONSTRAINT [PK_LovUpdate] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[EmnePlanNummer]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EmnePlanNummer](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[EmnePlanID] [int] NOT NULL,
	[Nummer] [nvarchar](50) NOT NULL,
	[Navn] [nvarchar](300) NOT NULL,
	[Beskrivelse] [ntext] NULL,
	[Niveau] [int] NULL,
	[BevaringID] [int] NULL,
	[Oprettet] [datetime] NULL,
	[Rettet] [datetime] NULL,
	[Udgaaet] [datetime] NULL,
	[ErUdgaaet] [bit] NULL,
 CONSTRAINT [PK_EmnePlan] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 90) ON [PRIMARY],
 CONSTRAINT [IX_EmnePlanNummer] UNIQUE CLUSTERED
(
	[Nummer] ASC,
	[Niveau] ASC,
	[EmnePlanID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[EmneplanNummerAfloeserNummer]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EmneplanNummerAfloeserNummer](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[OprindeligEmnePlanNummerID] [int] NOT NULL,
	[AfloserEmnePlanNummerID] [int] NOT NULL,
 CONSTRAINT [PK_EmneplanNummerAfloeserNummer] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[EmneplanOpdatering]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EmneplanOpdatering](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[EmneplanID] [int] NOT NULL,
	[SendMail] [bit] NULL,
	[Opretnyhed] [bit] NULL,
	[SmtpServer] [nvarchar](200) NULL,
	[SSL] [bit] NULL,
	[Brugerkonto] [nvarchar](50) NULL,
	[Adgangskode] [nvarchar](50) NULL,
	[EmneplanUrl] [nvarchar](200) NULL,
	[StikordUrl] [nvarchar](200) NULL,
	[FacetUrl] [nvarchar](200) NULL,
	[TjekInterval] [int] NULL,
	[SidsteTjek] [datetime] NULL,
	[Aktiv] [bit] NOT NULL,
	[Mail] [nvarchar](100) NULL,
 CONSTRAINT [PK_EmneplanOpdatering] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[EmnePlanStikord]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EmnePlanStikord](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[EmnePlanID] [int] NOT NULL,
	[ForeslaaNummer] [nvarchar](10) NULL,
	[ForeslaaFacetKode] [nvarchar](10) NULL,
	[EmneOrd] [nvarchar](200) NULL,
 CONSTRAINT [PK_EmnePlanStikord] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Erindring]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Erindring](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](200) NOT NULL,
	[Beskrivelse] [nvarchar](500) NULL,
	[ErindringTypeID] [int] NOT NULL,
	[CreatedByID] [int] NULL,
	[Created] [datetime] NULL,
	[LastChangedByID] [int] NULL,
	[LastChanged] [datetime] NULL,
	[OpretterID] [int] NOT NULL,
	[AnsvarligID] [int] NOT NULL,
	[Uddelegeret] [datetime] NULL,
	[ErAfsluttet] [bit] NOT NULL,
	[AfsluttetAfID] [int] NULL,
	[Afsluttet] [datetime] NULL,
	[ErAnnulleret] [bit] NOT NULL,
	[AnnulleretAfID] [int] NULL,
	[Annulleret] [datetime] NULL,
	[SagID] [int] NOT NULL,
	[DelforloebID] [int] NULL,
	[DokumentRegistreringID] [int] NULL,
	[KladdeRegistreringID] [int] NULL,
	[HarDeadline] [bit] NULL,
	[Deadline] [datetime] NULL,
	[AfsluttetNotat] [nvarchar](500) NULL,
	[PopupStatus] [int] NOT NULL,
	[SagsPartID] [int] NULL,
	[DagsordenpunktsBehandlingID] [int] NULL,
	[KopierEfterUdfoerelse] [bit] NOT NULL,
	[KopierTilID] [int] NULL,
	[ReturEfterUdfoerelse] [bit] NOT NULL,
	[JournalArkNoteID] [int] NULL,
	[ProcessPostAction] [int] NOT NULL,
	[SynligFra] [datetime] NULL,
	[SendSomMailRetryCount] [int] NULL,
 CONSTRAINT [PK_Erindring] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_Erindring_Sag]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_Erindring_Sag] ON [dbo].[Erindring]
(
	[SagID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ErindringDataRegistrering]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ErindringDataRegistrering](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[ErindringID] [int] NOT NULL,
	[DataRegistreringType] [int] NOT NULL,
	[RegistreringID] [int] NOT NULL,
 CONSTRAINT [PK_ErindringDataRegistrering] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ErindringHandling]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ErindringHandling](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[ErindringID] [int] NOT NULL,
	[HandlingID] [int] NOT NULL,
 CONSTRAINT [pk_ErindringHandling] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ErindringRegel]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ErindringRegel](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Alder] [int] NOT NULL,
	[AntalDage] [int] NOT NULL,
	[BeforeOrAfter] [bit] NOT NULL,
	[SagSkabelonID] [int] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ErindringSkabelon]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ErindringSkabelon](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](200) NOT NULL,
	[Beskrivelse] [nvarchar](500) NULL,
	[ErindringTypeID] [int] NOT NULL,
	[AnsvarligBrugerID] [int] NULL,
	[Normtid] [int] NOT NULL,
	[HierakiMedlemID] [int] NULL,
 CONSTRAINT [pk_ErindringSkabelon] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ErindringSomMail]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ErindringSomMail](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NULL,
	[AnsaettelsesstedID] [int] NULL,
 CONSTRAINT [PK_ErindringSomMail] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ErindringTrin]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ErindringTrin](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagID] [int] NOT NULL,
	[ErindringID] [int] NOT NULL,
	[TrinID] [int] NOT NULL,
 CONSTRAINT [PK_ErindringTrin] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ErindringTypeOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ErindringTypeOpslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[KeyName] [nvarchar](30) NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
	[SynlighedIDage] [int] NULL,
	[DeadlineIDage] [int] NULL,
	[HierakiMedlemID] [int] NULL,
	[SkjulErindring] [bit] NOT NULL,
	[TilladKunSystemhaandtering] [bit] NOT NULL,
 CONSTRAINT [PK_ErindringType] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Facet]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Facet](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Nummer] [nvarchar](10) NOT NULL,
	[FacetTypeID] [int] NOT NULL,
	[Navn] [nvarchar](150) NOT NULL,
	[Beskrivelse] [ntext] NULL,
	[ErBrugerDefineret] [bit] NULL,
	[BevaringID] [int] NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [bit] NULL,
	[Oprettet] [datetime] NULL,
	[Rettet] [datetime] NULL,
	[Udgaaet] [datetime] NULL,
 CONSTRAINT [PK_tblInstitution] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 90) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Index [IX_Facet_FacetType]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_Facet_FacetType] ON [dbo].[Facet]
(
	[FacetTypeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FacetType]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FacetType](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](75) NOT NULL,
	[Beskrivelse] [nvarchar](3900) NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [bit] NULL,
	[EmnePlanID] [int] NOT NULL,
	[Oprettet] [datetime] NULL,
	[Rettet] [datetime] NULL,
	[Udgaaet] [datetime] NULL,
	[FacetTypeKode] [nvarchar](10) NULL,
 CONSTRAINT [PK_tblInstitutionsType] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_FacetType_Emneplan]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_FacetType_Emneplan] ON [dbo].[FacetType]
(
	[EmnePlanID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FagOmraade]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FagOmraade](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[FagomraadeIdentity] [uniqueidentifier] NOT NULL,
 CONSTRAINT [PK_tblFagOmr] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 90) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Firma]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Firma](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[AdresseID] [int] NULL,
	[Navn1] [nvarchar](200) NULL,
	[Navn2] [nvarchar](200) NULL,
	[CVRNummer] [varchar](8) NULL,
	[SENummer] [varchar](8) NULL,
	[PNummer] [varchar](10) NULL,
	[Homepage] [varchar](400) NULL,
	[ExternalSourceLastUpdate] [datetime] NULL,
	[ExternalSourceID] [nvarchar](50) NULL,
	[ExternalSourceName] [nvarchar](50) NULL,
	[EANNummer] [varchar](13) NULL,
	[KontaktForm] [int] NOT NULL,
	[BrancheID] [int] NULL,
	[AntalAnsatte] [int] NULL,
	[Note] [nvarchar](200) NULL,
	[KommuneID] [int] NULL,
	[PartOprydningsKeyCheckSum] [int] NULL,
	[ErJuridiskEnhed] [bit] NULL,
	[JuridiskEnhedAdresseID] [int] NULL,
	[TilmeldtDigitalPost] [bit] NOT NULL,
	[FirmaIdentity] [uniqueidentifier] NOT NULL,
 CONSTRAINT [PK_tFirma] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[FirmaIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FirmaAttentionPerson]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FirmaAttentionPerson](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[FirmaID] [int] NOT NULL,
	[Navn] [nvarchar](300) NULL,
	[AdresseID] [int] NOT NULL,
	[Telefonnummer] [nvarchar](50) NULL,
	[EmailAdresse] [nvarchar](200) NULL,
	[Afdeling] [nvarchar](200) NULL,
 CONSTRAINT [PK_FirmaAttentionPerson] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_FirmaAttentionPerson]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_FirmaAttentionPerson] ON [dbo].[FirmaAttentionPerson]
(
	[FirmaID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FirmaPart]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FirmaPart](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[FirmaID] [int] NOT NULL,
	[PartType] [int] NOT NULL,
	[PartID] [int] NOT NULL,
	[FirmaPartRolleID] [int] NULL,
	[OprindeligAdresseID] [int] NULL,
	[Oprettet] [datetime] NOT NULL,
 CONSTRAINT [PK_PersonFirma] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FirmaPartRolle]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FirmaPartRolle](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[Beskrivelse] [nvarchar](500) NULL,
 CONSTRAINT [PK_FirmaPartRolle] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FirmaType]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FirmaType](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](80) NOT NULL,
 CONSTRAINT [PK_tFirmaType] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FkOrgAnsaettelsesstedReference]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FkOrgAnsaettelsesstedReference](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[AnsaettelsesstedID] [int] NOT NULL,
	[FkOrgUuid] [uniqueidentifier] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FkOrgBrugerReference]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FkOrgBrugerReference](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[FkOrgUuid] [uniqueidentifier] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FkOrgHierarkiMedlemReference]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FkOrgHierarkiMedlemReference](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[HierarkiMedlemID] [int] NOT NULL,
	[FkOrgUuid] [uniqueidentifier] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FlettetFirma]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FlettetFirma](
	[ID] [int] NOT NULL,
	[AdresseID] [int] NULL,
	[Navn1] [nvarchar](200) NULL,
	[Navn2] [nvarchar](200) NULL,
	[CVRNummer] [varchar](8) NULL,
	[SENummer] [varchar](8) NULL,
	[PNummer] [varchar](10) NULL,
	[Homepage] [varchar](400) NULL,
	[ExternalSourceLastUpdate] [datetime] NULL,
	[ExternalSourceID] [nvarchar](50) NULL,
	[ExternalSourceName] [nvarchar](50) NULL,
	[EANNummer] [varchar](13) NULL,
	[KontaktForm] [int] NOT NULL,
	[BrancheID] [int] NULL,
	[AntalAnsatte] [int] NULL,
	[Note] [nvarchar](200) NULL,
	[KommuneID] [int] NULL,
 CONSTRAINT [PK_FlettetFirma] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FlettetPerson]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FlettetPerson](
	[ID] [int] NOT NULL,
	[Initialer] [nvarchar](10) NULL,
	[Titel] [nvarchar](50) NULL,
	[Uddannelse] [nvarchar](50) NULL,
	[Stilling] [nvarchar](50) NULL,
	[Note] [nvarchar](200) NULL,
	[CprNummer] [varchar](11) NULL,
	[Koen] [tinyint] NULL,
	[AdresseID] [int] NULL,
	[ExternalSourceLastUpdate] [datetime] NULL,
	[ExternalSourceID] [nvarchar](50) NULL,
	[ExternalSourceName] [nvarchar](50) NULL,
	[Navn] [nvarchar](300) NULL,
	[FoedeDato] [datetime] NULL,
	[Ansaettelsessted] [nvarchar](100) NULL,
	[KontaktForm] [int] NOT NULL,
	[CivilstandID] [int] NULL,
	[AegtefaelleCPR] [varchar](11) NULL,
	[MorCPR] [varchar](11) NULL,
	[FarCPR] [varchar](11) NULL,
	[KommuneID] [int] NULL,
 CONSTRAINT [PK_FlettetPerson] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FlettetSagspart]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FlettetSagspart](
	[ID] [int] NOT NULL,
	[SagID] [int] NOT NULL,
	[PartType] [int] NOT NULL,
	[PartID] [int] NOT NULL,
	[SagsPartRolleID] [int] NULL,
	[OprindeligAdresseID] [int] NULL,
	[Oprettet] [datetime] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Flow]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Flow](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DokumentID] [int] NULL,
	[KladdeID] [int] NULL,
	[FlowForloeb] [int] NOT NULL,
	[Navn] [nvarchar](max) NOT NULL,
	[Oprettet] [datetime] NOT NULL,
	[OprettetAf] [int] NOT NULL,
	[NextFristDato] [datetime] NULL,
	[Status] [int] NOT NULL,
	[Discriminator] [nvarchar](max) NOT NULL,
PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FlowModtager]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FlowModtager](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[FlowID] [int] NOT NULL,
	[BrugerID] [int] NOT NULL,
	[Opgave] [nvarchar](max) NOT NULL,
	[Bemaerkninger] [nvarchar](max) NULL,
	[Tidsfrist] [datetime] NOT NULL,
	[ErindringID] [int] NULL,
PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FlowModtagerSvar]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FlowModtagerSvar](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[FlowModtagerID] [int] NOT NULL,
	[BrugerID] [int] NOT NULL,
	[SvarDato] [datetime] NOT NULL,
	[Kommentar] [nvarchar](max) NULL,
	[Svar] [int] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FlowSkabelon]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FlowSkabelon](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](max) NOT NULL,
	[FlowForloeb] [int] NOT NULL,
	[AnsaettelsesstedID] [int] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FlowSkabelonModtager]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FlowSkabelonModtager](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[FlowSkabelonID] [int] NOT NULL,
	[BrugerID] [int] NOT NULL,
	[Opgave] [nvarchar](max) NOT NULL,
	[Bemaerkninger] [nvarchar](max) NULL,
	[TidsfristDage] [int] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Forloeb]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Forloeb](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[ForloebTypeID] [int] NOT NULL,
	[Beskrivelse] [nvarchar](255) NOT NULL,
	[Note] [text] NULL,
	[RegistreretAfID] [int] NOT NULL,
	[SagID] [int] NOT NULL,
	[DelforloebID] [int] NULL,
	[Tidspunkt] [datetime] NOT NULL,
	[TargetType] [int] NOT NULL,
	[TargetID] [int] NOT NULL,
	[ErindringID] [int] NULL,
	[ForloebData] [nvarchar](max) NULL,
 CONSTRAINT [PK_Forloeb] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Index [IX_Forloeb_Sag]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_Forloeb_Sag] ON [dbo].[Forloeb]
(
	[SagID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 90) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ForloebTypeOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ForloebTypeOpslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[Beskrivelse] [nvarchar](254) NULL,
	[KeyName] [nvarchar](30) NOT NULL,
	[HasIcon] [bit] NULL,
	[IconName] [nvarchar](50) NULL,
	[IsDetail] [bit] NOT NULL,
 CONSTRAINT [PK_ForloebType] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_ForloebType_KeyName] UNIQUE NONCLUSTERED
(
	[KeyName] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Fravaer]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Fravaer](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[UdvalgspersonId] [int] NOT NULL,
	[MoedeId] [int] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FravaerDagsorden]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FravaerDagsorden](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[FravaerId] [int] NOT NULL,
	[DagsordenId] [int] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FravaerDagsordenpunktsBehandling]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FravaerDagsordenpunktsBehandling](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[FravaerId] [int] NOT NULL,
	[DagsordenpunktsBehandlingId] [int] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[GeneratorIndstillinger]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[GeneratorIndstillinger](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[InkluderLukkedePunkterIFuldVersion] [bit] NOT NULL,
	[TilladKunBilagSomPDF] [bit] NOT NULL,
	[TilladBilagSomIkkeOffentligtDokument] [bit] NOT NULL,
	[TilladBilagSomScanningUdenPDF] [bit] NOT NULL,
	[OpdelIAabneOgLukkedePunkter] [bit] NOT NULL,
	[AnvendGruppering] [bit] NOT NULL,
	[Tilbagejournalisering] [bit] NOT NULL,
	[Bilagsliste] [bit] NOT NULL,
	[Indkaldelse] [bit] NOT NULL,
	[Underskriftsark] [bit] NOT NULL,
	[Forside] [bit] NOT NULL,
	[Indholdsfortegnelse] [bit] NOT NULL,
	[Created] [datetime] NULL,
	[CreatedBy] [int] NULL,
	[LastChanged] [datetime] NULL,
	[LastChangedBy] [int] NULL,
	[DagsordenID] [int] NULL,
	[BrugerID] [int] NULL,
	[UdvalgID] [int] NULL,
	[SidstGenereredeDagsordenSti] [nvarchar](512) NULL,
	[DagsordenType] [nvarchar](100) NULL,
	[VisBeslutningsvejUnderBeslutning] [bit] NOT NULL,
	[Bilagstegn] [nvarchar](10) NULL,
	[BilagslistePlacering] [int] NOT NULL,
	[OmgivIndstillingslinjerMedTabel] [bit] NOT NULL,
	[MedtagTommeFelter] [bit] NOT NULL,
	[MedtagTomtBeslutningsfelt] [bit] NOT NULL,
 CONSTRAINT [PK__GeneratorIndstil__7F3866D5] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[GeneratorIndstillingerFeltRegistrering]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[GeneratorIndstillingerFeltRegistrering](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[GeneratorIndstillingerID] [int] NOT NULL,
	[DagsordenpunktFeltID] [int] NOT NULL,
 CONSTRAINT [PK_GeneratorIndstillingerFeltRegistrering] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[GenstandRegistrering]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[GenstandRegistrering](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagID] [int] NOT NULL,
	[GenstandType] [int] NOT NULL,
	[GenstandID] [int] NOT NULL,
 CONSTRAINT [PK_GenstandRegistrering] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[GenstandTypeOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[GenstandTypeOpslag](
	[ID] [int] NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
 CONSTRAINT [PK_GenstandType] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Geometri]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Geometri](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Oprettet] [datetime] NOT NULL,
	[GeometriFormatID] [int] NOT NULL,
	[Data] [ntext] NULL,
 CONSTRAINT [PK_Areal] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[GeometriFormatOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[GeometriFormatOpslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[Kode] [nvarchar](50) NOT NULL,
	[IsBuiltin] [bit] NOT NULL,
 CONSTRAINT [PK_ArealFormat] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[GridLayout]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[GridLayout](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[Context] [nvarchar](100) NOT NULL,
	[Layout] [ntext] NULL,
	[SplitterPercent] [int] NULL,
	[SplitterHorizontal] [bit] NOT NULL,
 CONSTRAINT [PK_GridLayout] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Gruppering]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Gruppering](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Tekst] [nvarchar](255) NOT NULL,
	[Aktiv] [bit] NOT NULL,
 CONSTRAINT [PK__Gruppering__745AE5AF] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[HaendelseLog]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[HaendelseLog](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[HaendelseType] [int] NOT NULL,
	[TargetType] [int] NULL,
 CONSTRAINT [PK_HaendelseLog] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Handling]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Handling](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[ErindringSkabelonID] [int] NULL,
	[SkabelonID] [int] NULL,
	[SkabelonTypeID] [int] NULL,
	[SagSkabelonID] [int] NULL,
	[AnvendErindringSkabelonID] [int] NULL,
	[JournalNotatOverskrift] [nvarchar](255) NULL,
	[JournalNotatNote] [nvarchar](max) NULL,
 CONSTRAINT [pk_Handling] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Heartbeat]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Heartbeat](
	[BrugerID] [int] NOT NULL,
	[BrugerLogonID] [nvarchar](100) NOT NULL,
	[MachineName] [nvarchar](200) NOT NULL,
	[LastHeartbeat] [datetime] NOT NULL,
 CONSTRAINT [IX_Heartbeat] UNIQUE CLUSTERED
(
	[BrugerID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[HeartbeatHistory]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[HeartbeatHistory](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Tidspunkt] [datetime] NOT NULL,
	[Antal] [int] NOT NULL,
 CONSTRAINT [PK_HeartbeatHistory] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Hieraki]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Hieraki](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[Beskrivelse] [nvarchar](300) NULL,
	[EksternID] [nvarchar](50) NULL,
 CONSTRAINT [PK_Hieraki] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[HierakiMedlem]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[HierakiMedlem](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NULL,
	[HierakiID] [int] NOT NULL,
	[ParentID] [int] NULL,
	[EksternID] [nvarchar](50) NULL,
	[SortIndex] [int] NULL,
 CONSTRAINT [PK_HierakiMedlem] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[JournalArk]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[JournalArk](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagID] [int] NOT NULL,
 CONSTRAINT [PK_JournalArk] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[JournalArkNote]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[JournalArkNote](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[JournalArkID] [int] NOT NULL,
	[OprettetAf] [int] NOT NULL,
	[Oprettet] [datetime] NOT NULL,
	[KontaktTidspunkt] [datetime] NOT NULL,
	[Overskrift] [nvarchar](255) NULL,
	[Note] [ntext] NULL,
	[OmfattetAfAktindsigt] [bit] NOT NULL,
	[SlettetDato] [datetime] NULL,
	[SlettetAfBrugerID] [int] NULL,
	[JournalArkNoteIdentity] [uniqueidentifier] NOT NULL,
	[AktindsigtBeskrivelse] [nvarchar](500) NULL,
 CONSTRAINT [PK_JournalArkNote] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[JournalArkNoteOverskrift]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[JournalArkNoteOverskrift](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Overskrift] [varchar](255) NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[JournalArkNoteOverskriftAnsaettelsessted]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[JournalArkNoteOverskriftAnsaettelsessted](
	[JournalArkNoteOverskriftID] [int] NOT NULL,
	[AnsaettelsesstedID] [int] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[JournalArkNoteStandardText]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[JournalArkNoteStandardText](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Label] [char](50) NOT NULL,
	[Text] [ntext] NULL,
 CONSTRAINT [PK_JournalNoteStandardText] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[JournalArkNoteStandardTextAnsaettelsessted]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[JournalArkNoteStandardTextAnsaettelsessted](
	[JournalArkNoteStandardTextID] [int] NOT NULL,
	[AnsaettelsesstedID] [int] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[JournalArkNoteVedrPart]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[JournalArkNoteVedrPart](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[JournalArkNoteID] [int] NOT NULL,
	[SagspartID] [int] NOT NULL,
 CONSTRAINT [PK_JournalArkNoteVedrPart] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[JournalArkVisningsFontOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[JournalArkVisningsFontOpslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[FontStoerrelse] [int] NOT NULL,
 CONSTRAINT [PK_JournalArkVisningsFontOpslag] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Kladde]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Kladde](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Beskrivelse] [nvarchar](255) NULL,
	[Emne] [nvarchar](300) NULL,
	[Created] [datetime] NULL,
	[CreatedByID] [int] NULL,
	[LastChanged] [datetime] NULL,
	[LastChangedByID] [int] NULL,
	[FileName] [nvarchar](255) NOT NULL,
	[FileExtension] [nvarchar](50) NOT NULL,
	[IsCheckedOut] [bit] NULL,
	[IsArchived] [bit] NULL,
	[CheckedOutFileName] [nvarchar](255) NULL,
	[CheckedOutFilePath] [nvarchar](255) NULL,
	[CheckedOutByID] [int] NULL,
	[CheckedOut] [datetime] NULL,
	[CheckedOutMachineName] [nvarchar](100) NULL,
	[CheckedOutMachineAddress] [nvarchar](50) NULL,
	[CheckedOutUserName] [nvarchar](50) NULL,
	[LastCheckedInByID] [int] NULL,
	[LastCheckedIn] [datetime] NULL,
	[CurrentVersion] [int] NOT NULL,
	[Navn] [nvarchar](200) NOT NULL,
	[MergeData] [ntext] NULL,
	[MergeDataFileName] [nvarchar](300) NULL,
	[KeepCheckedOut] [bit] NOT NULL,
	[MailBody] [ntext] NULL,
	[MailSubject] [nvarchar](200) NULL,
	[PrinterName] [nvarchar](200) NULL,
	[KladdeFletteStrategi] [int] NOT NULL,
	[KladdeRedigeringGenoptaget] [bit] NOT NULL,
	[DeletedState] [tinyint] NOT NULL,
	[DeletedDate] [datetime] NULL,
	[DeletedByID] [int] NULL,
	[DeletedReason] [nvarchar](100) NULL,
	[DeleteConfirmed] [datetime] NULL,
	[DeleteConfirmedByID] [int] NULL,
	[MaterialeType] [nvarchar](255) NULL,
	[IndexingStatus] [tinyint] NOT NULL,
	[Keywords] [ntext] NULL,
	[FileSize] [bigint] NULL,
	[ImporteretFraKnownEksternSystemID] [int] NULL,
	[EksternID] [nvarchar](50) NULL,
	[KladdeArt] [nvarchar](30) NULL,
 CONSTRAINT [PK_tblBreve] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[KladdePart]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[KladdePart](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[KladdeID] [int] NOT NULL,
	[PartID] [int] NOT NULL,
	[PartType] [int] NOT NULL,
	[KontaktForm] [int] NOT NULL,
	[AnvendtAdresse] [nvarchar](300) NULL,
	[SekundaerPart] [bit] NOT NULL,
	[Markeret] [bit] NOT NULL,
	[MergeData] [ntext] NULL,
	[FirmaAttentionPersonID] [int] NULL,
	[Status] [tinyint] NOT NULL,
	[StatusInfo] [nvarchar](200) NULL,
	[StatusTidspunkt] [datetime] NULL,
 CONSTRAINT [PK_KladdePart] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UNIQUE_KLADDEPART] UNIQUE NONCLUSTERED
(
	[KladdeID] ASC,
	[PartID] ASC,
	[PartType] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[KladdePartDokument]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[KladdePartDokument](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[KladdeID] [int] NOT NULL,
	[KladdePartID] [int] NULL,
	[DokumentID] [int] NOT NULL,
 CONSTRAINT [PK_KladdePartDokument] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_KladdePartDokument] UNIQUE CLUSTERED
(
	[KladdeID] ASC,
	[KladdePartID] ASC,
	[DokumentID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[KladdeRegistrering]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[KladdeRegistrering](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagID] [int] NOT NULL,
	[KladdeID] [int] NOT NULL,
	[ErBeskyttet] [bit] NOT NULL,
	[SecuritySetID] [int] NULL,
	[RegistreretAfID] [int] NOT NULL,
	[Registreret] [datetime] NOT NULL,
	[Beskrivelse] [nvarchar](255) NULL,
	[SagsPartID] [int] NULL,
	[Navn] [nvarchar](200) NOT NULL,
	[DeletedState] [tinyint] NOT NULL,
	[DeletedDate] [datetime] NULL,
	[DeletedByID] [int] NULL,
	[DeletedReason] [nvarchar](100) NULL,
	[DeleteConfirmed] [datetime] NULL,
	[DeleteConfirmedByID] [int] NULL,
 CONSTRAINT [PK_SagKladde] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_KladdeRegistrering_Sag]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_KladdeRegistrering_Sag] ON [dbo].[KladdeRegistrering]
(
	[SagID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[KnownEksterntSystem]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[KnownEksterntSystem](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[VistNavn] [nvarchar](300) NOT NULL,
	[SystemKey] [uniqueidentifier] NULL,
	[SystemXPathQuery] [nvarchar](200) NULL,
	[SagstypeXPathQuery] [nvarchar](200) NULL,
 CONSTRAINT [PK_KnownEksterntSystem] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[KnownEksterntSystemStylesheetMap]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[KnownEksterntSystemStylesheetMap](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[KnownEksternSystemID] [int] NOT NULL,
	[Notat] [nvarchar](200) NULL,
	[SagstypeVaerdi] [nvarchar](50) NULL,
	[StylesheetID] [int] NOT NULL,
 CONSTRAINT [PK_KnownEksterntSystemStylesheetMap] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[KnownFileTypeOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[KnownFileTypeOpslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Extension] [nvarchar](30) NOT NULL,
	[MimeType] [nvarchar](100) NULL,
	[OpensInBrowser] [bit] NOT NULL,
	[WatchTechnique] [tinyint] NOT NULL,
	[ChangeCheckTechnique] [tinyint] NOT NULL,
	[KanBrugesSomKladde] [bit] NOT NULL,
 CONSTRAINT [PK_KnownFileType] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_KnownFileType_Extension] UNIQUE NONCLUSTERED
(
	[Extension] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[KommuneFoer2007Opslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[KommuneFoer2007Opslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Nummer] [int] NOT NULL,
	[NytNummer] [int] NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
 CONSTRAINT [PK_KommuneFoer2007] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_KommuneFoer2007_Navn] UNIQUE NONCLUSTERED
(
	[Navn] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_KommuneFoer2007_Nummer] UNIQUE NONCLUSTERED
(
	[Nummer] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[KommuneOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[KommuneOpslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Nummer] [int] NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[RegionNummer] [int] NOT NULL,
 CONSTRAINT [PK_Kommune] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_Kommune_Nummer] UNIQUE NONCLUSTERED
(
	[Nummer] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[KontaktFormOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[KontaktFormOpslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
 CONSTRAINT [PK_KontaktForm] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Kontor]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Kontor](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Kode] [nvarchar](10) NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[Nummer] [int] NOT NULL,
 CONSTRAINT [PK_Kontor] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[LandOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[LandOpslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Landekode] [nvarchar](3) NULL,
	[Navn] [nvarchar](80) NOT NULL,
 CONSTRAINT [PK_Land] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_Land_Landekode] UNIQUE NONCLUSTERED
(
	[Landekode] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Log]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Log](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[Comments] [nvarchar](400) NULL,
	[Type] [nvarchar](50) NULL,
	[Severity] [int] NULL,
	[ProductVersion] [nvarchar](50) NULL,
	[ProductName] [nvarchar](50) NULL,
	[Logged] [datetime] NOT NULL,
	[Category] [nvarchar](100) NULL,
	[Message] [nvarchar](1024) NULL,
	[Source] [nvarchar](100) NULL,
	[SqlCommand] [ntext] NULL,
	[StackTrace] [ntext] NULL,
	[InnerException] [ntext] NULL,
	[OSUserName] [nvarchar](100) NULL,
	[OSRegionalSettings] [nvarchar](50) NULL,
	[OSMachineName] [nvarchar](100) NULL,
	[OSVersion] [nvarchar](50) NULL,
	[NetRuntimeVersion] [nvarchar](50) NULL,
	[ReviewComments] [nvarchar](255) NULL,
	[ReviewedBy] [nvarchar](50) NULL,
	[ReviewDate] [datetime] NULL,
	[ReviewIgnore] [bit] NULL,
	[IsSolved] [bit] NULL,
	[ExceptionType] [nvarchar](100) NULL,
	[RuntimeLog] [ntext] NULL,
	[Occurences] [int] NOT NULL,
	[BuildLabel] [nvarchar](50) NOT NULL,
 CONSTRAINT [PK_Log] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Lokation]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS OFF
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Lokation](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[KommuneID] [int] NOT NULL,
	[Beskrivelse] [nvarchar](500) NULL,
	[Oprettet] [datetime] NOT NULL,
	[VejNavn] [nvarchar](100) NOT NULL,
	[HusNummer] [nvarchar](50) NOT NULL,
	[PostNummerID] [int] NOT NULL,
	[ExternalSourceLastUpdate] [datetime] NULL,
	[ExternalSourceID] [nvarchar](50) NULL,
	[ExternalSourceName] [nvarchar](50) NULL,
	[Beliggenhed] [nvarchar](500) NULL,
	[Historisk] [bit] NOT NULL,
	[LokationIdentity] [uniqueidentifier] NOT NULL,
 CONSTRAINT [PK_Lokation] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[LokationIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Mail]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Mail](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[NativeID] [nvarchar](500) NULL,
	[FromDisplayName] [nvarchar](255) NULL,
	[FromEmailAddress] [nvarchar](200) NULL,
	[Subject] [nvarchar](255) NULL,
	[SentDate] [datetime] NULL,
	[ReceivedDate] [datetime] NULL,
	[IsSentItem] [bit] NOT NULL,
	[AccountID] [nvarchar](255) NULL,
	[AccountDisplayName] [nvarchar](255) NULL,
	[ParentFolderID] [nvarchar](255) NULL,
	[ParentFolderDisplayName] [nvarchar](255) NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
	[UniqueID] [nvarchar](100) NULL,
	[MailType] [int] NOT NULL,
	[DigitalPostMaterialeType] [nvarchar](50) NULL,
	[DigitalPostSenderPostkasse] [nvarchar](50) NULL,
 CONSTRAINT [PK_tblMail] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[MailRecipient]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[MailRecipient](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[MailID] [int] NOT NULL,
	[Navn] [nvarchar](200) NULL,
	[Adresse] [nvarchar](300) NULL,
	[MailRecipientType] [int] NULL,
	[CPR] [nvarchar](20) NULL,
	[CVR] [nvarchar](20) NULL,
	[Pnummer] [nvarchar](30) NULL,
	[ContextSagID] [int] NOT NULL,
 CONSTRAINT [PK_MailRecipient] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[MapDelforloeb]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[MapDelforloeb](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[MapSagID] [int] NOT NULL,
	[Kode] [nvarchar](50) NOT NULL,
	[Titel] [nvarchar](200) NULL,
 CONSTRAINT [PK_MapDelforloeb] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[MapDelforloebDokument]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[MapDelforloebDokument](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[MapDelforloebID] [int] NOT NULL,
	[Kode] [nvarchar](50) NOT NULL,
	[Titel] [nvarchar](200) NULL,
 CONSTRAINT [PK_MapDelforloebDokument] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[MapNemJournaliseringSagSkabelon]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[MapNemJournaliseringSagSkabelon](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Blanket] [nvarchar](max) NULL,
	[KLE] [nvarchar](20) NULL,
	[SagSkabelonID] [int] NULL,
	[Aktiv] [bit] NOT NULL,
 CONSTRAINT [PK_MapNemJournaliseringSagSkabelon] PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[MapSag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[MapSag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Kode] [nvarchar](50) NOT NULL,
	[Titel] [nvarchar](200) NULL,
	[EmneplanID] [int] NOT NULL,
	[EmneplanNummerID] [int] NOT NULL,
	[FacetID] [int] NULL,
	[MaxSagsnummerLaengde] [int] NOT NULL,
	[SagsbehandlerID] [int] NULL,
	[SaetSagspartSomPrimaer] [bit] NOT NULL,
 CONSTRAINT [PK_MapSag] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Matrikel]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Matrikel](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Beskrivelse] [nvarchar](500) NULL,
	[Oprettet] [datetime] NOT NULL,
	[MatrikelNummer] [nvarchar](15) NOT NULL,
	[KommuneID] [int] NOT NULL,
	[Ejerlav] [nvarchar](50) NULL,
	[EjerlavKode] [int] NULL,
	[ExternalSourceLastUpdate] [datetime] NULL,
	[ExternalSourceID] [nvarchar](50) NULL,
	[ExternalSourceName] [nvarchar](50) NULL,
	[Beliggenhed] [nvarchar](500) NULL,
	[LandsEjerlav] [nvarchar](50) NULL,
	[LandsEjerlavKode] [int] NULL,
	[Historisk] [bit] NOT NULL,
	[ArtID] [int] NOT NULL,
	[Parcelnummer] [nvarchar](10) NULL,
	[Ejerlejlighedsnummer] [nvarchar](50) NULL,
	[BeliggenhedAdresseID] [int] NULL,
	[EjendomsNummer] [nvarchar](20) NULL,
	[MatrikelIdentity] [uniqueidentifier] NOT NULL,
	[BFENummer] [bigint] NOT NULL,
 CONSTRAINT [PK_Matrikel] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[MatrikelIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[MatrikelArt]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[MatrikelArt](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Kode] [int] NOT NULL,
	[Navn] [nvarchar](200) NULL,
 CONSTRAINT [PK_MatrikelArt_ID] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[MatrikelEjendom]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[MatrikelEjendom](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[MatrikelID] [int] NOT NULL,
	[EjendomID] [int] NOT NULL,
 CONSTRAINT [PK_MatrikelEjendom] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Memo]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Memo](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Message] [nvarchar](max) NOT NULL,
	[Scheme] [nvarchar](50) NOT NULL,
	[Version] [nvarchar](50) NOT NULL,
	[DokumentRegistreringID] [int] NOT NULL,
	[Modtaget] [bit] NOT NULL,
 CONSTRAINT [PK_Memo] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[MergeData]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[MergeData](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[PartID] [int] NOT NULL,
	[PartType] [int] NOT NULL,
	[MainDokumentDataInfoID] [int] NOT NULL,
	[SubDokumentDataInfoID] [int] NOT NULL,
	[MergeDataContent] [nvarchar](max) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Moede]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Moede](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[MoedeIdentity] [uniqueidentifier] NOT NULL,
	[Dato] [datetime] NOT NULL,
	[Sted] [nvarchar](100) NULL,
	[Aktiv] [bit] NOT NULL,
	[PunktnummereringStart] [int] NOT NULL,
	[FortloebendePunktnummerering] [bit] NOT NULL,
	[Afsluttet] [bit] NOT NULL,
	[FoerstAfsluttet] [datetime] NULL,
	[Created] [datetime] NOT NULL,
	[CreatedBy] [int] NOT NULL,
	[LastChanged] [datetime] NOT NULL,
	[LastChangedBy] [int] NOT NULL,
	[UdvalgID] [int] NULL,
	[ErSkabelon] [bit] NOT NULL,
	[SkabelonNavn] [nvarchar](200) NULL,
	[Klarmeldingsfrist] [datetime] NULL,
	[Sluttidspunkt] [datetime] NULL,
 CONSTRAINT [PK__Moede__6CB9C3E7] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[MoedeIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[MostRecentInfo]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[MostRecentInfo](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Text] [nvarchar](450) NOT NULL,
	[GroupName] [nvarchar](50) NOT NULL,
	[ItemID] [int] NOT NULL,
	[Created] [datetime] NOT NULL,
	[OwnerID] [int] NOT NULL,
	[ClassName] [nvarchar](200) NULL,
 CONSTRAINT [PK_MostRecentInfo] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_MostRecentInfo] UNIQUE NONCLUSTERED
(
	[OwnerID] ASC,
	[GroupName] ASC,
	[ItemID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Nyhed]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Nyhed](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](300) NOT NULL,
	[OprettetDato] [datetime] NOT NULL,
	[OprettetAfID] [int] NOT NULL,
	[Indhold] [ntext] NOT NULL,
	[ErUdgaaet] [bit] NOT NULL,
 CONSTRAINT [PK_Nyhed] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[PartTypeOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PartTypeOpslag](
	[ID] [int] NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
 CONSTRAINT [PK_PartTypeOpslag] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Person]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Person](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Initialer] [nvarchar](10) NULL,
	[Titel] [nvarchar](50) NULL,
	[Uddannelse] [nvarchar](50) NULL,
	[Stilling] [nvarchar](50) NULL,
	[Note] [nvarchar](200) NULL,
	[CprNummer] [varchar](11) NULL,
	[Koen] [tinyint] NOT NULL,
	[AdresseID] [int] NULL,
	[ExternalSourceLastUpdate] [datetime] NULL,
	[ExternalSourceID] [nvarchar](50) NULL,
	[ExternalSourceName] [nvarchar](50) NULL,
	[Navn] [nvarchar](300) NULL,
	[FoedeDato] [datetime] NULL,
	[Ansaettelsessted] [nvarchar](100) NULL,
	[KontaktForm] [int] NOT NULL,
	[CivilstandID] [int] NULL,
	[AegtefaelleCPR] [varchar](11) NULL,
	[MorCPR] [varchar](11) NULL,
	[FarCPR] [varchar](11) NULL,
	[KommuneID] [int] NULL,
	[PartOprydningsKeyCheckSum] [int] NULL,
	[TilmeldtDigitalPost] [bit] NOT NULL,
	[PersonIdentity] [uniqueidentifier] NOT NULL,
 CONSTRAINT [PK_Person] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[PersonIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[PessimisticLockInfo]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PessimisticLockInfo](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[TargetID] [int] NOT NULL,
	[TargetName] [nvarchar](100) NOT NULL,
	[LockedByID] [int] NOT NULL,
	[Locked] [datetime] NOT NULL,
	[LockType] [int] NOT NULL,
	[UnLockedByID] [int] NULL,
	[UnLocked] [datetime] NULL,
 CONSTRAINT [PK_PessimisticLockInfo] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_PessimisticLockInfo_Target]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE CLUSTERED INDEX [IX_PessimisticLockInfo_Target] ON [dbo].[PessimisticLockInfo]
(
	[TargetID] ASC,
	[TargetName] ASC,
	[LockedByID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[PluginConfigurationSecuritySet]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PluginConfigurationSecuritySet](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[TrustedAssemblyID] [int] NOT NULL,
	[SecuritySetID] [int] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Postnummer]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Postnummer](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Nummer] [int] NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
 CONSTRAINT [PK_Postnummer] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_Postnummer] UNIQUE NONCLUSTERED
(
	[Nummer] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[PostnummerKommune]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PostnummerKommune](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[PostnummerID] [int] NOT NULL,
	[KommuneID] [int] NOT NULL,
 CONSTRAINT [PK_PostnummerKommune] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_PostnummerKommune]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_PostnummerKommune] ON [dbo].[PostnummerKommune]
(
	[KommuneID] ASC,
	[PostnummerID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ProcessStatusOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ProcessStatusOpslag](
	[ID] [int] NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
 CONSTRAINT [PK_ProcessStatus] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[PropertyBagItem]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PropertyBagItem](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BagID] [uniqueidentifier] NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[Vaerdi] [ntext] NULL,
	[OwnerID] [int] NOT NULL,
 CONSTRAINT [PK_PropertyBagValue] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Index [IX_PropertyBagItem]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_PropertyBagItem] ON [dbo].[PropertyBagItem]
(
	[BagID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Publisering]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Publisering](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[Beskrivelse] [nvarchar](300) NULL,
	[Oprettet] [datetime] NOT NULL,
	[OprettetAfID] [int] NOT NULL,
	[Publiseres] [datetime] NOT NULL,
	[ErPubliseret] [bit] NOT NULL,
	[ErPrivatPublisering] [bit] NOT NULL,
	[Publiseret] [datetime] NULL,
	[SidsteStatement] [ntext] NULL,
 CONSTRAINT [PK_Publicering] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_Publicering_Navn_Unique] UNIQUE NONCLUSTERED
(
	[Navn] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[PubliseringDokument]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PubliseringDokument](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[PubliseringID] [int] NOT NULL,
	[DokumentRegistreringID] [int] NOT NULL,
	[Navn] [nvarchar](200) NOT NULL,
	[Beskrivelse] [nvarchar](300) NULL,
	[ErPubliseretFoer] [bit] NOT NULL,
 CONSTRAINT [PK_PubliceringDokument] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[PubliseringIndstillinger]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PubliseringIndstillinger](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
 CONSTRAINT [PK_PubliseringIndstillinger] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[PubliseringPlan]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PubliseringPlan](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NULL,
	[AgentIdentity] [uniqueidentifier] NOT NULL,
	[Aktiv] [bit] NOT NULL,
	[PubliseringIndstillingerID] [int] NOT NULL,
	[PubliseringNavn] [nvarchar](200) NULL,
	[Opfoersel] [tinyint] NULL,
	[SidstePubliseringID] [int] NULL,
	[SidsteKoersel] [datetime] NULL,
	[Statement] [ntext] NULL,
 CONSTRAINT [PK_PubliseringPlan] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[PubliseringTarget]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PubliseringTarget](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[PubliseringIndstillingerID] [int] NOT NULL,
	[OutputPath] [nvarchar](300) NULL,
	[OutputFileNameWithoutExtension] [nvarchar](100) NULL,
	[XslStylesheetID] [int] NOT NULL,
	[CssStylesheetID] [int] NOT NULL,
	[FileOutputBehavior] [tinyint] NOT NULL,
	[FolderNameBehavior] [tinyint] NOT NULL,
	[FolderNamePattern] [nvarchar](200) NULL,
	[FileOutputRule] [tinyint] NOT NULL,
	[PrepareRule] [tinyint] NOT NULL,
 CONSTRAINT [PK_PubliseringTarget] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[QueryProfil]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[QueryProfil](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[CreatedByID] [int] NULL,
	[Query] [ntext] NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[LastChanged] [datetime] NULL,
	[Context] [nvarchar](100) NULL,
 CONSTRAINT [PK_QueryProfil] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[QueueCommand]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[QueueCommand](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Oprettet] [datetime] NOT NULL,
	[BrugerID] [int] NOT NULL,
	[Status] [int] NOT NULL,
	[Navn] [nvarchar](200) NULL,
	[XML] [ntext] NULL,
	[Error] [ntext] NULL,
	[OriginalLocation] [nvarchar](300) NULL,
	[Behavior] [int] NOT NULL,
	[GUID] [uniqueidentifier] NULL,
 CONSTRAINT [PK_Que] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Index [IX_QueueCommand_]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_QueueCommand_] ON [dbo].[QueueCommand]
(
	[BrugerID] ASC,
	[Status] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[QueueCommandFile]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[QueueCommandFile](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[QueueCommandID] [int] NOT NULL,
	[Data] [image] NULL,
	[Filename] [nvarchar](300) NULL,
	[OriginalLocation] [nvarchar](400) NULL,
	[Length] [bigint] NOT NULL,
	[Sortering] [int] NOT NULL,
	[MetaName] [nvarchar](300) NULL,
 CONSTRAINT [PK_QueBlob] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[RegionOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RegionOpslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[Nummer] [int] NOT NULL,
 CONSTRAINT [PK_Region] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_Region_Nummer] UNIQUE NONCLUSTERED
(
	[Nummer] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[RelateretSag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RelateretSag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[RelateretFraSagID] [int] NOT NULL,
	[RelateretSagID] [int] NOT NULL,
 CONSTRAINT [PK_JournalUnderjournaler] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[RequestLog]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RequestLog](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Data] [nvarchar](max) NULL,
	[Method] [nvarchar](10) NULL,
	[BrugerID] [int] NULL,
	[URL] [nvarchar](400) NULL,
	[URLParameters] [nvarchar](400) NULL,
	[ResponseCode] [int] NULL,
	[DurationInMilliSeconds] [int] NULL,
	[Logged] [datetime2](7) NOT NULL,
	[Version] [nvarchar](50) NULL,
	[RequestHashCode] [int] NULL,
	[ClientIP] [nvarchar](100) NULL,
	[ClientName] [nvarchar](100) NULL,
	[ClientSession] [uniqueidentifier] NULL,
	[CorrelationId] [uniqueidentifier] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Ressource]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Ressource](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Identitet] [uniqueidentifier] NOT NULL,
	[Navn] [nvarchar](200) NULL,
	[Beskrivelse] [nvarchar](400) NULL,
	[Filename] [nvarchar](400) NULL,
	[MimeType] [nvarchar](200) NULL,
	[Data] [image] NULL,
	[DataSize] [bigint] NULL,
	[Kategori] [tinyint] NOT NULL,
 CONSTRAINT [PK_Ressource] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[RolleOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RolleOpslag](
	[ID] [bigint] NOT NULL,
	[Navn] [nvarchar](255) NOT NULL,
	[IsBuiltin] [bit] NOT NULL,
 CONSTRAINT [PK__DagsordenRolle__6700EA91] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[RolleTildeling]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RolleTildeling](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[UdvalgID] [int] NULL,
	[BrugerID] [int] NULL,
	[Roller] [bigint] NOT NULL,
	[SikkerhedsgruppeID] [int] NULL,
 CONSTRAINT [PK__RolleIUdvalg__6EA20C59] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Sag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Sag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagIdentity] [uniqueidentifier] NOT NULL,
	[Nummer] [nvarchar](50) NOT NULL,
	[Titel] [nvarchar](450) NOT NULL,
	[ErBeskyttet] [bit] NOT NULL,
	[Kommentar] [nvarchar](4000) NULL,
	[BevaringID] [int] NULL,
	[KommuneID] [int] NULL,
	[BehandlerID] [int] NOT NULL,
	[SagsStatusID] [int] NOT NULL,
	[CreatedByID] [int] NOT NULL,
	[Created] [datetime] NULL,
	[LastChangedByID] [int] NULL,
	[LastChanged] [datetime] NULL,
	[YderligereMaterialeFindes] [bit] NULL,
	[YderligereMaterialeBeskrivelse] [nvarchar](255) NULL,
	[AmtID] [int] NULL,
	[ErBesluttet] [bit] NULL,
	[Besluttet] [datetime] NULL,
	[BeslutningsTypeID] [int] NULL,
	[BeslutningNotat] [nvarchar](200) NULL,
	[BeslutningDeadline] [datetime] NULL,
	[BeslutningHarDeadline] [bit] NULL,
	[ErSamlesag] [bit] NULL,
	[FagomraadeID] [int] NULL,
	[SecuritySetID] [int] NULL,
	[SagsNummerID] [int] NULL,
	[LastStatusChange] [datetime] NULL,
	[LastStatusChangeComments] [nvarchar](400) NULL,
	[Kassationsdato] [datetime] NULL,
	[SagsPartID] [int] NULL,
	[RegionID] [int] NULL,
	[KommuneFoer2007ID] [int] NULL,
	[Opstaaet] [datetime] NULL,
	[AnsaettelsesstedID] [int] NOT NULL,
	[ArkivAfklaringStatusID] [int] NOT NULL,
	[ArkivNote] [ntext] NULL,
	[StyringsreolHyldeID] [int] NULL,
	[SkabelonID] [int] NULL,
	[Sletningsdato] [datetime] NULL,
 CONSTRAINT [PK_Sag] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagEksternIdentitet]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagEksternIdentitet](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagID] [int] NOT NULL,
	[Oprettet] [datetime] NOT NULL,
	[EksternSystemID] [int] NOT NULL,
	[EksternIdentitet] [nvarchar](300) NOT NULL,
	[Status] [tinyint] NOT NULL,
 CONSTRAINT [PK_SagEksternIdentitet] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagEmneOrd]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagEmneOrd](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagID] [int] NOT NULL,
	[EmneOrdID] [int] NOT NULL,
 CONSTRAINT [PK_SagEmneOrd] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagerOverfort]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagerOverfort](
	[id] [int] NOT NULL,
	[Nummer] [nvarchar](50) NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagerTilFilarkiv]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagerTilFilarkiv](
	[id] [int] NOT NULL,
	[Nummer] [nvarchar](50) NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagHistorikStatus]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagHistorikStatus](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagID] [int] NOT NULL,
	[RegistreretAfID] [int] NOT NULL,
	[FraSagsStatusID] [int] NULL,
	[TilSagsStatusID] [int] NOT NULL,
	[Kommentar] [nvarchar](255) NULL,
	[Note] [text] NULL,
	[Tidspunkt] [datetime] NOT NULL,
	[VarighedsMinuter] [bigint] NULL,
 CONSTRAINT [PK_SagHistorikStatus] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagHistorikStyringsreolStatus]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagHistorikStyringsreolStatus](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[FraHyldeID] [int] NULL,
	[TilHyldeID] [int] NULL,
	[BrugerID] [int] NOT NULL,
	[Dato] [datetime] NOT NULL,
	[SagID] [int] NOT NULL,
 CONSTRAINT [PK_SagHistorikReolStatus] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagMetaData]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagMetaData](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagID] [int] NOT NULL,
	[KeyName] [nvarchar](50) NOT NULL,
	[Value] [nvarchar](400) NULL,
 CONSTRAINT [PK_SagMetaData] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_SagMetaData]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_SagMetaData] ON [dbo].[SagMetaData]
(
	[SagID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagSagsType]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagSagsType](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[SagId] [int] NOT NULL,
	[SagsTypeId] [int] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [UQ_Sag_SagsType] UNIQUE NONCLUSTERED
(
	[SagId] ASC,
	[SagsTypeId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagsFelt]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagsFelt](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[Noegle] [nvarchar](50) NOT NULL,
PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[Noegle] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagsfeltIndhold]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagsfeltIndhold](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagID] [int] NOT NULL,
	[SagsfeltID] [int] NOT NULL,
	[Vaerdi] [nvarchar](1024) NOT NULL,
 CONSTRAINT [PK_SagsfeltIndhold_Id] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [AK_SagsfeltIndhold_SagID_SagsfeltID] UNIQUE NONCLUSTERED
(
	[SagsfeltID] ASC,
	[SagID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagsFeltSagSkabelon]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagsFeltSagSkabelon](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[SagsFeltId] [int] NOT NULL,
	[SagSkabelonId] [int] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [AK_SagsFeltSagSkabelon_SagsFeltId_SagSkabelonId] UNIQUE NONCLUSTERED
(
	[SagsFeltId] ASC,
	[SagSkabelonId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagsHenvisning]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagsHenvisning](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[HenvisningFraID] [int] NOT NULL,
	[HenvisningTilID] [int] NOT NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
 CONSTRAINT [PK_JournalHenvisning] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagSkabelon]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagSkabelon](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](200) NOT NULL,
	[Beskrivelse] [ntext] NULL,
	[XmlData] [text] NOT NULL,
	[XmlSchema] [text] NOT NULL,
	[SchemaVersion] [nvarchar](50) NOT NULL,
	[SagSkabelonKategoriID] [int] NULL,
	[SagsTitel] [nvarchar](100) NULL,
	[ErBeskyttet] [bit] NOT NULL,
	[ForudFyldSagsbehandler] [bit] NOT NULL,
	[SecuritySetID] [int] NULL,
	[EmnePlanNummerID] [int] NULL,
	[FacetID] [int] NULL,
	[BrugerID] [int] NULL,
	[AnsaettelsesstedID] [int] NULL,
	[FagomraadeID] [int] NULL,
	[StyringsreolHyldeID] [int] NULL,
	[AnvendSikkerhedFraAnsaettelssted] [bit] NOT NULL,
	[Hierakimedlem] [int] NULL,
	[PartForlangAltid] [bit] NOT NULL,
	[PartForlangAltidPrimaer] [bit] NOT NULL,
	[PartAnvendIkke] [bit] NOT NULL,
	[GenstandForlangAltid] [bit] NOT NULL,
	[Aktiv] [bit] NOT NULL,
	[SagSkabelonIdentity] [uniqueidentifier] NOT NULL,
	[SagsTypeId] [int] NOT NULL,
	[SagsTitelKanAendresFoerOprettelse] [bit] NOT NULL,
	[SagsTitelKanAendresEfterOprettelse] [bit] NOT NULL,
	[AnsaettelsesstedKanAendresFoerOprettelse] [bit] NOT NULL,
	[AnsaettelsesstedKanAendresEfterOprettelse] [bit] NOT NULL,
	[StyringsreolKanAendresFoerOprettelse] [bit] NOT NULL,
	[StyringsreolKanAendresEfterOprettelse] [bit] NOT NULL,
	[DelforloebKanTilfoejesFoerOprettelse] [bit] NOT NULL,
	[DelforloebKanTilfoejesEfterOprettelse] [bit] NOT NULL,
	[DelforloebKanFjernesFoerOprettelse] [bit] NOT NULL,
	[DelforloebKanFjernesEfterOprettelse] [bit] NOT NULL,
	[ErBeskyttetKanAendresFoerOprettelse] [bit] NOT NULL,
	[ErBeskyttetKanAendresEfterOprettelse] [bit] NOT NULL,
	[AdgangslisteKanAendresFoerOprettelse] [bit] NOT NULL,
	[AdgangslisteKanAendresEfterOprettelse] [bit] NOT NULL,
	[EmneplanNummerOgFacetKanAendresFoerOprettelse] [bit] NOT NULL,
	[EmneplanNummerOgFacetKanAendresEfterOprettelse] [bit] NOT NULL,
 CONSTRAINT [PK_SagSkabelon] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[SagSkabelonIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagSkabelonEmneord]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagSkabelonEmneord](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagSkabelonID] [int] NOT NULL,
	[EmneordID] [int] NOT NULL,
 CONSTRAINT [CK_SagSkabelonEmneord_Unique] UNIQUE NONCLUSTERED
(
	[SagSkabelonID] ASC,
	[EmneordID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagSkabelonErindringSkabelon]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagSkabelonErindringSkabelon](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagSkabelonID] [int] NOT NULL,
	[ErindringSkabelonID] [int] NOT NULL,
	[Trin] [int] NULL,
 CONSTRAINT [PK_SagSkabelonErindringSkabelon] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagSkabelonKategori]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagSkabelonKategori](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NULL,
 CONSTRAINT [PK_SagSkabelonKategori] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagSkabelonPart]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagSkabelonPart](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagSkabelonID] [int] NOT NULL,
	[FirmaID] [int] NULL,
	[PersonID] [int] NULL,
	[PartTypeID] [int] NOT NULL,
	[Primaer] [bit] NOT NULL,
 CONSTRAINT [CK_SagSkabelonPart_TilladIkkeSammePartToGange] UNIQUE NONCLUSTERED
(
	[FirmaID] ASC,
	[SagSkabelonID] ASC,
	[PersonID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagSkabelonTilknyttetSagSkabelon]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagSkabelonTilknyttetSagSkabelon](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagSkabelonID] [int] NOT NULL,
	[SagSkabelonTilknyttetSagSkabelonID] [int] NOT NULL,
 CONSTRAINT [PK_SagSkabelonTilknyttetSagSkabelon] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagSkabelonTitler]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagSkabelonTitler](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Titel] [varchar](1000) NOT NULL,
	[SagSkabelonID] [int] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagsNummer]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagsNummer](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[EmnePlanID] [int] NOT NULL,
	[EmnePlanNummerID] [int] NOT NULL,
	[FacetID] [int] NULL,
	[SekvensNummer] [int] NOT NULL,
	[Aarstal] [int] NOT NULL,
 CONSTRAINT [PK_SagsNummer] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagsPart]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagsPart](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagID] [int] NOT NULL,
	[PartType] [int] NOT NULL,
	[PartID] [int] NOT NULL,
	[SagsPartRolleID] [int] NULL,
	[OprindeligAdresseID] [int] NULL,
	[Oprettet] [datetime] NOT NULL,
 CONSTRAINT [PK_SagsPart] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_SagsPart_Sag]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_SagsPart_Sag] ON [dbo].[SagsPart]
(
	[SagID] ASC,
	[PartID] ASC,
	[SagsPartRolleID] ASC,
	[OprindeligAdresseID] ASC,
	[Oprettet] ASC,
	[PartType] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagsPartRolle]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagsPartRolle](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[Beskrivelse] [nvarchar](500) NOT NULL,
 CONSTRAINT [PK_Rolle] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagsStatus]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagsStatus](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[Orden] [int] NOT NULL,
	[SagsTilstand] [int] NOT NULL,
	[RequireComments] [bit] NOT NULL,
	[IsDeleted] [bit] NOT NULL,
	[SagsForklaede] [int] NOT NULL,
 CONSTRAINT [PK_SagsStgatus] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagsTilstandOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagsTilstandOpslag](
	[ID] [int] NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
 CONSTRAINT [PK_SagsTilstand] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagsType]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagsType](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
 CONSTRAINT [PK_SagsType] PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [AK_SagsType_Navn] UNIQUE NONCLUSTERED
(
	[Navn] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SagsVisit]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SagsVisit](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagID] [int] NOT NULL,
	[BrugerID] [int] NOT NULL,
	[Tidspunkt] [datetime] NOT NULL,
 CONSTRAINT [PK_tblJournalVisit] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SearchLog]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SearchLog](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SearchGuid] [uniqueidentifier] NOT NULL,
	[SearchTab] [nvarchar](100) NULL,
	[SearchCriteria] [nvarchar](100) NULL,
	[LogDate] [datetime] NOT NULL,
 CONSTRAINT [PK_SearchLog] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SecuritySet]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SecuritySet](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [varchar](1) NULL,
 CONSTRAINT [PK_SecuritySet] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SecuritySetBrugere]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SecuritySetBrugere](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SecuritySetID] [int] NOT NULL,
	[BrugerID] [int] NOT NULL,
	[ErPermanent] [bit] NOT NULL,
 CONSTRAINT [PK_SecuritySetBrugere] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_SecuritySetBrugere_SecuritySetOgBruger]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE CLUSTERED INDEX [IX_SecuritySetBrugere_SecuritySetOgBruger] ON [dbo].[SecuritySetBrugere]
(
	[SecuritySetID] ASC,
	[BrugerID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SecuritySetSikkerhedsgrupper]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SecuritySetSikkerhedsgrupper](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SecuritySetID] [int] NOT NULL,
	[SikkerhedsgruppeID] [int] NOT NULL,
 CONSTRAINT [PK_SecuritySetOrganisationsEnheder] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_SecuritySetOrganisationsEnheder]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE CLUSTERED INDEX [IX_SecuritySetOrganisationsEnheder] ON [dbo].[SecuritySetSikkerhedsgrupper]
(
	[SecuritySetID] ASC,
	[SikkerhedsgruppeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Sekretariat]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Sekretariat](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](255) NOT NULL,
	[Stedbetegnelse] [nvarchar](255) NULL,
	[Institutionsnavn] [nvarchar](255) NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
 CONSTRAINT [PK__Sekretariat__6518A21F] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SendBOMBesvarelseBestilling]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SendBOMBesvarelseBestilling](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[BesvarelseID] [int] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SikkerhedsbeslutningOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SikkerhedsbeslutningOpslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Class] [nvarchar](200) NOT NULL,
	[Beskrivelse] [nvarchar](250) NULL,
	[Verbum] [nvarchar](100) NULL,
	[TildelteRoller] [bigint] NOT NULL,
	[BypassRoller] [bigint] NOT NULL,
	[Type] [int] NULL,
	[Krav] [ntext] NULL,
	[ErUdvalgsspecifik] [bit] NOT NULL,
 CONSTRAINT [PK_Sikkerhedsbeslutning] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Sikkerhedsgruppe]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Sikkerhedsgruppe](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[HierakiMedlemID] [int] NOT NULL,
	[EksternID] [nvarchar](50) NULL,
	[ObjectSid] [nvarchar](50) NULL,
 CONSTRAINT [PK_tblOrganisationsEnhed] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 90) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_Sikkerhedsgruppe]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_Sikkerhedsgruppe] ON [dbo].[Sikkerhedsgruppe]
(
	[HierakiMedlemID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SikkerhedsgruppeBrugere]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SikkerhedsgruppeBrugere](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[SikkerhedsgruppeID] [int] NOT NULL,
 CONSTRAINT [PK_BrugerOrganisationsenhed] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_BrugerOrganisationsEnheder_Unique] UNIQUE NONCLUSTERED
(
	[BrugerID] ASC,
	[SikkerhedsgruppeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_BrugerOrganisationsenhed_Bruger]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_BrugerOrganisationsenhed_Bruger] ON [dbo].[SikkerhedsgruppeBrugere]
(
	[BrugerID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Skabelon]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Skabelon](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](255) NOT NULL,
	[Beskrivelse] [nvarchar](255) NULL,
	[Redigeret] [datetime] NULL,
	[RedigeretAfID] [int] NULL,
	[GrundSkabelonID] [int] NULL,
	[VisTekstblokvaelger] [bit] NOT NULL,
 CONSTRAINT [PK_tblSkabelon] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SkabelonGrundSkabelon]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SkabelonGrundSkabelon](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[FilNavn] [nvarchar](255) NULL,
	[IndhentetFraFil] [nvarchar](255) NULL,
	[SkabelonData] [image] NULL,
 CONSTRAINT [PK_tblWordSkabelon] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 90) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SkabelonKladde]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SkabelonKladde](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SkabelonID] [int] NOT NULL,
	[KladdeID] [int] NOT NULL,
	[SkabelonGrundskabelonID] [int] NOT NULL,
 CONSTRAINT [PK_SkabelonKladde] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_SkabelonKladde_Unique] UNIQUE NONCLUSTERED
(
	[SkabelonID] ASC,
	[KladdeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SkabelonTekstblok]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SkabelonTekstblok](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](255) NOT NULL,
	[TekstRtf] [ntext] NOT NULL,
	[IsCheckedOut] [bit] NULL,
	[CheckOutpath] [nvarchar](255) NULL,
	[BrugerID] [int] NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
	[IsDefault] [bit] NULL,
 CONSTRAINT [PK_tblTekstBlok] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SkabelonTrin]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SkabelonTrin](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SkabelonID] [int] NOT NULL,
	[SkabelonTekstBlokID] [int] NOT NULL,
	[Trin] [int] NOT NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
 CONSTRAINT [PK_SkabelonTrin] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SkabelonType]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SkabelonType](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](255) NOT NULL,
	[Beskrivelse] [nvarchar](200) NULL,
	[SkabelonTypeGruppeID] [int] NOT NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
	[GrundSkabelonID] [int] NULL,
 CONSTRAINT [PK_tblSkabelontype] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 90) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_SkabelonType]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_SkabelonType] ON [dbo].[SkabelonType]
(
	[SkabelonTypeGruppeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SkabelonTypeGruppe]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SkabelonTypeGruppe](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](255) NOT NULL,
	[Beskrivelse] [nvarchar](200) NULL,
	[OrgPK_ID] [int] NULL,
	[IsImportedField] [int] NULL,
 CONSTRAINT [PK_tblSkabelontypeGruppe] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 90) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SkabelonTypeSkabelon]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SkabelonTypeSkabelon](
	[SkabelonID] [int] NOT NULL,
	[SkabelonTypeID] [int] NOT NULL,
	[ID] [int] IDENTITY(1,1) NOT NULL,
 CONSTRAINT [PK_SkabelontypeSkabelon] PRIMARY KEY NONCLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 90) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_SkabelonTypeSkabelon]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_SkabelonTypeSkabelon] ON [dbo].[SkabelonTypeSkabelon]
(
	[SkabelonID] ASC,
	[SkabelonTypeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SlettetEntitet]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SlettetEntitet](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[EntitetID] [int] NOT NULL,
	[EntitetIdentity] [uniqueidentifier] NOT NULL,
	[EntitetType] [int] NOT NULL,
	[SletTidspunkt] [datetime2](7) NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Index [IX_SlettetEntitet_SletTidspunkt]    Script Date: 27-05-2024 09:13:19 ******/
CREATE CLUSTERED INDEX [IX_SlettetEntitet_SletTidspunkt] ON [dbo].[SlettetEntitet]
(
	[SletTidspunkt] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Stedfaestelse]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Stedfaestelse](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Noegle] [nvarchar](50) NOT NULL,
	[StedfaestetAfID] [int] NOT NULL,
	[SystemId] [nvarchar](50) NOT NULL,
	[Oprettet] [datetime] NOT NULL,
	[StedfaestetType] [int] NOT NULL,
	[StedfaestetTypeId] [int] NOT NULL,
	[Status] [int] NOT NULL,
	[GeometriID] [int] NULL,
	[SagID] [int] NOT NULL,
	[DokumentRegistreringID] [int] NULL,
	[OprettetAutomatisk] [bit] NOT NULL,
	[Redigeret] [datetime] NULL,
 CONSTRAINT [PK_Stedfaestelse] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Stylesheet]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Stylesheet](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[Beskrivelse] [nvarchar](200) NULL,
	[Data] [ntext] NULL,
	[StylesheetTypeID] [int] NOT NULL,
	[Gruppering] [int] NOT NULL,
 CONSTRAINT [PK_Stylesheets] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[StylesheetTypeOpslag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[StylesheetTypeOpslag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[FileExtension] [nvarchar](10) NOT NULL,
 CONSTRAINT [PK_StylesheetTypeOpslag] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_StylesheetTypeOpslag] UNIQUE NONCLUSTERED
(
	[Navn] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Styringsreol]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Styringsreol](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [varchar](200) NOT NULL,
	[AnsaettelsesstedID] [int] NOT NULL,
	[FjernFraSoegReolEfterAntalDage] [int] NOT NULL,
	[EksterntMapped] [bit] NOT NULL,
	[ReadOnly] [bit] NOT NULL,
	[GUID] [uniqueidentifier] NULL,
 CONSTRAINT [PK_Styringsreol] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[StyringsreolHistorik]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[StyringsreolHistorik](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Tidspunkt] [datetime] NOT NULL,
	[BrugerID] [int] NOT NULL,
	[AnsaettelsesstedID] [int] NOT NULL,
	[ReolID] [int] NOT NULL,
	[ReolNavn] [nvarchar](200) NOT NULL,
	[HyldeID] [int] NOT NULL,
	[HyldeNavn] [nvarchar](200) NOT NULL,
	[HyldeSagsstatusID] [int] NOT NULL,
	[HyldeNormtidstype] [int] NOT NULL,
	[FagID] [int] NOT NULL,
	[FagNormtidDage] [int] NULL,
	[FagNormtidDato] [datetime] NULL,
 CONSTRAINT [PK_StyringsreolHistorik] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[StyringsreolHylde]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[StyringsreolHylde](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](200) NOT NULL,
	[SagsstatusID] [int] NOT NULL,
	[StyringsreolID] [int] NOT NULL,
	[Normtidstype] [int] NOT NULL,
	[SorteringsIndex] [int] NULL,
	[Skjult] [bit] NOT NULL,
 CONSTRAINT [PK_StyringsreolHylde] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[StyringsreolHyldeErindringSkabelon]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[StyringsreolHyldeErindringSkabelon](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[StyringsreolHyldeID] [int] NOT NULL,
	[ErindringSkabelonID] [int] NOT NULL,
 CONSTRAINT [pk_StyringsreolHyldeErindringSkabelon] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[StyringsreolHyldeFag]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[StyringsreolHyldeFag](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[FarveIndex] [int] NOT NULL,
	[NormtidDage] [int] NULL,
	[StyringsreolHyldeID] [int] NOT NULL,
	[NormtidDato] [datetime] NULL,
	[SorteringsIndex] [int] NULL,
 CONSTRAINT [PK_StyringsreolFag] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[StyringsreolSagsFelt]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[StyringsreolSagsFelt](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[InternalName] [nvarchar](50) NOT NULL,
	[DisplayName] [nvarchar](50) NOT NULL,
	[SagItemName] [nvarchar](50) NOT NULL,
	[Abbreviation] [nvarchar](50) NOT NULL,
	[IsDefault] [bit] NOT NULL,
 CONSTRAINT [PK_StyringsreolSagsFelt] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SystemConfiguration]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SystemConfiguration](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[VisRedigerMedWordKnapPaaDagsordenpunkt] [bit] NULL,
	[DefaultTemporaryFolderPath] [nvarchar](300) NULL,
	[DefaultCheckoutFolderPath] [nvarchar](300) NULL,
	[ForceTemporaryFolderPath] [bit] NULL,
	[ForceCheckoutFolderPath] [bit] NULL,
	[RequireErindringConclusion] [bit] NULL,
	[SbsysDatabaseVersion] [varchar](20) NULL,
	[AllowBlankPassword] [bit] NULL,
	[BulkJournaliseringsSti] [nvarchar](300) NULL,
	[DagsordenSystemAktivt] [bit] NOT NULL,
	[JournaliseringMaxFilesize] [int] NOT NULL,
	[Timestamp] [timestamp] NOT NULL,
	[KontrollerCheckOutTilSammeMaskineVedKladeJournalisering] [bit] NOT NULL,
	[HelpSystemUrl] [nvarchar](1000) NOT NULL,
	[Kommune] [nvarchar](500) NULL,
	[TrustedADDomains] [nvarchar](500) NULL,
	[KraevetGruppemedlemsskab] [nvarchar](255) NULL,
	[TilladAutomatiskLogon] [bit] NOT NULL,
	[SynkroniserADEgenskaber] [bit] NOT NULL,
	[SynkroniserADGrupperMedRoller] [bit] NOT NULL,
	[IntegreretBrugerID] [int] NOT NULL,
	[DefaultWorkFolderPath] [nvarchar](300) NULL,
	[ForceWorkFolderPath] [bit] NULL,
	[PostlisteQuery] [text] NOT NULL,
	[TilladAfslutUdenKladdeArkivering] [bit] NOT NULL,
	[TilladFletningVhaTekstbehandler] [bit] NOT NULL,
	[PaaSagStartView] [int] NOT NULL,
	[GrupperFaneblade] [bit] NOT NULL,
	[DagsordenWebGeneratorInternetRootPath] [nvarchar](300) NULL,
	[DagsordenWebGeneratorIntranetRootPath] [nvarchar](300) NULL,
	[DefaultPubliseringFolderRoot] [nvarchar](300) NULL,
	[ForcePubliseringFolderRoot] [bit] NOT NULL,
	[AnvendGenstande] [bit] NOT NULL,
	[VisOrdetÅbenIDagsordenOverskrift] [bit] NOT NULL,
	[DefaultDagsordenerVedMødeoprettelse] [int] NOT NULL,
	[KanPublicereDagsordenerMedKladdeBilag] [bit] NOT NULL,
	[BiholdUdvalgsMedlemmerPaaAdgangsliste] [bit] NOT NULL,
	[JournalNoteRedigeringsPeriode] [int] NOT NULL,
	[AnvendDokumentGalleri] [bit] NOT NULL,
	[JournalArkCss] [ntext] NULL,
	[JournalArkLogo] [image] NULL,
	[JournalArkLogoFilename] [nvarchar](300) NULL,
	[ServiceDatabaseConnectionString] [nvarchar](300) NULL,
	[TvingKommentarVedLogfejl] [bit] NOT NULL,
	[SendErindringTilSagsBehandlerVedJournalisering] [bit] NOT NULL,
	[InstallationIdentity] [uniqueidentifier] NOT NULL,
	[VisJournalNoterSomOversigt] [bit] NULL,
	[DagsordenPubliceringEmbedXml] [ntext] NULL,
	[SendFejlUrl] [nvarchar](300) NOT NULL,
	[JournalarkHyperlink] [nvarchar](300) NULL,
	[SendErindringTilNySagsBehandlerVedSkiftSagsbehandler] [bit] NOT NULL,
	[AnvendMaxLaengdePaaDagsordenBilag] [bit] NOT NULL,
	[MaxLaengdePaaDagsordenBilag] [int] NOT NULL,
	[AnvendDagsordenpunktVersioner] [bit] NOT NULL,
	[FastholdUdvalgOverskrift] [bit] NOT NULL,
	[SamlePDFUrl] [nvarchar](300) NULL,
	[DffForsendelsesType] [nvarchar](50) NULL,
 CONSTRAINT [PK_SystemConfiguration] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SystemDefaults]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SystemDefaults](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[ErindringTypeRingTilID] [int] NOT NULL,
	[ErindringTypeBemaerkID] [int] NOT NULL,
	[ErindringTypeLaesID] [int] NOT NULL,
	[ErindringTypeOpfoelgID] [int] NOT NULL,
	[DokumentArtJournaliserFilID] [int] NOT NULL,
	[DokumentArtDefaultID] [int] NOT NULL,
	[DokumentArtJournaliserSendtMailID] [int] NOT NULL,
	[DokumentArtJournaliserModtagetMailID] [int] NOT NULL,
	[DokumentArtJournaliserPapirID] [int] NOT NULL,
	[DokumentArtJournaliserScanningID] [int] NOT NULL,
	[DokumentArtJournaliserNotatID] [int] NOT NULL,
	[DokumentArtJournaliserInterntID] [int] NOT NULL,
	[DokumentArtJournaliserTelefonID] [int] NOT NULL,
	[SagsStatusID] [int] NOT NULL,
	[EmneplanID] [int] NOT NULL,
	[PubliceringXslStylesheetID] [int] NOT NULL,
	[PubliceringCssStylesheetID] [int] NOT NULL,
	[AnsaettelsesstedID] [int] NOT NULL,
	[FagomraadeID] [int] NOT NULL,
	[DokumentArtAvanceretFletID] [int] NOT NULL,
	[DokumentArtJournaliserTilbageJournaliserDOP] [int] NOT NULL,
	[GrundskabelonID] [int] NOT NULL,
	[KnownEksterntSystemID] [int] NOT NULL,
	[DelforloebTypeID] [int] NOT NULL,
	[ArkivAfklaringStatusID] [int] NOT NULL,
	[DagsordenXslStylesheetID] [int] NOT NULL,
	[DagsordenCssStylesheetID] [int] NOT NULL,
	[DagsordenGenereringRessourceID] [int] NOT NULL,
	[DagsordenTilbagejournaliseringRessourceID] [int] NOT NULL,
	[CivilstandNyPersonID] [int] NOT NULL,
	[SekretariatID] [int] NOT NULL,
 CONSTRAINT [PK_SystemDefaults] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[TidsPostering]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TidsPostering](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[TidsPosteringKategoriID] [int] NOT NULL,
	[Tekst] [varchar](100) NOT NULL,
	[Oprettet] [datetime] NOT NULL,
	[PosteringsDato] [datetime] NOT NULL,
	[BrugerID] [int] NOT NULL,
	[ContextSagID] [int] NULL,
	[ContextDelforloebID] [int] NULL,
	[ContextErindringID] [int] NULL,
PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[TidsPosteringKategori]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TidsPosteringKategori](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nchar](10) NOT NULL,
	[Aktiv] [bit] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[tmp_CasesToUpdateWithPermissions]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[tmp_CasesToUpdateWithPermissions](
	[nummer] [nvarchar](50) NOT NULL,
	[Titel] [nvarchar](450) NOT NULL,
	[sikkerhedsgruppe] [nvarchar](100) NOT NULL,
	[id] [int] NOT NULL,
	[skabelon] [nvarchar](200) NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[tmp_CasesToUpdateWithPermissions2]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[tmp_CasesToUpdateWithPermissions2](
	[nummer] [nvarchar](50) NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[TrustedAssembly]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TrustedAssembly](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SystemConfigurationID] [int] NOT NULL,
	[AssemblyFileName] [nvarchar](300) NOT NULL,
	[AssemblyGuid] [uniqueidentifier] NOT NULL,
	[Enabled] [bit] NOT NULL,
	[Navn] [nvarchar](200) NOT NULL,
 CONSTRAINT [PK_TrustedAssemblies] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
 CONSTRAINT [IX_TrustedAssembly] UNIQUE NONCLUSTERED
(
	[AssemblyGuid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Udvalg]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Udvalg](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[UdvalgIdentity] [uniqueidentifier] NOT NULL,
	[Navn] [nvarchar](100) NOT NULL,
	[Sortering] [int] NOT NULL,
	[Oprettet] [datetime] NULL,
	[Nedlagt] [datetime] NULL,
	[WebUndermappe] [nvarchar](255) NULL,
	[KanBeslutteAllePunkter] [bit] NOT NULL,
	[PunktnummereringStart] [int] NOT NULL,
	[FortloebendePunktnummerering] [bit] NOT NULL,
	[Created] [datetime] NOT NULL,
	[CreatedBy] [int] NOT NULL,
	[LastChanged] [datetime] NOT NULL,
	[LastChangedBy] [int] NOT NULL,
	[SekretariatID] [int] NOT NULL,
	[UdvalgsstrukturID] [int] NOT NULL,
	[PubliceringCss] [ntext] NULL,
	[IndstillingStandardTekst] [nvarchar](100) NOT NULL,
	[StedStandardTekst] [nvarchar](100) NOT NULL,
	[MoedetidspunktStandard] [datetime] NULL,
	[RydIndstillingVedKopiering] [bit] NOT NULL,
	[EksternSikkerhedsgruppe] [nvarchar](100) NULL,
	[TekstForBesluttendeUdvalg] [nvarchar](300) NOT NULL,
	[DefaultSagId] [int] NULL,
	[Klarmeldingsfrist] [int] NULL,
	[IndstillingSkalKopieresTilFeltID] [int] NULL,
	[BeslutningSkalKopieresTilFeltID] [int] NULL,
	[Forkortelse] [nvarchar](10) NOT NULL,
 CONSTRAINT [PK__Udvalg__7A13BF05] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[UdvalgIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Udvalgsmedlem]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Udvalgsmedlem](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Suppleant] [bit] NOT NULL,
	[UdvaelgspersonID] [int] NOT NULL,
	[UdvalgID] [int] NOT NULL,
	[Sortering] [int] NOT NULL,
 CONSTRAINT [PK__Udvaelgsmedlem__7DE44FE9] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Udvalgsperson]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Udvalgsperson](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Fornavn] [nvarchar](255) NOT NULL,
	[Efternavn] [nvarchar](255) NOT NULL,
	[ErAktiv] [bit] NOT NULL,
 CONSTRAINT [PK_Udvalgsperson] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Udvalgsstruktur]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Udvalgsstruktur](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Sortering] [int] NOT NULL,
	[Niveau] [int] NOT NULL,
	[Navn] [nvarchar](50) NOT NULL,
	[ParentID] [int] NULL,
 CONSTRAINT [PK__Udvalgsstruktur__782B7693] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[UsageLog]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[UsageLog](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL,
 CONSTRAINT [PK_UsageLog] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20140811_09_40_19]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20140811_09_40_19](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20140811_09_40_48]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20140811_09_40_48](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20140811_09_41_14]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20140811_09_41_14](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20140811_09_41_41]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20140811_09_41_41](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20150401_00_00_00]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20150401_00_00_00](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20150501_00_00_00]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20150501_00_00_00](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20150601_00_00_00]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20150601_00_00_00](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20150901_00_00_00]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20150901_00_00_00](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20151001_00_00_01]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20151001_00_00_01](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20151201_00_00_00]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20151201_00_00_00](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20160101_00_00_00]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20160101_00_00_00](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20160201_00_00_02]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20160201_00_00_02](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20160301_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20160301_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20160401_00_00_04]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20160401_00_00_04](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20160501_00_01_26]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20160501_00_01_26](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20160601_00_01_20]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20160601_00_01_20](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20160701_00_01_11]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20160701_00_01_11](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20160801_00_00_51]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20160801_00_00_51](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20160901_00_01_23]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20160901_00_01_23](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20161001_00_01_05]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20161001_00_01_05](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20161101_00_00_37]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20161101_00_00_37](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20161201_00_01_55]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20161201_00_01_55](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20170101_00_01_57]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20170101_00_01_57](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20170201_00_00_56]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20170201_00_00_56](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20170301_00_01_04]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20170301_00_01_04](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20170401_00_00_08]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20170401_00_00_08](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20170501_00_00_39]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20170501_00_00_39](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20170601_00_00_45]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20170601_00_00_45](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20170701_00_00_46]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20170701_00_00_46](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20170801_00_00_44]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20170801_00_00_44](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20170901_00_00_42]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20170901_00_00_42](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20171001_00_00_45]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20171001_00_00_45](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20171101_00_00_40]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20171101_00_00_40](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20171201_00_00_47]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20171201_00_00_47](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20180101_00_00_55]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20180101_00_00_55](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20180201_00_00_36]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20180201_00_00_36](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20180301_00_00_25]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20180301_00_00_25](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20180401_00_00_06]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20180401_00_00_06](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20180501_00_00_07]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20180501_00_00_07](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20180601_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20180601_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20180701_00_00_04]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20180701_00_00_04](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20180801_00_00_04]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20180801_00_00_04](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20180901_00_00_08]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20180901_00_00_08](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20181001_00_00_08]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20181001_00_00_08](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20181101_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20181101_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20181201_00_00_07]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20181201_00_00_07](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20190101_00_00_05]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20190101_00_00_05](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20190201_00_00_09]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20190201_00_00_09](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20190301_00_00_11]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20190301_00_00_11](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20190401_00_00_05]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20190401_00_00_05](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20190501_00_00_06]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20190501_00_00_06](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20190601_00_00_16]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20190601_00_00_16](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20190701_00_00_06]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20190701_00_00_06](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20190801_00_00_04]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20190801_00_00_04](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20190901_00_00_09]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20190901_00_00_09](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20191001_00_00_04]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20191001_00_00_04](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20191101_00_00_05]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20191101_00_00_05](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20191201_00_00_06]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20191201_00_00_06](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20200101_00_00_12]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20200101_00_00_12](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20200201_00_00_08]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20200201_00_00_08](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20200301_00_00_07]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20200301_00_00_07](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20200401_00_00_05]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20200401_00_00_05](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20200501_00_00_04]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20200501_00_00_04](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20200601_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20200601_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20200701_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20200701_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20200801_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20200801_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20200901_00_00_02]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20200901_00_00_02](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20201001_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20201001_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20201101_00_00_01]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20201101_00_00_01](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20201201_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20201201_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20210101_00_00_02]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20210101_00_00_02](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20210201_00_00_02]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20210201_00_00_02](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20210301_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20210301_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20210401_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20210401_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20210501_00_00_04]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20210501_00_00_04](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20210601_00_00_05]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20210601_00_00_05](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20210701_00_00_04]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20210701_00_00_04](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20210801_00_00_01]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20210801_00_00_01](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20210901_00_00_01]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20210901_00_00_01](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20211001_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20211001_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20211101_00_00_00]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20211101_00_00_00](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20211201_00_00_02]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20211201_00_00_02](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20220101_00_00_02]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20220101_00_00_02](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20220201_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20220201_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20220301_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20220301_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20220401_00_00_01]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20220401_00_00_01](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20220501_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20220501_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20220601_00_00_12]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20220601_00_00_12](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20220701_00_00_09]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20220701_00_00_09](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20220801_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20220801_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20220901_00_00_08]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20220901_00_00_08](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20221001_00_00_02]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20221001_00_00_02](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20221101_00_00_01]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20221101_00_00_01](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20221201_00_00_02]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20221201_00_00_02](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20230101_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20230101_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20230201_00_00_02]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20230201_00_00_02](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20230301_00_00_06]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20230301_00_00_06](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20230401_00_00_04]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20230401_00_00_04](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20230501_00_00_04]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20230501_00_00_04](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20230601_00_00_08]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20230601_00_00_08](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20230701_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20230701_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20230801_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20230801_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20230901_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20230901_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20231001_00_00_05]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20231001_00_00_05](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20231101_00_00_03]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20231101_00_00_03](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20231201_00_00_04]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20231201_00_00_04](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20240101_00_00_05]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20240101_00_00_05](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20240201_00_00_07]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20240201_00_00_07](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20240301_00_00_06]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20240301_00_00_06](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20240401_00_00_07]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20240401_00_00_07](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usagelog_20240501_00_00_16]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usagelog_20240501_00_00_16](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerID] [int] NOT NULL,
	[LogDate] [datetime] NOT NULL,
	[Event] [varchar](200) NULL,
	[Details] [text] NULL,
	[TargetID] [int] NULL,
	[DelforloebID] [int] NULL,
	[SagID] [int] NULL,
	[UsageType] [int] NOT NULL,
	[TargetType] [int] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Vej]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Vej](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[VejNummer] [nvarchar](20) NOT NULL,
	[Beskrivelse] [nvarchar](500) NULL,
	[Oprettet] [datetime] NOT NULL,
	[KilometerFra] [float] NULL,
	[KilometerTil] [float] NULL,
	[Position] [nvarchar](30) NULL,
	[KommuneID] [int] NOT NULL,
	[ExternalSourceLastUpdate] [datetime] NULL,
	[ExternalSourceID] [nvarchar](50) NULL,
	[ExternalSourceName] [nvarchar](50) NULL,
	[Beliggenhed] [nvarchar](500) NULL,
	[Historisk] [bit] NOT NULL,
	[VejIdentity] [uniqueidentifier] NOT NULL,
 CONSTRAINT [PK_Vej] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED
(
	[VejIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[WebApiAppAccess]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[WebApiAppAccess](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[ClientId] [nvarchar](200) NOT NULL,
	[ClientSecret] [nvarchar](200) NOT NULL,
	[Uri] [nvarchar](1000) NULL,
	[AllowAuthorizationCodeGrant] [bit] NOT NULL,
	[AllowImplicitCodeGrant] [bit] NOT NULL,
	[AllowResourceOwnerCredentialsGrant] [bit] NOT NULL,
	[AllowClientCredentialsGrant] [bit] NOT NULL,
	[RefreshTokenExpiration] [int] NOT NULL,
 CONSTRAINT [PK_WebApiAppAccess] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[WebApiRefreshToken]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[WebApiRefreshToken](
	[Id] [nchar](160) NOT NULL,
	[SerializedTicket] [nvarchar](max) NOT NULL,
	[IssuedUtc] [datetimeoffset](7) NOT NULL,
	[ExpiresUtc] [datetimeoffset](7) NOT NULL,
	[ClientId] [nvarchar](200) NOT NULL,
	[Revoked] [bit] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[WebWidget]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[WebWidget](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Navn] [nvarchar](1024) NULL,
	[Titel] [nvarchar](1024) NULL,
	[Url] [nvarchar](1024) NULL,
	[Aktiv] [bit] NOT NULL,
	[Indlejret] [bit] NOT NULL,
	[Placering] [int] NULL,
	[Icon] [varbinary](max) NULL,
	[Regel] [int] NULL,
	[SortIndex] [int] NOT NULL,
	[KonfigurationID] [uniqueidentifier] NOT NULL,
	[ErBU] [bit] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[WebWidgetBruger]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[WebWidgetBruger](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerId] [int] NULL,
	[WebWidgetId] [int] NULL,
PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[WebWidgetSagSkabelon]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[WebWidgetSagSkabelon](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagskabelonId] [int] NULL,
	[WebWidgetId] [int] NULL,
PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[WebWidgetSagstype]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[WebWidgetSagstype](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[SagstypeID] [int] NULL,
	[WebWidgetId] [int] NULL,
PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[WordGeneratorDagsordenExtension]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[WordGeneratorDagsordenExtension](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[DagsordenID] [int] NOT NULL,
	[Forsidetekst] [ntext] NULL,
	[TvungenSideskiftEfterPunkt] [bit] NOT NULL,
 CONSTRAINT [PK_WordGeneratorDagsordenExtension] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[WordGeneratorUdvalgExtension]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[WordGeneratorUdvalgExtension](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[UdvalgID] [int] NOT NULL,
	[WordTemplateGenerering] [image] NULL,
	[WordTemplateTilbagejournalisering] [image] NULL,
	[TvungenSideskiftEfterPunkt] [bit] NOT NULL,
	[UdrykPunktnummer] [bit] NOT NULL,
	[FjernLinks] [bit] NOT NULL,
	[WordTemplateGenereringFilename] [nvarchar](300) NULL,
	[WordTemplateTilbagejournaliseringFilename] [nvarchar](300) NULL,
 CONSTRAINT [PK_WordGeneratorUdvalgExtension] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [sts].[AnsaettelsesstedIdentitet]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [sts].[AnsaettelsesstedIdentitet](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[AnsaettelsesstedIdentity] [uniqueidentifier] NOT NULL,
	[STSAnsaettelsesstedIdentity] [uniqueidentifier] NOT NULL,
	[OrganisationIdentitetID] [int] NOT NULL,
 CONSTRAINT [PK_STSAnsaettelsesstedIdentitet] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [sts].[BrugerIdentitet]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [sts].[BrugerIdentitet](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[BrugerIdentity] [uniqueidentifier] NOT NULL,
	[STSBrugerIdentity] [uniqueidentifier] NOT NULL,
 CONSTRAINT [PK_STSBrugerIdentitet] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [sts].[OrganisationIdentitet]    Script Date: 27-05-2024 09:13:19 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [sts].[OrganisationIdentitet](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[STSOrganisationIdentity] [uniqueidentifier] NOT NULL,
 CONSTRAINT [PK_STSOrganisationIdentitet] PRIMARY KEY CLUSTERED
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Adresse]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Adresse] ON [dbo].[Adresse]
(
	[Adresse1] ASC
)
INCLUDE([Etage],[DoerBetegnelse]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Adresse_Bynavn]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Adresse_Bynavn] ON [dbo].[Adresse]
(
	[Bynavn] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_AdresseGenstand_EsrEjendomsNummer]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_AdresseGenstand_EsrEjendomsNummer] ON [dbo].[AdresseGenstand]
(
	[EsrEjendomsNummer] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Aktindsigt]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_Aktindsigt] ON [dbo].[AktindsigtSaves]
(
	[Id] ASC
)
INCLUDE([Oprettet],[BrugerId],[SavedProgress]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_ArkivPeriode_ArkivPeriodeIdentity]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_ArkivPeriode_ArkivPeriodeIdentity] ON [dbo].[ArkivPeriode]
(
	[ArkivPeriodeIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Beskedfordeling_DokumentKonverteringBestillingId]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Beskedfordeling_DokumentKonverteringBestillingId] ON [dbo].[Beskedfordeling]
(
	[HandledBy] ASC,
	[DokumentKonverteringBestillingId] DESC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_BeskedFordeling_ForloebId]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_BeskedFordeling_ForloebId] ON [dbo].[Beskedfordeling]
(
	[HandledBy] ASC,
	[ForloebId] DESC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Beskedfordeling_UsageLogId]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Beskedfordeling_UsageLogId] ON [dbo].[Beskedfordeling]
(
	[HandledBy] ASC,
	[UsageLogId] DESC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_KladdeRegistrering_Aktiv_Dokumentregistrering]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_KladdeRegistrering_Aktiv_Dokumentregistrering] ON [dbo].[Bilag]
(
	[KladdeRegistreringID] ASC,
	[Aktiv] ASC,
	[DokumentRegistreringID] ASC
)
INCLUDE([ID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Bruger_BrugerIdentity]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_Bruger_BrugerIdentity] ON [dbo].[Bruger]
(
	[BrugerIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Bruger_LoginID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_Bruger_LoginID] ON [dbo].[Bruger]
(
	[LogonID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Bruger_Logon]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_Bruger_Logon] ON [dbo].[Bruger]
(
	[LogonID] ASC,
	[LogonPassword] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_tblBrugerGruppe_Brugere_Link]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_tblBrugerGruppe_Brugere_Link] ON [dbo].[BrugerGruppeBruger]
(
	[BrugerGruppeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_tblBrugerGruppe_Brugere_Link_1]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_tblBrugerGruppe_Brugere_Link_1] ON [dbo].[BrugerGruppeBruger]
(
	[BrugerID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_BrugerSettingsDropFolderConfiguration_BrugersettingsID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_BrugerSettingsDropFolderConfiguration_BrugersettingsID] ON [dbo].[BrugerSettingsDropFolderConfiguration]
(
	[BrugerSettingsID] ASC
)
INCLUDE([Navn],[Beskrivelse],[DropFolderSti],[Enabled],[InkluderUnderFoldere]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_MailSystemSessionInfo_BrugerSettings]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_MailSystemSessionInfo_BrugerSettings] ON [dbo].[BrugerSettingsEmailKontoRegistrering]
(
	[BrugerSettingsID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_BrugerSettingsFavoritSag_BrugerSettingsID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_BrugerSettingsFavoritSag_BrugerSettingsID] ON [dbo].[BrugerSettingsFavoritSag]
(
	[BrugerSettingsID] ASC
)
INCLUDE([SagID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Bygning_BygningIdentity]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_Bygning_BygningIdentity] ON [dbo].[Bygning]
(
	[BygningIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_CompatibleVersions_Composite]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_CompatibleVersions_Composite] ON [dbo].[CompatibleVersions]
(
	[SbsysDatabaseVersion] ASC,
	[SbsysClientVersion] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Dagsorden_Moede]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Dagsorden_Moede] ON [dbo].[Dagsorden]
(
	[MoedeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Dagsordenpunkt_SagID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Dagsordenpunkt_SagID] ON [dbo].[Dagsordenpunkt]
(
	[SagID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DagsordenpunktBehandlingBilag_BehandlingID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DagsordenpunktBehandlingBilag_BehandlingID] ON [dbo].[DagsordenPunktBehandlingBilag]
(
	[BehandlingID] ASC
)
INCLUDE([BilagID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DagsordenpunktbehanldingID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DagsordenpunktbehanldingID] ON [dbo].[DagsordenpunktBehandlingFeltIndhold]
(
	[DagsordenpunktsBehandlingId] ASC
)
INCLUDE([DagsordenpunktFeltIndholdId]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DagsordenpunktsBehandling_DagsordenId]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DagsordenpunktsBehandling_DagsordenId] ON [dbo].[DagsordenpunktsBehandling]
(
	[DagsordenId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DagsordenpunktsBehandling_DagsordenpunktId]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DagsordenpunktsBehandling_DagsordenpunktId] ON [dbo].[DagsordenpunktsBehandling]
(
	[DagsordenpunktId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Delforloeb_DelforloebType]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Delforloeb_DelforloebType] ON [dbo].[Delforloeb]
(
	[DelforloebTypeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Delforloeb_ID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Delforloeb_ID] ON [dbo].[Delforloeb]
(
	[ID] ASC
)
INCLUDE([Titel]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DelforloebDokumentRegistrering_Delforloeb]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DelforloebDokumentRegistrering_Delforloeb] ON [dbo].[DelforloebDokumentRegistrering]
(
	[DokumentRegistreringID] ASC
)
INCLUDE([DelforloebID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DelforloebDokumentRegistrering_DelforloebID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DelforloebDokumentRegistrering_DelforloebID] ON [dbo].[DelforloebDokumentRegistrering]
(
	[DelforloebID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Delforloeb_KladdeRegistrering]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Delforloeb_KladdeRegistrering] ON [dbo].[DelforloebKladdeRegistrering]
(
	[DelforloebID] ASC,
	[KladdeRegistreringID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DocumentProcesseringHistorik_InputDokumentDataInfoID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DocumentProcesseringHistorik_InputDokumentDataInfoID] ON [dbo].[DocumentProcesseringHistorik]
(
	[InputDokumentDataInfoID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DocumentProcesseringHistorik_InputDokumentID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DocumentProcesseringHistorik_InputDokumentID] ON [dbo].[DocumentProcesseringHistorik]
(
	[InputDokumentID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [_dta_index_DokImport_JournalPostID_til_konvertering]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [_dta_index_DokImport_JournalPostID_til_konvertering] ON [dbo].[DokImport]
(
	[JournalPostID] ASC
)
INCLUDE([Filnavn],[PrimaryDokument]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [_dta_index_DokImport_JournalPostID2_til_konvertering]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [_dta_index_DokImport_JournalPostID2_til_konvertering] ON [dbo].[DokImport]
(
	[JournalPostID] ASC
)
INCLUDE([Filnavn],[FilEkstension],[DokumentGuid],[PrimaryDokument]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Dokument_EksternID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Dokument_EksternID] ON [dbo].[Dokument]
(
	[EksternId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Dokument_ParentDokumentID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Dokument_ParentDokumentID] ON [dbo].[Dokument]
(
	[ParentDokumentID] ASC
)
INCLUDE([ID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Dokument_ProcessStatus]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Dokument_ProcessStatus] ON [dbo].[Dokument]
(
	[ProcessStatus] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Dokument_ProcessStatus_ProcessPostAction]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Dokument_ProcessStatus_ProcessPostAction] ON [dbo].[Dokument]
(
	[ProcessStatus] ASC,
	[ProcessPostAction] ASC
)
INCLUDE([DokumentArtID],[Beskrivelse],[OprettetAfID],[Oprettet],[DokumentType],[YderligereMaterialeFindes],[YderligereMaterialeBeskrivelse],[MailID],[ParentDokumentID],[Navn],[IsImported],[PaaPostliste],[PostlisteTitel],[PostlisteBeskrivelse],[ImporteretFraKnownEksternSystemID],[EksternId],[IsParent],[IsComposite],[PrintDate],[PrimaryDokumentDataInfoID],[DeletedState],[DeletedDate],[DeletedByID],[DeletedReason],[DeleteConfirmed],[DeleteConfirmedByID],[OmfattetAfAktindsigt],[AktindsigtKommentar],[DokumentIdentity],[StatusTekst]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DokumentDataInfo]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DokumentDataInfo] ON [dbo].[DokumentDataInfo]
(
	[AlternateOfID] ASC,
	[DokumentDataInfoType] ASC,
	[DokumentDataType] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DokumentDataInfo_DokumentID_Cover]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DokumentDataInfo_DokumentID_Cover] ON [dbo].[DokumentDataInfo]
(
	[DokumentID] ASC
)
INCLUDE([DokumentDataType],[FileName],[FileExtension],[FilePath],[FileSize],[FileLastAccessed],[FileCreated],[DokumentDataInfoType],[HasSnapshot],[HasThumbnail],[IndexingStatus],[AlternateOfID],[PageFormat],[TextEncoding],[IsDeleted],[FileIdentity],[ContentID],[ThumbnailID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DokumentDataInfo_ID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DokumentDataInfo_ID] ON [dbo].[DokumentDataInfo]
(
	[ID] ASC
)
INCLUDE([Rank],[FilePath],[FileSize],[FileLastAccessed],[FileCreated],[DokumentDataInfoType],[HasSnapshot],[HasThumbnail],[ThumbnailID],[IndexingStatus],[AlternateOfID],[OCRStatus],[PageFormat],[TextEncoding],[IsDeleted],[FileIdentity],[ContentID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DokumentPart_DokumentID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DokumentPart_DokumentID] ON [dbo].[DokumentPart]
(
	[DokumentID] ASC
)
INCLUDE([PartID],[PartType],[KontaktForm],[AnvendtAdresse]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DokumentProcessingQueue]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DokumentProcessingQueue] ON [dbo].[DokumentProcessingQueue]
(
	[InputDokumentDataInfoID] ASC,
	[Action] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DokumentRegistrering_Dokument]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DokumentRegistrering_Dokument] ON [dbo].[DokumentRegistrering]
(
	[DokumentID] ASC
)
INCLUDE([ID],[SagspartID],[OprindeligSagspartAdresse],[ErBeskyttet],[Registreret],[RegistreretAfID],[Beskrivelse],[SecuritySetID],[Navn],[DeletedState],[DeletedDate],[DeletedByID],[DeletedReason],[DeleteConfirmed],[DeleteConfirmedByID],[DokumentRegistreringIdentity]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DokumentRegistrering_ID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DokumentRegistrering_ID] ON [dbo].[DokumentRegistrering]
(
	[ID] ASC
)
INCLUDE([DokumentID],[ErBeskyttet],[RegistreretAfID],[SecuritySetID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DokumentRegistrering_Registreret]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DokumentRegistrering_Registreret] ON [dbo].[DokumentRegistrering]
(
	[Registreret] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DokumentRegistrering_RegistreretAf]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DokumentRegistrering_RegistreretAf] ON [dbo].[DokumentRegistrering]
(
	[RegistreretAfID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_DokumentRegistrering_SagsPart]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_DokumentRegistrering_SagsPart] ON [dbo].[DokumentRegistrering]
(
	[SagspartID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Erindring_AnsvarligID_ProcessPostAction]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Erindring_AnsvarligID_ProcessPostAction] ON [dbo].[Erindring]
(
	[AnsvarligID] ASC,
	[ProcessPostAction] ASC
)
INCLUDE([ID],[Navn],[Beskrivelse],[ErindringTypeID],[CreatedByID],[Created],[LastChangedByID],[LastChanged],[OpretterID],[Uddelegeret],[ErAfsluttet],[AfsluttetAfID],[Afsluttet],[ErAnnulleret],[AnnulleretAfID],[Annulleret],[SagID],[DelforloebID],[DokumentRegistreringID],[KladdeRegistreringID],[HarDeadline],[Deadline],[AfsluttetNotat],[PopupStatus],[SagsPartID],[DagsordenpunktsBehandlingID],[KopierEfterUdfoerelse],[KopierTilID],[ReturEfterUdfoerelse],[JournalArkNoteID],[SynligFra],[SendSomMailRetryCount]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Erindring_Cover]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Erindring_Cover] ON [dbo].[Erindring]
(
	[KladdeRegistreringID] ASC,
	[DokumentRegistreringID] ASC,
	[DagsordenpunktsBehandlingID] ASC,
	[ErindringTypeID] ASC,
	[SagsPartID] ASC,
	[AnsvarligID] ASC,
	[CreatedByID] ASC,
	[SagID] ASC
)
INCLUDE([ID],[SynligFra],[JournalArkNoteID],[ErAfsluttet],[ErAnnulleret],[OpretterID],[LastChanged],[Created],[Uddelegeret],[AfsluttetAfID],[AnnulleretAfID],[DelforloebID],[HarDeadline],[Deadline],[PopupStatus],[KopierEfterUdfoerelse],[KopierTilID],[ReturEfterUdfoerelse]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Erindring_DelforloebID_ErAfsluttet]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Erindring_DelforloebID_ErAfsluttet] ON [dbo].[Erindring]
(
	[DelforloebID] ASC,
	[ErAfsluttet] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Erindring_Popup]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Erindring_Popup] ON [dbo].[Erindring]
(
	[PopupStatus] ASC,
	[AnsvarligID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_ErindringDataRegistrering_Erindring]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_ErindringDataRegistrering_Erindring] ON [dbo].[ErindringDataRegistrering]
(
	[ErindringID] ASC
)
INCLUDE([DataRegistreringType],[RegistreringID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_ErindringSomMail_2]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_ErindringSomMail_2] ON [dbo].[ErindringSomMail]
(
	[AnsaettelsesstedID] ASC,
	[BrugerID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Firma_AdresseId]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Firma_AdresseId] ON [dbo].[Firma]
(
	[AdresseID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Firma_CvrNummer]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Firma_CvrNummer] ON [dbo].[Firma]
(
	[CVRNummer] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Firma_PNummer]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Firma_PNummer] ON [dbo].[Firma]
(
	[PNummer] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Forloeb_Delforloeb]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Forloeb_Delforloeb] ON [dbo].[Forloeb]
(
	[DelforloebID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Forloeb_Erindring]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Forloeb_Erindring] ON [dbo].[Forloeb]
(
	[ID] ASC,
	[ErindringID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Forloeb_Erindring_sag]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Forloeb_Erindring_sag] ON [dbo].[Forloeb]
(
	[ErindringID] ASC
)
INCLUDE([SagID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Forloeb_RegistreretAf]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Forloeb_RegistreretAf] ON [dbo].[Forloeb]
(
	[RegistreretAfID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Forloeb_Target]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Forloeb_Target] ON [dbo].[Forloeb]
(
	[TargetType] ASC,
	[TargetID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_ForloebType_KeyName_Opslag]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_ForloebType_KeyName_Opslag] ON [dbo].[ForloebTypeOpslag]
(
	[KeyName] ASC
)
INCLUDE([Navn],[Beskrivelse],[HasIcon],[IconName],[IsDetail]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Fravaer_MoedeId_UdvalgspersonId]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_Fravaer_MoedeId_UdvalgspersonId] ON [dbo].[Fravaer]
(
	[MoedeId] ASC,
	[UdvalgspersonId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_FravaerDagsorden_FravaerId_DagsordenId]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_FravaerDagsorden_FravaerId_DagsordenId] ON [dbo].[FravaerDagsorden]
(
	[FravaerId] ASC,
	[DagsordenId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_FravaerDagsordenpunktsBehandling_FravaerId_DagsordenpunktsBehandlingId]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_FravaerDagsordenpunktsBehandling_FravaerId_DagsordenpunktsBehandlingId] ON [dbo].[FravaerDagsordenpunktsBehandling]
(
	[FravaerId] ASC,
	[DagsordenpunktsBehandlingId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_GeneratorIndstillingerFeltRegistrering]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_GeneratorIndstillingerFeltRegistrering] ON [dbo].[GeneratorIndstillingerFeltRegistrering]
(
	[DagsordenpunktFeltID] ASC
)
INCLUDE([GeneratorIndstillingerID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Journalark_SagID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Journalark_SagID] ON [dbo].[JournalArk]
(
	[SagID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_JournalarkNote]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_JournalarkNote] ON [dbo].[JournalArkNote]
(
	[ID] ASC,
	[JournalArkID] ASC,
	[OprettetAf] ASC,
	[SlettetAfBrugerID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Support_Cluster_JournalarkNote]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Support_Cluster_JournalarkNote] ON [dbo].[JournalArkNote]
(
	[JournalArkID] ASC
)
INCLUDE([OprettetAf],[SlettetAfBrugerID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_JournalarkNoteID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_JournalarkNoteID] ON [dbo].[JournalArkNoteVedrPart]
(
	[JournalArkNoteID] ASC
)
INCLUDE([SagspartID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Sagspart_JournalArkNote]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Sagspart_JournalArkNote] ON [dbo].[JournalArkNoteVedrPart]
(
	[SagspartID] ASC
)
INCLUDE([JournalArkNoteID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Kladde_Created]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Kladde_Created] ON [dbo].[Kladde]
(
	[CreatedByID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Kladde_ID_CreatedByID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Kladde_ID_CreatedByID] ON [dbo].[Kladde]
(
	[CreatedByID] ASC,
	[ID] ASC
)
INCLUDE([Beskrivelse],[Emne],[Created],[LastChanged],[LastChangedByID],[FileName],[FileExtension],[IsCheckedOut],[IsArchived],[CheckedOutFileName],[CheckedOutFilePath],[CheckedOutByID],[CheckedOut],[CheckedOutMachineName],[CheckedOutMachineAddress],[CheckedOutUserName],[LastCheckedInByID],[LastCheckedIn],[CurrentVersion],[Navn],[MergeDataFileName],[KeepCheckedOut],[MailSubject],[PrinterName],[KladdeFletteStrategi],[KladdeRedigeringGenoptaget],[DeletedState],[DeletedDate],[DeletedByID],[DeletedReason],[DeleteConfirmed],[DeleteConfirmedByID],[MaterialeType],[IndexingStatus],[FileSize],[ImporteretFraKnownEksternSystemID],[EksternID],[KladdeArt]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Kladde_IsCheckedOut]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Kladde_IsCheckedOut] ON [dbo].[Kladde]
(
	[IsCheckedOut] ASC
)
INCLUDE([ID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_KladdePart_KladdeID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_KladdePart_KladdeID] ON [dbo].[KladdePart]
(
	[KladdeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_KladdeRegistrering_KladdeID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_KladdeRegistrering_KladdeID] ON [dbo].[KladdeRegistrering]
(
	[KladdeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Lokation_LokationIdentity]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_Lokation_LokationIdentity] ON [dbo].[Lokation]
(
	[LokationIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_MailRecipient_MailID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_MailRecipient_MailID] ON [dbo].[MailRecipient]
(
	[MailID] ASC
)
INCLUDE([Navn],[Adresse],[MailRecipientType],[CPR],[CVR],[Pnummer],[ContextSagID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Matrikel_Lookup]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Matrikel_Lookup] ON [dbo].[Matrikel]
(
	[KommuneID] ASC,
	[ArtID] ASC,
	[LandsEjerlavKode] ASC,
	[MatrikelNummer] ASC,
	[Ejerlejlighedsnummer] ASC,
	[Parcelnummer] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Matrikel_Nummer]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Matrikel_Nummer] ON [dbo].[Matrikel]
(
	[MatrikelNummer] ASC,
	[LandsEjerlavKode] ASC
)
INCLUDE([Beskrivelse],[Oprettet],[KommuneID],[Ejerlav],[EjerlavKode],[ExternalSourceLastUpdate],[ExternalSourceID],[ExternalSourceName],[Beliggenhed],[LandsEjerlav],[Historisk],[ArtID],[Parcelnummer],[Ejerlejlighedsnummer],[BeliggenhedAdresseID],[EjendomsNummer],[MatrikelIdentity]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_MatrikelArt_Kode]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_MatrikelArt_Kode] ON [dbo].[MatrikelArt]
(
	[Kode] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Memo_DokumentRegistreringID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Memo_DokumentRegistreringID] ON [dbo].[Memo]
(
	[DokumentRegistreringID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_MergeData_MainDokumentDataInfoID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_MergeData_MainDokumentDataInfoID] ON [dbo].[MergeData]
(
	[MainDokumentDataInfoID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 100) ON [PRIMARY]
GO
/****** Object:  Index [IX_Moede_Udvalg]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Moede_Udvalg] ON [dbo].[Moede]
(
	[UdvalgID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_MOSTRECENT_OwnerID_GroupName_Created]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_MOSTRECENT_OwnerID_GroupName_Created] ON [dbo].[MostRecentInfo]
(
	[OwnerID] ASC,
	[GroupName] ASC,
	[Created] ASC
)
INCLUDE([ID],[Text],[ItemID],[ClassName]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Mir_Person_FarCPR]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Mir_Person_FarCPR] ON [dbo].[Person]
(
	[FarCPR] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Mir_Person_MorCPR]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Mir_Person_MorCPR] ON [dbo].[Person]
(
	[MorCPR] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Person]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Person] ON [dbo].[Person]
(
	[CprNummer] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Person_AdresseId]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Person_AdresseId] ON [dbo].[Person]
(
	[AdresseID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Person_Navn]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Person_Navn] ON [dbo].[Person]
(
	[Navn] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_PubliceringDokument]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_PubliceringDokument] ON [dbo].[PubliseringDokument]
(
	[PubliseringID] ASC,
	[DokumentRegistreringID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Cover_BehandlerID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Cover_BehandlerID] ON [dbo].[Sag]
(
	[BehandlerID] ASC
)
INCLUDE([ID],[SagIdentity],[Nummer],[Titel],[ErBeskyttet],[Kommentar],[BevaringID],[KommuneID],[SagsStatusID],[CreatedByID],[Created],[LastChangedByID],[LastChanged],[YderligereMaterialeFindes],[YderligereMaterialeBeskrivelse],[AmtID],[ErBesluttet],[Besluttet],[BeslutningsTypeID],[BeslutningNotat],[BeslutningDeadline],[ErSamlesag],[FagomraadeID],[SecuritySetID],[SagsNummerID],[LastStatusChange],[LastStatusChangeComments],[Kassationsdato],[SagsPartID],[RegionID],[KommuneFoer2007ID],[Opstaaet],[AnsaettelsesstedID],[ArkivAfklaringStatusID],[StyringsreolHyldeID],[SkabelonID],[Sletningsdato]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Gammel_Soeg_Sag]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Gammel_Soeg_Sag] ON [dbo].[Sag]
(
	[ID] ASC,
	[ErBeskyttet] ASC,
	[BehandlerID] ASC,
	[SecuritySetID] ASC
)
INCLUDE([SagIdentity],[Nummer],[Titel],[Created],[LastChanged],[LastStatusChange]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Mir_SagSecurity]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Mir_SagSecurity] ON [dbo].[Sag]
(
	[ID] ASC,
	[SecuritySetID] ASC,
	[ErBeskyttet] ASC,
	[BehandlerID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Sag_Behandler_Sag_Ansaet_Created_Status]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Sag_Behandler_Sag_Ansaet_Created_Status] ON [dbo].[Sag]
(
	[BehandlerID] ASC,
	[AnsaettelsesstedID] ASC,
	[SagsStatusID] ASC,
	[Created] ASC
)
INCLUDE([ID],[Nummer],[Titel],[ErBeskyttet],[SecuritySetID],[Opstaaet]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Sag_Created]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Sag_Created] ON [dbo].[Sag]
(
	[Created] ASC
)
INCLUDE([SagIdentity],[Nummer],[Titel],[ErBeskyttet],[Kommentar],[BevaringID],[KommuneID],[BehandlerID],[SagsStatusID],[CreatedByID],[LastChangedByID],[LastChanged],[YderligereMaterialeFindes],[YderligereMaterialeBeskrivelse],[AmtID],[ErBesluttet],[Besluttet],[BeslutningsTypeID],[BeslutningNotat],[BeslutningDeadline],[ErSamlesag],[FagomraadeID],[SecuritySetID],[SagsNummerID],[LastStatusChange],[LastStatusChangeComments],[Kassationsdato],[SagsPartID],[RegionID],[KommuneFoer2007ID],[Opstaaet],[AnsaettelsesstedID],[ArkivAfklaringStatusID],[StyringsreolHyldeID],[SkabelonID],[Sletningsdato]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Sag_LastStatusChange]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Sag_LastStatusChange] ON [dbo].[Sag]
(
	[LastStatusChange] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Sag_OprettetAf]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Sag_OprettetAf] ON [dbo].[Sag]
(
	[CreatedByID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Sag_SagIdentity]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_Sag_SagIdentity] ON [dbo].[Sag]
(
	[SagIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Sag_SagsStatusID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Sag_SagsStatusID] ON [dbo].[Sag]
(
	[SagsStatusID] ASC
)
INCLUDE([ID],[Nummer],[Titel],[ErBeskyttet],[KommuneID],[BehandlerID],[CreatedByID],[Created],[LastChangedByID],[BeslutningDeadline],[FagomraadeID],[SecuritySetID],[LastStatusChange],[SagsPartID],[Opstaaet],[AnsaettelsesstedID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_Sag_Titel]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Sag_Titel] ON [dbo].[Sag]
(
	[Titel] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_SagsNummer]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_SagsNummer] ON [dbo].[Sag]
(
	[Nummer] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_SagEksternIdentitet_SagID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_SagEksternIdentitet_SagID] ON [dbo].[SagEksternIdentitet]
(
	[SagID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_SagEmneOrd_Sag]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_SagEmneOrd_Sag] ON [dbo].[SagEmneOrd]
(
	[SagID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [Unikt_sagsnummer]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [Unikt_sagsnummer] ON [dbo].[SagsNummer]
(
	[EmnePlanNummerID] ASC,
	[SekvensNummer] ASC,
	[Aarstal] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_SagsPart]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_SagsPart] ON [dbo].[SagsPart]
(
	[PartType] ASC,
	[PartID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Sagspart_Ink_PartType_OprindeligAdresseid]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Sagspart_Ink_PartType_OprindeligAdresseid] ON [dbo].[SagsPart]
(
	[PartType] ASC,
	[OprindeligAdresseID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Sagsvisit_SagId]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Sagsvisit_SagId] ON [dbo].[SagsVisit]
(
	[SagID] ASC,
	[Tidspunkt] DESC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_SecuritySetBrugere_SecuritySetID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_SecuritySetBrugere_SecuritySetID] ON [dbo].[SecuritySetBrugere]
(
	[BrugerID] ASC
)
INCLUDE([SecuritySetID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_SecuritySetSikkerhedsgrupper_SikkerhedsgruppeID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_SecuritySetSikkerhedsgrupper_SikkerhedsgruppeID] ON [dbo].[SecuritySetSikkerhedsgrupper]
(
	[SikkerhedsgruppeID] ASC
)
INCLUDE([SecuritySetID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_UniktVerbum]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_UniktVerbum] ON [dbo].[SikkerhedsbeslutningOpslag]
(
	[Verbum] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_UniqueClassName]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_UniqueClassName] ON [dbo].[SikkerhedsbeslutningOpslag]
(
	[Class] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Sikkerhedsgruppe_ID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Sikkerhedsgruppe_ID] ON [dbo].[Sikkerhedsgruppe]
(
	[ID] ASC
)
INCLUDE([Navn],[EksternID],[ObjectSid]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_BrugerOrganisationsenhed_OrganisationsEnhed]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_BrugerOrganisationsenhed_OrganisationsEnhed] ON [dbo].[SikkerhedsgruppeBrugere]
(
	[SikkerhedsgruppeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Sikkerhedsgruppe_BrugerID]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Sikkerhedsgruppe_BrugerID] ON [dbo].[SikkerhedsgruppeBrugere]
(
	[SikkerhedsgruppeID] ASC
)
INCLUDE([ID],[BrugerID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_SikkerhedsgruppeBrugere]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_SikkerhedsgruppeBrugere] ON [dbo].[SikkerhedsgruppeBrugere]
(
	[SikkerhedsgruppeID] ASC
)
INCLUDE([ID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_SkabelonKladde]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_SkabelonKladde] ON [dbo].[SkabelonKladde]
(
	[KladdeID] ASC
)
INCLUDE([SkabelonID],[SkabelonGrundskabelonID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Stedfaestelse_Status]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Stedfaestelse_Status] ON [dbo].[Stedfaestelse]
(
	[SagID] ASC,
	[Status] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_TidsPostering_Column]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_TidsPostering_Column] ON [dbo].[TidsPostering]
(
	[ContextSagID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Udvalg_Mappe]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_Udvalg_Mappe] ON [dbo].[Udvalg]
(
	[UdvalgsstrukturID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_Vej_VejIdentity]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_Vej_VejIdentity] ON [dbo].[Vej]
(
	[VejIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_WebApiAppAccess_ClientId]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_WebApiAppAccess_ClientId] ON [dbo].[WebApiAppAccess]
(
	[ClientId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_WebApiAppAccess_Uri]    Script Date: 27-05-2024 09:13:19 ******/
CREATE NONCLUSTERED INDEX [IX_WebApiAppAccess_Uri] ON [dbo].[WebApiAppAccess]
(
	[Uri] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_WordGeneratorDagsordenExtension]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_WordGeneratorDagsordenExtension] ON [dbo].[WordGeneratorDagsordenExtension]
(
	[DagsordenID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_WordGeneratorUdvalgExtension]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_WordGeneratorUdvalgExtension] ON [dbo].[WordGeneratorUdvalgExtension]
(
	[UdvalgID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_AnsaettelsesstedIdentitet_AnsaettelsesstedIdentity]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_AnsaettelsesstedIdentitet_AnsaettelsesstedIdentity] ON [sts].[AnsaettelsesstedIdentitet]
(
	[AnsaettelsesstedIdentity] ASC
)
INCLUDE([ID],[STSAnsaettelsesstedIdentity],[OrganisationIdentitetID]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_AnsaettelsesstedIdentitet_STSAnsaettelsesstedIdentity]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_AnsaettelsesstedIdentitet_STSAnsaettelsesstedIdentity] ON [sts].[AnsaettelsesstedIdentitet]
(
	[STSAnsaettelsesstedIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_BrugerIdentitet_BrugerIdentity]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_BrugerIdentitet_BrugerIdentity] ON [sts].[BrugerIdentitet]
(
	[BrugerIdentity] ASC
)
INCLUDE([ID],[STSBrugerIdentity]) WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_BrugerIdentitet_STSBrugerIdentity]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_BrugerIdentitet_STSBrugerIdentity] ON [sts].[BrugerIdentitet]
(
	[STSBrugerIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
/****** Object:  Index [IX_OrganisationIdentitet_STSOrganisationIdentity]    Script Date: 27-05-2024 09:13:19 ******/
CREATE UNIQUE NONCLUSTERED INDEX [IX_OrganisationIdentitet_STSOrganisationIdentity] ON [sts].[OrganisationIdentitet]
(
	[STSOrganisationIdentity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
ALTER TABLE [dbo].[Adresse] ADD  CONSTRAINT [DF_Adresse_ErBeskyttet]  DEFAULT ((0)) FOR [ErBeskyttet]
GO
ALTER TABLE [dbo].[Adresse] ADD  DEFAULT (NULL) FOR [AdresseIdentity]
GO
ALTER TABLE [dbo].[Adresse] ADD  DEFAULT (NULL) FOR [AdgangsAdresseIdentity]
GO
ALTER TABLE [dbo].[AdresseGenstand] ADD  DEFAULT (newid()) FOR [AdresseIdentity]
GO
ALTER TABLE [dbo].[AktindsigtSaves] ADD  DEFAULT (getdate()) FOR [Oprettet]
GO
ALTER TABLE [dbo].[Ansaettelsessted] ADD  CONSTRAINT [DF_Ansaettelsessted_VisAdgangsListeVedOpretSag]  DEFAULT ((0)) FOR [VisAdgangsListeVedOpretSag]
GO
ALTER TABLE [dbo].[Ansaettelsessted] ADD  CONSTRAINT [DF_Ansaettelsessted_TilladBrugerAtSkiftePassword]  DEFAULT ((1)) FOR [TilladBrugerAtSkiftePassword]
GO
ALTER TABLE [dbo].[Ansaettelsessted] ADD  CONSTRAINT [DF_Ansaettelsessted_TilladPublicering]  DEFAULT ((1)) FOR [TilladPublicering]
GO
ALTER TABLE [dbo].[Ansaettelsessted] ADD  DEFAULT ((0)) FOR [EksterneAdviseringer]
GO
ALTER TABLE [dbo].[Ansaettelsessted] ADD  DEFAULT ((1)) FOR [AutomatiskErindringVedJournalisering]
GO
ALTER TABLE [dbo].[Ansaettelsessted] ADD  DEFAULT ((1)) FOR [StandardAktindsigtVedJournalisering]
GO
ALTER TABLE [dbo].[Ansaettelsessted] ADD  DEFAULT ((1)) FOR [VisCPR]
GO
ALTER TABLE [dbo].[Ansaettelsessted] ADD  DEFAULT (newid()) FOR [AnsaettelsesstedIdentity]
GO
ALTER TABLE [dbo].[Ansaettelsessted] ADD  DEFAULT ((1)) FOR [VisCVR]
GO
ALTER TABLE [dbo].[AnsaettelsesstedEksternMapning] ADD  CONSTRAINT [DF_AnsaettelsesstedEksternMapning_EksternSystemID]  DEFAULT (N'BSK') FOR [EksternSystemID]
GO
ALTER TABLE [dbo].[ArkivPeriode] ADD  CONSTRAINT [DF_ArkivPeriode_Created]  DEFAULT (getdate()) FOR [Created]
GO
ALTER TABLE [dbo].[ArkivPeriode] ADD  CONSTRAINT [DF_ArkivPeriode_LastChanged]  DEFAULT (getdate()) FOR [LastChanged]
GO
ALTER TABLE [dbo].[ArkivPeriode] ADD  DEFAULT (newid()) FOR [ArkivPeriodeIdentity]
GO
ALTER TABLE [dbo].[Beskedfordeling] ADD  DEFAULT (NULL) FOR [ForloebId]
GO
ALTER TABLE [dbo].[Beskedfordeling] ADD  DEFAULT (NULL) FOR [UsageLogId]
GO
ALTER TABLE [dbo].[Beskedfordeling] ADD  DEFAULT (NULL) FOR [Error]
GO
ALTER TABLE [dbo].[Beskedfordeling] ADD  DEFAULT ((0)) FOR [ForsoegtGensendt]
GO
ALTER TABLE [dbo].[Beskedfordeling] ADD  DEFAULT (NULL) FOR [DokumentKonverteringBestillingId]
GO
ALTER TABLE [dbo].[Beskedfordeling] ADD  DEFAULT (NULL) FOR [HandledBy]
GO
ALTER TABLE [dbo].[Beskedfordeling] ADD  DEFAULT (NULL) FOR [SendBOMBesvarelseBestillingId]
GO
ALTER TABLE [dbo].[BevaringOpslag] ADD  CONSTRAINT [DF_Bevaring_KassationsBeregning]  DEFAULT ((1)) FOR [KassationsBeregning]
GO
ALTER TABLE [dbo].[Bilag] ADD  CONSTRAINT [DF_Bilag_MaaPubliceres]  DEFAULT ((0)) FOR [MaaPubliceres]
GO
ALTER TABLE [dbo].[Bilag] ADD  DEFAULT (newid()) FOR [BilagIdentity]
GO
ALTER TABLE [dbo].[Bruger] ADD  CONSTRAINT [DF_tblBrugere_BrugerPWD]  DEFAULT (N'd41d8cd98f00b204e9800998ecf8427e') FOR [LogonPassword]
GO
ALTER TABLE [dbo].[Bruger] ADD  DEFAULT ('MD5') FOR [LogonAlgorithm]
GO
ALTER TABLE [dbo].[Bruger] ADD  DEFAULT ((0)) FOR [LogonFailedAttemptCount]
GO
ALTER TABLE [dbo].[Bruger] ADD  CONSTRAINT [DF__Temporary__KONTO__300424B4]  DEFAULT ((0)) FOR [KontorID]
GO
ALTER TABLE [dbo].[Bruger] ADD  CONSTRAINT [DF_Bruger_Status]  DEFAULT ((0)) FOR [Status]
GO
ALTER TABLE [dbo].[Bruger] ADD  DEFAULT (newid()) FOR [BrugerIdentity]
GO
ALTER TABLE [dbo].[Bruger] ADD  DEFAULT ((0)) FOR [ErSystembruger]
GO
ALTER TABLE [dbo].[BrugerLogonLog] ADD  CONSTRAINT [DF_BrugerLogonLog_Date]  DEFAULT (getdate()) FOR [Occured]
GO
ALTER TABLE [dbo].[BrugerLogonLog] ADD  CONSTRAINT [DF_BrugerLogonLog_Success]  DEFAULT ((0)) FOR [Action]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  DEFAULT ((30)) FOR [MaxSenesteSager]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_UdfyldDelforloebFaneblad]  DEFAULT ((1)) FOR [UdfyldDelforloebFaneblad]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_UdfyldErindringerFaneblad]  DEFAULT ((1)) FOR [UdfyldErindringerFaneblad]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_UdfyldDokumenterFaneblad]  DEFAULT ((1)) FOR [UdfyldDokumenterFaneblad]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_UdfyldForloebFaneblad]  DEFAULT ((1)) FOR [UdfyldForloebFaneblad]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_UdfyldKladderFaneblad]  DEFAULT ((1)) FOR [UdfyldKladderFaneblad]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_VisPanel]  DEFAULT ((0)) FOR [VisPanel]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_VisBeskedEfterSagGem]  DEFAULT ((0)) FOR [VisBeskedEfterSagGem]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_VisDagsordensystem]  DEFAULT ((1)) FOR [VisDagsordensystem]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_VisPreviewPaaDokumentOgKladdeLister]  DEFAULT ((1)) FOR [VisPreviewPaaDokumentOgKladdeLister]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_VisDokumentTabBlock]  DEFAULT ((1)) FOR [VisDokumentTabBlock]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings__DokumentLaesningsLayout]  DEFAULT ((0)) FOR [DokumentLaesningsLayout]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_ErStandardForNyeBrugere]  DEFAULT ((0)) FOR [ErStandardForNyeBrugere]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_SplitterDistancePercentage]  DEFAULT ((0)) FOR [SplitterDistancePercentage]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_AutoArkiverKladder]  DEFAULT ((1)) FOR [AutoArkiverKladder]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_AutoFortrydUaendredeKladder]  DEFAULT ((1)) FOR [AutoFortrydUaendredeKladder]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_VisKladdeProcessInfo]  DEFAULT ((1)) FOR [VisKladdeProcessInfo]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_PubliseringIndstilling]  DEFAULT ((3)) FOR [DagsordenPubliseringIndstilling]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_AnvendDokumentNavnTilAttachment]  DEFAULT ((0)) FOR [AnvendDokumentNavnTilAttachment]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_PostlisteIndstilling]  DEFAULT ((3)) FOR [PostlisteIndstilling]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_VisPostlister]  DEFAULT ((0)) FOR [VisPostlister]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_VisSbsysIdag]  DEFAULT ((1)) FOR [VisSbsysIdag]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_DagsordenpunktSoegningType]  DEFAULT ((0)) FOR [DagsordenpunktSoegningType]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_VisDagsordenpunktSoegning]  DEFAULT ((1)) FOR [VisDagsordenpunktSoegning]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_VisJournalArkSogning]  DEFAULT ((1)) FOR [VisJournalArkSogning]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  DEFAULT ((1)) FOR [VisJournalNoteTabBlock]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  DEFAULT ((1)) FOR [AnvendDokumenterSomJournalNote]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_SendFejl_1]  DEFAULT ((0)) FOR [SendFejl]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_FlashQueueBell]  DEFAULT ((1)) FOR [FlashQueueBell]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_AutomaticallyExecuteCommandsQueue]  DEFAULT ((1)) FOR [AutomaticallyExecuteCommandsQueue]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_VerificerProgramLukning]  DEFAULT ((0)) FOR [VerificerProgramLukning]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_MailSignaturVedSvarVideresend]  DEFAULT ((0)) FOR [MailSignaturVedSvarVideresend]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_VisInaktiveBrugere]  DEFAULT ((1)) FOR [VisInaktiveBrugere]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_SagStartView]  DEFAULT ((-1)) FOR [SagStartView]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  CONSTRAINT [DF_BrugerSettings_VisDokumentReadonlyAdvarselVedEksternAabning]  DEFAULT ((1)) FOR [VisDokumentReadonlyAdvarselVedEksternAabning]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  DEFAULT ((0)) FOR [AnvendSagspartSomStartvisningVedSoegSag]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  DEFAULT ((1)) FOR [ModtagErindringSomMail]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  DEFAULT ((0)) FOR [ShowAllCprCvr]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  DEFAULT ((0)) FOR [ObfuscateAllCprCvr]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  DEFAULT ((0)) FOR [ObfuscateLastCharactersInCpr]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  DEFAULT ((0)) FOR [ObfuscateCvr]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  DEFAULT ((0)) FOR [VisIkkeLukkedePunkter]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  DEFAULT ((1)) FOR [AnvendSenesteKladdeVedOpretKladde]
GO
ALTER TABLE [dbo].[BrugerSettings] ADD  DEFAULT ((0)) FOR [StandardErindringRetur]
GO
ALTER TABLE [dbo].[BrugerSettingsDropFolderConfiguration] ADD  CONSTRAINT [DF_BrugerSettingsDropFolderConfiguration_Enabled]  DEFAULT ((1)) FOR [Enabled]
GO
ALTER TABLE [dbo].[BrugerSettingsDropFolderConfiguration] ADD  CONSTRAINT [DF_BrugerSettingsDropFolderConfiguration_Notificer]  DEFAULT ((1)) FOR [Notificer]
GO
ALTER TABLE [dbo].[BrugerSettingsDropFolderConfiguration] ADD  CONSTRAINT [DF_BrugerSettingsDropFolderConfiguration_IncludeSubDirectories]  DEFAULT ((0)) FOR [InkluderUnderFoldere]
GO
ALTER TABLE [dbo].[BrugerSettingsDropFolderConfiguration] ADD  CONSTRAINT [DF_BrugerSettingsDropFolderConfiguration_ErJournaliseringskoe]  DEFAULT ((0)) FOR [ErJournaliseringskoe]
GO
ALTER TABLE [dbo].[BrugerSettingsFavoritSag] ADD  DEFAULT ((0)) FOR [Order]
GO
ALTER TABLE [dbo].[Bygning] ADD  CONSTRAINT [DF_Bygning_Oprettet]  DEFAULT (getdate()) FOR [Oprettet]
GO
ALTER TABLE [dbo].[Bygning] ADD  CONSTRAINT [DF_Bygning_Historisk]  DEFAULT ((0)) FOR [Historisk]
GO
ALTER TABLE [dbo].[Bygning] ADD  DEFAULT (newid()) FOR [BygningIdentity]
GO
ALTER TABLE [dbo].[Dagsorden] ADD  DEFAULT (newid()) FOR [DagsordenIdentity]
GO
ALTER TABLE [dbo].[Dagsorden] ADD  CONSTRAINT [DF_Dagsorden_Sortering]  DEFAULT ((32767)) FOR [Sortering]
GO
ALTER TABLE [dbo].[Dagsorden] ADD  CONSTRAINT [DF_Dagsorden_Historik]  DEFAULT ('') FOR [Historik]
GO
ALTER TABLE [dbo].[Dagsorden] ADD  CONSTRAINT [DF_Dagsorden_ErSkablon]  DEFAULT ((0)) FOR [ErSkabelon]
GO
ALTER TABLE [dbo].[Dagsordenpunkt] ADD  DEFAULT (newid()) FOR [DagsordenpunktIdentity]
GO
ALTER TABLE [dbo].[DagsordenpunktFelt] ADD  CONSTRAINT [DF_DagsordenpunktFelt_ErIndtastningFelt]  DEFAULT ((0)) FOR [ErIndtastningFelt]
GO
ALTER TABLE [dbo].[DagsordenpunktFeltIndhold] ADD  DEFAULT ('') FOR [Html]
GO
ALTER TABLE [dbo].[DagsordenpunktFeltIndhold] ADD  DEFAULT ('') FOR [Tekst]
GO
ALTER TABLE [dbo].[DagsordenpunktFeltIndhold] ADD  DEFAULT (newid()) FOR [FeltIndholdIdentity]
GO
ALTER TABLE [dbo].[DagsordenpunktFeltIndhold] ADD  DEFAULT ((0)) FOR [TilknyttetStjernehoering]
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling] ADD  DEFAULT ((1)) FOR [DagsordenRaekkefoelge]
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling] ADD  DEFAULT ((1)) FOR [BehandlingRaekkefoelge]
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling] ADD  DEFAULT ((0)) FOR [Laast]
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling] ADD  DEFAULT ((0)) FOR [Aabent]
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling] ADD  DEFAULT ((0)) FOR [AnsvarligID]
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling] ADD  DEFAULT ((0)) FOR [HarBeslutning]
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling] ADD  DEFAULT ('') FOR [Overskrift]
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling] ADD  DEFAULT (getdate()) FOR [LastChanged]
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling] ADD  DEFAULT ((0)) FOR [LastChangedBy]
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling] ADD  DEFAULT (newid()) FOR [DagsordenpunktsBehandlingIdentity]
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling] ADD  DEFAULT ((0)) FOR [IsStjernehoering]
GO
ALTER TABLE [dbo].[DagsordenpunktTypeDagsordenpunktFelt] ADD  DEFAULT ((0)) FOR [IsBuiltin]
GO
ALTER TABLE [dbo].[DagsordenpunkttypeIUdvalg] ADD  CONSTRAINT [DF_DagsordenpunkttypeIUdvalg_Sortering]  DEFAULT ((0)) FOR [Sortering]
GO
ALTER TABLE [dbo].[DagsordenpunktVersion] ADD  DEFAULT ((1)) FOR [Version]
GO
ALTER TABLE [dbo].[DagsordenpunktVersionFeltIndhold] ADD  DEFAULT ((1)) FOR [Redigerbar]
GO
ALTER TABLE [dbo].[DelforloebEksternIdentitet] ADD  CONSTRAINT [DF_DelforloebEksternIdentitet_Oprettet]  DEFAULT (getdate()) FOR [Oprettet]
GO
ALTER TABLE [dbo].[DelforloebEksternIdentitet] ADD  CONSTRAINT [DF_DelforloebEksternIdentitet_Status]  DEFAULT ((0)) FOR [Status]
GO
ALTER TABLE [dbo].[DocumentProcesseringHistorik] ADD  DEFAULT ((5)) FOR [TotalDurationSeconds]
GO
ALTER TABLE [dbo].[DocumentProcesseringHistorik] ADD  DEFAULT ((1)) FOR [AttemptCount]
GO
ALTER TABLE [dbo].[DocumentProcesseringHistorik] ADD  DEFAULT ('Færdig processeret') FOR [Message]
GO
ALTER TABLE [dbo].[Dokument] ADD  CONSTRAINT [DF_tDokument_ProcessStatus]  DEFAULT ((0)) FOR [ProcessStatus]
GO
ALTER TABLE [dbo].[Dokument] ADD  CONSTRAINT [DF_Dokument_IsImported]  DEFAULT ((0)) FOR [IsImported]
GO
ALTER TABLE [dbo].[Dokument] ADD  CONSTRAINT [DF_Dokument_PaaPostliste]  DEFAULT ((0)) FOR [PaaPostliste]
GO
ALTER TABLE [dbo].[Dokument] ADD  CONSTRAINT [DF_Dokument_ProcessPostAction]  DEFAULT ((0)) FOR [ProcessPostAction]
GO
ALTER TABLE [dbo].[Dokument] ADD  CONSTRAINT [DF_Dokument_IsParent]  DEFAULT ((0)) FOR [IsParent]
GO
ALTER TABLE [dbo].[Dokument] ADD  CONSTRAINT [DF_Dokument_IsComposite]  DEFAULT ((0)) FOR [IsComposite]
GO
ALTER TABLE [dbo].[Dokument] ADD  DEFAULT ((0)) FOR [DeletedState]
GO
ALTER TABLE [dbo].[Dokument] ADD  DEFAULT ((1)) FOR [OmfattetAfAktindsigt]
GO
ALTER TABLE [dbo].[Dokument] ADD  DEFAULT (newid()) FOR [DokumentIdentity]
GO
ALTER TABLE [dbo].[DokumentArtOpslag] ADD  CONSTRAINT [DF_DokumentArt_TilladPaaPostliste]  DEFAULT ((1)) FOR [UbeskyttetStandardMarkering]
GO
ALTER TABLE [dbo].[DokumentArtOpslag] ADD  CONSTRAINT [DF_DokumentArt_MaaPubliseres]  DEFAULT ((1)) FOR [MaaPubliseresPaaDagsorden]
GO
ALTER TABLE [dbo].[DokumentArtOpslag] ADD  CONSTRAINT [DF_DokumentArtOpslag_TilladPostlisteMarkeringAendring]  DEFAULT ((1)) FOR [UbeskyttetTilladAendring]
GO
ALTER TABLE [dbo].[DokumentArtOpslag] ADD  CONSTRAINT [DF_DokumentArtOpslag_SagBeskyttetStandardMarkering]  DEFAULT ((0)) FOR [SagBeskyttetStandardMarkering]
GO
ALTER TABLE [dbo].[DokumentArtOpslag] ADD  CONSTRAINT [DF_DokumentArtOpslag_SagBeskyttetTilladAendring]  DEFAULT ((0)) FOR [SagBeskyttetTilladAendring]
GO
ALTER TABLE [dbo].[DokumentArtOpslag] ADD  CONSTRAINT [DF_DokumentArtOpslag_DokumentBeskyttetStandardMarkering]  DEFAULT ((0)) FOR [DokumentBeskyttetStandardMarkering]
GO
ALTER TABLE [dbo].[DokumentArtOpslag] ADD  CONSTRAINT [DF_DokumentArtOpslag_DokumentBeskyttetTilladAendring]  DEFAULT ((0)) FOR [DokumentBeskyttetTilladAendring]
GO
ALTER TABLE [dbo].[DokumentArtOpslag] ADD  CONSTRAINT [DF_DokumentArtOpslag_SagOgDokumentBeskyttetStandardMarkering]  DEFAULT ((0)) FOR [SagOgDokumentBeskyttetStandardMarkering]
GO
ALTER TABLE [dbo].[DokumentArtOpslag] ADD  CONSTRAINT [DF_DokumentArtOpslag_SagOgDokumentBeskyttetTilladAendring]  DEFAULT ((0)) FOR [SagOgDokumentBeskyttetTilladAendring]
GO
ALTER TABLE [dbo].[DokumentArtOpslag] ADD  DEFAULT (newid()) FOR [DokumentArtIdentifier]
GO
ALTER TABLE [dbo].[DokumentBoksHistorik] ADD  DEFAULT ((-1)) FOR [AfsenderId]
GO
ALTER TABLE [dbo].[DokumentBoksWebserviceQueue] ADD  CONSTRAINT [DF_DokumentBoksWebserviceQueue_createdDate]  DEFAULT (getdate()) FOR [CreatedDate]
GO
ALTER TABLE [dbo].[DokumentBoksWebserviceQueue] ADD  DEFAULT ((0)) FOR [AfsenderID]
GO
ALTER TABLE [dbo].[DokumentDataInfo] ADD  DEFAULT ((0)) FOR [FileSize]
GO
ALTER TABLE [dbo].[DokumentDataInfo] ADD  CONSTRAINT [DF_DokumentDataInfo_HasSnapshot]  DEFAULT ((0)) FOR [HasSnapshot]
GO
ALTER TABLE [dbo].[DokumentDataInfo] ADD  CONSTRAINT [DF_DokumentDataInfo_HasThumbnail]  DEFAULT ((0)) FOR [HasThumbnail]
GO
ALTER TABLE [dbo].[DokumentDataInfo] ADD  CONSTRAINT [DF_DokumentDataInfo_IndexingStatus]  DEFAULT ((1)) FOR [IndexingStatus]
GO
ALTER TABLE [dbo].[DokumentDataInfo] ADD  CONSTRAINT [DF_DokumentDataInfo_OCRStatus]  DEFAULT ((1)) FOR [OCRStatus]
GO
ALTER TABLE [dbo].[DokumentDataInfo] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[DokumentDataInfo] ADD  DEFAULT (newid()) FOR [FileIdentity]
GO
ALTER TABLE [dbo].[DokumentProcessingQueue] ADD  CONSTRAINT [DF_ProcessQueue_Action]  DEFAULT ((0)) FOR [Action]
GO
ALTER TABLE [dbo].[DokumentProcessingQueue] ADD  CONSTRAINT [DF_ProcessQueue_Queued]  DEFAULT (getdate()) FOR [Queued]
GO
ALTER TABLE [dbo].[DokumentProcessingQueue] ADD  CONSTRAINT [DF_ProcessQueue_AttemptCount]  DEFAULT ((0)) FOR [AttemptCount]
GO
ALTER TABLE [dbo].[DokumentProcessingQueue] ADD  CONSTRAINT [DF_ProcessQueue_IsSuccessfull]  DEFAULT ((0)) FOR [Status]
GO
ALTER TABLE [dbo].[DokumentProcessingQueue] ADD  CONSTRAINT [DF_DokumentProcessingQueue_TotalDurationSeconds]  DEFAULT ((0)) FOR [TotalDurationSeconds]
GO
ALTER TABLE [dbo].[DokumentProcessingQueue] ADD  CONSTRAINT [DF_DokumentProcessingQueue_Timeout]  DEFAULT ((10)) FOR [TimeoutSeconds]
GO
ALTER TABLE [dbo].[DokumentRegistrering] ADD  DEFAULT ((0)) FOR [ErBeskyttet]
GO
ALTER TABLE [dbo].[DokumentRegistrering] ADD  DEFAULT ((0)) FOR [DeletedState]
GO
ALTER TABLE [dbo].[DokumentRegistrering] ADD  DEFAULT (newid()) FOR [DokumentRegistreringIdentity]
GO
ALTER TABLE [dbo].[DokumentRegistreringSletning] ADD  CONSTRAINT [DF_DokumentRegistreringSletning_TimeStamp]  DEFAULT (getdate()) FOR [TimeStamp]
GO
ALTER TABLE [dbo].[Ejendom] ADD  CONSTRAINT [DF_Ejendom_Historisk]  DEFAULT ((0)) FOR [Historisk]
GO
ALTER TABLE [dbo].[Ejendom] ADD  DEFAULT (newid()) FOR [EjendomIdentity]
GO
ALTER TABLE [dbo].[Ejendom] ADD  DEFAULT ((0)) FOR [BFENummer]
GO
ALTER TABLE [dbo].[EmailKontoExchangeConfiguration] ADD  DEFAULT ((0)) FOR [ExchangeOnlineAuthenticationMethod]
GO
ALTER TABLE [dbo].[EmneOrd] ADD  CONSTRAINT [DF_tblEmneOrd_bAktiv]  DEFAULT ((1)) FOR [ErAktiv]
GO
ALTER TABLE [dbo].[EmnePlan] ADD  DEFAULT ((0)) FOR [AnvendDelforloeb]
GO
ALTER TABLE [dbo].[EmnePlan] ADD  DEFAULT ((0)) FOR [RequireFacet]
GO
ALTER TABLE [dbo].[EmnePlan] ADD  DEFAULT ((0)) FOR [AllowChangingNummer]
GO
ALTER TABLE [dbo].[EmnePlan] ADD  CONSTRAINT [DF_EmnePlan_EmnePlanNummerType]  DEFAULT ((0)) FOR [EmnePlanNummerType]
GO
ALTER TABLE [dbo].[EmnePlan] ADD  CONSTRAINT [DF_EmnePlan_NySagBeskyttes]  DEFAULT ((0)) FOR [NySagBeskyttes]
GO
ALTER TABLE [dbo].[EmnePlan] ADD  DEFAULT ((0)) FOR [TilladOprettlseUdFraudgaaetNummer]
GO
ALTER TABLE [dbo].[EmnePlan] ADD  CONSTRAINT [DF_EmnePlan_BrugLavesteNiveau]  DEFAULT ((0)) FOR [BrugLavesteNiveau]
GO
ALTER TABLE [dbo].[EmneplanOpdatering] ADD  CONSTRAINT [DF_EmneplanOpdatering_TjekInterval]  DEFAULT ((30)) FOR [TjekInterval]
GO
ALTER TABLE [dbo].[EmneplanOpdatering] ADD  CONSTRAINT [DF_EmneplanOpdatering_Aktiv]  DEFAULT ((0)) FOR [Aktiv]
GO
ALTER TABLE [dbo].[Erindring] ADD  CONSTRAINT [DF_Erindring_ErAfsluttet]  DEFAULT ((0)) FOR [ErAfsluttet]
GO
ALTER TABLE [dbo].[Erindring] ADD  DEFAULT ((0)) FOR [ErAnnulleret]
GO
ALTER TABLE [dbo].[Erindring] ADD  CONSTRAINT [DF_Erindring_PopupStatus]  DEFAULT ((0)) FOR [PopupStatus]
GO
ALTER TABLE [dbo].[Erindring] ADD  CONSTRAINT [DF_Erindring_KopierEfterUdfoerelse]  DEFAULT ((0)) FOR [KopierEfterUdfoerelse]
GO
ALTER TABLE [dbo].[Erindring] ADD  CONSTRAINT [DF_Erindring_ReturEfterUdfoerelse]  DEFAULT ((0)) FOR [ReturEfterUdfoerelse]
GO
ALTER TABLE [dbo].[Erindring] ADD  CONSTRAINT [DF_Erindring_ProcessPostAction]  DEFAULT ((0)) FOR [ProcessPostAction]
GO
ALTER TABLE [dbo].[ErindringSkabelon] ADD  DEFAULT ((0)) FOR [Normtid]
GO
ALTER TABLE [dbo].[ErindringTypeOpslag] ADD  DEFAULT ((0)) FOR [SkjulErindring]
GO
ALTER TABLE [dbo].[ErindringTypeOpslag] ADD  DEFAULT ((0)) FOR [TilladKunSystemhaandtering]
GO
ALTER TABLE [dbo].[FagOmraade] ADD  DEFAULT (newid()) FOR [FagomraadeIdentity]
GO
ALTER TABLE [dbo].[Firma] ADD  CONSTRAINT [DF_Firma_KontaktForm]  DEFAULT ((1)) FOR [KontaktForm]
GO
ALTER TABLE [dbo].[Firma] ADD  DEFAULT ((0)) FOR [ErJuridiskEnhed]
GO
ALTER TABLE [dbo].[Firma] ADD  DEFAULT ((0)) FOR [TilmeldtDigitalPost]
GO
ALTER TABLE [dbo].[Firma] ADD  DEFAULT (newid()) FOR [FirmaIdentity]
GO
ALTER TABLE [dbo].[FirmaPart] ADD  CONSTRAINT [DF_FirmaPart_Oprettet]  DEFAULT (getdate()) FOR [Oprettet]
GO
ALTER TABLE [dbo].[Forloeb] ADD  CONSTRAINT [DF_Forloeb_Tidspunkt]  DEFAULT (getdate()) FOR [Tidspunkt]
GO
ALTER TABLE [dbo].[ForloebTypeOpslag] ADD  CONSTRAINT [DF_ForloebTypeOpslag_IsDetail]  DEFAULT ((0)) FOR [IsDetail]
GO
ALTER TABLE [dbo].[GeneratorIndstillinger] ADD  CONSTRAINT [DF_GeneratorIndstillinger_Tilbagejournalisering]  DEFAULT ((0)) FOR [Tilbagejournalisering]
GO
ALTER TABLE [dbo].[GeneratorIndstillinger] ADD  CONSTRAINT [DF_GeneratorIndstillinger_VisDatoOgStedUnderBeslutning]  DEFAULT ((0)) FOR [VisBeslutningsvejUnderBeslutning]
GO
ALTER TABLE [dbo].[GeneratorIndstillinger] ADD  CONSTRAINT [DF_GeneratorIndstillinger_BilagslistePlacering]  DEFAULT ((0)) FOR [BilagslistePlacering]
GO
ALTER TABLE [dbo].[GeneratorIndstillinger] ADD  CONSTRAINT [DF_GeneratorIndstillinger_OmgivIndstillingslinjerMedTabel]  DEFAULT ((1)) FOR [OmgivIndstillingslinjerMedTabel]
GO
ALTER TABLE [dbo].[GeneratorIndstillinger] ADD  CONSTRAINT [DF_GeneratorIndstillinger_MedtagTommeFelter]  DEFAULT ((0)) FOR [MedtagTommeFelter]
GO
ALTER TABLE [dbo].[GeneratorIndstillinger] ADD  CONSTRAINT [DF_GeneratorIndstillinger_MedtagTomtBeslutningsfelt]  DEFAULT ((0)) FOR [MedtagTomtBeslutningsfelt]
GO
ALTER TABLE [dbo].[Geometri] ADD  CONSTRAINT [DF_Areal_Oprettet]  DEFAULT (getdate()) FOR [Oprettet]
GO
ALTER TABLE [dbo].[GeometriFormatOpslag] ADD  CONSTRAINT [DF_GeometriFormat_IsBuiltin]  DEFAULT ((0)) FOR [IsBuiltin]
GO
ALTER TABLE [dbo].[GridLayout] ADD  CONSTRAINT [DF_GridLayout_SplitterHorizontal]  DEFAULT ((1)) FOR [SplitterHorizontal]
GO
ALTER TABLE [dbo].[Gruppering] ADD  DEFAULT ((1)) FOR [Aktiv]
GO
ALTER TABLE [dbo].[HaendelseLog] ADD  CONSTRAINT [DF_HaendelseLog_LogDate]  DEFAULT (getdate()) FOR [LogDate]
GO
ALTER TABLE [dbo].[HeartbeatHistory] ADD  CONSTRAINT [DF_HeartbeatHistory_Tidspunkt]  DEFAULT (getdate()) FOR [Tidspunkt]
GO
ALTER TABLE [dbo].[JournalArkNote] ADD  CONSTRAINT [DF_JournalArkNote_Oprettet]  DEFAULT (getdate()) FOR [Oprettet]
GO
ALTER TABLE [dbo].[JournalArkNote] ADD  DEFAULT ((1)) FOR [OmfattetAfAktindsigt]
GO
ALTER TABLE [dbo].[JournalArkNote] ADD  DEFAULT (newid()) FOR [JournalArkNoteIdentity]
GO
ALTER TABLE [dbo].[Kladde] ADD  CONSTRAINT [DF_Kladde_KeepCheckedOut]  DEFAULT ((0)) FOR [KeepCheckedOut]
GO
ALTER TABLE [dbo].[Kladde] ADD  CONSTRAINT [DF_Kladde_KladdeFletteStrategi]  DEFAULT ((1)) FOR [KladdeFletteStrategi]
GO
ALTER TABLE [dbo].[Kladde] ADD  CONSTRAINT [DF_Kladde_KladdeRedigeringGenoptaget]  DEFAULT ((0)) FOR [KladdeRedigeringGenoptaget]
GO
ALTER TABLE [dbo].[Kladde] ADD  DEFAULT ((0)) FOR [DeletedState]
GO
ALTER TABLE [dbo].[Kladde] ADD  DEFAULT ((1)) FOR [IndexingStatus]
GO
ALTER TABLE [dbo].[Kladde] ADD  DEFAULT (NULL) FOR [KladdeArt]
GO
ALTER TABLE [dbo].[KladdePart] ADD  CONSTRAINT [DF_KladdePart_Status]  DEFAULT ((0)) FOR [Status]
GO
ALTER TABLE [dbo].[KladdeRegistrering] ADD  DEFAULT ((0)) FOR [ErBeskyttet]
GO
ALTER TABLE [dbo].[KladdeRegistrering] ADD  DEFAULT ((0)) FOR [DeletedState]
GO
ALTER TABLE [dbo].[KnownFileTypeOpslag] ADD  CONSTRAINT [DF_KnownFileType_OpenInBrowser]  DEFAULT ((1)) FOR [OpensInBrowser]
GO
ALTER TABLE [dbo].[KnownFileTypeOpslag] ADD  CONSTRAINT [DF_KnownFileTypeOpslag_WatchTechnique]  DEFAULT ((1)) FOR [WatchTechnique]
GO
ALTER TABLE [dbo].[KnownFileTypeOpslag] ADD  CONSTRAINT [DF_KnownFileTypeOpslag_ChangeCheckTechnique]  DEFAULT ((1)) FOR [ChangeCheckTechnique]
GO
ALTER TABLE [dbo].[KnownFileTypeOpslag] ADD  CONSTRAINT [DF_KnownFileTypeOpslag_KanBrugesSomKladde]  DEFAULT ((0)) FOR [KanBrugesSomKladde]
GO
ALTER TABLE [dbo].[Log] ADD  CONSTRAINT [DF_Log_Occurences]  DEFAULT ((1)) FOR [Occurences]
GO
ALTER TABLE [dbo].[Lokation] ADD  CONSTRAINT [DF_Lokation_Historisk]  DEFAULT ((0)) FOR [Historisk]
GO
ALTER TABLE [dbo].[Lokation] ADD  DEFAULT (newid()) FOR [LokationIdentity]
GO
ALTER TABLE [dbo].[Mail] ADD  DEFAULT ((0)) FOR [IsSentItem]
GO
ALTER TABLE [dbo].[Mail] ADD  DEFAULT ((0)) FOR [MailType]
GO
ALTER TABLE [dbo].[MailRecipient] ADD  DEFAULT ((0)) FOR [ContextSagID]
GO
ALTER TABLE [dbo].[MapNemJournaliseringSagSkabelon] ADD  DEFAULT ((0)) FOR [Aktiv]
GO
ALTER TABLE [dbo].[MapSag] ADD  CONSTRAINT [DF_MapSag_MaxSagsnummerLaengde]  DEFAULT ((0)) FOR [MaxSagsnummerLaengde]
GO
ALTER TABLE [dbo].[MapSag] ADD  CONSTRAINT [DF_MapSag_SaetSagspartSomPrimaer]  DEFAULT ((0)) FOR [SaetSagspartSomPrimaer]
GO
ALTER TABLE [dbo].[Matrikel] ADD  CONSTRAINT [DF_Matrikel_Oprettet]  DEFAULT (getdate()) FOR [Oprettet]
GO
ALTER TABLE [dbo].[Matrikel] ADD  CONSTRAINT [DF_Matrikel_Historisk]  DEFAULT ((0)) FOR [Historisk]
GO
ALTER TABLE [dbo].[Matrikel] ADD  DEFAULT ((1)) FOR [ArtID]
GO
ALTER TABLE [dbo].[Matrikel] ADD  DEFAULT (newid()) FOR [MatrikelIdentity]
GO
ALTER TABLE [dbo].[Matrikel] ADD  DEFAULT ((0)) FOR [BFENummer]
GO
ALTER TABLE [dbo].[Moede] ADD  DEFAULT (newid()) FOR [MoedeIdentity]
GO
ALTER TABLE [dbo].[Moede] ADD  CONSTRAINT [DF_Moede_ErSkabelon]  DEFAULT ((0)) FOR [ErSkabelon]
GO
ALTER TABLE [dbo].[Nyhed] ADD  CONSTRAINT [DF_Nyhed_OprettetDato]  DEFAULT (getdate()) FOR [OprettetDato]
GO
ALTER TABLE [dbo].[Nyhed] ADD  CONSTRAINT [DF_Nyhed_Udgaaet]  DEFAULT ((0)) FOR [ErUdgaaet]
GO
ALTER TABLE [dbo].[Person] ADD  CONSTRAINT [DF_Person_KontaktForm]  DEFAULT ((1)) FOR [KontaktForm]
GO
ALTER TABLE [dbo].[Person] ADD  DEFAULT ((0)) FOR [TilmeldtDigitalPost]
GO
ALTER TABLE [dbo].[Person] ADD  DEFAULT (newid()) FOR [PersonIdentity]
GO
ALTER TABLE [dbo].[PessimisticLockInfo] ADD  CONSTRAINT [DF_PessimisticLockInfo_LockType]  DEFAULT ((1)) FOR [LockType]
GO
ALTER TABLE [dbo].[PropertyBagItem] ADD  CONSTRAINT [DF_PropertyBagItem_OwnerID]  DEFAULT ((0)) FOR [OwnerID]
GO
ALTER TABLE [dbo].[Publisering] ADD  CONSTRAINT [DF_Publicering_Oprettet]  DEFAULT (getdate()) FOR [Oprettet]
GO
ALTER TABLE [dbo].[Publisering] ADD  CONSTRAINT [DF_Publicering_Publiceres]  DEFAULT (getdate()) FOR [Publiseres]
GO
ALTER TABLE [dbo].[Publisering] ADD  CONSTRAINT [DF_Publicering_ErPubliceret]  DEFAULT ((0)) FOR [ErPubliseret]
GO
ALTER TABLE [dbo].[Publisering] ADD  CONSTRAINT [DF_Publicering_ErPrivatPublicering]  DEFAULT ((0)) FOR [ErPrivatPublisering]
GO
ALTER TABLE [dbo].[PubliseringDokument] ADD  CONSTRAINT [DF_PubliseringDokument_ErPubliseretFoer]  DEFAULT ((0)) FOR [ErPubliseretFoer]
GO
ALTER TABLE [dbo].[PubliseringPlan] ADD  CONSTRAINT [DF_PubliseringPlan_Aktiv]  DEFAULT ((1)) FOR [Aktiv]
GO
ALTER TABLE [dbo].[PubliseringTarget] ADD  CONSTRAINT [DF_PubliseringTarget_FileOutputBehavior]  DEFAULT ((0)) FOR [FileOutputBehavior]
GO
ALTER TABLE [dbo].[PubliseringTarget] ADD  CONSTRAINT [DF_PubliseringTarget_FolderNameBehavior]  DEFAULT ((0)) FOR [FolderNameBehavior]
GO
ALTER TABLE [dbo].[PubliseringTarget] ADD  CONSTRAINT [DF_PubliseringTarget_FileOutputRule]  DEFAULT ((0)) FOR [FileOutputRule]
GO
ALTER TABLE [dbo].[PubliseringTarget] ADD  CONSTRAINT [DF_PubliseringTarget_PrepareRule]  DEFAULT ((2)) FOR [PrepareRule]
GO
ALTER TABLE [dbo].[QueueCommand] ADD  CONSTRAINT [DF_Que_Oprettet]  DEFAULT (getdate()) FOR [Oprettet]
GO
ALTER TABLE [dbo].[QueueCommand] ADD  CONSTRAINT [DF_Que_Status]  DEFAULT ((1)) FOR [Status]
GO
ALTER TABLE [dbo].[QueueCommand] ADD  CONSTRAINT [DF_QueueCommand_Behavior]  DEFAULT ((1)) FOR [Behavior]
GO
ALTER TABLE [dbo].[QueueCommandFile] ADD  DEFAULT ((0)) FOR [Sortering]
GO
ALTER TABLE [dbo].[RequestLog] ADD  DEFAULT (sysdatetime()) FOR [Logged]
GO
ALTER TABLE [dbo].[Ressource] ADD  CONSTRAINT [DF_Ressource_Identitet]  DEFAULT (newid()) FOR [Identitet]
GO
ALTER TABLE [dbo].[Ressource] ADD  CONSTRAINT [DF_Ressource_Kategori]  DEFAULT ((0)) FOR [Kategori]
GO
ALTER TABLE [dbo].[RolleOpslag] ADD  CONSTRAINT [DF_Rolle_IsBuiltin]  DEFAULT ((0)) FOR [IsBuiltin]
GO
ALTER TABLE [dbo].[RolleTildeling] ADD  CONSTRAINT [DF_RolleTildeling_Roller]  DEFAULT ((0)) FOR [Roller]
GO
ALTER TABLE [dbo].[Sag] ADD  CONSTRAINT [DF_Sag_Identity]  DEFAULT (newid()) FOR [SagIdentity]
GO
ALTER TABLE [dbo].[Sag] ADD  CONSTRAINT [DF__tblJourna__bBesk__687E5358]  DEFAULT ((0)) FOR [ErBeskyttet]
GO
ALTER TABLE [dbo].[Sag] ADD  CONSTRAINT [DF_tblJournal_JournalDato]  DEFAULT (getdate()) FOR [Created]
GO
ALTER TABLE [dbo].[Sag] ADD  CONSTRAINT [DF_tJournal_dSidstRettet]  DEFAULT (getdate()) FOR [LastChanged]
GO
ALTER TABLE [dbo].[Sag] ADD  CONSTRAINT [DF_Sag_ArkivStatusID]  DEFAULT ((1)) FOR [ArkivAfklaringStatusID]
GO
ALTER TABLE [dbo].[SagEksternIdentitet] ADD  CONSTRAINT [DF_SagEksternIdentitet_Oprettet]  DEFAULT (getdate()) FOR [Oprettet]
GO
ALTER TABLE [dbo].[SagEksternIdentitet] ADD  CONSTRAINT [DF_SagEksternIdentitet_Status]  DEFAULT ((0)) FOR [Status]
GO
ALTER TABLE [dbo].[SagHistorikStatus] ADD  CONSTRAINT [DF_SagHistorikStatus_Tidspunkt]  DEFAULT (getdate()) FOR [Tidspunkt]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((0)) FOR [PartForlangAltid]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((0)) FOR [PartForlangAltidPrimaer]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((0)) FOR [PartAnvendIkke]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((0)) FOR [GenstandForlangAltid]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [Aktiv]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT (newid()) FOR [SagSkabelonIdentity]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [SagsTypeId]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [SagsTitelKanAendresFoerOprettelse]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [SagsTitelKanAendresEfterOprettelse]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [AnsaettelsesstedKanAendresFoerOprettelse]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [AnsaettelsesstedKanAendresEfterOprettelse]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [StyringsreolKanAendresFoerOprettelse]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [StyringsreolKanAendresEfterOprettelse]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [DelforloebKanTilfoejesFoerOprettelse]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [DelforloebKanTilfoejesEfterOprettelse]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [DelforloebKanFjernesFoerOprettelse]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [DelforloebKanFjernesEfterOprettelse]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [ErBeskyttetKanAendresFoerOprettelse]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [ErBeskyttetKanAendresEfterOprettelse]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [AdgangslisteKanAendresFoerOprettelse]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [AdgangslisteKanAendresEfterOprettelse]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [EmneplanNummerOgFacetKanAendresFoerOprettelse]
GO
ALTER TABLE [dbo].[SagSkabelon] ADD  DEFAULT ((1)) FOR [EmneplanNummerOgFacetKanAendresEfterOprettelse]
GO
ALTER TABLE [dbo].[SagSkabelonPart] ADD  DEFAULT ((0)) FOR [Primaer]
GO
ALTER TABLE [dbo].[SagsNummer] ADD  CONSTRAINT [DF_SagsNummer_SekvensNummer]  DEFAULT ((1)) FOR [SekvensNummer]
GO
ALTER TABLE [dbo].[SagsNummer] ADD  CONSTRAINT [DF_SagsNummer_Aarstal]  DEFAULT (datepart(year,getdate())) FOR [Aarstal]
GO
ALTER TABLE [dbo].[SagsPart] ADD  CONSTRAINT [DF_SagsPart_Oprettet]  DEFAULT (getdate()) FOR [Oprettet]
GO
ALTER TABLE [dbo].[SagsStatus] ADD  CONSTRAINT [DF_SagsStatus_RequireComments]  DEFAULT ((0)) FOR [RequireComments]
GO
ALTER TABLE [dbo].[SagsStatus] ADD  CONSTRAINT [DF_SagsStatus_IsDeleted]  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[SagsStatus] ADD  DEFAULT ((0)) FOR [SagsForklaede]
GO
ALTER TABLE [dbo].[SagsVisit] ADD  CONSTRAINT [DF_JournalVisit_Tidspunkt]  DEFAULT (getdate()) FOR [Tidspunkt]
GO
ALTER TABLE [dbo].[SecuritySetBrugere] ADD  CONSTRAINT [DF_SecuritySetBrugere_ErPermanent]  DEFAULT ((0)) FOR [ErPermanent]
GO
ALTER TABLE [dbo].[SikkerhedsbeslutningOpslag] ADD  CONSTRAINT [DF_Sikkerhedsbeslutning_Roller]  DEFAULT ((0)) FOR [TildelteRoller]
GO
ALTER TABLE [dbo].[SikkerhedsbeslutningOpslag] ADD  CONSTRAINT [DF_Sikkerhedsbeslutning_BypassRoller]  DEFAULT ((0)) FOR [BypassRoller]
GO
ALTER TABLE [dbo].[SikkerhedsbeslutningOpslag] ADD  CONSTRAINT [DF_Sikkerhedsbeslutning_Kategori]  DEFAULT ((0)) FOR [Type]
GO
ALTER TABLE [dbo].[SikkerhedsbeslutningOpslag] ADD  CONSTRAINT [DF_SikkerhedsbeslutningOpslag_ErUdvalgsspecifik]  DEFAULT ((0)) FOR [ErUdvalgsspecifik]
GO
ALTER TABLE [dbo].[Skabelon] ADD  DEFAULT ('False') FOR [VisTekstblokvaelger]
GO
ALTER TABLE [dbo].[SkabelonTekstblok] ADD  DEFAULT ('') FOR [TekstRtf]
GO
ALTER TABLE [dbo].[SkabelonType] ADD  CONSTRAINT [DF_tblSkabelontype_SkabelontypeGruppeIDRef]  DEFAULT ((0)) FOR [SkabelonTypeGruppeID]
GO
ALTER TABLE [dbo].[Stylesheet] ADD  CONSTRAINT [DF_Stylesheet_Gruppering]  DEFAULT ((1)) FOR [Gruppering]
GO
ALTER TABLE [dbo].[Styringsreol] ADD  DEFAULT ((0)) FOR [EksterntMapped]
GO
ALTER TABLE [dbo].[Styringsreol] ADD  DEFAULT ((0)) FOR [ReadOnly]
GO
ALTER TABLE [dbo].[StyringsreolHylde] ADD  CONSTRAINT [DF_StyringsreolHylde_Normtidstype]  DEFAULT ((1)) FOR [Normtidstype]
GO
ALTER TABLE [dbo].[StyringsreolHylde] ADD  CONSTRAINT [DF_StyringsreolHylde_Skjult]  DEFAULT ((0)) FOR [Skjult]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_VisRedigerMedWordKnapPaaDagsordenpunkt]  DEFAULT ((0)) FOR [VisRedigerMedWordKnapPaaDagsordenpunkt]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_DefaultTemporaryFolderPath]  DEFAULT (N'[MyDocuments]\SBSYS\Temp') FOR [DefaultTemporaryFolderPath]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_DefaultCheckoutFolderPath]  DEFAULT (N'[MyDocuments]\SBSYS\Kladder') FOR [DefaultCheckoutFolderPath]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_DagsordenSystemAktivt]  DEFAULT ((1)) FOR [DagsordenSystemAktivt]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_MaxJournaliseringFilesize]  DEFAULT ((50)) FOR [JournaliseringMaxFilesize]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_KontrollerCheckOutTilSammeMaskineVedKladeJournalisering]  DEFAULT ((1)) FOR [KontrollerCheckOutTilSammeMaskineVedKladeJournalisering]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_HelpSystemUrl]  DEFAULT (N'http://www.sbsys.dk/Hjaelp/Show.aspx?N={0}&V={1}&I={2}') FOR [HelpSystemUrl]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_TilladAutomatiskLogon]  DEFAULT ((0)) FOR [TilladAutomatiskLogon]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_SynkroniserADEgenskaber]  DEFAULT ((1)) FOR [SynkroniserADEgenskaber]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_SynkroniserADGrupperMedRoller]  DEFAULT ((0)) FOR [SynkroniserADGrupperMedRoller]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_DefaultWorkFolderPath]  DEFAULT (N'[MyDocuments]\SBSYS\Work') FOR [DefaultWorkFolderPath]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_PostlisteQuery]  DEFAULT ('select distinct DokumentRegistrering.ID from Dokument inner join DokumentRegistrering on DokumentRegistrering.DokumentID = Dokument.ID where PaaPostliste = 1 and datediff(Day, Oprettet, getdate()) = 0') FOR [PostlisteQuery]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_TilladAfslutUdenKladdeArkivering]  DEFAULT ((0)) FOR [TilladAfslutUdenKladdeArkivering]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_TilladFletningVhaTekstbehandler]  DEFAULT ((0)) FOR [TilladFletningVhaTekstbehandler]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_PaaSagStartView]  DEFAULT ((4)) FOR [PaaSagStartView]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_GrupperFaneblade]  DEFAULT ((0)) FOR [GrupperFaneblade]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_PubliseringFolderRootLocked]  DEFAULT ((0)) FOR [ForcePubliseringFolderRoot]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_AnvendGenstande]  DEFAULT ((1)) FOR [AnvendGenstande]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_VisOrdetÅbenIDagsordenOverskrift]  DEFAULT ((1)) FOR [VisOrdetÅbenIDagsordenOverskrift]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_DefaultDagsordenerVedMødeoprettelse]  DEFAULT ((15)) FOR [DefaultDagsordenerVedMødeoprettelse]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_KanPublicereDagsordenerMedKladdeBilag]  DEFAULT ((0)) FOR [KanPublicereDagsordenerMedKladdeBilag]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_BiholdUdvalgsMedlemmerPaaAdgangsliste]  DEFAULT ((0)) FOR [BiholdUdvalgsMedlemmerPaaAdgangsliste]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_JournalNoteRedigeringsPeriode]  DEFAULT ((36)) FOR [JournalNoteRedigeringsPeriode]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_AnvendDokumentGalleri]  DEFAULT ((0)) FOR [AnvendDokumentGalleri]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_TvingKommentarVedLogfejl]  DEFAULT ((0)) FOR [TvingKommentarVedLogfejl]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_SendErindringTilSagsBehandlerVedJournalisering]  DEFAULT ((1)) FOR [SendErindringTilSagsBehandlerVedJournalisering]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_InstallationIdentity]  DEFAULT (newid()) FOR [InstallationIdentity]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_SendFejlUrl]  DEFAULT (N'mailto:support@ditmer.dk?subject=Fejl i Sbsys.Net version {0}&body={1}') FOR [SendFejlUrl]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  CONSTRAINT [DF_SystemConfiguration_SendErindringTilNySagsBehandlerVedSkiftSagsbehandler]  DEFAULT ((1)) FOR [SendErindringTilNySagsBehandlerVedSkiftSagsbehandler]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  DEFAULT ((0)) FOR [AnvendMaxLaengdePaaDagsordenBilag]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  DEFAULT ((40)) FOR [MaxLaengdePaaDagsordenBilag]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  DEFAULT ((0)) FOR [AnvendDagsordenpunktVersioner]
GO
ALTER TABLE [dbo].[SystemConfiguration] ADD  DEFAULT ((0)) FOR [FastholdUdvalgOverskrift]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_ErindringTypeRingTilID]  DEFAULT ((1)) FOR [ErindringTypeRingTilID]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_ErindringTypeBemaerkID]  DEFAULT ((2)) FOR [ErindringTypeBemaerkID]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_ErindringTypeLaesID]  DEFAULT ((3)) FOR [ErindringTypeLaesID]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_ErindringTypeOpfoelgID]  DEFAULT ((4)) FOR [ErindringTypeOpfoelgID]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_DokumentArtJournaliserFilID]  DEFAULT ((6)) FOR [DokumentArtJournaliserFilID]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_DokumentArtDefaultID]  DEFAULT ((6)) FOR [DokumentArtDefaultID]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_DokumentArtJournaliserSendtMailID]  DEFAULT ((2)) FOR [DokumentArtJournaliserSendtMailID]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_DokumentArtJournaliserModtagetMailID]  DEFAULT ((1)) FOR [DokumentArtJournaliserModtagetMailID]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_DokumentArtJournaliserPapirID]  DEFAULT ((6)) FOR [DokumentArtJournaliserPapirID]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_DokumentArtJournaliserScanningID]  DEFAULT ((1)) FOR [DokumentArtJournaliserScanningID]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_DokumentArtJournaliserNotatID]  DEFAULT ((5)) FOR [DokumentArtJournaliserNotatID]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_DokumentArtJournaliserInterntID]  DEFAULT ((3)) FOR [DokumentArtJournaliserInterntID]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_DokumentArtJournaliserTelefonID]  DEFAULT ((6)) FOR [DokumentArtJournaliserTelefonID]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_SagsStatusID]  DEFAULT ((0)) FOR [SagsStatusID]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_EmneplanID]  DEFAULT ((1)) FOR [EmneplanID]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_DokumentArtJournaliserSendtMailID1]  DEFAULT ((4)) FOR [DokumentArtJournaliserTilbageJournaliserDOP]
GO
ALTER TABLE [dbo].[SystemDefaults] ADD  CONSTRAINT [DF_SystemDefaults_ArkivStatusID]  DEFAULT ((1)) FOR [ArkivAfklaringStatusID]
GO
ALTER TABLE [dbo].[TidsPosteringKategori] ADD  DEFAULT ((0)) FOR [Aktiv]
GO
ALTER TABLE [dbo].[TrustedAssembly] ADD  CONSTRAINT [DF_TrustedAssembly_Enabled]  DEFAULT ((0)) FOR [Enabled]
GO
ALTER TABLE [dbo].[Udvalg] ADD  DEFAULT (newid()) FOR [UdvalgIdentity]
GO
ALTER TABLE [dbo].[Udvalg] ADD  CONSTRAINT [DF_Udvalg_Sortering]  DEFAULT ((-1)) FOR [Sortering]
GO
ALTER TABLE [dbo].[Udvalg] ADD  CONSTRAINT [DF_Udvalg_IndstillingStandardTekst]  DEFAULT (N'Direktionen indstiller,') FOR [IndstillingStandardTekst]
GO
ALTER TABLE [dbo].[Udvalg] ADD  CONSTRAINT [DF_Udvalg_MoedelokaleStandardTekst]  DEFAULT (N'Ikke angivet') FOR [StedStandardTekst]
GO
ALTER TABLE [dbo].[Udvalg] ADD  CONSTRAINT [DF_Udvalg_RydIndstillingVedKopiering]  DEFAULT ((1)) FOR [RydIndstillingVedKopiering]
GO
ALTER TABLE [dbo].[Udvalg] ADD  CONSTRAINT [DF_Udvalg_TekstForBesluttendeUdvalg]  DEFAULT (N'Udvalget har beslutningskompetence for punkter markeret med *.') FOR [TekstForBesluttendeUdvalg]
GO
ALTER TABLE [dbo].[Udvalg] ADD  DEFAULT (N'NYFORK') FOR [Forkortelse]
GO
ALTER TABLE [dbo].[Udvalgsmedlem] ADD  DEFAULT ((-1)) FOR [Sortering]
GO
ALTER TABLE [dbo].[Udvalgsperson] ADD  DEFAULT ((1)) FOR [ErAktiv]
GO
ALTER TABLE [dbo].[Udvalgsstruktur] ADD  CONSTRAINT [DF_Udvalgsstruktur_Sortering]  DEFAULT ((-1)) FOR [Sortering]
GO
ALTER TABLE [dbo].[UsageLog] ADD  CONSTRAINT [DF_UsageLog_LogDate]  DEFAULT (getdate()) FOR [LogDate]
GO
ALTER TABLE [dbo].[UsageLog] ADD  CONSTRAINT [DF_UsageLog_EventType]  DEFAULT ((1)) FOR [UsageType]
GO
ALTER TABLE [dbo].[Vej] ADD  CONSTRAINT [DF_Vej_Oprettet]  DEFAULT (getdate()) FOR [Oprettet]
GO
ALTER TABLE [dbo].[Vej] ADD  CONSTRAINT [DF_Vej_Historisk]  DEFAULT ((0)) FOR [Historisk]
GO
ALTER TABLE [dbo].[Vej] ADD  DEFAULT (newid()) FOR [VejIdentity]
GO
ALTER TABLE [dbo].[WebApiAppAccess] ADD  DEFAULT ((0)) FOR [AllowAuthorizationCodeGrant]
GO
ALTER TABLE [dbo].[WebApiAppAccess] ADD  DEFAULT ((0)) FOR [AllowImplicitCodeGrant]
GO
ALTER TABLE [dbo].[WebApiAppAccess] ADD  DEFAULT ((0)) FOR [AllowResourceOwnerCredentialsGrant]
GO
ALTER TABLE [dbo].[WebApiAppAccess] ADD  DEFAULT ((0)) FOR [AllowClientCredentialsGrant]
GO
ALTER TABLE [dbo].[WebApiAppAccess] ADD  DEFAULT ((14)) FOR [RefreshTokenExpiration]
GO
ALTER TABLE [dbo].[WebApiRefreshToken] ADD  DEFAULT ((0)) FOR [Revoked]
GO
ALTER TABLE [dbo].[WebWidget] ADD  DEFAULT ((1)) FOR [Indlejret]
GO
ALTER TABLE [dbo].[WebWidget] ADD  DEFAULT ((0)) FOR [ErBU]
GO
ALTER TABLE [dbo].[WordGeneratorDagsordenExtension] ADD  CONSTRAINT [DF_WordGeneratorDagsordenExtension_Underskriftsark]  DEFAULT ((1)) FOR [TvungenSideskiftEfterPunkt]
GO
ALTER TABLE [dbo].[WordGeneratorUdvalgExtension] ADD  CONSTRAINT [DF_WordGeneratorUdvalgExtension_TvungenSideskiftEfterPunkt]  DEFAULT ((1)) FOR [TvungenSideskiftEfterPunkt]
GO
ALTER TABLE [dbo].[WordGeneratorUdvalgExtension] ADD  CONSTRAINT [DF_WordGeneratorUdvalgExtension_UdrykPunktnummer]  DEFAULT ((0)) FOR [UdrykPunktnummer]
GO
ALTER TABLE [dbo].[WordGeneratorUdvalgExtension] ADD  CONSTRAINT [DF_WordGeneratorUdvalgExtension_FjernLinks]  DEFAULT ((0)) FOR [FjernLinks]
GO
ALTER TABLE [dbo].[AdministrativProfilAnsaettelsessteder]  WITH NOCHECK ADD  CONSTRAINT [FK_AdministrativProfil_Profil] FOREIGN KEY([AdministrativProfilID])
REFERENCES [dbo].[AdministrativProfil] ([ID])
GO
ALTER TABLE [dbo].[AdministrativProfilAnsaettelsessteder] CHECK CONSTRAINT [FK_AdministrativProfil_Profil]
GO
ALTER TABLE [dbo].[AdministrativProfilAnsaettelsessteder]  WITH CHECK ADD  CONSTRAINT [GK_AdministrativProfil_Ansaettelessted] FOREIGN KEY([AnsaettelsesstedID])
REFERENCES [dbo].[Ansaettelsessted] ([ID])
GO
ALTER TABLE [dbo].[AdministrativProfilAnsaettelsessteder] CHECK CONSTRAINT [GK_AdministrativProfil_Ansaettelessted]
GO
ALTER TABLE [dbo].[AdministrativProfilBruger]  WITH CHECK ADD  CONSTRAINT [FK_AdministrativProfilBruger_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[AdministrativProfilBruger] CHECK CONSTRAINT [FK_AdministrativProfilBruger_Bruger]
GO
ALTER TABLE [dbo].[AdministrativProfilBruger]  WITH NOCHECK ADD  CONSTRAINT [FK_AdminProfilBruger_profil] FOREIGN KEY([AdministrativProfilID])
REFERENCES [dbo].[AdministrativProfil] ([ID])
GO
ALTER TABLE [dbo].[AdministrativProfilBruger] CHECK CONSTRAINT [FK_AdminProfilBruger_profil]
GO
ALTER TABLE [dbo].[AdministrativProfilRettigheder]  WITH CHECK ADD  CONSTRAINT [FK_AdministrativProfil_Rettighed] FOREIGN KEY([AdministrativProfilID])
REFERENCES [dbo].[AdministrativProfil] ([ID])
GO
ALTER TABLE [dbo].[AdministrativProfilRettigheder] CHECK CONSTRAINT [FK_AdministrativProfil_Rettighed]
GO
ALTER TABLE [dbo].[AdministrativProfilRettigheder]  WITH NOCHECK ADD  CONSTRAINT [FK_AdministrativProfil_rettigheder_sikkerhedsopslag] FOREIGN KEY([SikkerhedsbeslutningID])
REFERENCES [dbo].[SikkerhedsbeslutningOpslag] ([ID])
GO
ALTER TABLE [dbo].[AdministrativProfilRettigheder] CHECK CONSTRAINT [FK_AdministrativProfil_rettigheder_sikkerhedsopslag]
GO
ALTER TABLE [dbo].[AdresseGenstand]  WITH CHECK ADD  CONSTRAINT [FK_AdresseGenstand_Ejendom] FOREIGN KEY([EjendomID])
REFERENCES [dbo].[Ejendom] ([ID])
GO
ALTER TABLE [dbo].[AdresseGenstand] CHECK CONSTRAINT [FK_AdresseGenstand_Ejendom]
GO
ALTER TABLE [dbo].[AdresseGenstand]  WITH CHECK ADD  CONSTRAINT [FK_AdresseGenstand_KommuneOpslag] FOREIGN KEY([KommuneID])
REFERENCES [dbo].[KommuneOpslag] ([ID])
GO
ALTER TABLE [dbo].[AdresseGenstand] CHECK CONSTRAINT [FK_AdresseGenstand_KommuneOpslag]
GO
ALTER TABLE [dbo].[AktindsigtSaves]  WITH CHECK ADD  CONSTRAINT [FK_AktindsigtSaves_ToTable] FOREIGN KEY([BrugerId])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[AktindsigtSaves] CHECK CONSTRAINT [FK_AktindsigtSaves_ToTable]
GO
ALTER TABLE [dbo].[Ansaettelsessted]  WITH CHECK ADD  CONSTRAINT [FK_Ansaettelsessted_Adresse] FOREIGN KEY([PostAdresseID])
REFERENCES [dbo].[Adresse] ([ID])
GO
ALTER TABLE [dbo].[Ansaettelsessted] CHECK CONSTRAINT [FK_Ansaettelsessted_Adresse]
GO
ALTER TABLE [dbo].[Ansaettelsessted]  WITH CHECK ADD  CONSTRAINT [FK_Ansaettelsessted_DefaultSecuritySet] FOREIGN KEY([DefaultSagSecuritySetID])
REFERENCES [dbo].[SecuritySet] ([ID])
GO
ALTER TABLE [dbo].[Ansaettelsessted] CHECK CONSTRAINT [FK_Ansaettelsessted_DefaultSecuritySet]
GO
ALTER TABLE [dbo].[Ansaettelsessted]  WITH CHECK ADD  CONSTRAINT [FK_Ansaettelsessted_EmnePlan] FOREIGN KEY([DefaultEmneplanID])
REFERENCES [dbo].[EmnePlan] ([ID])
GO
ALTER TABLE [dbo].[Ansaettelsessted] CHECK CONSTRAINT [FK_Ansaettelsessted_EmnePlan]
GO
ALTER TABLE [dbo].[Ansaettelsessted]  WITH CHECK ADD  CONSTRAINT [FK_Ansaettelsessted_FagOmraade] FOREIGN KEY([FagomraadeID])
REFERENCES [dbo].[FagOmraade] ([ID])
GO
ALTER TABLE [dbo].[Ansaettelsessted] CHECK CONSTRAINT [FK_Ansaettelsessted_FagOmraade]
GO
ALTER TABLE [dbo].[Ansaettelsessted]  WITH CHECK ADD  CONSTRAINT [FK_Ansaettelsessted_FysiskAdresse] FOREIGN KEY([FysiskAdresseID])
REFERENCES [dbo].[Adresse] ([ID])
GO
ALTER TABLE [dbo].[Ansaettelsessted] CHECK CONSTRAINT [FK_Ansaettelsessted_FysiskAdresse]
GO
ALTER TABLE [dbo].[Ansaettelsessted]  WITH CHECK ADD  CONSTRAINT [FK_Ansaettelsessted_HierakiMedlem] FOREIGN KEY([HierakiMedlemID])
REFERENCES [dbo].[HierakiMedlem] ([ID])
GO
ALTER TABLE [dbo].[Ansaettelsessted] CHECK CONSTRAINT [FK_Ansaettelsessted_HierakiMedlem]
GO
ALTER TABLE [dbo].[AnsaettelsesstedEksternMapning]  WITH CHECK ADD  CONSTRAINT [FK_AnsaettelsesstedEksternMapning_Ansaettelsessted] FOREIGN KEY([AnsaettelsesstedID])
REFERENCES [dbo].[Ansaettelsessted] ([ID])
GO
ALTER TABLE [dbo].[AnsaettelsesstedEksternMapning] CHECK CONSTRAINT [FK_AnsaettelsesstedEksternMapning_Ansaettelsessted]
GO
ALTER TABLE [dbo].[AnsaettelsesstedEksternMapning]  WITH CHECK ADD  CONSTRAINT [FK_AnsaettelsesstedEksternMapning_Ansaettelsessted_Passiv] FOREIGN KEY([PassivAnsaettelsesstedID])
REFERENCES [dbo].[Ansaettelsessted] ([ID])
GO
ALTER TABLE [dbo].[AnsaettelsesstedEksternMapning] CHECK CONSTRAINT [FK_AnsaettelsesstedEksternMapning_Ansaettelsessted_Passiv]
GO
ALTER TABLE [dbo].[AnsaettelsesstedEksternMapning]  WITH NOCHECK ADD  CONSTRAINT [FK_AnsaettelsesstedEksternMapning_DefaultSikkerhdsGruppe] FOREIGN KEY([DefaultSikkerhedsGruppeID])
REFERENCES [dbo].[Sikkerhedsgruppe] ([ID])
GO
ALTER TABLE [dbo].[AnsaettelsesstedEksternMapning] CHECK CONSTRAINT [FK_AnsaettelsesstedEksternMapning_DefaultSikkerhdsGruppe]
GO
ALTER TABLE [dbo].[AnsaettelsesstedEksternMapning]  WITH NOCHECK ADD  CONSTRAINT [FK_AnsaettelsesstedEksternMapning_Sikkerhedsgruppe_passiv] FOREIGN KEY([PassivSikkerhedsGruppeID])
REFERENCES [dbo].[Sikkerhedsgruppe] ([ID])
GO
ALTER TABLE [dbo].[AnsaettelsesstedEksternMapning] CHECK CONSTRAINT [FK_AnsaettelsesstedEksternMapning_Sikkerhedsgruppe_passiv]
GO
ALTER TABLE [dbo].[AnsaettelsesstedStandardSikkerhedsGrupper]  WITH CHECK ADD  CONSTRAINT [FK_AnsaettelsesstedStandardSikkerhedsGrupper_Ansaettelsessted] FOREIGN KEY([AnsaettelsesstedID])
REFERENCES [dbo].[Ansaettelsessted] ([ID])
GO
ALTER TABLE [dbo].[AnsaettelsesstedStandardSikkerhedsGrupper] CHECK CONSTRAINT [FK_AnsaettelsesstedStandardSikkerhedsGrupper_Ansaettelsessted]
GO
ALTER TABLE [dbo].[AnsaettelsesstedStandardSikkerhedsGrupper]  WITH NOCHECK ADD  CONSTRAINT [FK_AnsaettelsesstedStandardSikkerhedsGrupper_Sikkerhedsgruppe] FOREIGN KEY([SikkerhedsgruppeID])
REFERENCES [dbo].[Sikkerhedsgruppe] ([ID])
GO
ALTER TABLE [dbo].[AnsaettelsesstedStandardSikkerhedsGrupper] CHECK CONSTRAINT [FK_AnsaettelsesstedStandardSikkerhedsGrupper_Sikkerhedsgruppe]
GO
ALTER TABLE [dbo].[ArkivPeriode]  WITH NOCHECK ADD  CONSTRAINT [FK_ArkivPeriode_ArkivPeriodeStatus] FOREIGN KEY([ArkivPeriodeStatusID])
REFERENCES [dbo].[ArkivPeriodeStatus] ([ID])
GO
ALTER TABLE [dbo].[ArkivPeriode] CHECK CONSTRAINT [FK_ArkivPeriode_ArkivPeriodeStatus]
GO
ALTER TABLE [dbo].[ArkivPeriode]  WITH CHECK ADD  CONSTRAINT [FK_ArkivPeriode_CreatedByBruger] FOREIGN KEY([CreatedByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[ArkivPeriode] CHECK CONSTRAINT [FK_ArkivPeriode_CreatedByBruger]
GO
ALTER TABLE [dbo].[ArkivPeriode]  WITH CHECK ADD  CONSTRAINT [FK_ArkivPeriode_LastChangedBruger] FOREIGN KEY([LastChangedByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[ArkivPeriode] CHECK CONSTRAINT [FK_ArkivPeriode_LastChangedBruger]
GO
ALTER TABLE [dbo].[Beskedfordeling]  WITH CHECK ADD  CONSTRAINT [FK_Beskedfordeling_DokumentKonverteringBestilling] FOREIGN KEY([DokumentKonverteringBestillingId])
REFERENCES [dbo].[DokumentKonverteringBestilling] ([ID])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Beskedfordeling] CHECK CONSTRAINT [FK_Beskedfordeling_DokumentKonverteringBestilling]
GO
ALTER TABLE [dbo].[Beskedfordeling]  WITH CHECK ADD  CONSTRAINT [FK_Beskedfordeling_ForloebId] FOREIGN KEY([ForloebId])
REFERENCES [dbo].[Forloeb] ([ID])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Beskedfordeling] CHECK CONSTRAINT [FK_Beskedfordeling_ForloebId]
GO
ALTER TABLE [dbo].[Beskedfordeling]  WITH CHECK ADD  CONSTRAINT [FK_Beskedfordeling_SendBOMBesvarelseBestilling] FOREIGN KEY([SendBOMBesvarelseBestillingId])
REFERENCES [dbo].[SendBOMBesvarelseBestilling] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Beskedfordeling] CHECK CONSTRAINT [FK_Beskedfordeling_SendBOMBesvarelseBestilling]
GO
ALTER TABLE [dbo].[Beskedfordeling]  WITH CHECK ADD  CONSTRAINT [FK_Beskedfordeling_UsageLog] FOREIGN KEY([UsageLogId])
REFERENCES [dbo].[UsageLog] ([ID])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Beskedfordeling] CHECK CONSTRAINT [FK_Beskedfordeling_UsageLog]
GO
ALTER TABLE [dbo].[BeslutningsType]  WITH NOCHECK ADD  CONSTRAINT [BeslutningsType_BeslutningsTypeGruppe] FOREIGN KEY([BeslutningsTypeGruppeID])
REFERENCES [dbo].[BeslutningsTypeGruppe] ([ID])
GO
ALTER TABLE [dbo].[BeslutningsType] CHECK CONSTRAINT [BeslutningsType_BeslutningsTypeGruppe]
GO
ALTER TABLE [dbo].[Beslutningsvej]  WITH NOCHECK ADD  CONSTRAINT [FK_Beslutningsvej_Dagsordenpunkt] FOREIGN KEY([DagsordenpunktID])
REFERENCES [dbo].[Dagsordenpunkt] ([ID])
GO
ALTER TABLE [dbo].[Beslutningsvej] CHECK CONSTRAINT [FK_Beslutningsvej_Dagsordenpunkt]
GO
ALTER TABLE [dbo].[Beslutningsvej]  WITH CHECK ADD  CONSTRAINT [FK_Beslutningsvej_Moede] FOREIGN KEY([MoedeID])
REFERENCES [dbo].[Moede] ([ID])
GO
ALTER TABLE [dbo].[Beslutningsvej] CHECK CONSTRAINT [FK_Beslutningsvej_Moede]
GO
ALTER TABLE [dbo].[Bilag]  WITH NOCHECK ADD  CONSTRAINT [FK_Bilag_DokumentRegistrering] FOREIGN KEY([DokumentRegistreringID])
REFERENCES [dbo].[DokumentRegistrering] ([ID])
GO
ALTER TABLE [dbo].[Bilag] CHECK CONSTRAINT [FK_Bilag_DokumentRegistrering]
GO
ALTER TABLE [dbo].[Bilag]  WITH NOCHECK ADD  CONSTRAINT [FK_Bilag_KladdeRegistrering] FOREIGN KEY([KladdeRegistreringID])
REFERENCES [dbo].[KladdeRegistrering] ([ID])
GO
ALTER TABLE [dbo].[Bilag] CHECK CONSTRAINT [FK_Bilag_KladdeRegistrering]
GO
ALTER TABLE [dbo].[Bruger]  WITH CHECK ADD  CONSTRAINT [Bruger_Adresse] FOREIGN KEY([AdresseID])
REFERENCES [dbo].[Adresse] ([ID])
GO
ALTER TABLE [dbo].[Bruger] CHECK CONSTRAINT [Bruger_Adresse]
GO
ALTER TABLE [dbo].[Bruger]  WITH CHECK ADD  CONSTRAINT [Bruger_FagOmraade] FOREIGN KEY([FagomraadeID])
REFERENCES [dbo].[FagOmraade] ([ID])
GO
ALTER TABLE [dbo].[Bruger] CHECK CONSTRAINT [Bruger_FagOmraade]
GO
ALTER TABLE [dbo].[Bruger]  WITH CHECK ADD  CONSTRAINT [Bruger_Kontor] FOREIGN KEY([KontorID])
REFERENCES [dbo].[Kontor] ([ID])
GO
ALTER TABLE [dbo].[Bruger] CHECK CONSTRAINT [Bruger_Kontor]
GO
ALTER TABLE [dbo].[Bruger]  WITH CHECK ADD  CONSTRAINT [FK_Bruger_Ansaettelsessted] FOREIGN KEY([AnsaettelsesstedID])
REFERENCES [dbo].[Ansaettelsessted] ([ID])
GO
ALTER TABLE [dbo].[Bruger] CHECK CONSTRAINT [FK_Bruger_Ansaettelsessted]
GO
ALTER TABLE [dbo].[BrugerGruppeBruger]  WITH CHECK ADD  CONSTRAINT [BrugerGruppeBruger_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[BrugerGruppeBruger] CHECK CONSTRAINT [BrugerGruppeBruger_Bruger]
GO
ALTER TABLE [dbo].[BrugerGruppeBruger]  WITH NOCHECK ADD  CONSTRAINT [BrugerGruppeBrugere_BrugerGruppe] FOREIGN KEY([BrugerGruppeID])
REFERENCES [dbo].[BrugerGruppe] ([ID])
GO
ALTER TABLE [dbo].[BrugerGruppeBruger] CHECK CONSTRAINT [BrugerGruppeBrugere_BrugerGruppe]
GO
ALTER TABLE [dbo].[BrugerGruppeEjer]  WITH CHECK ADD  CONSTRAINT [BrugerGruppeEjer_Bruger] FOREIGN KEY([BrugerSettingsID])
REFERENCES [dbo].[BrugerSettings] ([ID])
GO
ALTER TABLE [dbo].[BrugerGruppeEjer] CHECK CONSTRAINT [BrugerGruppeEjer_Bruger]
GO
ALTER TABLE [dbo].[BrugerGruppeEjer]  WITH NOCHECK ADD  CONSTRAINT [BrugerGruppeEjer_BrugerGruppe] FOREIGN KEY([BrugerGruppeID])
REFERENCES [dbo].[BrugerGruppe] ([ID])
GO
ALTER TABLE [dbo].[BrugerGruppeEjer] CHECK CONSTRAINT [BrugerGruppeEjer_BrugerGruppe]
GO
ALTER TABLE [dbo].[BrugerLogonLog]  WITH CHECK ADD  CONSTRAINT [FK_BrugerLogonLog_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[BrugerLogonLog] CHECK CONSTRAINT [FK_BrugerLogonLog_Bruger]
GO
ALTER TABLE [dbo].[BrugerSettings]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettings_AmtOpslag] FOREIGN KEY([DefaultAmtVedSagsoprettelseID])
REFERENCES [dbo].[AmtOpslag] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettings] CHECK CONSTRAINT [FK_BrugerSettings_AmtOpslag]
GO
ALTER TABLE [dbo].[BrugerSettings]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettings_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettings] CHECK CONSTRAINT [FK_BrugerSettings_Bruger]
GO
ALTER TABLE [dbo].[BrugerSettings]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettings_DefaultSagSecuritySet] FOREIGN KEY([DefaultSagSecuritySetID])
REFERENCES [dbo].[SecuritySet] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettings] CHECK CONSTRAINT [FK_BrugerSettings_DefaultSagSecuritySet]
GO
ALTER TABLE [dbo].[BrugerSettings]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettings_KommuneOpslag] FOREIGN KEY([DefaultKommuneVedSagsoprettelseID])
REFERENCES [dbo].[KommuneOpslag] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettings] CHECK CONSTRAINT [FK_BrugerSettings_KommuneOpslag]
GO
ALTER TABLE [dbo].[BrugerSettings]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettings_PubliseringIndstillinger] FOREIGN KEY([SenestePubliceringIndstillingerID])
REFERENCES [dbo].[PubliseringIndstillinger] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettings] CHECK CONSTRAINT [FK_BrugerSettings_PubliseringIndstillinger]
GO
ALTER TABLE [dbo].[BrugerSettings]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettings_RegionOpslag] FOREIGN KEY([DefaultRegionVedSagsoprettelseID])
REFERENCES [dbo].[RegionOpslag] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettings] CHECK CONSTRAINT [FK_BrugerSettings_RegionOpslag]
GO
ALTER TABLE [dbo].[BrugerSettingsAnsaettelsessted]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettingsAnsaettelsessteder_Ansaettelsessted] FOREIGN KEY([AnsaettelsesstedID])
REFERENCES [dbo].[Ansaettelsessted] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettingsAnsaettelsessted] CHECK CONSTRAINT [FK_BrugerSettingsAnsaettelsessteder_Ansaettelsessted]
GO
ALTER TABLE [dbo].[BrugerSettingsAnsaettelsessted]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettingsAnsaettelsessteder_BrugerSettings] FOREIGN KEY([BrugerSettingsID])
REFERENCES [dbo].[BrugerSettings] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettingsAnsaettelsessted] CHECK CONSTRAINT [FK_BrugerSettingsAnsaettelsessteder_BrugerSettings]
GO
ALTER TABLE [dbo].[BrugerSettingsAnvendteEmailAdresser]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettingsAnvendteEmailAdresser_BrugerSettings] FOREIGN KEY([BrugerSettingsID])
REFERENCES [dbo].[BrugerSettings] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettingsAnvendteEmailAdresser] CHECK CONSTRAINT [FK_BrugerSettingsAnvendteEmailAdresser_BrugerSettings]
GO
ALTER TABLE [dbo].[BrugerSettingsDropFolderConfiguration]  WITH CHECK ADD  CONSTRAINT [BrugerSettingsDropFolderConfiguration_BrugerSettings] FOREIGN KEY([BrugerSettingsID])
REFERENCES [dbo].[BrugerSettings] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettingsDropFolderConfiguration] CHECK CONSTRAINT [BrugerSettingsDropFolderConfiguration_BrugerSettings]
GO
ALTER TABLE [dbo].[BrugerSettingsEmailKontoRegistrering]  WITH CHECK ADD FOREIGN KEY([EmailKontoExchangeConfigurationId])
REFERENCES [dbo].[EmailKontoExchangeConfiguration] ([Id])
GO
ALTER TABLE [dbo].[BrugerSettingsEmailKontoRegistrering]  WITH CHECK ADD  CONSTRAINT [MailSystemSessionInfo_BrugerSettings] FOREIGN KEY([BrugerSettingsID])
REFERENCES [dbo].[BrugerSettings] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettingsEmailKontoRegistrering] CHECK CONSTRAINT [MailSystemSessionInfo_BrugerSettings]
GO
ALTER TABLE [dbo].[BrugerSettingsFavoritSag]  WITH CHECK ADD  CONSTRAINT [BrugerSettingsFavoritSag_BrugerSettings] FOREIGN KEY([BrugerSettingsID])
REFERENCES [dbo].[BrugerSettings] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettingsFavoritSag] CHECK CONSTRAINT [BrugerSettingsFavoritSag_BrugerSettings]
GO
ALTER TABLE [dbo].[BrugerSettingsFavoritSag]  WITH NOCHECK ADD  CONSTRAINT [BrugerSettingsFavoritSag_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettingsFavoritSag] CHECK CONSTRAINT [BrugerSettingsFavoritSag_Sag]
GO
ALTER TABLE [dbo].[BrugerSettingsFavoritSagSkabelon]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettingsFavoritSagSkabelon_BrugerSettings] FOREIGN KEY([BrugerSettingsID])
REFERENCES [dbo].[BrugerSettings] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettingsFavoritSagSkabelon] CHECK CONSTRAINT [FK_BrugerSettingsFavoritSagSkabelon_BrugerSettings]
GO
ALTER TABLE [dbo].[BrugerSettingsFavoritSagSkabelon]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettingsFavoritSagSkabelon_SagSkabelon] FOREIGN KEY([SagSkabelonID])
REFERENCES [dbo].[SagSkabelon] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettingsFavoritSagSkabelon] CHECK CONSTRAINT [FK_BrugerSettingsFavoritSagSkabelon_SagSkabelon]
GO
ALTER TABLE [dbo].[BrugerSettingsFavoritSkabelon]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettingsFavoritSkabelon_BrugerSettings] FOREIGN KEY([BrugerSettingsID])
REFERENCES [dbo].[BrugerSettings] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettingsFavoritSkabelon] CHECK CONSTRAINT [FK_BrugerSettingsFavoritSkabelon_BrugerSettings]
GO
ALTER TABLE [dbo].[BrugerSettingsFavoritSkabelon]  WITH NOCHECK ADD  CONSTRAINT [FK_BrugerSettingsFavoritSkabelon_Skabelon] FOREIGN KEY([SkabelonID])
REFERENCES [dbo].[Skabelon] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettingsFavoritSkabelon] CHECK CONSTRAINT [FK_BrugerSettingsFavoritSkabelon_Skabelon]
GO
ALTER TABLE [dbo].[BrugerSettingsSagsstatus]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettingsSagsstatus_BrugerSettings] FOREIGN KEY([BrugerSettingsID])
REFERENCES [dbo].[BrugerSettings] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettingsSagsstatus] CHECK CONSTRAINT [FK_BrugerSettingsSagsstatus_BrugerSettings]
GO
ALTER TABLE [dbo].[BrugerSettingsSagsstatus]  WITH NOCHECK ADD  CONSTRAINT [FK_BrugerSettingsSagsstatus_Sagsstatus] FOREIGN KEY([SagsstatusID])
REFERENCES [dbo].[SagsStatus] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettingsSagsstatus] CHECK CONSTRAINT [FK_BrugerSettingsSagsstatus_Sagsstatus]
GO
ALTER TABLE [dbo].[BrugerSettingsSagsType]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettingsSagsType_BrugerSettings] FOREIGN KEY([BrugerSettingsID])
REFERENCES [dbo].[BrugerSettings] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettingsSagsType] CHECK CONSTRAINT [FK_BrugerSettingsSagsType_BrugerSettings]
GO
ALTER TABLE [dbo].[BrugerSettingsSagsType]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettingsSagsType_SagsType] FOREIGN KEY([SagsTypeID])
REFERENCES [dbo].[SagsType] ([Id])
GO
ALTER TABLE [dbo].[BrugerSettingsSagsType] CHECK CONSTRAINT [FK_BrugerSettingsSagsType_SagsType]
GO
ALTER TABLE [dbo].[BrugerSettingsStyringsreolSagsfelt]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettingsStyringsreolsagsfelt_BrugerSettings] FOREIGN KEY([BrugerSettingsID])
REFERENCES [dbo].[BrugerSettings] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettingsStyringsreolSagsfelt] CHECK CONSTRAINT [FK_BrugerSettingsStyringsreolsagsfelt_BrugerSettings]
GO
ALTER TABLE [dbo].[BrugerSettingsStyringsreolSagsfelt]  WITH CHECK ADD  CONSTRAINT [FK_BrugerSettingsStyringsreolsagsfelt_Styringsreolsagsfelt] FOREIGN KEY([StyringsreolSagsfeltID])
REFERENCES [dbo].[StyringsreolSagsFelt] ([ID])
GO
ALTER TABLE [dbo].[BrugerSettingsStyringsreolSagsfelt] CHECK CONSTRAINT [FK_BrugerSettingsStyringsreolsagsfelt_Styringsreolsagsfelt]
GO
ALTER TABLE [dbo].[Bygning]  WITH NOCHECK ADD  CONSTRAINT [FK_Bygning_Kommune] FOREIGN KEY([KommuneID])
REFERENCES [dbo].[KommuneOpslag] ([ID])
GO
ALTER TABLE [dbo].[Bygning] CHECK CONSTRAINT [FK_Bygning_Kommune]
GO
ALTER TABLE [dbo].[CprBrokerPersonReference]  WITH NOCHECK ADD FOREIGN KEY([PersonId])
REFERENCES [dbo].[Person] ([ID])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Dagsorden]  WITH CHECK ADD  CONSTRAINT [FK_Dagsorden_Bruger_CreatedBy] FOREIGN KEY([CreatedBy])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Dagsorden] CHECK CONSTRAINT [FK_Dagsorden_Bruger_CreatedBy]
GO
ALTER TABLE [dbo].[Dagsorden]  WITH CHECK ADD  CONSTRAINT [FK_Dagsorden_Bruger_LastChangedBy] FOREIGN KEY([LastChangedBy])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Dagsorden] CHECK CONSTRAINT [FK_Dagsorden_Bruger_LastChangedBy]
GO
ALTER TABLE [dbo].[Dagsorden]  WITH CHECK ADD  CONSTRAINT [FK_Dagsorden_Dagsordener_Moede] FOREIGN KEY([MoedeID])
REFERENCES [dbo].[Moede] ([ID])
GO
ALTER TABLE [dbo].[Dagsorden] CHECK CONSTRAINT [FK_Dagsorden_Dagsordener_Moede]
GO
ALTER TABLE [dbo].[Dagsordenpunkt]  WITH CHECK ADD  CONSTRAINT [FK_Dagsordenpunkt_BesluttendeUdvalg_Udvalg] FOREIGN KEY([BesluttendeUdvalgID])
REFERENCES [dbo].[Udvalg] ([ID])
GO
ALTER TABLE [dbo].[Dagsordenpunkt] CHECK CONSTRAINT [FK_Dagsordenpunkt_BesluttendeUdvalg_Udvalg]
GO
ALTER TABLE [dbo].[Dagsordenpunkt]  WITH CHECK ADD  CONSTRAINT [FK_Dagsordenpunkt_Bruger_CreatedBy] FOREIGN KEY([CreatedBy])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Dagsordenpunkt] CHECK CONSTRAINT [FK_Dagsordenpunkt_Bruger_CreatedBy]
GO
ALTER TABLE [dbo].[Dagsordenpunkt]  WITH NOCHECK ADD  CONSTRAINT [FK_Dagsordenpunkt_Dagsordenpunkttype] FOREIGN KEY([DagsordenpunktTypeID])
REFERENCES [dbo].[DagsordenpunktType] ([ID])
GO
ALTER TABLE [dbo].[Dagsordenpunkt] CHECK CONSTRAINT [FK_Dagsordenpunkt_Dagsordenpunkttype]
GO
ALTER TABLE [dbo].[Dagsordenpunkt]  WITH CHECK ADD  CONSTRAINT [FK_Dagsordenpunkt_RedigresAfBruger] FOREIGN KEY([RedigeresLigeNuAfID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Dagsordenpunkt] CHECK CONSTRAINT [FK_Dagsordenpunkt_RedigresAfBruger]
GO
ALTER TABLE [dbo].[Dagsordenpunkt]  WITH NOCHECK ADD  CONSTRAINT [FK_Dagsordenpunkt_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[Dagsordenpunkt] CHECK CONSTRAINT [FK_Dagsordenpunkt_Sag]
GO
ALTER TABLE [dbo].[DagsordenPunktBehandlingBilag]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenPunktBehandlingBilag_Bilag] FOREIGN KEY([BilagID])
REFERENCES [dbo].[Bilag] ([ID])
GO
ALTER TABLE [dbo].[DagsordenPunktBehandlingBilag] CHECK CONSTRAINT [FK_DagsordenPunktBehandlingBilag_Bilag]
GO
ALTER TABLE [dbo].[DagsordenPunktBehandlingBilag]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenPunktBehandlingBilag_DagsordenpunktsBehandling] FOREIGN KEY([BehandlingID])
REFERENCES [dbo].[DagsordenpunktsBehandling] ([Id])
GO
ALTER TABLE [dbo].[DagsordenPunktBehandlingBilag] CHECK CONSTRAINT [FK_DagsordenPunktBehandlingBilag_DagsordenpunktsBehandling]
GO
ALTER TABLE [dbo].[DagsordenpunktBehandlingFeltIndhold]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenpunktBehandlingFeltIndhold_DagsordenpunktFeltIndhold] FOREIGN KEY([DagsordenpunktFeltIndholdId])
REFERENCES [dbo].[DagsordenpunktFeltIndhold] ([Id])
GO
ALTER TABLE [dbo].[DagsordenpunktBehandlingFeltIndhold] CHECK CONSTRAINT [FK_DagsordenpunktBehandlingFeltIndhold_DagsordenpunktFeltIndhold]
GO
ALTER TABLE [dbo].[DagsordenpunktBehandlingFeltIndhold]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenpunktBehandlingFeltIndhold_DagsordenpunktsBehandling] FOREIGN KEY([DagsordenpunktsBehandlingId])
REFERENCES [dbo].[DagsordenpunktsBehandling] ([Id])
GO
ALTER TABLE [dbo].[DagsordenpunktBehandlingFeltIndhold] CHECK CONSTRAINT [FK_DagsordenpunktBehandlingFeltIndhold_DagsordenpunktsBehandling]
GO
ALTER TABLE [dbo].[DagsordenpunktFelt]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenpunktFelt_DagsordenpunktFeltType] FOREIGN KEY([DagsordenpunktFeltTypeId])
REFERENCES [dbo].[DagsordenpunktFeltType] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktFelt] CHECK CONSTRAINT [FK_DagsordenpunktFelt_DagsordenpunktFeltType]
GO
ALTER TABLE [dbo].[DagsordenpunktFeltIndhold]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenpunktFeltIndhold_DagsordenpunktFeltTypeId] FOREIGN KEY([DagsordenpunktFeltId])
REFERENCES [dbo].[DagsordenpunktFelt] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktFeltIndhold] CHECK CONSTRAINT [FK_DagsordenpunktFeltIndhold_DagsordenpunktFeltTypeId]
GO
ALTER TABLE [dbo].[DagsordenpunktRessource]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenpunktRessource_Dagsordenpunkt] FOREIGN KEY([DagsordenpunktID])
REFERENCES [dbo].[Dagsordenpunkt] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktRessource] CHECK CONSTRAINT [FK_DagsordenpunktRessource_Dagsordenpunkt]
GO
ALTER TABLE [dbo].[DagsordenpunktRessource]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenpunktRessource_Ressource] FOREIGN KEY([RessourceID])
REFERENCES [dbo].[Ressource] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktRessource] CHECK CONSTRAINT [FK_DagsordenpunktRessource_Ressource]
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling]  WITH CHECK ADD  CONSTRAINT [FK_DagsordenpunktsBehandling_Bruger_AnsvarligID] FOREIGN KEY([AnsvarligID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling] CHECK CONSTRAINT [FK_DagsordenpunktsBehandling_Bruger_AnsvarligID]
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling]  WITH CHECK ADD  CONSTRAINT [FK_DagsordenpunktsBehandling_Bruger_LastChangedBy] FOREIGN KEY([LastChangedBy])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling] CHECK CONSTRAINT [FK_DagsordenpunktsBehandling_Bruger_LastChangedBy]
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling]  WITH CHECK ADD  CONSTRAINT [FK_DagsordenpunktsBehandling_Dagsorden] FOREIGN KEY([DagsordenId])
REFERENCES [dbo].[Dagsorden] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling] CHECK CONSTRAINT [FK_DagsordenpunktsBehandling_Dagsorden]
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenpunktsBehandling_Dagsordenpunkt] FOREIGN KEY([DagsordenpunktId])
REFERENCES [dbo].[Dagsordenpunkt] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling] CHECK CONSTRAINT [FK_DagsordenpunktsBehandling_Dagsordenpunkt]
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenpunktsBehandling_Dokument] FOREIGN KEY([TilbagejournaliseretDokumentID])
REFERENCES [dbo].[Dokument] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktsBehandling] CHECK CONSTRAINT [FK_DagsordenpunktsBehandling_Dokument]
GO
ALTER TABLE [dbo].[DagsordenpunktTypeDagsordenpunktFelt]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenpunktTypeDagsordenpunktFelt_DagsordenpunktFelt] FOREIGN KEY([DagsordenpunktFeltId])
REFERENCES [dbo].[DagsordenpunktFelt] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktTypeDagsordenpunktFelt] CHECK CONSTRAINT [FK_DagsordenpunktTypeDagsordenpunktFelt_DagsordenpunktFelt]
GO
ALTER TABLE [dbo].[DagsordenpunktTypeDagsordenpunktFelt]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenpunktTypeDagsordenpunktFelt_DagsordenpunktType] FOREIGN KEY([DagsordenpunkttypeID])
REFERENCES [dbo].[DagsordenpunktType] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktTypeDagsordenpunktFelt] CHECK CONSTRAINT [FK_DagsordenpunktTypeDagsordenpunktFelt_DagsordenpunktType]
GO
ALTER TABLE [dbo].[DagsordenpunkttypeIUdvalg]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenpunkttypeIUdvalg_Dagsordenpunkttype] FOREIGN KEY([DagsordenpunkttypeID])
REFERENCES [dbo].[DagsordenpunktType] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunkttypeIUdvalg] CHECK CONSTRAINT [FK_DagsordenpunkttypeIUdvalg_Dagsordenpunkttype]
GO
ALTER TABLE [dbo].[DagsordenpunkttypeIUdvalg]  WITH CHECK ADD  CONSTRAINT [FK_DagsordenpunkttypeIUdvalg_Udvalg] FOREIGN KEY([UdvalgID])
REFERENCES [dbo].[Udvalg] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunkttypeIUdvalg] CHECK CONSTRAINT [FK_DagsordenpunkttypeIUdvalg_Udvalg]
GO
ALTER TABLE [dbo].[DagsordenpunktVersion]  WITH CHECK ADD  CONSTRAINT [FK_DagsordenpunktVersion_BesluttendeUdvalg_Udvalg] FOREIGN KEY([BesluttendeUdvalgID])
REFERENCES [dbo].[Udvalg] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktVersion] CHECK CONSTRAINT [FK_DagsordenpunktVersion_BesluttendeUdvalg_Udvalg]
GO
ALTER TABLE [dbo].[DagsordenpunktVersion]  WITH CHECK ADD  CONSTRAINT [FK_DagsordenpunktVersion_Bruger_AnsvarligID] FOREIGN KEY([AnsvarligID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktVersion] CHECK CONSTRAINT [FK_DagsordenpunktVersion_Bruger_AnsvarligID]
GO
ALTER TABLE [dbo].[DagsordenpunktVersion]  WITH CHECK ADD  CONSTRAINT [FK_DagsordenpunktVersion_Bruger_CreatedBy] FOREIGN KEY([CreatedBy])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktVersion] CHECK CONSTRAINT [FK_DagsordenpunktVersion_Bruger_CreatedBy]
GO
ALTER TABLE [dbo].[DagsordenpunktVersion]  WITH CHECK ADD  CONSTRAINT [FK_DagsordenpunktVersion_Bruger_LastChangedBy] FOREIGN KEY([LastChangedBy])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktVersion] CHECK CONSTRAINT [FK_DagsordenpunktVersion_Bruger_LastChangedBy]
GO
ALTER TABLE [dbo].[DagsordenpunktVersion]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenpunktVersion_Dagsordenpunkttype] FOREIGN KEY([DagsordenpunktTypeID])
REFERENCES [dbo].[DagsordenpunktType] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktVersion] CHECK CONSTRAINT [FK_DagsordenpunktVersion_Dagsordenpunkttype]
GO
ALTER TABLE [dbo].[DagsordenpunktVersion]  WITH CHECK ADD  CONSTRAINT [FK_DagsordenpunktVersion_RedigresAfBruger] FOREIGN KEY([RedigeresLigeNuAfID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktVersion] CHECK CONSTRAINT [FK_DagsordenpunktVersion_RedigresAfBruger]
GO
ALTER TABLE [dbo].[DagsordenpunktVersion]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenpunktVersion_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktVersion] CHECK CONSTRAINT [FK_DagsordenpunktVersion_Sag]
GO
ALTER TABLE [dbo].[DagsordenpunktVersionFeltIndhold]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenpunktVersionFeltIndhold_DagsordenpunktFeltIndhold] FOREIGN KEY([DagsordenpunktFeltIndholdId])
REFERENCES [dbo].[DagsordenpunktFeltIndhold] ([Id])
GO
ALTER TABLE [dbo].[DagsordenpunktVersionFeltIndhold] CHECK CONSTRAINT [FK_DagsordenpunktVersionFeltIndhold_DagsordenpunktFeltIndhold]
GO
ALTER TABLE [dbo].[DagsordenpunktVersionFeltIndhold]  WITH NOCHECK ADD  CONSTRAINT [FK_DagsordenpunktVersionFeltIndhold_DagsordenpunktsVersion] FOREIGN KEY([DagsordenpunktVersionId])
REFERENCES [dbo].[DagsordenpunktVersion] ([ID])
GO
ALTER TABLE [dbo].[DagsordenpunktVersionFeltIndhold] CHECK CONSTRAINT [FK_DagsordenpunktVersionFeltIndhold_DagsordenpunktsVersion]
GO
ALTER TABLE [dbo].[Delforloeb]  WITH CHECK ADD  CONSTRAINT [Delforloeb_Behandler] FOREIGN KEY([BehandlerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Delforloeb] CHECK CONSTRAINT [Delforloeb_Behandler]
GO
ALTER TABLE [dbo].[Delforloeb]  WITH NOCHECK ADD  CONSTRAINT [Delforloeb_BeslutningsType] FOREIGN KEY([BeslutningsTypeID])
REFERENCES [dbo].[BeslutningsType] ([ID])
GO
ALTER TABLE [dbo].[Delforloeb] CHECK CONSTRAINT [Delforloeb_BeslutningsType]
GO
ALTER TABLE [dbo].[Delforloeb]  WITH NOCHECK ADD  CONSTRAINT [Delforloeb_Bevaring] FOREIGN KEY([BevaringID])
REFERENCES [dbo].[BevaringOpslag] ([ID])
GO
ALTER TABLE [dbo].[Delforloeb] CHECK CONSTRAINT [Delforloeb_Bevaring]
GO
ALTER TABLE [dbo].[Delforloeb]  WITH CHECK ADD  CONSTRAINT [Delforloeb_CreatedBy] FOREIGN KEY([CreatedByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Delforloeb] CHECK CONSTRAINT [Delforloeb_CreatedBy]
GO
ALTER TABLE [dbo].[Delforloeb]  WITH CHECK ADD  CONSTRAINT [Delforloeb_DelforloebType] FOREIGN KEY([DelforloebTypeID])
REFERENCES [dbo].[DelforloebType] ([ID])
GO
ALTER TABLE [dbo].[Delforloeb] CHECK CONSTRAINT [Delforloeb_DelforloebType]
GO
ALTER TABLE [dbo].[Delforloeb]  WITH NOCHECK ADD  CONSTRAINT [Delforloeb_FagOmraade] FOREIGN KEY([FagomraadeID])
REFERENCES [dbo].[FagOmraade] ([ID])
GO
ALTER TABLE [dbo].[Delforloeb] CHECK CONSTRAINT [Delforloeb_FagOmraade]
GO
ALTER TABLE [dbo].[Delforloeb]  WITH NOCHECK ADD  CONSTRAINT [Delforloeb_Kommune] FOREIGN KEY([KommuneID])
REFERENCES [dbo].[KommuneOpslag] ([ID])
GO
ALTER TABLE [dbo].[Delforloeb] CHECK CONSTRAINT [Delforloeb_Kommune]
GO
ALTER TABLE [dbo].[Delforloeb]  WITH NOCHECK ADD  CONSTRAINT [Delforloeb_KommuneFoer2007] FOREIGN KEY([KommuneFoer2007ID])
REFERENCES [dbo].[KommuneFoer2007Opslag] ([ID])
GO
ALTER TABLE [dbo].[Delforloeb] CHECK CONSTRAINT [Delforloeb_KommuneFoer2007]
GO
ALTER TABLE [dbo].[Delforloeb]  WITH NOCHECK ADD  CONSTRAINT [Delforloeb_Kontor] FOREIGN KEY([KontorID])
REFERENCES [dbo].[Kontor] ([ID])
GO
ALTER TABLE [dbo].[Delforloeb] CHECK CONSTRAINT [Delforloeb_Kontor]
GO
ALTER TABLE [dbo].[Delforloeb]  WITH CHECK ADD  CONSTRAINT [Delforloeb_LastChangedBy] FOREIGN KEY([LastChangedByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Delforloeb] CHECK CONSTRAINT [Delforloeb_LastChangedBy]
GO
ALTER TABLE [dbo].[Delforloeb]  WITH NOCHECK ADD  CONSTRAINT [Delforloeb_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[Delforloeb] CHECK CONSTRAINT [Delforloeb_Sag]
GO
ALTER TABLE [dbo].[Delforloeb]  WITH CHECK ADD  CONSTRAINT [Delforloeb_Sagspart] FOREIGN KEY([SagspartID])
REFERENCES [dbo].[SagsPart] ([ID])
GO
ALTER TABLE [dbo].[Delforloeb] CHECK CONSTRAINT [Delforloeb_Sagspart]
GO
ALTER TABLE [dbo].[Delforloeb]  WITH NOCHECK ADD  CONSTRAINT [Delforloeb_SagsPartRolle] FOREIGN KEY([SagspartRolleID])
REFERENCES [dbo].[SagsPartRolle] ([ID])
GO
ALTER TABLE [dbo].[Delforloeb] CHECK CONSTRAINT [Delforloeb_SagsPartRolle]
GO
ALTER TABLE [dbo].[DelforloebDagsordenpunkt]  WITH NOCHECK ADD  CONSTRAINT [FK_DelforloebDagsordenpunkt_Dagsordenpunkt] FOREIGN KEY([DagsordenpunktID])
REFERENCES [dbo].[Dagsordenpunkt] ([ID])
GO
ALTER TABLE [dbo].[DelforloebDagsordenpunkt] CHECK CONSTRAINT [FK_DelforloebDagsordenpunkt_Dagsordenpunkt]
GO
ALTER TABLE [dbo].[DelforloebDagsordenpunkt]  WITH NOCHECK ADD  CONSTRAINT [FK_DelforloebDagsordenpunkt_Delforloeb] FOREIGN KEY([DelforloebID])
REFERENCES [dbo].[Delforloeb] ([ID])
GO
ALTER TABLE [dbo].[DelforloebDagsordenpunkt] CHECK CONSTRAINT [FK_DelforloebDagsordenpunkt_Delforloeb]
GO
ALTER TABLE [dbo].[DelforloebDokumentRegistrering]  WITH NOCHECK ADD  CONSTRAINT [DelforloebDokumentRegistrering_Delforloeb] FOREIGN KEY([DelforloebID])
REFERENCES [dbo].[Delforloeb] ([ID])
GO
ALTER TABLE [dbo].[DelforloebDokumentRegistrering] CHECK CONSTRAINT [DelforloebDokumentRegistrering_Delforloeb]
GO
ALTER TABLE [dbo].[DelforloebDokumentRegistrering]  WITH NOCHECK ADD  CONSTRAINT [DelforloebDokumentRegistrering_DokumentRegistrering] FOREIGN KEY([DokumentRegistreringID])
REFERENCES [dbo].[DokumentRegistrering] ([ID])
GO
ALTER TABLE [dbo].[DelforloebDokumentRegistrering] CHECK CONSTRAINT [DelforloebDokumentRegistrering_DokumentRegistrering]
GO
ALTER TABLE [dbo].[DelforloebEksternIdentitet]  WITH NOCHECK ADD  CONSTRAINT [FK_DelforloebEksternIdentitet_Delforloeb] FOREIGN KEY([DelforloebID])
REFERENCES [dbo].[Delforloeb] ([ID])
GO
ALTER TABLE [dbo].[DelforloebEksternIdentitet] CHECK CONSTRAINT [FK_DelforloebEksternIdentitet_Delforloeb]
GO
ALTER TABLE [dbo].[DelforloebEksternIdentitet]  WITH NOCHECK ADD  CONSTRAINT [FK_DelforloebEksternIdentitet_KnownEksterntSystem] FOREIGN KEY([EksternSystemID])
REFERENCES [dbo].[KnownEksterntSystem] ([ID])
GO
ALTER TABLE [dbo].[DelforloebEksternIdentitet] CHECK CONSTRAINT [FK_DelforloebEksternIdentitet_KnownEksterntSystem]
GO
ALTER TABLE [dbo].[DelforloebEmneOrd]  WITH NOCHECK ADD  CONSTRAINT [DelforloebEmneOrd_Delforloeb] FOREIGN KEY([DelforloebID])
REFERENCES [dbo].[Delforloeb] ([ID])
GO
ALTER TABLE [dbo].[DelforloebEmneOrd] CHECK CONSTRAINT [DelforloebEmneOrd_Delforloeb]
GO
ALTER TABLE [dbo].[DelforloebEmneOrd]  WITH NOCHECK ADD  CONSTRAINT [DelforloebEmneOrd_EmneOrd] FOREIGN KEY([EmneOrdID])
REFERENCES [dbo].[EmneOrd] ([ID])
GO
ALTER TABLE [dbo].[DelforloebEmneOrd] CHECK CONSTRAINT [DelforloebEmneOrd_EmneOrd]
GO
ALTER TABLE [dbo].[DelforloebKladdeRegistrering]  WITH NOCHECK ADD  CONSTRAINT [DelforloebKladdeRegistrering_Delforloeb] FOREIGN KEY([DelforloebID])
REFERENCES [dbo].[Delforloeb] ([ID])
GO
ALTER TABLE [dbo].[DelforloebKladdeRegistrering] CHECK CONSTRAINT [DelforloebKladdeRegistrering_Delforloeb]
GO
ALTER TABLE [dbo].[DelforloebKladdeRegistrering]  WITH NOCHECK ADD  CONSTRAINT [DelforloebKladdeRegistrering_KladdeRegistrering] FOREIGN KEY([KladdeRegistreringID])
REFERENCES [dbo].[KladdeRegistrering] ([ID])
GO
ALTER TABLE [dbo].[DelforloebKladdeRegistrering] CHECK CONSTRAINT [DelforloebKladdeRegistrering_KladdeRegistrering]
GO
ALTER TABLE [dbo].[DelforloebType]  WITH CHECK ADD  CONSTRAINT [DelforloebType_DelforloebTypeGruppe] FOREIGN KEY([DelforloebTypeGruppeID])
REFERENCES [dbo].[DelforloebTypeGruppe] ([ID])
GO
ALTER TABLE [dbo].[DelforloebType] CHECK CONSTRAINT [DelforloebType_DelforloebTypeGruppe]
GO
ALTER TABLE [dbo].[Dokument]  WITH NOCHECK ADD  CONSTRAINT [Dokument_DokumentArt] FOREIGN KEY([DokumentArtID])
REFERENCES [dbo].[DokumentArtOpslag] ([ID])
GO
ALTER TABLE [dbo].[Dokument] CHECK CONSTRAINT [Dokument_DokumentArt]
GO
ALTER TABLE [dbo].[Dokument]  WITH NOCHECK ADD  CONSTRAINT [Dokument_DokumentType] FOREIGN KEY([DokumentType])
REFERENCES [dbo].[DokumentTypeOpslag] ([ID])
GO
ALTER TABLE [dbo].[Dokument] CHECK CONSTRAINT [Dokument_DokumentType]
GO
ALTER TABLE [dbo].[Dokument]  WITH NOCHECK ADD  CONSTRAINT [Dokument_Mail] FOREIGN KEY([MailID])
REFERENCES [dbo].[Mail] ([ID])
GO
ALTER TABLE [dbo].[Dokument] CHECK CONSTRAINT [Dokument_Mail]
GO
ALTER TABLE [dbo].[Dokument]  WITH CHECK ADD  CONSTRAINT [Dokument_OprettetAfBruger] FOREIGN KEY([OprettetAfID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Dokument] CHECK CONSTRAINT [Dokument_OprettetAfBruger]
GO
ALTER TABLE [dbo].[Dokument]  WITH NOCHECK ADD  CONSTRAINT [Dokument_ParentDokument] FOREIGN KEY([ParentDokumentID])
REFERENCES [dbo].[Dokument] ([ID])
GO
ALTER TABLE [dbo].[Dokument] CHECK CONSTRAINT [Dokument_ParentDokument]
GO
ALTER TABLE [dbo].[Dokument]  WITH CHECK ADD  CONSTRAINT [FK_Dokument_DeletedByBruger] FOREIGN KEY([DeletedByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Dokument] CHECK CONSTRAINT [FK_Dokument_DeletedByBruger]
GO
ALTER TABLE [dbo].[Dokument]  WITH CHECK ADD  CONSTRAINT [FK_Dokument_DokumentDataInfo_Primary] FOREIGN KEY([PrimaryDokumentDataInfoID])
REFERENCES [dbo].[DokumentDataInfo] ([ID])
GO
ALTER TABLE [dbo].[Dokument] CHECK CONSTRAINT [FK_Dokument_DokumentDataInfo_Primary]
GO
ALTER TABLE [dbo].[Dokument]  WITH NOCHECK ADD  CONSTRAINT [FK_Dokument_ProcessStatusOpslag] FOREIGN KEY([ProcessStatus])
REFERENCES [dbo].[ProcessStatusOpslag] ([ID])
GO
ALTER TABLE [dbo].[Dokument] CHECK CONSTRAINT [FK_Dokument_ProcessStatusOpslag]
GO
ALTER TABLE [dbo].[DokumentBoksHistorik]  WITH NOCHECK ADD FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[DokumentDataInfo]  WITH CHECK ADD  CONSTRAINT [DokumentDataInfo_Dokument] FOREIGN KEY([DokumentID])
REFERENCES [dbo].[Dokument] ([ID])
GO
ALTER TABLE [dbo].[DokumentDataInfo] CHECK CONSTRAINT [DokumentDataInfo_Dokument]
GO
ALTER TABLE [dbo].[DokumentDataInfo]  WITH CHECK ADD  CONSTRAINT [DokumentDataInfo_DokumentDataInfoType] FOREIGN KEY([DokumentDataInfoType])
REFERENCES [dbo].[DokumentDataInfoTypeOpslag] ([ID])
GO
ALTER TABLE [dbo].[DokumentDataInfo] CHECK CONSTRAINT [DokumentDataInfo_DokumentDataInfoType]
GO
ALTER TABLE [dbo].[DokumentDataInfo]  WITH CHECK ADD  CONSTRAINT [DokumentDataInfo_DokumentDataType] FOREIGN KEY([DokumentDataType])
REFERENCES [dbo].[DokumentDataTypeOpslag] ([ID])
GO
ALTER TABLE [dbo].[DokumentDataInfo] CHECK CONSTRAINT [DokumentDataInfo_DokumentDataType]
GO
ALTER TABLE [dbo].[DokumentDataInfo]  WITH CHECK ADD  CONSTRAINT [FK_DokumentDataInfo_AlternateOf] FOREIGN KEY([AlternateOfID])
REFERENCES [dbo].[DokumentDataInfo] ([ID])
GO
ALTER TABLE [dbo].[DokumentDataInfo] CHECK CONSTRAINT [FK_DokumentDataInfo_AlternateOf]
GO
ALTER TABLE [dbo].[DokumentDataInfo]  WITH CHECK ADD  CONSTRAINT [FK_DokumentDataInfo_DokumentThumbnail] FOREIGN KEY([ThumbnailID])
REFERENCES [dbo].[DokumentThumbnail] ([ID])
GO
ALTER TABLE [dbo].[DokumentDataInfo] CHECK CONSTRAINT [FK_DokumentDataInfo_DokumentThumbnail]
GO
ALTER TABLE [dbo].[DokumentMetaData]  WITH NOCHECK ADD  CONSTRAINT [FK_DokumentMetaData_Dokument] FOREIGN KEY([DokumentID])
REFERENCES [dbo].[Dokument] ([ID])
GO
ALTER TABLE [dbo].[DokumentMetaData] CHECK CONSTRAINT [FK_DokumentMetaData_Dokument]
GO
ALTER TABLE [dbo].[DokumentPart]  WITH NOCHECK ADD  CONSTRAINT [DokumentPart_Dokument] FOREIGN KEY([DokumentID])
REFERENCES [dbo].[Dokument] ([ID])
GO
ALTER TABLE [dbo].[DokumentPart] CHECK CONSTRAINT [DokumentPart_Dokument]
GO
ALTER TABLE [dbo].[DokumentPart]  WITH NOCHECK ADD  CONSTRAINT [DokumentPart_KontaktForm] FOREIGN KEY([KontaktForm])
REFERENCES [dbo].[KontaktFormOpslag] ([ID])
GO
ALTER TABLE [dbo].[DokumentPart] CHECK CONSTRAINT [DokumentPart_KontaktForm]
GO
ALTER TABLE [dbo].[DokumentProcessingQueue]  WITH NOCHECK ADD  CONSTRAINT [FK_DokumentProcessingQueue_Dokument] FOREIGN KEY([InputDokumentID])
REFERENCES [dbo].[Dokument] ([ID])
GO
ALTER TABLE [dbo].[DokumentProcessingQueue] CHECK CONSTRAINT [FK_DokumentProcessingQueue_Dokument]
GO
ALTER TABLE [dbo].[DokumentProcessingQueue]  WITH CHECK ADD  CONSTRAINT [FK_DokumentProcessingQueue_DokumentDataInfo_Input] FOREIGN KEY([InputDokumentDataInfoID])
REFERENCES [dbo].[DokumentDataInfo] ([ID])
GO
ALTER TABLE [dbo].[DokumentProcessingQueue] CHECK CONSTRAINT [FK_DokumentProcessingQueue_DokumentDataInfo_Input]
GO
ALTER TABLE [dbo].[DokumentProcessingQueue]  WITH CHECK ADD  CONSTRAINT [FK_DokumentProcessingQueue_DokumentDataInfo_Output] FOREIGN KEY([OutputDokumentDataInfoID])
REFERENCES [dbo].[DokumentDataInfo] ([ID])
GO
ALTER TABLE [dbo].[DokumentProcessingQueue] CHECK CONSTRAINT [FK_DokumentProcessingQueue_DokumentDataInfo_Output]
GO
ALTER TABLE [dbo].[DokumentProcessingQueue]  WITH NOCHECK ADD  CONSTRAINT [FK_DokumentProcessingQueue_DokumentProcessingQeueueAction] FOREIGN KEY([Action])
REFERENCES [dbo].[DokumentProcessingQueueAction] ([ID])
GO
ALTER TABLE [dbo].[DokumentProcessingQueue] CHECK CONSTRAINT [FK_DokumentProcessingQueue_DokumentProcessingQeueueAction]
GO
ALTER TABLE [dbo].[DokumentProcessingQueue]  WITH NOCHECK ADD  CONSTRAINT [FK_DokumentProcessingQueue_DokumentProcessingQueueStatus] FOREIGN KEY([Status])
REFERENCES [dbo].[DokumentProcessingQueueStatus] ([ID])
GO
ALTER TABLE [dbo].[DokumentProcessingQueue] CHECK CONSTRAINT [FK_DokumentProcessingQueue_DokumentProcessingQueueStatus]
GO
ALTER TABLE [dbo].[DokumentRegistrering]  WITH NOCHECK ADD  CONSTRAINT [DokumentRegistrering_Dokument] FOREIGN KEY([DokumentID])
REFERENCES [dbo].[Dokument] ([ID])
GO
ALTER TABLE [dbo].[DokumentRegistrering] CHECK CONSTRAINT [DokumentRegistrering_Dokument]
GO
ALTER TABLE [dbo].[DokumentRegistrering]  WITH NOCHECK ADD  CONSTRAINT [DokumentRegistrering_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[DokumentRegistrering] CHECK CONSTRAINT [DokumentRegistrering_Sag]
GO
ALTER TABLE [dbo].[DokumentRegistrering]  WITH CHECK ADD  CONSTRAINT [DokumentRegistrering_SagsPart] FOREIGN KEY([SagspartID])
REFERENCES [dbo].[SagsPart] ([ID])
GO
ALTER TABLE [dbo].[DokumentRegistrering] CHECK CONSTRAINT [DokumentRegistrering_SagsPart]
GO
ALTER TABLE [dbo].[DokumentRegistrering]  WITH NOCHECK ADD  CONSTRAINT [DokumentRegistrering_SecuritySet] FOREIGN KEY([SecuritySetID])
REFERENCES [dbo].[SecuritySet] ([ID])
GO
ALTER TABLE [dbo].[DokumentRegistrering] CHECK CONSTRAINT [DokumentRegistrering_SecuritySet]
GO
ALTER TABLE [dbo].[DokumentRegistrering]  WITH CHECK ADD  CONSTRAINT [FK_DokumentRegistrering_Bruger] FOREIGN KEY([RegistreretAfID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[DokumentRegistrering] CHECK CONSTRAINT [FK_DokumentRegistrering_Bruger]
GO
ALTER TABLE [dbo].[DokumentRegistreringSletning]  WITH CHECK ADD  CONSTRAINT [FK_DokumentRegistreringSletning_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[DokumentRegistreringSletning] CHECK CONSTRAINT [FK_DokumentRegistreringSletning_Bruger]
GO
ALTER TABLE [dbo].[DokumentRegistreringSletning]  WITH NOCHECK ADD  CONSTRAINT [FK_DokumentRegistreringSletning_DokumentRegistrering] FOREIGN KEY([DokumentRegistreringID])
REFERENCES [dbo].[DokumentRegistrering] ([ID])
GO
ALTER TABLE [dbo].[DokumentRegistreringSletning] CHECK CONSTRAINT [FK_DokumentRegistreringSletning_DokumentRegistrering]
GO
ALTER TABLE [dbo].[DokumentTypeOpslag]  WITH NOCHECK ADD  CONSTRAINT [DokumentType_DokumentArt] FOREIGN KEY([DefaultDokumentArtID])
REFERENCES [dbo].[DokumentArtOpslag] ([ID])
GO
ALTER TABLE [dbo].[DokumentTypeOpslag] CHECK CONSTRAINT [DokumentType_DokumentArt]
GO
ALTER TABLE [dbo].[Ejendom]  WITH NOCHECK ADD  CONSTRAINT [FK_Ejendom_Kommune] FOREIGN KEY([KommuneID])
REFERENCES [dbo].[KommuneOpslag] ([ID])
GO
ALTER TABLE [dbo].[Ejendom] CHECK CONSTRAINT [FK_Ejendom_Kommune]
GO
ALTER TABLE [dbo].[EmneOrd]  WITH NOCHECK ADD  CONSTRAINT [EmneOrd_EmneOrdGruppe] FOREIGN KEY([EmneOrdGruppeID])
REFERENCES [dbo].[EmneOrdGruppe] ([ID])
GO
ALTER TABLE [dbo].[EmneOrd] CHECK CONSTRAINT [EmneOrd_EmneOrdGruppe]
GO
ALTER TABLE [dbo].[EmneOrdGruppe]  WITH NOCHECK ADD  CONSTRAINT [EmneOrdGruppe_EmneOrdOvergruppe] FOREIGN KEY([EmneordOvergruppeID])
REFERENCES [dbo].[EmneOrdOvergruppe] ([ID])
GO
ALTER TABLE [dbo].[EmneOrdGruppe] CHECK CONSTRAINT [EmneOrdGruppe_EmneOrdOvergruppe]
GO
ALTER TABLE [dbo].[EmneordOvergruppeEmnePlanNummer]  WITH CHECK ADD  CONSTRAINT [FK_EmneordOvergruppeEmnePlanNummer_EmneordOvergruppe] FOREIGN KEY([EmneordOvergruppeID])
REFERENCES [dbo].[EmneOrdOvergruppe] ([ID])
GO
ALTER TABLE [dbo].[EmneordOvergruppeEmnePlanNummer] CHECK CONSTRAINT [FK_EmneordOvergruppeEmnePlanNummer_EmneordOvergruppe]
GO
ALTER TABLE [dbo].[EmneordOvergruppeEmnePlanNummer]  WITH CHECK ADD  CONSTRAINT [FK_EmneordOvergruppeEmnePlanNummer_EmnePlanNummer] FOREIGN KEY([EmnePlanNummerID])
REFERENCES [dbo].[EmnePlanNummer] ([ID])
GO
ALTER TABLE [dbo].[EmneordOvergruppeEmnePlanNummer] CHECK CONSTRAINT [FK_EmneordOvergruppeEmnePlanNummer_EmnePlanNummer]
GO
ALTER TABLE [dbo].[EmneordOvergruppeEmnePlanNummer]  WITH CHECK ADD  CONSTRAINT [FK_EmneordOvergruppeEmnePlanNummer_Facet] FOREIGN KEY([FacetID])
REFERENCES [dbo].[Facet] ([ID])
GO
ALTER TABLE [dbo].[EmneordOvergruppeEmnePlanNummer] CHECK CONSTRAINT [FK_EmneordOvergruppeEmnePlanNummer_Facet]
GO
ALTER TABLE [dbo].[EmnePlanLovGrundlag]  WITH NOCHECK ADD  CONSTRAINT [FK_EmnePlanLovGrundlag_EmnePlan] FOREIGN KEY([EmnePlanID])
REFERENCES [dbo].[EmnePlan] ([ID])
GO
ALTER TABLE [dbo].[EmnePlanLovGrundlag] CHECK CONSTRAINT [FK_EmnePlanLovGrundlag_EmnePlan]
GO
ALTER TABLE [dbo].[EmnePlanNummer]  WITH NOCHECK ADD  CONSTRAINT [EmnePlanNummer_Bevaring] FOREIGN KEY([BevaringID])
REFERENCES [dbo].[BevaringOpslag] ([ID])
GO
ALTER TABLE [dbo].[EmnePlanNummer] CHECK CONSTRAINT [EmnePlanNummer_Bevaring]
GO
ALTER TABLE [dbo].[EmnePlanNummer]  WITH NOCHECK ADD  CONSTRAINT [FK_EmnePlanNummer_EmnePlan] FOREIGN KEY([EmnePlanID])
REFERENCES [dbo].[EmnePlan] ([ID])
GO
ALTER TABLE [dbo].[EmnePlanNummer] CHECK CONSTRAINT [FK_EmnePlanNummer_EmnePlan]
GO
ALTER TABLE [dbo].[EmneplanNummerAfloeserNummer]  WITH NOCHECK ADD  CONSTRAINT [FK_EmneplanNummerAfloeserNummer_EmnePlanNummer] FOREIGN KEY([OprindeligEmnePlanNummerID])
REFERENCES [dbo].[EmnePlanNummer] ([ID])
GO
ALTER TABLE [dbo].[EmneplanNummerAfloeserNummer] CHECK CONSTRAINT [FK_EmneplanNummerAfloeserNummer_EmnePlanNummer]
GO
ALTER TABLE [dbo].[EmneplanNummerAfloeserNummer]  WITH NOCHECK ADD  CONSTRAINT [FK_OprindeligEmnePlanNummer_EmnePlanNummer] FOREIGN KEY([AfloserEmnePlanNummerID])
REFERENCES [dbo].[EmnePlanNummer] ([ID])
GO
ALTER TABLE [dbo].[EmneplanNummerAfloeserNummer] CHECK CONSTRAINT [FK_OprindeligEmnePlanNummer_EmnePlanNummer]
GO
ALTER TABLE [dbo].[EmneplanOpdatering]  WITH NOCHECK ADD  CONSTRAINT [FK_EmneplanOpdatering_EmnePlan] FOREIGN KEY([EmneplanID])
REFERENCES [dbo].[EmnePlan] ([ID])
GO
ALTER TABLE [dbo].[EmneplanOpdatering] CHECK CONSTRAINT [FK_EmneplanOpdatering_EmnePlan]
GO
ALTER TABLE [dbo].[EmnePlanStikord]  WITH NOCHECK ADD  CONSTRAINT [EmnePlanStikord_EmnePlan] FOREIGN KEY([EmnePlanID])
REFERENCES [dbo].[EmnePlan] ([ID])
GO
ALTER TABLE [dbo].[EmnePlanStikord] CHECK CONSTRAINT [EmnePlanStikord_EmnePlan]
GO
ALTER TABLE [dbo].[Erindring]  WITH CHECK ADD  CONSTRAINT [Erindring_AfsluttetAfBruger] FOREIGN KEY([AfsluttetAfID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Erindring] CHECK CONSTRAINT [Erindring_AfsluttetAfBruger]
GO
ALTER TABLE [dbo].[Erindring]  WITH CHECK ADD  CONSTRAINT [Erindring_Ansvarlig] FOREIGN KEY([AnsvarligID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Erindring] CHECK CONSTRAINT [Erindring_Ansvarlig]
GO
ALTER TABLE [dbo].[Erindring]  WITH NOCHECK ADD  CONSTRAINT [Erindring_Delforloeb] FOREIGN KEY([DelforloebID])
REFERENCES [dbo].[Delforloeb] ([ID])
GO
ALTER TABLE [dbo].[Erindring] CHECK CONSTRAINT [Erindring_Delforloeb]
GO
ALTER TABLE [dbo].[Erindring]  WITH NOCHECK ADD  CONSTRAINT [Erindring_DokumentRegistrering] FOREIGN KEY([DokumentRegistreringID])
REFERENCES [dbo].[DokumentRegistrering] ([ID])
GO
ALTER TABLE [dbo].[Erindring] CHECK CONSTRAINT [Erindring_DokumentRegistrering]
GO
ALTER TABLE [dbo].[Erindring]  WITH NOCHECK ADD  CONSTRAINT [Erindring_ErindringType] FOREIGN KEY([ErindringTypeID])
REFERENCES [dbo].[ErindringTypeOpslag] ([ID])
GO
ALTER TABLE [dbo].[Erindring] CHECK CONSTRAINT [Erindring_ErindringType]
GO
ALTER TABLE [dbo].[Erindring]  WITH NOCHECK ADD  CONSTRAINT [Erindring_KladdeRegistrering] FOREIGN KEY([KladdeRegistreringID])
REFERENCES [dbo].[KladdeRegistrering] ([ID])
GO
ALTER TABLE [dbo].[Erindring] CHECK CONSTRAINT [Erindring_KladdeRegistrering]
GO
ALTER TABLE [dbo].[Erindring]  WITH CHECK ADD  CONSTRAINT [Erindring_OprettetAfBruger] FOREIGN KEY([CreatedByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Erindring] CHECK CONSTRAINT [Erindring_OprettetAfBruger]
GO
ALTER TABLE [dbo].[Erindring]  WITH NOCHECK ADD  CONSTRAINT [Erindring_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[Erindring] CHECK CONSTRAINT [Erindring_Sag]
GO
ALTER TABLE [dbo].[Erindring]  WITH CHECK ADD  CONSTRAINT [Erindring_SagsPart] FOREIGN KEY([SagsPartID])
REFERENCES [dbo].[SagsPart] ([ID])
GO
ALTER TABLE [dbo].[Erindring] CHECK CONSTRAINT [Erindring_SagsPart]
GO
ALTER TABLE [dbo].[Erindring]  WITH CHECK ADD  CONSTRAINT [Erindring_SidstRettetAfBruger] FOREIGN KEY([LastChangedByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Erindring] CHECK CONSTRAINT [Erindring_SidstRettetAfBruger]
GO
ALTER TABLE [dbo].[Erindring]  WITH CHECK ADD  CONSTRAINT [FK_Erindring_AnnulleretAf] FOREIGN KEY([AnnulleretAfID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Erindring] CHECK CONSTRAINT [FK_Erindring_AnnulleretAf]
GO
ALTER TABLE [dbo].[Erindring]  WITH CHECK ADD  CONSTRAINT [FK_Erindring_Bruger] FOREIGN KEY([KopierTilID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Erindring] CHECK CONSTRAINT [FK_Erindring_Bruger]
GO
ALTER TABLE [dbo].[Erindring]  WITH CHECK ADD  CONSTRAINT [FK_Erindring_Bruger_OprettetAf] FOREIGN KEY([OpretterID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Erindring] CHECK CONSTRAINT [FK_Erindring_Bruger_OprettetAf]
GO
ALTER TABLE [dbo].[Erindring]  WITH NOCHECK ADD  CONSTRAINT [FK_Erindring_DagsordenpunktsBehandling] FOREIGN KEY([DagsordenpunktsBehandlingID])
REFERENCES [dbo].[DagsordenpunktsBehandling] ([Id])
GO
ALTER TABLE [dbo].[Erindring] CHECK CONSTRAINT [FK_Erindring_DagsordenpunktsBehandling]
GO
ALTER TABLE [dbo].[Erindring]  WITH NOCHECK ADD  CONSTRAINT [FK_Erindring_JournalArkNote] FOREIGN KEY([JournalArkNoteID])
REFERENCES [dbo].[JournalArkNote] ([ID])
GO
ALTER TABLE [dbo].[Erindring] CHECK CONSTRAINT [FK_Erindring_JournalArkNote]
GO
ALTER TABLE [dbo].[ErindringDataRegistrering]  WITH NOCHECK ADD  CONSTRAINT [FK_ErindringDataRegistrering_ErindringID] FOREIGN KEY([ErindringID])
REFERENCES [dbo].[Erindring] ([ID])
GO
ALTER TABLE [dbo].[ErindringDataRegistrering] CHECK CONSTRAINT [FK_ErindringDataRegistrering_ErindringID]
GO
ALTER TABLE [dbo].[ErindringHandling]  WITH NOCHECK ADD  CONSTRAINT [FK_ErindringHandling_Erindring] FOREIGN KEY([ErindringID])
REFERENCES [dbo].[Erindring] ([ID])
GO
ALTER TABLE [dbo].[ErindringHandling] CHECK CONSTRAINT [FK_ErindringHandling_Erindring]
GO
ALTER TABLE [dbo].[ErindringHandling]  WITH NOCHECK ADD  CONSTRAINT [FK_ErindringHandling_Handling] FOREIGN KEY([HandlingID])
REFERENCES [dbo].[Handling] ([ID])
GO
ALTER TABLE [dbo].[ErindringHandling] CHECK CONSTRAINT [FK_ErindringHandling_Handling]
GO
ALTER TABLE [dbo].[ErindringRegel]  WITH CHECK ADD  CONSTRAINT [FK_ErindringRegel_SagSkabelon] FOREIGN KEY([SagSkabelonID])
REFERENCES [dbo].[SagSkabelon] ([ID])
GO
ALTER TABLE [dbo].[ErindringRegel] CHECK CONSTRAINT [FK_ErindringRegel_SagSkabelon]
GO
ALTER TABLE [dbo].[ErindringSkabelon]  WITH NOCHECK ADD  CONSTRAINT [ErindringSkabelon_ErindringType] FOREIGN KEY([ErindringTypeID])
REFERENCES [dbo].[ErindringTypeOpslag] ([ID])
GO
ALTER TABLE [dbo].[ErindringSkabelon] CHECK CONSTRAINT [ErindringSkabelon_ErindringType]
GO
ALTER TABLE [dbo].[ErindringSkabelon]  WITH CHECK ADD  CONSTRAINT [FK_ErindringSkabelon_Bruger] FOREIGN KEY([AnsvarligBrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[ErindringSkabelon] CHECK CONSTRAINT [FK_ErindringSkabelon_Bruger]
GO
ALTER TABLE [dbo].[ErindringSkabelon]  WITH NOCHECK ADD  CONSTRAINT [FK_ErindringSkabelon_HierakiMedlem] FOREIGN KEY([HierakiMedlemID])
REFERENCES [dbo].[HierakiMedlem] ([ID])
GO
ALTER TABLE [dbo].[ErindringSkabelon] CHECK CONSTRAINT [FK_ErindringSkabelon_HierakiMedlem]
GO
ALTER TABLE [dbo].[ErindringSomMail]  WITH CHECK ADD  CONSTRAINT [FK_ErindringSomMail_Ansaettelsessted] FOREIGN KEY([AnsaettelsesstedID])
REFERENCES [dbo].[Ansaettelsessted] ([ID])
GO
ALTER TABLE [dbo].[ErindringSomMail] CHECK CONSTRAINT [FK_ErindringSomMail_Ansaettelsessted]
GO
ALTER TABLE [dbo].[ErindringSomMail]  WITH CHECK ADD  CONSTRAINT [FK_ErindringSomMail_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[ErindringSomMail] CHECK CONSTRAINT [FK_ErindringSomMail_Bruger]
GO
ALTER TABLE [dbo].[ErindringTrin]  WITH NOCHECK ADD  CONSTRAINT [FK_ErindringTrin_Erindring] FOREIGN KEY([ErindringID])
REFERENCES [dbo].[Erindring] ([ID])
GO
ALTER TABLE [dbo].[ErindringTrin] CHECK CONSTRAINT [FK_ErindringTrin_Erindring]
GO
ALTER TABLE [dbo].[ErindringTrin]  WITH NOCHECK ADD  CONSTRAINT [FK_ErindringTrin_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[ErindringTrin] CHECK CONSTRAINT [FK_ErindringTrin_Sag]
GO
ALTER TABLE [dbo].[ErindringTypeOpslag]  WITH NOCHECK ADD  CONSTRAINT [FK_ErindringTypeOpslag_HierakiMedlem] FOREIGN KEY([HierakiMedlemID])
REFERENCES [dbo].[HierakiMedlem] ([ID])
GO
ALTER TABLE [dbo].[ErindringTypeOpslag] CHECK CONSTRAINT [FK_ErindringTypeOpslag_HierakiMedlem]
GO
ALTER TABLE [dbo].[Facet]  WITH NOCHECK ADD  CONSTRAINT [Facet_Bevaring] FOREIGN KEY([BevaringID])
REFERENCES [dbo].[BevaringOpslag] ([ID])
GO
ALTER TABLE [dbo].[Facet] CHECK CONSTRAINT [Facet_Bevaring]
GO
ALTER TABLE [dbo].[Facet]  WITH NOCHECK ADD  CONSTRAINT [Facet_FacetType] FOREIGN KEY([FacetTypeID])
REFERENCES [dbo].[FacetType] ([ID])
GO
ALTER TABLE [dbo].[Facet] CHECK CONSTRAINT [Facet_FacetType]
GO
ALTER TABLE [dbo].[FacetType]  WITH NOCHECK ADD  CONSTRAINT [FK_FacetType_EmnePlan] FOREIGN KEY([EmnePlanID])
REFERENCES [dbo].[EmnePlan] ([ID])
GO
ALTER TABLE [dbo].[FacetType] CHECK CONSTRAINT [FK_FacetType_EmnePlan]
GO
ALTER TABLE [dbo].[Firma]  WITH NOCHECK ADD  CONSTRAINT [Firma_Adresse] FOREIGN KEY([AdresseID])
REFERENCES [dbo].[Adresse] ([ID])
GO
ALTER TABLE [dbo].[Firma] CHECK CONSTRAINT [Firma_Adresse]
GO
ALTER TABLE [dbo].[Firma]  WITH NOCHECK ADD  CONSTRAINT [Firma_KontaktForm] FOREIGN KEY([KontaktForm])
REFERENCES [dbo].[KontaktFormOpslag] ([ID])
GO
ALTER TABLE [dbo].[Firma] CHECK CONSTRAINT [Firma_KontaktForm]
GO
ALTER TABLE [dbo].[Firma]  WITH NOCHECK ADD  CONSTRAINT [FK_Firma_Branche] FOREIGN KEY([BrancheID])
REFERENCES [dbo].[Branche] ([ID])
GO
ALTER TABLE [dbo].[Firma] CHECK CONSTRAINT [FK_Firma_Branche]
GO
ALTER TABLE [dbo].[Firma]  WITH NOCHECK ADD  CONSTRAINT [FK_Firma_KommuneOpslag] FOREIGN KEY([KommuneID])
REFERENCES [dbo].[KommuneOpslag] ([ID])
GO
ALTER TABLE [dbo].[Firma] CHECK CONSTRAINT [FK_Firma_KommuneOpslag]
GO
ALTER TABLE [dbo].[FirmaAttentionPerson]  WITH NOCHECK ADD  CONSTRAINT [FK_FirmaAttentionPerson_Adresse] FOREIGN KEY([AdresseID])
REFERENCES [dbo].[Adresse] ([ID])
GO
ALTER TABLE [dbo].[FirmaAttentionPerson] CHECK CONSTRAINT [FK_FirmaAttentionPerson_Adresse]
GO
ALTER TABLE [dbo].[FirmaAttentionPerson]  WITH NOCHECK ADD  CONSTRAINT [FK_FirmaAttentionPerson_Firma] FOREIGN KEY([FirmaID])
REFERENCES [dbo].[Firma] ([ID])
GO
ALTER TABLE [dbo].[FirmaAttentionPerson] CHECK CONSTRAINT [FK_FirmaAttentionPerson_Firma]
GO
ALTER TABLE [dbo].[FirmaPart]  WITH NOCHECK ADD  CONSTRAINT [FirmaPart_FirmaPartRolle] FOREIGN KEY([FirmaPartRolleID])
REFERENCES [dbo].[FirmaPartRolle] ([ID])
GO
ALTER TABLE [dbo].[FirmaPart] CHECK CONSTRAINT [FirmaPart_FirmaPartRolle]
GO
ALTER TABLE [dbo].[FirmaPart]  WITH NOCHECK ADD  CONSTRAINT [FirmaPart_OprindeligAdresse] FOREIGN KEY([OprindeligAdresseID])
REFERENCES [dbo].[Adresse] ([ID])
GO
ALTER TABLE [dbo].[FirmaPart] CHECK CONSTRAINT [FirmaPart_OprindeligAdresse]
GO
ALTER TABLE [dbo].[FirmaPart]  WITH NOCHECK ADD  CONSTRAINT [FK_FirmaPart_PartTypeOpslag] FOREIGN KEY([PartType])
REFERENCES [dbo].[PartTypeOpslag] ([ID])
GO
ALTER TABLE [dbo].[FirmaPart] CHECK CONSTRAINT [FK_FirmaPart_PartTypeOpslag]
GO
ALTER TABLE [dbo].[FirmaPart]  WITH NOCHECK ADD  CONSTRAINT [PersonFirma_Firma] FOREIGN KEY([FirmaID])
REFERENCES [dbo].[Firma] ([ID])
GO
ALTER TABLE [dbo].[FirmaPart] CHECK CONSTRAINT [PersonFirma_Firma]
GO
ALTER TABLE [dbo].[FkOrgAnsaettelsesstedReference]  WITH CHECK ADD  CONSTRAINT [FK_FkorgAnsaettelsesstedreference_Ansaettelsessted] FOREIGN KEY([AnsaettelsesstedID])
REFERENCES [dbo].[Ansaettelsessted] ([ID])
GO
ALTER TABLE [dbo].[FkOrgAnsaettelsesstedReference] CHECK CONSTRAINT [FK_FkorgAnsaettelsesstedreference_Ansaettelsessted]
GO
ALTER TABLE [dbo].[FkOrgBrugerReference]  WITH CHECK ADD  CONSTRAINT [FK_FkorgBrugerreference_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[FkOrgBrugerReference] CHECK CONSTRAINT [FK_FkorgBrugerreference_Bruger]
GO
ALTER TABLE [dbo].[FkOrgHierarkiMedlemReference]  WITH CHECK ADD  CONSTRAINT [FK_FkorgHierarkimedlemreference_Hierarkimedlem] FOREIGN KEY([HierarkiMedlemID])
REFERENCES [dbo].[HierakiMedlem] ([ID])
GO
ALTER TABLE [dbo].[FkOrgHierarkiMedlemReference] CHECK CONSTRAINT [FK_FkorgHierarkimedlemreference_Hierarkimedlem]
GO
ALTER TABLE [dbo].[Flow]  WITH CHECK ADD  CONSTRAINT [FK_Flow_Bruger] FOREIGN KEY([OprettetAf])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Flow] CHECK CONSTRAINT [FK_Flow_Bruger]
GO
ALTER TABLE [dbo].[Flow]  WITH CHECK ADD  CONSTRAINT [FK_Flow_Dokument] FOREIGN KEY([DokumentID])
REFERENCES [dbo].[Dokument] ([ID])
GO
ALTER TABLE [dbo].[Flow] CHECK CONSTRAINT [FK_Flow_Dokument]
GO
ALTER TABLE [dbo].[Flow]  WITH CHECK ADD  CONSTRAINT [FK_Flow_Kladde] FOREIGN KEY([KladdeID])
REFERENCES [dbo].[Kladde] ([ID])
GO
ALTER TABLE [dbo].[Flow] CHECK CONSTRAINT [FK_Flow_Kladde]
GO
ALTER TABLE [dbo].[FlowModtager]  WITH CHECK ADD  CONSTRAINT [FK_FlowModtager_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[FlowModtager] CHECK CONSTRAINT [FK_FlowModtager_Bruger]
GO
ALTER TABLE [dbo].[FlowModtager]  WITH CHECK ADD  CONSTRAINT [FK_FlowModtager_Flow] FOREIGN KEY([FlowID])
REFERENCES [dbo].[Flow] ([ID])
GO
ALTER TABLE [dbo].[FlowModtager] CHECK CONSTRAINT [FK_FlowModtager_Flow]
GO
ALTER TABLE [dbo].[FlowModtagerSvar]  WITH CHECK ADD  CONSTRAINT [FK_FlowModtagerSvar_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[FlowModtagerSvar] CHECK CONSTRAINT [FK_FlowModtagerSvar_Bruger]
GO
ALTER TABLE [dbo].[FlowModtagerSvar]  WITH CHECK ADD  CONSTRAINT [FK_FlowModtagerSvar_FlowModtager] FOREIGN KEY([FlowModtagerID])
REFERENCES [dbo].[FlowModtager] ([ID])
GO
ALTER TABLE [dbo].[FlowModtagerSvar] CHECK CONSTRAINT [FK_FlowModtagerSvar_FlowModtager]
GO
ALTER TABLE [dbo].[FlowSkabelon]  WITH CHECK ADD  CONSTRAINT [FK_FlowSkabelon_Ansaettelsessted] FOREIGN KEY([AnsaettelsesstedID])
REFERENCES [dbo].[Ansaettelsessted] ([ID])
GO
ALTER TABLE [dbo].[FlowSkabelon] CHECK CONSTRAINT [FK_FlowSkabelon_Ansaettelsessted]
GO
ALTER TABLE [dbo].[FlowSkabelonModtager]  WITH CHECK ADD  CONSTRAINT [FK_FlowSkabelonModtager_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[FlowSkabelonModtager] CHECK CONSTRAINT [FK_FlowSkabelonModtager_Bruger]
GO
ALTER TABLE [dbo].[FlowSkabelonModtager]  WITH CHECK ADD  CONSTRAINT [FK_FlowSkabelonModtager_FlowSkabelon] FOREIGN KEY([FlowSkabelonID])
REFERENCES [dbo].[FlowSkabelon] ([ID])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[FlowSkabelonModtager] CHECK CONSTRAINT [FK_FlowSkabelonModtager_FlowSkabelon]
GO
ALTER TABLE [dbo].[Forloeb]  WITH NOCHECK ADD  CONSTRAINT [FK_Forloeb_Erindring] FOREIGN KEY([ErindringID])
REFERENCES [dbo].[Erindring] ([ID])
GO
ALTER TABLE [dbo].[Forloeb] CHECK CONSTRAINT [FK_Forloeb_Erindring]
GO
ALTER TABLE [dbo].[Forloeb]  WITH CHECK ADD  CONSTRAINT [Forloeb_Bruger] FOREIGN KEY([RegistreretAfID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Forloeb] CHECK CONSTRAINT [Forloeb_Bruger]
GO
ALTER TABLE [dbo].[Forloeb]  WITH NOCHECK ADD  CONSTRAINT [Forloeb_Delforloeb] FOREIGN KEY([DelforloebID])
REFERENCES [dbo].[Delforloeb] ([ID])
GO
ALTER TABLE [dbo].[Forloeb] CHECK CONSTRAINT [Forloeb_Delforloeb]
GO
ALTER TABLE [dbo].[Forloeb]  WITH NOCHECK ADD  CONSTRAINT [Forloeb_ForloebType] FOREIGN KEY([ForloebTypeID])
REFERENCES [dbo].[ForloebTypeOpslag] ([ID])
GO
ALTER TABLE [dbo].[Forloeb] CHECK CONSTRAINT [Forloeb_ForloebType]
GO
ALTER TABLE [dbo].[Forloeb]  WITH NOCHECK ADD  CONSTRAINT [Forloeb_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[Forloeb] CHECK CONSTRAINT [Forloeb_Sag]
GO
ALTER TABLE [dbo].[Fravaer]  WITH CHECK ADD  CONSTRAINT [FK_Fravaer_Moede] FOREIGN KEY([MoedeId])
REFERENCES [dbo].[Moede] ([ID])
GO
ALTER TABLE [dbo].[Fravaer] CHECK CONSTRAINT [FK_Fravaer_Moede]
GO
ALTER TABLE [dbo].[Fravaer]  WITH NOCHECK ADD  CONSTRAINT [FK_Fravaer_Udvalgsperson] FOREIGN KEY([UdvalgspersonId])
REFERENCES [dbo].[Udvalgsperson] ([ID])
GO
ALTER TABLE [dbo].[Fravaer] CHECK CONSTRAINT [FK_Fravaer_Udvalgsperson]
GO
ALTER TABLE [dbo].[FravaerDagsorden]  WITH CHECK ADD  CONSTRAINT [FK_FravaerDagsorden_Dagsorden] FOREIGN KEY([DagsordenId])
REFERENCES [dbo].[Dagsorden] ([ID])
GO
ALTER TABLE [dbo].[FravaerDagsorden] CHECK CONSTRAINT [FK_FravaerDagsorden_Dagsorden]
GO
ALTER TABLE [dbo].[FravaerDagsorden]  WITH NOCHECK ADD  CONSTRAINT [FK_FravaerDagsorden_Fravaer] FOREIGN KEY([FravaerId])
REFERENCES [dbo].[Fravaer] ([Id])
GO
ALTER TABLE [dbo].[FravaerDagsorden] CHECK CONSTRAINT [FK_FravaerDagsorden_Fravaer]
GO
ALTER TABLE [dbo].[FravaerDagsordenpunktsBehandling]  WITH NOCHECK ADD  CONSTRAINT [FK_FravaerDagsordenpunktsBehandling_DagsordenPunktsBehandling] FOREIGN KEY([DagsordenpunktsBehandlingId])
REFERENCES [dbo].[DagsordenpunktsBehandling] ([Id])
GO
ALTER TABLE [dbo].[FravaerDagsordenpunktsBehandling] CHECK CONSTRAINT [FK_FravaerDagsordenpunktsBehandling_DagsordenPunktsBehandling]
GO
ALTER TABLE [dbo].[FravaerDagsordenpunktsBehandling]  WITH NOCHECK ADD  CONSTRAINT [FK_FravaerDagsordenpunktsBehandling_Fravaer] FOREIGN KEY([FravaerId])
REFERENCES [dbo].[Fravaer] ([Id])
GO
ALTER TABLE [dbo].[FravaerDagsordenpunktsBehandling] CHECK CONSTRAINT [FK_FravaerDagsordenpunktsBehandling_Fravaer]
GO
ALTER TABLE [dbo].[GeneratorIndstillinger]  WITH CHECK ADD  CONSTRAINT [FK_GeneratorIndstillinger_Bruger_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[GeneratorIndstillinger] CHECK CONSTRAINT [FK_GeneratorIndstillinger_Bruger_Bruger]
GO
ALTER TABLE [dbo].[GeneratorIndstillinger]  WITH CHECK ADD  CONSTRAINT [FK_GeneratorIndstillinger_Bruger_CreatedBy] FOREIGN KEY([CreatedBy])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[GeneratorIndstillinger] CHECK CONSTRAINT [FK_GeneratorIndstillinger_Bruger_CreatedBy]
GO
ALTER TABLE [dbo].[GeneratorIndstillinger]  WITH CHECK ADD  CONSTRAINT [FK_GeneratorIndstillinger_Bruger_LastChangedBy] FOREIGN KEY([LastChangedBy])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[GeneratorIndstillinger] CHECK CONSTRAINT [FK_GeneratorIndstillinger_Bruger_LastChangedBy]
GO
ALTER TABLE [dbo].[GeneratorIndstillinger]  WITH CHECK ADD  CONSTRAINT [FK_GeneratorIndstillinger_Dagsorden_Dagsorden] FOREIGN KEY([DagsordenID])
REFERENCES [dbo].[Dagsorden] ([ID])
GO
ALTER TABLE [dbo].[GeneratorIndstillinger] CHECK CONSTRAINT [FK_GeneratorIndstillinger_Dagsorden_Dagsorden]
GO
ALTER TABLE [dbo].[GeneratorIndstillinger]  WITH CHECK ADD  CONSTRAINT [FK_GeneratorIndstillinger_Udvalg] FOREIGN KEY([UdvalgID])
REFERENCES [dbo].[Udvalg] ([ID])
GO
ALTER TABLE [dbo].[GeneratorIndstillinger] CHECK CONSTRAINT [FK_GeneratorIndstillinger_Udvalg]
GO
ALTER TABLE [dbo].[GeneratorIndstillingerFeltRegistrering]  WITH CHECK ADD  CONSTRAINT [FK_GeneratorIndstillingerFeltRegistrering_DagsordenpunktFelt] FOREIGN KEY([DagsordenpunktFeltID])
REFERENCES [dbo].[DagsordenpunktFelt] ([ID])
GO
ALTER TABLE [dbo].[GeneratorIndstillingerFeltRegistrering] CHECK CONSTRAINT [FK_GeneratorIndstillingerFeltRegistrering_DagsordenpunktFelt]
GO
ALTER TABLE [dbo].[GeneratorIndstillingerFeltRegistrering]  WITH CHECK ADD  CONSTRAINT [FK_GeneratorIndstillingerFeltRegistrering_GeneratorIndstillinger] FOREIGN KEY([GeneratorIndstillingerID])
REFERENCES [dbo].[GeneratorIndstillinger] ([ID])
GO
ALTER TABLE [dbo].[GeneratorIndstillingerFeltRegistrering] CHECK CONSTRAINT [FK_GeneratorIndstillingerFeltRegistrering_GeneratorIndstillinger]
GO
ALTER TABLE [dbo].[GenstandRegistrering]  WITH NOCHECK ADD  CONSTRAINT [GenstandRegistrering_GenstandType] FOREIGN KEY([GenstandType])
REFERENCES [dbo].[GenstandTypeOpslag] ([ID])
GO
ALTER TABLE [dbo].[GenstandRegistrering] CHECK CONSTRAINT [GenstandRegistrering_GenstandType]
GO
ALTER TABLE [dbo].[GenstandRegistrering]  WITH NOCHECK ADD  CONSTRAINT [GenstandRegistrering_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[GenstandRegistrering] CHECK CONSTRAINT [GenstandRegistrering_Sag]
GO
ALTER TABLE [dbo].[Geometri]  WITH NOCHECK ADD  CONSTRAINT [FK_Geometri_GeometriFormat] FOREIGN KEY([GeometriFormatID])
REFERENCES [dbo].[GeometriFormatOpslag] ([ID])
GO
ALTER TABLE [dbo].[Geometri] CHECK CONSTRAINT [FK_Geometri_GeometriFormat]
GO
ALTER TABLE [dbo].[GridLayout]  WITH CHECK ADD  CONSTRAINT [FK_GridLayout_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[GridLayout] CHECK CONSTRAINT [FK_GridLayout_Bruger]
GO
ALTER TABLE [dbo].[Handling]  WITH NOCHECK ADD  CONSTRAINT [FK_Handling_AnvendErindringSkabelon] FOREIGN KEY([AnvendErindringSkabelonID])
REFERENCES [dbo].[ErindringSkabelon] ([ID])
GO
ALTER TABLE [dbo].[Handling] CHECK CONSTRAINT [FK_Handling_AnvendErindringSkabelon]
GO
ALTER TABLE [dbo].[Handling]  WITH NOCHECK ADD  CONSTRAINT [FK_Handling_ErindringSkabelon] FOREIGN KEY([ErindringSkabelonID])
REFERENCES [dbo].[ErindringSkabelon] ([ID])
GO
ALTER TABLE [dbo].[Handling] CHECK CONSTRAINT [FK_Handling_ErindringSkabelon]
GO
ALTER TABLE [dbo].[Handling]  WITH CHECK ADD  CONSTRAINT [FK_Handling_SagSkabelon] FOREIGN KEY([SagSkabelonID])
REFERENCES [dbo].[SagSkabelon] ([ID])
GO
ALTER TABLE [dbo].[Handling] CHECK CONSTRAINT [FK_Handling_SagSkabelon]
GO
ALTER TABLE [dbo].[Handling]  WITH NOCHECK ADD  CONSTRAINT [FK_Handling_Skabelon] FOREIGN KEY([SkabelonID])
REFERENCES [dbo].[Skabelon] ([ID])
GO
ALTER TABLE [dbo].[Handling] CHECK CONSTRAINT [FK_Handling_Skabelon]
GO
ALTER TABLE [dbo].[Handling]  WITH NOCHECK ADD  CONSTRAINT [FK_Handling_SkabelonType] FOREIGN KEY([SkabelonTypeID])
REFERENCES [dbo].[SkabelonType] ([ID])
GO
ALTER TABLE [dbo].[Handling] CHECK CONSTRAINT [FK_Handling_SkabelonType]
GO
ALTER TABLE [dbo].[Heartbeat]  WITH CHECK ADD  CONSTRAINT [FK_Heartbeat_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Heartbeat] CHECK CONSTRAINT [FK_Heartbeat_Bruger]
GO
ALTER TABLE [dbo].[HierakiMedlem]  WITH NOCHECK ADD  CONSTRAINT [FK_HierakiMedlem_Hieraki] FOREIGN KEY([HierakiID])
REFERENCES [dbo].[Hieraki] ([ID])
GO
ALTER TABLE [dbo].[HierakiMedlem] CHECK CONSTRAINT [FK_HierakiMedlem_Hieraki]
GO
ALTER TABLE [dbo].[HierakiMedlem]  WITH NOCHECK ADD  CONSTRAINT [FK_HierakiMedlem_HierakiMedlem] FOREIGN KEY([ParentID])
REFERENCES [dbo].[HierakiMedlem] ([ID])
GO
ALTER TABLE [dbo].[HierakiMedlem] CHECK CONSTRAINT [FK_HierakiMedlem_HierakiMedlem]
GO
ALTER TABLE [dbo].[JournalArk]  WITH NOCHECK ADD  CONSTRAINT [FK_JournalArk_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[JournalArk] CHECK CONSTRAINT [FK_JournalArk_Sag]
GO
ALTER TABLE [dbo].[JournalArkNote]  WITH CHECK ADD  CONSTRAINT [FK_JournalArkNote_Bruger] FOREIGN KEY([OprettetAf])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[JournalArkNote] CHECK CONSTRAINT [FK_JournalArkNote_Bruger]
GO
ALTER TABLE [dbo].[JournalArkNote]  WITH NOCHECK ADD  CONSTRAINT [FK_JournalArkNote_JournalArk] FOREIGN KEY([JournalArkID])
REFERENCES [dbo].[JournalArk] ([ID])
GO
ALTER TABLE [dbo].[JournalArkNote] CHECK CONSTRAINT [FK_JournalArkNote_JournalArk]
GO
ALTER TABLE [dbo].[JournalArkNoteVedrPart]  WITH NOCHECK ADD  CONSTRAINT [FK_JournalArkNoteVedrPart_JournalArkNote] FOREIGN KEY([JournalArkNoteID])
REFERENCES [dbo].[JournalArkNote] ([ID])
GO
ALTER TABLE [dbo].[JournalArkNoteVedrPart] CHECK CONSTRAINT [FK_JournalArkNoteVedrPart_JournalArkNote]
GO
ALTER TABLE [dbo].[JournalArkNoteVedrPart]  WITH CHECK ADD  CONSTRAINT [FK_JournalArkNoteVedrPart_SagsPart] FOREIGN KEY([SagspartID])
REFERENCES [dbo].[SagsPart] ([ID])
GO
ALTER TABLE [dbo].[JournalArkNoteVedrPart] CHECK CONSTRAINT [FK_JournalArkNoteVedrPart_SagsPart]
GO
ALTER TABLE [dbo].[Kladde]  WITH CHECK ADD  CONSTRAINT [FK_Kladde_Bruger_LastChangedBy] FOREIGN KEY([LastChangedByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Kladde] CHECK CONSTRAINT [FK_Kladde_Bruger_LastChangedBy]
GO
ALTER TABLE [dbo].[Kladde]  WITH CHECK ADD  CONSTRAINT [FK_Kladde_DeletedByBruger] FOREIGN KEY([DeletedByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Kladde] CHECK CONSTRAINT [FK_Kladde_DeletedByBruger]
GO
ALTER TABLE [dbo].[Kladde]  WITH CHECK ADD  CONSTRAINT [Kladde_CheckedOutByBruger] FOREIGN KEY([CheckedOutByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Kladde] CHECK CONSTRAINT [Kladde_CheckedOutByBruger]
GO
ALTER TABLE [dbo].[Kladde]  WITH CHECK ADD  CONSTRAINT [Kladde_CreatedByBruger] FOREIGN KEY([CreatedByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Kladde] CHECK CONSTRAINT [Kladde_CreatedByBruger]
GO
ALTER TABLE [dbo].[Kladde]  WITH CHECK ADD  CONSTRAINT [Kladde_LastCheckedInByBruger] FOREIGN KEY([LastCheckedInByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Kladde] CHECK CONSTRAINT [Kladde_LastCheckedInByBruger]
GO
ALTER TABLE [dbo].[KladdePart]  WITH NOCHECK ADD  CONSTRAINT [FK_KladdePart_FirmaAttentionPerson] FOREIGN KEY([FirmaAttentionPersonID])
REFERENCES [dbo].[FirmaAttentionPerson] ([ID])
GO
ALTER TABLE [dbo].[KladdePart] CHECK CONSTRAINT [FK_KladdePart_FirmaAttentionPerson]
GO
ALTER TABLE [dbo].[KladdePart]  WITH NOCHECK ADD  CONSTRAINT [KladdePart_Kladde] FOREIGN KEY([KladdeID])
REFERENCES [dbo].[Kladde] ([ID])
GO
ALTER TABLE [dbo].[KladdePart] CHECK CONSTRAINT [KladdePart_Kladde]
GO
ALTER TABLE [dbo].[KladdePart]  WITH NOCHECK ADD  CONSTRAINT [KladdePart_KontaktForm] FOREIGN KEY([KontaktForm])
REFERENCES [dbo].[KontaktFormOpslag] ([ID])
GO
ALTER TABLE [dbo].[KladdePart] CHECK CONSTRAINT [KladdePart_KontaktForm]
GO
ALTER TABLE [dbo].[KladdePartDokument]  WITH NOCHECK ADD  CONSTRAINT [FK_KladdePartDokument_Dokument] FOREIGN KEY([DokumentID])
REFERENCES [dbo].[Dokument] ([ID])
GO
ALTER TABLE [dbo].[KladdePartDokument] CHECK CONSTRAINT [FK_KladdePartDokument_Dokument]
GO
ALTER TABLE [dbo].[KladdePartDokument]  WITH NOCHECK ADD  CONSTRAINT [FK_KladdePartDokument_KladdePart] FOREIGN KEY([KladdePartID])
REFERENCES [dbo].[KladdePart] ([ID])
GO
ALTER TABLE [dbo].[KladdePartDokument] CHECK CONSTRAINT [FK_KladdePartDokument_KladdePart]
GO
ALTER TABLE [dbo].[KladdeRegistrering]  WITH CHECK ADD  CONSTRAINT [KladdeRegistrering_Bruger] FOREIGN KEY([RegistreretAfID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[KladdeRegistrering] CHECK CONSTRAINT [KladdeRegistrering_Bruger]
GO
ALTER TABLE [dbo].[KladdeRegistrering]  WITH NOCHECK ADD  CONSTRAINT [KladdeRegistrering_Kladde] FOREIGN KEY([KladdeID])
REFERENCES [dbo].[Kladde] ([ID])
GO
ALTER TABLE [dbo].[KladdeRegistrering] CHECK CONSTRAINT [KladdeRegistrering_Kladde]
GO
ALTER TABLE [dbo].[KladdeRegistrering]  WITH NOCHECK ADD  CONSTRAINT [KladdeRegistrering_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[KladdeRegistrering] CHECK CONSTRAINT [KladdeRegistrering_Sag]
GO
ALTER TABLE [dbo].[KladdeRegistrering]  WITH CHECK ADD  CONSTRAINT [KladdeRegistrering_SagsPart] FOREIGN KEY([SagsPartID])
REFERENCES [dbo].[SagsPart] ([ID])
GO
ALTER TABLE [dbo].[KladdeRegistrering] CHECK CONSTRAINT [KladdeRegistrering_SagsPart]
GO
ALTER TABLE [dbo].[KladdeRegistrering]  WITH NOCHECK ADD  CONSTRAINT [KladdeRegistrering_SecuritySet] FOREIGN KEY([SecuritySetID])
REFERENCES [dbo].[SecuritySet] ([ID])
GO
ALTER TABLE [dbo].[KladdeRegistrering] CHECK CONSTRAINT [KladdeRegistrering_SecuritySet]
GO
ALTER TABLE [dbo].[KnownEksterntSystemStylesheetMap]  WITH NOCHECK ADD  CONSTRAINT [FK_KnownEksterntSystemStylesheetMap_KnownEksterntSystemOpslag] FOREIGN KEY([KnownEksternSystemID])
REFERENCES [dbo].[KnownEksterntSystem] ([ID])
GO
ALTER TABLE [dbo].[KnownEksterntSystemStylesheetMap] CHECK CONSTRAINT [FK_KnownEksterntSystemStylesheetMap_KnownEksterntSystemOpslag]
GO
ALTER TABLE [dbo].[KnownEksterntSystemStylesheetMap]  WITH NOCHECK ADD  CONSTRAINT [FK_KnownEksterntSystemStylesheetMap_Stylesheet] FOREIGN KEY([StylesheetID])
REFERENCES [dbo].[Stylesheet] ([ID])
GO
ALTER TABLE [dbo].[KnownEksterntSystemStylesheetMap] CHECK CONSTRAINT [FK_KnownEksterntSystemStylesheetMap_Stylesheet]
GO
ALTER TABLE [dbo].[Log]  WITH CHECK ADD  CONSTRAINT [Log_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Log] CHECK CONSTRAINT [Log_Bruger]
GO
ALTER TABLE [dbo].[Lokation]  WITH NOCHECK ADD  CONSTRAINT [FK_Lokation_KommuneOpslag] FOREIGN KEY([KommuneID])
REFERENCES [dbo].[KommuneOpslag] ([ID])
GO
ALTER TABLE [dbo].[Lokation] CHECK CONSTRAINT [FK_Lokation_KommuneOpslag]
GO
ALTER TABLE [dbo].[Lokation]  WITH NOCHECK ADD  CONSTRAINT [FK_Lokation_PostnummerOpslag] FOREIGN KEY([PostNummerID])
REFERENCES [dbo].[Postnummer] ([ID])
GO
ALTER TABLE [dbo].[Lokation] CHECK CONSTRAINT [FK_Lokation_PostnummerOpslag]
GO
ALTER TABLE [dbo].[MailRecipient]  WITH NOCHECK ADD  CONSTRAINT [FK_MailRecipient_Mail] FOREIGN KEY([MailID])
REFERENCES [dbo].[Mail] ([ID])
GO
ALTER TABLE [dbo].[MailRecipient] CHECK CONSTRAINT [FK_MailRecipient_Mail]
GO
ALTER TABLE [dbo].[MapDelforloeb]  WITH NOCHECK ADD  CONSTRAINT [FK_MapDelforloeb_MapSag] FOREIGN KEY([MapSagID])
REFERENCES [dbo].[MapSag] ([ID])
GO
ALTER TABLE [dbo].[MapDelforloeb] CHECK CONSTRAINT [FK_MapDelforloeb_MapSag]
GO
ALTER TABLE [dbo].[MapDelforloebDokument]  WITH NOCHECK ADD  CONSTRAINT [FK_MapDelforloebDokument_MapDelforloeb] FOREIGN KEY([MapDelforloebID])
REFERENCES [dbo].[MapDelforloeb] ([ID])
GO
ALTER TABLE [dbo].[MapDelforloebDokument] CHECK CONSTRAINT [FK_MapDelforloebDokument_MapDelforloeb]
GO
ALTER TABLE [dbo].[MapNemJournaliseringSagSkabelon]  WITH CHECK ADD  CONSTRAINT [FK_MapNemJournalisering_SagSkabelon] FOREIGN KEY([SagSkabelonID])
REFERENCES [dbo].[SagSkabelon] ([ID])
GO
ALTER TABLE [dbo].[MapNemJournaliseringSagSkabelon] CHECK CONSTRAINT [FK_MapNemJournalisering_SagSkabelon]
GO
ALTER TABLE [dbo].[MapSag]  WITH CHECK ADD  CONSTRAINT [FK_MapSag_Sagsbehandler] FOREIGN KEY([SagsbehandlerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[MapSag] CHECK CONSTRAINT [FK_MapSag_Sagsbehandler]
GO
ALTER TABLE [dbo].[Matrikel]  WITH NOCHECK ADD  CONSTRAINT [FK_Matrikel_Kommune] FOREIGN KEY([KommuneID])
REFERENCES [dbo].[KommuneOpslag] ([ID])
GO
ALTER TABLE [dbo].[Matrikel] CHECK CONSTRAINT [FK_Matrikel_Kommune]
GO
ALTER TABLE [dbo].[Matrikel]  WITH NOCHECK ADD  CONSTRAINT [FK_Matrikel_MatrikelArt] FOREIGN KEY([ArtID])
REFERENCES [dbo].[MatrikelArt] ([ID])
GO
ALTER TABLE [dbo].[Matrikel] CHECK CONSTRAINT [FK_Matrikel_MatrikelArt]
GO
ALTER TABLE [dbo].[Matrikel]  WITH NOCHECK ADD  CONSTRAINT [Matrikel_BeliggenhedAdresse] FOREIGN KEY([BeliggenhedAdresseID])
REFERENCES [dbo].[Adresse] ([ID])
GO
ALTER TABLE [dbo].[Matrikel] CHECK CONSTRAINT [Matrikel_BeliggenhedAdresse]
GO
ALTER TABLE [dbo].[MatrikelEjendom]  WITH NOCHECK ADD  CONSTRAINT [FK_MatrikelEjendom_Ejendom] FOREIGN KEY([EjendomID])
REFERENCES [dbo].[Ejendom] ([ID])
GO
ALTER TABLE [dbo].[MatrikelEjendom] CHECK CONSTRAINT [FK_MatrikelEjendom_Ejendom]
GO
ALTER TABLE [dbo].[MatrikelEjendom]  WITH NOCHECK ADD  CONSTRAINT [FK_MatrikelEjendom_Matrikel] FOREIGN KEY([MatrikelID])
REFERENCES [dbo].[Matrikel] ([ID])
GO
ALTER TABLE [dbo].[MatrikelEjendom] CHECK CONSTRAINT [FK_MatrikelEjendom_Matrikel]
GO
ALTER TABLE [dbo].[Memo]  WITH CHECK ADD  CONSTRAINT [FK_Memo_DokumentRegistrering] FOREIGN KEY([DokumentRegistreringID])
REFERENCES [dbo].[DokumentRegistrering] ([ID])
GO
ALTER TABLE [dbo].[Memo] CHECK CONSTRAINT [FK_Memo_DokumentRegistrering]
GO
ALTER TABLE [dbo].[Moede]  WITH CHECK ADD  CONSTRAINT [FK_Moede_Bruger_CreatedBy] FOREIGN KEY([CreatedBy])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Moede] CHECK CONSTRAINT [FK_Moede_Bruger_CreatedBy]
GO
ALTER TABLE [dbo].[Moede]  WITH CHECK ADD  CONSTRAINT [FK_Moede_Bruger_LastChangedBy] FOREIGN KEY([LastChangedBy])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Moede] CHECK CONSTRAINT [FK_Moede_Bruger_LastChangedBy]
GO
ALTER TABLE [dbo].[Moede]  WITH CHECK ADD  CONSTRAINT [FK_Moede_Moeder_Udvalg] FOREIGN KEY([UdvalgID])
REFERENCES [dbo].[Udvalg] ([ID])
GO
ALTER TABLE [dbo].[Moede] CHECK CONSTRAINT [FK_Moede_Moeder_Udvalg]
GO
ALTER TABLE [dbo].[MostRecentInfo]  WITH CHECK ADD  CONSTRAINT [FK_MostRecentInfo_Bruger] FOREIGN KEY([OwnerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[MostRecentInfo] CHECK CONSTRAINT [FK_MostRecentInfo_Bruger]
GO
ALTER TABLE [dbo].[Nyhed]  WITH CHECK ADD  CONSTRAINT [FK_Nyhed_OprettetAfBruger] FOREIGN KEY([OprettetAfID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Nyhed] CHECK CONSTRAINT [FK_Nyhed_OprettetAfBruger]
GO
ALTER TABLE [dbo].[Person]  WITH NOCHECK ADD  CONSTRAINT [FK_Person_CivilstandOpslag] FOREIGN KEY([CivilstandID])
REFERENCES [dbo].[CivilstandOpslag] ([ID])
GO
ALTER TABLE [dbo].[Person] CHECK CONSTRAINT [FK_Person_CivilstandOpslag]
GO
ALTER TABLE [dbo].[Person]  WITH NOCHECK ADD  CONSTRAINT [FK_Person_KommuneOpslag] FOREIGN KEY([KommuneID])
REFERENCES [dbo].[KommuneOpslag] ([ID])
GO
ALTER TABLE [dbo].[Person] CHECK CONSTRAINT [FK_Person_KommuneOpslag]
GO
ALTER TABLE [dbo].[Person]  WITH NOCHECK ADD  CONSTRAINT [Person_Adresse] FOREIGN KEY([AdresseID])
REFERENCES [dbo].[Adresse] ([ID])
NOT FOR REPLICATION
GO
ALTER TABLE [dbo].[Person] CHECK CONSTRAINT [Person_Adresse]
GO
ALTER TABLE [dbo].[Person]  WITH NOCHECK ADD  CONSTRAINT [Person_KontaktForm] FOREIGN KEY([KontaktForm])
REFERENCES [dbo].[KontaktFormOpslag] ([ID])
GO
ALTER TABLE [dbo].[Person] CHECK CONSTRAINT [Person_KontaktForm]
GO
ALTER TABLE [dbo].[PessimisticLockInfo]  WITH CHECK ADD  CONSTRAINT [FK_PessimisticLockInfo_Bruger] FOREIGN KEY([LockedByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[PessimisticLockInfo] CHECK CONSTRAINT [FK_PessimisticLockInfo_Bruger]
GO
ALTER TABLE [dbo].[PessimisticLockInfo]  WITH CHECK ADD  CONSTRAINT [FK_PessimisticLockInfo_UnlockedByBruger] FOREIGN KEY([UnLockedByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[PessimisticLockInfo] CHECK CONSTRAINT [FK_PessimisticLockInfo_UnlockedByBruger]
GO
ALTER TABLE [dbo].[PluginConfigurationSecuritySet]  WITH CHECK ADD  CONSTRAINT [FK_SecuritySet_TrustedAssembly] FOREIGN KEY([SecuritySetID])
REFERENCES [dbo].[SecuritySet] ([ID])
GO
ALTER TABLE [dbo].[PluginConfigurationSecuritySet] CHECK CONSTRAINT [FK_SecuritySet_TrustedAssembly]
GO
ALTER TABLE [dbo].[PluginConfigurationSecuritySet]  WITH CHECK ADD  CONSTRAINT [FK_TrustedAssembly_SecuritySet] FOREIGN KEY([TrustedAssemblyID])
REFERENCES [dbo].[TrustedAssembly] ([ID])
GO
ALTER TABLE [dbo].[PluginConfigurationSecuritySet] CHECK CONSTRAINT [FK_TrustedAssembly_SecuritySet]
GO
ALTER TABLE [dbo].[PostnummerKommune]  WITH NOCHECK ADD  CONSTRAINT [FK_PostnummerKommune_KommuneOpslag] FOREIGN KEY([KommuneID])
REFERENCES [dbo].[KommuneOpslag] ([ID])
GO
ALTER TABLE [dbo].[PostnummerKommune] CHECK CONSTRAINT [FK_PostnummerKommune_KommuneOpslag]
GO
ALTER TABLE [dbo].[PostnummerKommune]  WITH NOCHECK ADD  CONSTRAINT [FK_PostnummerKommune_Postnummer] FOREIGN KEY([PostnummerID])
REFERENCES [dbo].[Postnummer] ([ID])
GO
ALTER TABLE [dbo].[PostnummerKommune] CHECK CONSTRAINT [FK_PostnummerKommune_Postnummer]
GO
ALTER TABLE [dbo].[Publisering]  WITH CHECK ADD  CONSTRAINT [FK_Publicering_Bruger] FOREIGN KEY([OprettetAfID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Publisering] CHECK CONSTRAINT [FK_Publicering_Bruger]
GO
ALTER TABLE [dbo].[PubliseringDokument]  WITH NOCHECK ADD  CONSTRAINT [FK_PubliceringDokument_Publicering] FOREIGN KEY([PubliseringID])
REFERENCES [dbo].[Publisering] ([ID])
GO
ALTER TABLE [dbo].[PubliseringDokument] CHECK CONSTRAINT [FK_PubliceringDokument_Publicering]
GO
ALTER TABLE [dbo].[PubliseringDokument]  WITH NOCHECK ADD  CONSTRAINT [FK_PubliseringDokument_DokumentRegistrering] FOREIGN KEY([DokumentRegistreringID])
REFERENCES [dbo].[DokumentRegistrering] ([ID])
GO
ALTER TABLE [dbo].[PubliseringDokument] CHECK CONSTRAINT [FK_PubliseringDokument_DokumentRegistrering]
GO
ALTER TABLE [dbo].[PubliseringPlan]  WITH NOCHECK ADD  CONSTRAINT [FK_PubliseringPlan_Publisering] FOREIGN KEY([SidstePubliseringID])
REFERENCES [dbo].[Publisering] ([ID])
GO
ALTER TABLE [dbo].[PubliseringPlan] CHECK CONSTRAINT [FK_PubliseringPlan_Publisering]
GO
ALTER TABLE [dbo].[PubliseringPlan]  WITH NOCHECK ADD  CONSTRAINT [FK_PubliseringPlan_PubliseringIndstillinger] FOREIGN KEY([PubliseringIndstillingerID])
REFERENCES [dbo].[PubliseringIndstillinger] ([ID])
GO
ALTER TABLE [dbo].[PubliseringPlan] CHECK CONSTRAINT [FK_PubliseringPlan_PubliseringIndstillinger]
GO
ALTER TABLE [dbo].[PubliseringTarget]  WITH NOCHECK ADD  CONSTRAINT [FK_PubliseringTarget_PubliseringIndstillinger] FOREIGN KEY([PubliseringIndstillingerID])
REFERENCES [dbo].[PubliseringIndstillinger] ([ID])
GO
ALTER TABLE [dbo].[PubliseringTarget] CHECK CONSTRAINT [FK_PubliseringTarget_PubliseringIndstillinger]
GO
ALTER TABLE [dbo].[PubliseringTarget]  WITH NOCHECK ADD  CONSTRAINT [FK_PubliseringTarget_Stylesheet] FOREIGN KEY([XslStylesheetID])
REFERENCES [dbo].[Stylesheet] ([ID])
GO
ALTER TABLE [dbo].[PubliseringTarget] CHECK CONSTRAINT [FK_PubliseringTarget_Stylesheet]
GO
ALTER TABLE [dbo].[PubliseringTarget]  WITH NOCHECK ADD  CONSTRAINT [FK_PubliseringTarget_Stylesheet1] FOREIGN KEY([CssStylesheetID])
REFERENCES [dbo].[Stylesheet] ([ID])
GO
ALTER TABLE [dbo].[PubliseringTarget] CHECK CONSTRAINT [FK_PubliseringTarget_Stylesheet1]
GO
ALTER TABLE [dbo].[QueryProfil]  WITH CHECK ADD  CONSTRAINT [FK_QueryProfil_Bruger] FOREIGN KEY([CreatedByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[QueryProfil] CHECK CONSTRAINT [FK_QueryProfil_Bruger]
GO
ALTER TABLE [dbo].[QueueCommand]  WITH CHECK ADD  CONSTRAINT [FK_Que_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[QueueCommand] CHECK CONSTRAINT [FK_Que_Bruger]
GO
ALTER TABLE [dbo].[QueueCommandFile]  WITH CHECK ADD  CONSTRAINT [FK_CommandQueueFile_CommandQueue] FOREIGN KEY([QueueCommandID])
REFERENCES [dbo].[QueueCommand] ([ID])
GO
ALTER TABLE [dbo].[QueueCommandFile] CHECK CONSTRAINT [FK_CommandQueueFile_CommandQueue]
GO
ALTER TABLE [dbo].[RelateretSag]  WITH NOCHECK ADD  CONSTRAINT [RelateretSag_FraSag] FOREIGN KEY([RelateretFraSagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[RelateretSag] CHECK CONSTRAINT [RelateretSag_FraSag]
GO
ALTER TABLE [dbo].[RelateretSag]  WITH NOCHECK ADD  CONSTRAINT [RelateretSag_TilSag] FOREIGN KEY([RelateretSagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[RelateretSag] CHECK CONSTRAINT [RelateretSag_TilSag]
GO
ALTER TABLE [dbo].[RolleTildeling]  WITH CHECK ADD  CONSTRAINT [FK_RolleIUdvalg_Udvalg_Udvalg] FOREIGN KEY([UdvalgID])
REFERENCES [dbo].[Udvalg] ([ID])
GO
ALTER TABLE [dbo].[RolleTildeling] CHECK CONSTRAINT [FK_RolleIUdvalg_Udvalg_Udvalg]
GO
ALTER TABLE [dbo].[RolleTildeling]  WITH CHECK ADD  CONSTRAINT [FK_RolleTildeling_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[RolleTildeling] CHECK CONSTRAINT [FK_RolleTildeling_Bruger]
GO
ALTER TABLE [dbo].[RolleTildeling]  WITH NOCHECK ADD  CONSTRAINT [FK_RolleTildeling_Sikkerhedsgruppe] FOREIGN KEY([SikkerhedsgruppeID])
REFERENCES [dbo].[Sikkerhedsgruppe] ([ID])
GO
ALTER TABLE [dbo].[RolleTildeling] CHECK CONSTRAINT [FK_RolleTildeling_Sikkerhedsgruppe]
GO
ALTER TABLE [dbo].[Sag]  WITH CHECK ADD  CONSTRAINT [FK_Sag_Ansaettelsessted] FOREIGN KEY([AnsaettelsesstedID])
REFERENCES [dbo].[Ansaettelsessted] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [FK_Sag_Ansaettelsessted]
GO
ALTER TABLE [dbo].[Sag]  WITH NOCHECK ADD  CONSTRAINT [FK_Sag_ArkivStatus] FOREIGN KEY([ArkivAfklaringStatusID])
REFERENCES [dbo].[ArkivAfklaringStatus] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [FK_Sag_ArkivStatus]
GO
ALTER TABLE [dbo].[Sag]  WITH CHECK ADD  CONSTRAINT [FK_Sag_SagSkabelon] FOREIGN KEY([SkabelonID])
REFERENCES [dbo].[SagSkabelon] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [FK_Sag_SagSkabelon]
GO
ALTER TABLE [dbo].[Sag]  WITH NOCHECK ADD  CONSTRAINT [FK_Sag_StyringsreolHylde] FOREIGN KEY([StyringsreolHyldeID])
REFERENCES [dbo].[StyringsreolHylde] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [FK_Sag_StyringsreolHylde]
GO
ALTER TABLE [dbo].[Sag]  WITH NOCHECK ADD  CONSTRAINT [Sag_Amt] FOREIGN KEY([AmtID])
REFERENCES [dbo].[AmtOpslag] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [Sag_Amt]
GO
ALTER TABLE [dbo].[Sag]  WITH CHECK ADD  CONSTRAINT [Sag_Behandler] FOREIGN KEY([BehandlerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [Sag_Behandler]
GO
ALTER TABLE [dbo].[Sag]  WITH NOCHECK ADD  CONSTRAINT [Sag_BeslutningsType] FOREIGN KEY([BeslutningsTypeID])
REFERENCES [dbo].[BeslutningsType] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [Sag_BeslutningsType]
GO
ALTER TABLE [dbo].[Sag]  WITH NOCHECK ADD  CONSTRAINT [Sag_Bevaring] FOREIGN KEY([BevaringID])
REFERENCES [dbo].[BevaringOpslag] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [Sag_Bevaring]
GO
ALTER TABLE [dbo].[Sag]  WITH CHECK ADD  CONSTRAINT [Sag_CreatedBy] FOREIGN KEY([CreatedByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [Sag_CreatedBy]
GO
ALTER TABLE [dbo].[Sag]  WITH NOCHECK ADD  CONSTRAINT [Sag_FagOmraade] FOREIGN KEY([FagomraadeID])
REFERENCES [dbo].[FagOmraade] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [Sag_FagOmraade]
GO
ALTER TABLE [dbo].[Sag]  WITH NOCHECK ADD  CONSTRAINT [Sag_Kommune] FOREIGN KEY([KommuneID])
REFERENCES [dbo].[KommuneOpslag] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [Sag_Kommune]
GO
ALTER TABLE [dbo].[Sag]  WITH NOCHECK ADD  CONSTRAINT [Sag_KommuneFoer2007] FOREIGN KEY([KommuneFoer2007ID])
REFERENCES [dbo].[KommuneFoer2007Opslag] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [Sag_KommuneFoer2007]
GO
ALTER TABLE [dbo].[Sag]  WITH CHECK ADD  CONSTRAINT [Sag_LastChangedBy] FOREIGN KEY([LastChangedByID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [Sag_LastChangedBy]
GO
ALTER TABLE [dbo].[Sag]  WITH NOCHECK ADD  CONSTRAINT [Sag_Region] FOREIGN KEY([RegionID])
REFERENCES [dbo].[RegionOpslag] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [Sag_Region]
GO
ALTER TABLE [dbo].[Sag]  WITH NOCHECK ADD  CONSTRAINT [Sag_SagsNummer] FOREIGN KEY([SagsNummerID])
REFERENCES [dbo].[SagsNummer] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [Sag_SagsNummer]
GO
ALTER TABLE [dbo].[Sag]  WITH CHECK ADD  CONSTRAINT [Sag_SagsPart] FOREIGN KEY([SagsPartID])
REFERENCES [dbo].[SagsPart] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [Sag_SagsPart]
GO
ALTER TABLE [dbo].[Sag]  WITH NOCHECK ADD  CONSTRAINT [Sag_SagsStatus] FOREIGN KEY([SagsStatusID])
REFERENCES [dbo].[SagsStatus] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [Sag_SagsStatus]
GO
ALTER TABLE [dbo].[Sag]  WITH NOCHECK ADD  CONSTRAINT [Sag_SecuritySet] FOREIGN KEY([SecuritySetID])
REFERENCES [dbo].[SecuritySet] ([ID])
GO
ALTER TABLE [dbo].[Sag] CHECK CONSTRAINT [Sag_SecuritySet]
GO
ALTER TABLE [dbo].[SagEksternIdentitet]  WITH NOCHECK ADD  CONSTRAINT [FK_SagEksternIdentitet_KnownEksterntSystem] FOREIGN KEY([EksternSystemID])
REFERENCES [dbo].[KnownEksterntSystem] ([ID])
GO
ALTER TABLE [dbo].[SagEksternIdentitet] CHECK CONSTRAINT [FK_SagEksternIdentitet_KnownEksterntSystem]
GO
ALTER TABLE [dbo].[SagEksternIdentitet]  WITH NOCHECK ADD  CONSTRAINT [FK_SagEksternIdentitet_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[SagEksternIdentitet] CHECK CONSTRAINT [FK_SagEksternIdentitet_Sag]
GO
ALTER TABLE [dbo].[SagEmneOrd]  WITH NOCHECK ADD  CONSTRAINT [SagEmneOrd_EmneOrd] FOREIGN KEY([EmneOrdID])
REFERENCES [dbo].[EmneOrd] ([ID])
GO
ALTER TABLE [dbo].[SagEmneOrd] CHECK CONSTRAINT [SagEmneOrd_EmneOrd]
GO
ALTER TABLE [dbo].[SagEmneOrd]  WITH NOCHECK ADD  CONSTRAINT [SagEmneOrd_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[SagEmneOrd] CHECK CONSTRAINT [SagEmneOrd_Sag]
GO
ALTER TABLE [dbo].[SagHistorikStatus]  WITH CHECK ADD  CONSTRAINT [FK_SagHistorikStatus_Bruger] FOREIGN KEY([RegistreretAfID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[SagHistorikStatus] CHECK CONSTRAINT [FK_SagHistorikStatus_Bruger]
GO
ALTER TABLE [dbo].[SagHistorikStatus]  WITH NOCHECK ADD  CONSTRAINT [FK_SagHistorikStatus_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[SagHistorikStatus] CHECK CONSTRAINT [FK_SagHistorikStatus_Sag]
GO
ALTER TABLE [dbo].[SagHistorikStatus]  WITH NOCHECK ADD  CONSTRAINT [FK_SagHistorikStatus_SagsStatus] FOREIGN KEY([FraSagsStatusID])
REFERENCES [dbo].[SagsStatus] ([ID])
GO
ALTER TABLE [dbo].[SagHistorikStatus] CHECK CONSTRAINT [FK_SagHistorikStatus_SagsStatus]
GO
ALTER TABLE [dbo].[SagHistorikStatus]  WITH NOCHECK ADD  CONSTRAINT [FK_SagHistorikStatus_SagsStatus1] FOREIGN KEY([TilSagsStatusID])
REFERENCES [dbo].[SagsStatus] ([ID])
GO
ALTER TABLE [dbo].[SagHistorikStatus] CHECK CONSTRAINT [FK_SagHistorikStatus_SagsStatus1]
GO
ALTER TABLE [dbo].[SagHistorikStyringsreolStatus]  WITH CHECK ADD  CONSTRAINT [FK_SagHistorikStyringsreolStatus_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[SagHistorikStyringsreolStatus] CHECK CONSTRAINT [FK_SagHistorikStyringsreolStatus_Bruger]
GO
ALTER TABLE [dbo].[SagHistorikStyringsreolStatus]  WITH NOCHECK ADD  CONSTRAINT [FK_SagHistorikStyringsreolStatus_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[SagHistorikStyringsreolStatus] CHECK CONSTRAINT [FK_SagHistorikStyringsreolStatus_Sag]
GO
ALTER TABLE [dbo].[SagHistorikStyringsreolStatus]  WITH NOCHECK ADD  CONSTRAINT [FK_SagHistorikStyringsreolStatus_StyringsreolHylde_Fra] FOREIGN KEY([FraHyldeID])
REFERENCES [dbo].[StyringsreolHylde] ([ID])
GO
ALTER TABLE [dbo].[SagHistorikStyringsreolStatus] CHECK CONSTRAINT [FK_SagHistorikStyringsreolStatus_StyringsreolHylde_Fra]
GO
ALTER TABLE [dbo].[SagHistorikStyringsreolStatus]  WITH NOCHECK ADD  CONSTRAINT [FK_SagHistorikStyringsreolStatus_StyringsreolHylde_Til] FOREIGN KEY([TilHyldeID])
REFERENCES [dbo].[StyringsreolHylde] ([ID])
GO
ALTER TABLE [dbo].[SagHistorikStyringsreolStatus] CHECK CONSTRAINT [FK_SagHistorikStyringsreolStatus_StyringsreolHylde_Til]
GO
ALTER TABLE [dbo].[SagMetaData]  WITH NOCHECK ADD  CONSTRAINT [FK_SagMetaData_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[SagMetaData] CHECK CONSTRAINT [FK_SagMetaData_Sag]
GO
ALTER TABLE [dbo].[SagSagsType]  WITH NOCHECK ADD  CONSTRAINT [FK_SagSagsType_Sag] FOREIGN KEY([SagId])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[SagSagsType] CHECK CONSTRAINT [FK_SagSagsType_Sag]
GO
ALTER TABLE [dbo].[SagSagsType]  WITH NOCHECK ADD  CONSTRAINT [FK_SagSagsType_SagsType] FOREIGN KEY([SagsTypeId])
REFERENCES [dbo].[SagsType] ([Id])
GO
ALTER TABLE [dbo].[SagSagsType] CHECK CONSTRAINT [FK_SagSagsType_SagsType]
GO
ALTER TABLE [dbo].[SagsfeltIndhold]  WITH CHECK ADD  CONSTRAINT [FK_SagsfeltVaerdi_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[SagsfeltIndhold] CHECK CONSTRAINT [FK_SagsfeltVaerdi_Sag]
GO
ALTER TABLE [dbo].[SagsfeltIndhold]  WITH CHECK ADD  CONSTRAINT [FK_SagsfeltVaerdi_Sagsfelt] FOREIGN KEY([SagsfeltID])
REFERENCES [dbo].[SagsFelt] ([Id])
GO
ALTER TABLE [dbo].[SagsfeltIndhold] CHECK CONSTRAINT [FK_SagsfeltVaerdi_Sagsfelt]
GO
ALTER TABLE [dbo].[SagsFeltSagSkabelon]  WITH NOCHECK ADD  CONSTRAINT [FK_SagsFeltSagSkabelon_SagsFelt] FOREIGN KEY([SagsFeltId])
REFERENCES [dbo].[SagsFelt] ([Id])
GO
ALTER TABLE [dbo].[SagsFeltSagSkabelon] CHECK CONSTRAINT [FK_SagsFeltSagSkabelon_SagsFelt]
GO
ALTER TABLE [dbo].[SagsFeltSagSkabelon]  WITH CHECK ADD  CONSTRAINT [FK_SagsFeltSagSkabelon_SagSkabelon] FOREIGN KEY([SagSkabelonId])
REFERENCES [dbo].[SagSkabelon] ([ID])
GO
ALTER TABLE [dbo].[SagsFeltSagSkabelon] CHECK CONSTRAINT [FK_SagsFeltSagSkabelon_SagSkabelon]
GO
ALTER TABLE [dbo].[SagsHenvisning]  WITH NOCHECK ADD  CONSTRAINT [SagHenvisning_SagFra] FOREIGN KEY([HenvisningFraID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[SagsHenvisning] CHECK CONSTRAINT [SagHenvisning_SagFra]
GO
ALTER TABLE [dbo].[SagsHenvisning]  WITH NOCHECK ADD  CONSTRAINT [SagHenvisning_SagTil] FOREIGN KEY([HenvisningTilID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[SagsHenvisning] CHECK CONSTRAINT [SagHenvisning_SagTil]
GO
ALTER TABLE [dbo].[SagSkabelon]  WITH CHECK ADD  CONSTRAINT [FK_SagSkabelon_Hierakimedlem] FOREIGN KEY([Hierakimedlem])
REFERENCES [dbo].[HierakiMedlem] ([ID])
GO
ALTER TABLE [dbo].[SagSkabelon] CHECK CONSTRAINT [FK_SagSkabelon_Hierakimedlem]
GO
ALTER TABLE [dbo].[SagSkabelon]  WITH CHECK ADD  CONSTRAINT [FK_SagSkabelon_SagSkabelonKategori] FOREIGN KEY([SagSkabelonKategoriID])
REFERENCES [dbo].[SagSkabelonKategori] ([ID])
GO
ALTER TABLE [dbo].[SagSkabelon] CHECK CONSTRAINT [FK_SagSkabelon_SagSkabelonKategori]
GO
ALTER TABLE [dbo].[SagSkabelon]  WITH CHECK ADD  CONSTRAINT [FK_SagSkabelon_SagsType] FOREIGN KEY([SagsTypeId])
REFERENCES [dbo].[SagsType] ([Id])
GO
ALTER TABLE [dbo].[SagSkabelon] CHECK CONSTRAINT [FK_SagSkabelon_SagsType]
GO
ALTER TABLE [dbo].[SagSkabelonEmneord]  WITH CHECK ADD  CONSTRAINT [FK_SagSkabelonEmneord_Emneord] FOREIGN KEY([EmneordID])
REFERENCES [dbo].[EmneOrd] ([ID])
GO
ALTER TABLE [dbo].[SagSkabelonEmneord] CHECK CONSTRAINT [FK_SagSkabelonEmneord_Emneord]
GO
ALTER TABLE [dbo].[SagSkabelonEmneord]  WITH CHECK ADD  CONSTRAINT [FK_SagSkabelonEmneord_SagSkabelon] FOREIGN KEY([SagSkabelonID])
REFERENCES [dbo].[SagSkabelon] ([ID])
GO
ALTER TABLE [dbo].[SagSkabelonEmneord] CHECK CONSTRAINT [FK_SagSkabelonEmneord_SagSkabelon]
GO
ALTER TABLE [dbo].[SagSkabelonErindringSkabelon]  WITH NOCHECK ADD  CONSTRAINT [FK_SagSkabelonErindringSkabelon_ErindringSkabelon] FOREIGN KEY([ErindringSkabelonID])
REFERENCES [dbo].[ErindringSkabelon] ([ID])
GO
ALTER TABLE [dbo].[SagSkabelonErindringSkabelon] CHECK CONSTRAINT [FK_SagSkabelonErindringSkabelon_ErindringSkabelon]
GO
ALTER TABLE [dbo].[SagSkabelonErindringSkabelon]  WITH CHECK ADD  CONSTRAINT [FK_SagSkabelonErindringSkabelon_SagSkabelon] FOREIGN KEY([SagSkabelonID])
REFERENCES [dbo].[SagSkabelon] ([ID])
GO
ALTER TABLE [dbo].[SagSkabelonErindringSkabelon] CHECK CONSTRAINT [FK_SagSkabelonErindringSkabelon_SagSkabelon]
GO
ALTER TABLE [dbo].[SagSkabelonPart]  WITH CHECK ADD  CONSTRAINT [FK_SagSkabelonPart_Firma] FOREIGN KEY([FirmaID])
REFERENCES [dbo].[Firma] ([ID])
GO
ALTER TABLE [dbo].[SagSkabelonPart] CHECK CONSTRAINT [FK_SagSkabelonPart_Firma]
GO
ALTER TABLE [dbo].[SagSkabelonPart]  WITH CHECK ADD  CONSTRAINT [FK_SagSkabelonPart_Part] FOREIGN KEY([PersonID])
REFERENCES [dbo].[Person] ([ID])
GO
ALTER TABLE [dbo].[SagSkabelonPart] CHECK CONSTRAINT [FK_SagSkabelonPart_Part]
GO
ALTER TABLE [dbo].[SagSkabelonPart]  WITH CHECK ADD  CONSTRAINT [FK_SagSkabelonPart_PartTypeOpslag] FOREIGN KEY([PartTypeID])
REFERENCES [dbo].[PartTypeOpslag] ([ID])
GO
ALTER TABLE [dbo].[SagSkabelonPart] CHECK CONSTRAINT [FK_SagSkabelonPart_PartTypeOpslag]
GO
ALTER TABLE [dbo].[SagSkabelonTilknyttetSagSkabelon]  WITH CHECK ADD  CONSTRAINT [FK_SagSkabelonTilknyttetSagSkabelon_SagSkabelon] FOREIGN KEY([SagSkabelonID])
REFERENCES [dbo].[SagSkabelon] ([ID])
GO
ALTER TABLE [dbo].[SagSkabelonTilknyttetSagSkabelon] CHECK CONSTRAINT [FK_SagSkabelonTilknyttetSagSkabelon_SagSkabelon]
GO
ALTER TABLE [dbo].[SagSkabelonTilknyttetSagSkabelon]  WITH CHECK ADD  CONSTRAINT [FK_SagSkabelonTilknyttetSagSkabelon_TilknyttetSagSkabelon] FOREIGN KEY([SagSkabelonTilknyttetSagSkabelonID])
REFERENCES [dbo].[SagSkabelon] ([ID])
GO
ALTER TABLE [dbo].[SagSkabelonTilknyttetSagSkabelon] CHECK CONSTRAINT [FK_SagSkabelonTilknyttetSagSkabelon_TilknyttetSagSkabelon]
GO
ALTER TABLE [dbo].[SagSkabelonTitler]  WITH CHECK ADD  CONSTRAINT [FK_SagSkabelonTitler_SagSkabelon] FOREIGN KEY([SagSkabelonID])
REFERENCES [dbo].[SagSkabelon] ([ID])
GO
ALTER TABLE [dbo].[SagSkabelonTitler] CHECK CONSTRAINT [FK_SagSkabelonTitler_SagSkabelon]
GO
ALTER TABLE [dbo].[SagsNummer]  WITH NOCHECK ADD  CONSTRAINT [SagsNummer_EmnePlan] FOREIGN KEY([EmnePlanID])
REFERENCES [dbo].[EmnePlan] ([ID])
GO
ALTER TABLE [dbo].[SagsNummer] CHECK CONSTRAINT [SagsNummer_EmnePlan]
GO
ALTER TABLE [dbo].[SagsNummer]  WITH NOCHECK ADD  CONSTRAINT [SagsNummer_EmnePlanNummer] FOREIGN KEY([EmnePlanNummerID])
REFERENCES [dbo].[EmnePlanNummer] ([ID])
GO
ALTER TABLE [dbo].[SagsNummer] CHECK CONSTRAINT [SagsNummer_EmnePlanNummer]
GO
ALTER TABLE [dbo].[SagsNummer]  WITH NOCHECK ADD  CONSTRAINT [SagsNummer_Facet] FOREIGN KEY([FacetID])
REFERENCES [dbo].[Facet] ([ID])
GO
ALTER TABLE [dbo].[SagsNummer] CHECK CONSTRAINT [SagsNummer_Facet]
GO
ALTER TABLE [dbo].[SagsPart]  WITH CHECK ADD  CONSTRAINT [FK_SagsPart_PartTypeOpslag] FOREIGN KEY([PartType])
REFERENCES [dbo].[PartTypeOpslag] ([ID])
GO
ALTER TABLE [dbo].[SagsPart] CHECK CONSTRAINT [FK_SagsPart_PartTypeOpslag]
GO
ALTER TABLE [dbo].[SagsPart]  WITH CHECK ADD  CONSTRAINT [SagsPart_OprindeligAdresse] FOREIGN KEY([OprindeligAdresseID])
REFERENCES [dbo].[Adresse] ([ID])
GO
ALTER TABLE [dbo].[SagsPart] CHECK CONSTRAINT [SagsPart_OprindeligAdresse]
GO
ALTER TABLE [dbo].[SagsPart]  WITH CHECK ADD  CONSTRAINT [SagsPart_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[SagsPart] CHECK CONSTRAINT [SagsPart_Sag]
GO
ALTER TABLE [dbo].[SagsPart]  WITH CHECK ADD  CONSTRAINT [SagsPart_SagsPartRolle] FOREIGN KEY([SagsPartRolleID])
REFERENCES [dbo].[SagsPartRolle] ([ID])
GO
ALTER TABLE [dbo].[SagsPart] CHECK CONSTRAINT [SagsPart_SagsPartRolle]
GO
ALTER TABLE [dbo].[SagsStatus]  WITH NOCHECK ADD  CONSTRAINT [SagsStatus_SagsTilstand] FOREIGN KEY([SagsTilstand])
REFERENCES [dbo].[SagsTilstandOpslag] ([ID])
GO
ALTER TABLE [dbo].[SagsStatus] CHECK CONSTRAINT [SagsStatus_SagsTilstand]
GO
ALTER TABLE [dbo].[SagsVisit]  WITH CHECK ADD  CONSTRAINT [SagVisit_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[SagsVisit] CHECK CONSTRAINT [SagVisit_Bruger]
GO
ALTER TABLE [dbo].[SagsVisit]  WITH NOCHECK ADD  CONSTRAINT [SagVisit_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[SagsVisit] CHECK CONSTRAINT [SagVisit_Sag]
GO
ALTER TABLE [dbo].[SecuritySetBrugere]  WITH CHECK ADD  CONSTRAINT [SecuritySetBrugere_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[SecuritySetBrugere] CHECK CONSTRAINT [SecuritySetBrugere_Bruger]
GO
ALTER TABLE [dbo].[SecuritySetBrugere]  WITH NOCHECK ADD  CONSTRAINT [SecuritySetBrugere_SecuritySet] FOREIGN KEY([SecuritySetID])
REFERENCES [dbo].[SecuritySet] ([ID])
GO
ALTER TABLE [dbo].[SecuritySetBrugere] CHECK CONSTRAINT [SecuritySetBrugere_SecuritySet]
GO
ALTER TABLE [dbo].[SecuritySetSikkerhedsgrupper]  WITH NOCHECK ADD  CONSTRAINT [SecuritySetOrganisationsEnheder_OrganisationsEnhed] FOREIGN KEY([SikkerhedsgruppeID])
REFERENCES [dbo].[Sikkerhedsgruppe] ([ID])
GO
ALTER TABLE [dbo].[SecuritySetSikkerhedsgrupper] CHECK CONSTRAINT [SecuritySetOrganisationsEnheder_OrganisationsEnhed]
GO
ALTER TABLE [dbo].[SecuritySetSikkerhedsgrupper]  WITH NOCHECK ADD  CONSTRAINT [SecuritySetOrganisationsEnheder_SecuritySet] FOREIGN KEY([SecuritySetID])
REFERENCES [dbo].[SecuritySet] ([ID])
GO
ALTER TABLE [dbo].[SecuritySetSikkerhedsgrupper] CHECK CONSTRAINT [SecuritySetOrganisationsEnheder_SecuritySet]
GO
ALTER TABLE [dbo].[Sikkerhedsgruppe]  WITH NOCHECK ADD  CONSTRAINT [FK_Sikkerhedsgruppe_HierakiMedlem] FOREIGN KEY([HierakiMedlemID])
REFERENCES [dbo].[HierakiMedlem] ([ID])
GO
ALTER TABLE [dbo].[Sikkerhedsgruppe] CHECK CONSTRAINT [FK_Sikkerhedsgruppe_HierakiMedlem]
GO
ALTER TABLE [dbo].[SikkerhedsgruppeBrugere]  WITH CHECK ADD  CONSTRAINT [BrugerOrganisationsEnheder_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[SikkerhedsgruppeBrugere] CHECK CONSTRAINT [BrugerOrganisationsEnheder_Bruger]
GO
ALTER TABLE [dbo].[SikkerhedsgruppeBrugere]  WITH NOCHECK ADD  CONSTRAINT [BrugerOrganisationsenheder_OrganisationsEnhed] FOREIGN KEY([SikkerhedsgruppeID])
REFERENCES [dbo].[Sikkerhedsgruppe] ([ID])
GO
ALTER TABLE [dbo].[SikkerhedsgruppeBrugere] CHECK CONSTRAINT [BrugerOrganisationsenheder_OrganisationsEnhed]
GO
ALTER TABLE [dbo].[Skabelon]  WITH CHECK ADD  CONSTRAINT [FK_Skabelon_Bruger] FOREIGN KEY([RedigeretAfID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Skabelon] CHECK CONSTRAINT [FK_Skabelon_Bruger]
GO
ALTER TABLE [dbo].[Skabelon]  WITH NOCHECK ADD  CONSTRAINT [Skabelon_SkabelonGrundSkabelon] FOREIGN KEY([GrundSkabelonID])
REFERENCES [dbo].[SkabelonGrundSkabelon] ([ID])
GO
ALTER TABLE [dbo].[Skabelon] CHECK CONSTRAINT [Skabelon_SkabelonGrundSkabelon]
GO
ALTER TABLE [dbo].[SkabelonKladde]  WITH NOCHECK ADD  CONSTRAINT [FK_SkabelonKladde_SkabelonGrundSkabelon] FOREIGN KEY([SkabelonGrundskabelonID])
REFERENCES [dbo].[SkabelonGrundSkabelon] ([ID])
GO
ALTER TABLE [dbo].[SkabelonKladde] CHECK CONSTRAINT [FK_SkabelonKladde_SkabelonGrundSkabelon]
GO
ALTER TABLE [dbo].[SkabelonKladde]  WITH NOCHECK ADD  CONSTRAINT [SkabelonKladde_Kladde] FOREIGN KEY([KladdeID])
REFERENCES [dbo].[Kladde] ([ID])
GO
ALTER TABLE [dbo].[SkabelonKladde] CHECK CONSTRAINT [SkabelonKladde_Kladde]
GO
ALTER TABLE [dbo].[SkabelonKladde]  WITH NOCHECK ADD  CONSTRAINT [SkabelonKladde_Skabelon] FOREIGN KEY([SkabelonID])
REFERENCES [dbo].[Skabelon] ([ID])
GO
ALTER TABLE [dbo].[SkabelonKladde] CHECK CONSTRAINT [SkabelonKladde_Skabelon]
GO
ALTER TABLE [dbo].[SkabelonTekstblok]  WITH CHECK ADD  CONSTRAINT [SkabelonTekstblok_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[SkabelonTekstblok] CHECK CONSTRAINT [SkabelonTekstblok_Bruger]
GO
ALTER TABLE [dbo].[SkabelonTrin]  WITH NOCHECK ADD  CONSTRAINT [SkabelonTrin_Skabelon] FOREIGN KEY([SkabelonID])
REFERENCES [dbo].[Skabelon] ([ID])
GO
ALTER TABLE [dbo].[SkabelonTrin] CHECK CONSTRAINT [SkabelonTrin_Skabelon]
GO
ALTER TABLE [dbo].[SkabelonTrin]  WITH NOCHECK ADD  CONSTRAINT [SkabelonTrin_SkabelonTekstblok] FOREIGN KEY([SkabelonTekstBlokID])
REFERENCES [dbo].[SkabelonTekstblok] ([ID])
GO
ALTER TABLE [dbo].[SkabelonTrin] CHECK CONSTRAINT [SkabelonTrin_SkabelonTekstblok]
GO
ALTER TABLE [dbo].[SkabelonType]  WITH NOCHECK ADD  CONSTRAINT [FK_SkabelonType_SkabelonGrundSkabelon] FOREIGN KEY([GrundSkabelonID])
REFERENCES [dbo].[SkabelonGrundSkabelon] ([ID])
GO
ALTER TABLE [dbo].[SkabelonType] CHECK CONSTRAINT [FK_SkabelonType_SkabelonGrundSkabelon]
GO
ALTER TABLE [dbo].[SkabelonType]  WITH NOCHECK ADD  CONSTRAINT [Skabelontype_SkabelonTypeGruppe] FOREIGN KEY([SkabelonTypeGruppeID])
REFERENCES [dbo].[SkabelonTypeGruppe] ([ID])
GO
ALTER TABLE [dbo].[SkabelonType] CHECK CONSTRAINT [Skabelontype_SkabelonTypeGruppe]
GO
ALTER TABLE [dbo].[SkabelonTypeSkabelon]  WITH NOCHECK ADD  CONSTRAINT [SkabelonType_Skabelon] FOREIGN KEY([SkabelonID])
REFERENCES [dbo].[Skabelon] ([ID])
GO
ALTER TABLE [dbo].[SkabelonTypeSkabelon] CHECK CONSTRAINT [SkabelonType_Skabelon]
GO
ALTER TABLE [dbo].[SkabelonTypeSkabelon]  WITH NOCHECK ADD  CONSTRAINT [SkabelonType_SkabelonType] FOREIGN KEY([SkabelonTypeID])
REFERENCES [dbo].[SkabelonType] ([ID])
GO
ALTER TABLE [dbo].[SkabelonTypeSkabelon] CHECK CONSTRAINT [SkabelonType_SkabelonType]
GO
ALTER TABLE [dbo].[Stedfaestelse]  WITH CHECK ADD  CONSTRAINT [FK_Stedfaestelse_Bruger] FOREIGN KEY([StedfaestetAfID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Stedfaestelse] CHECK CONSTRAINT [FK_Stedfaestelse_Bruger]
GO
ALTER TABLE [dbo].[Stedfaestelse]  WITH NOCHECK ADD  CONSTRAINT [FK_Stedfaestelse_DokumentRegistrering] FOREIGN KEY([DokumentRegistreringID])
REFERENCES [dbo].[DokumentRegistrering] ([ID])
GO
ALTER TABLE [dbo].[Stedfaestelse] CHECK CONSTRAINT [FK_Stedfaestelse_DokumentRegistrering]
GO
ALTER TABLE [dbo].[Stedfaestelse]  WITH NOCHECK ADD  CONSTRAINT [FK_Stedfaestelse_Geometri] FOREIGN KEY([GeometriID])
REFERENCES [dbo].[Geometri] ([ID])
GO
ALTER TABLE [dbo].[Stedfaestelse] CHECK CONSTRAINT [FK_Stedfaestelse_Geometri]
GO
ALTER TABLE [dbo].[Stedfaestelse]  WITH NOCHECK ADD  CONSTRAINT [FK_Stedfaestelse_Sag] FOREIGN KEY([SagID])
REFERENCES [dbo].[Sag] ([ID])
GO
ALTER TABLE [dbo].[Stedfaestelse] CHECK CONSTRAINT [FK_Stedfaestelse_Sag]
GO
ALTER TABLE [dbo].[Stylesheet]  WITH NOCHECK ADD  CONSTRAINT [FK_Stylesheets_StylesheetTypeOpslag] FOREIGN KEY([StylesheetTypeID])
REFERENCES [dbo].[StylesheetTypeOpslag] ([ID])
GO
ALTER TABLE [dbo].[Stylesheet] CHECK CONSTRAINT [FK_Stylesheets_StylesheetTypeOpslag]
GO
ALTER TABLE [dbo].[Styringsreol]  WITH CHECK ADD  CONSTRAINT [FK_Styringsreol_Ansaettelsessted] FOREIGN KEY([AnsaettelsesstedID])
REFERENCES [dbo].[Ansaettelsessted] ([ID])
GO
ALTER TABLE [dbo].[Styringsreol] CHECK CONSTRAINT [FK_Styringsreol_Ansaettelsessted]
GO
ALTER TABLE [dbo].[StyringsreolHistorik]  WITH CHECK ADD  CONSTRAINT [FK_StyringsreolHistorik_Ansaettelsessted] FOREIGN KEY([AnsaettelsesstedID])
REFERENCES [dbo].[Ansaettelsessted] ([ID])
GO
ALTER TABLE [dbo].[StyringsreolHistorik] CHECK CONSTRAINT [FK_StyringsreolHistorik_Ansaettelsessted]
GO
ALTER TABLE [dbo].[StyringsreolHistorik]  WITH CHECK ADD  CONSTRAINT [FK_StyringsreolHistorik_Bruger] FOREIGN KEY([BrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[StyringsreolHistorik] CHECK CONSTRAINT [FK_StyringsreolHistorik_Bruger]
GO
ALTER TABLE [dbo].[StyringsreolHistorik]  WITH NOCHECK ADD  CONSTRAINT [FK_StyringsreolHistorik_SagsStatus] FOREIGN KEY([HyldeSagsstatusID])
REFERENCES [dbo].[SagsStatus] ([ID])
GO
ALTER TABLE [dbo].[StyringsreolHistorik] CHECK CONSTRAINT [FK_StyringsreolHistorik_SagsStatus]
GO
ALTER TABLE [dbo].[StyringsreolHistorik]  WITH NOCHECK ADD  CONSTRAINT [FK_StyringsreolHistorik_Styringsreol] FOREIGN KEY([ReolID])
REFERENCES [dbo].[Styringsreol] ([ID])
GO
ALTER TABLE [dbo].[StyringsreolHistorik] CHECK CONSTRAINT [FK_StyringsreolHistorik_Styringsreol]
GO
ALTER TABLE [dbo].[StyringsreolHistorik]  WITH NOCHECK ADD  CONSTRAINT [FK_StyringsreolHistorik_StyringsreolHylde] FOREIGN KEY([HyldeID])
REFERENCES [dbo].[StyringsreolHylde] ([ID])
GO
ALTER TABLE [dbo].[StyringsreolHistorik] CHECK CONSTRAINT [FK_StyringsreolHistorik_StyringsreolHylde]
GO
ALTER TABLE [dbo].[StyringsreolHistorik]  WITH NOCHECK ADD  CONSTRAINT [FK_StyringsreolHistorik_StyringsreolHyldeFag] FOREIGN KEY([FagID])
REFERENCES [dbo].[StyringsreolHyldeFag] ([ID])
GO
ALTER TABLE [dbo].[StyringsreolHistorik] CHECK CONSTRAINT [FK_StyringsreolHistorik_StyringsreolHyldeFag]
GO
ALTER TABLE [dbo].[StyringsreolHylde]  WITH NOCHECK ADD  CONSTRAINT [FK_StyringsreolHylde_Styringsreol] FOREIGN KEY([StyringsreolID])
REFERENCES [dbo].[Styringsreol] ([ID])
GO
ALTER TABLE [dbo].[StyringsreolHylde] CHECK CONSTRAINT [FK_StyringsreolHylde_Styringsreol]
GO
ALTER TABLE [dbo].[StyringsreolHylde]  WITH NOCHECK ADD  CONSTRAINT [FK_StyringsreolStatus_SagsStatus] FOREIGN KEY([SagsstatusID])
REFERENCES [dbo].[SagsStatus] ([ID])
GO
ALTER TABLE [dbo].[StyringsreolHylde] CHECK CONSTRAINT [FK_StyringsreolStatus_SagsStatus]
GO
ALTER TABLE [dbo].[StyringsreolHyldeErindringSkabelon]  WITH NOCHECK ADD  CONSTRAINT [fk_StyringsreolHyldeErindringSkabelon_ErindringSkabelon] FOREIGN KEY([ErindringSkabelonID])
REFERENCES [dbo].[ErindringSkabelon] ([ID])
GO
ALTER TABLE [dbo].[StyringsreolHyldeErindringSkabelon] CHECK CONSTRAINT [fk_StyringsreolHyldeErindringSkabelon_ErindringSkabelon]
GO
ALTER TABLE [dbo].[StyringsreolHyldeErindringSkabelon]  WITH NOCHECK ADD  CONSTRAINT [fk_StyringsreolHyldeErindringSkabelon_StyringsreolHylde] FOREIGN KEY([StyringsreolHyldeID])
REFERENCES [dbo].[StyringsreolHylde] ([ID])
GO
ALTER TABLE [dbo].[StyringsreolHyldeErindringSkabelon] CHECK CONSTRAINT [fk_StyringsreolHyldeErindringSkabelon_StyringsreolHylde]
GO
ALTER TABLE [dbo].[StyringsreolHyldeFag]  WITH NOCHECK ADD  CONSTRAINT [FK_StyringsreolHyldeFag_StyringsreolHylde] FOREIGN KEY([StyringsreolHyldeID])
REFERENCES [dbo].[StyringsreolHylde] ([ID])
GO
ALTER TABLE [dbo].[StyringsreolHyldeFag] CHECK CONSTRAINT [FK_StyringsreolHyldeFag_StyringsreolHylde]
GO
ALTER TABLE [dbo].[SystemConfiguration]  WITH CHECK ADD  CONSTRAINT [FK_SystemConfiguration_Bruger] FOREIGN KEY([IntegreretBrugerID])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[SystemConfiguration] CHECK CONSTRAINT [FK_SystemConfiguration_Bruger]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH CHECK ADD  CONSTRAINT [FK_SystemDefaults_Ansaettelsessted] FOREIGN KEY([AnsaettelsesstedID])
REFERENCES [dbo].[Ansaettelsessted] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_Ansaettelsessted]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_ArkivStatus] FOREIGN KEY([ArkivAfklaringStatusID])
REFERENCES [dbo].[ArkivAfklaringStatus] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_ArkivStatus]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_CivilstandNyPerson] FOREIGN KEY([CivilstandNyPersonID])
REFERENCES [dbo].[CivilstandOpslag] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_CivilstandNyPerson]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_DagsordenCssStylesheet] FOREIGN KEY([DagsordenCssStylesheetID])
REFERENCES [dbo].[Stylesheet] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_DagsordenCssStylesheet]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_DagsordenGenereringRessource] FOREIGN KEY([DagsordenGenereringRessourceID])
REFERENCES [dbo].[Ressource] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_DagsordenGenereringRessource]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_DagsordenTilbagejournaliseringRessource] FOREIGN KEY([DagsordenTilbagejournaliseringRessourceID])
REFERENCES [dbo].[Ressource] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_DagsordenTilbagejournaliseringRessource]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_DagsordenXslStylesheet] FOREIGN KEY([DagsordenXslStylesheetID])
REFERENCES [dbo].[Stylesheet] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_DagsordenXslStylesheet]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH CHECK ADD  CONSTRAINT [FK_SystemDefaults_DelforloebType] FOREIGN KEY([DelforloebTypeID])
REFERENCES [dbo].[DelforloebType] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_DelforloebType]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_DokumentArt_Default] FOREIGN KEY([DokumentArtDefaultID])
REFERENCES [dbo].[DokumentArtOpslag] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_DokumentArt_Default]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_DokumentArt_JournaliserFil] FOREIGN KEY([DokumentArtJournaliserFilID])
REFERENCES [dbo].[DokumentArtOpslag] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_DokumentArt_JournaliserFil]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_DokumentArt_JournaliserInternt] FOREIGN KEY([DokumentArtJournaliserInterntID])
REFERENCES [dbo].[DokumentArtOpslag] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_DokumentArt_JournaliserInternt]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_DokumentArt_JournaliserModtagetMail] FOREIGN KEY([DokumentArtJournaliserModtagetMailID])
REFERENCES [dbo].[DokumentArtOpslag] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_DokumentArt_JournaliserModtagetMail]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_DokumentArt_JournaliserNotat] FOREIGN KEY([DokumentArtJournaliserNotatID])
REFERENCES [dbo].[DokumentArtOpslag] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_DokumentArt_JournaliserNotat]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_DokumentArt_JournaliserSendtMail] FOREIGN KEY([DokumentArtJournaliserSendtMailID])
REFERENCES [dbo].[DokumentArtOpslag] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_DokumentArt_JournaliserSendtMail]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_DokumentArt_JournaliserTelefon] FOREIGN KEY([DokumentArtJournaliserTelefonID])
REFERENCES [dbo].[DokumentArtOpslag] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_DokumentArt_JournaliserTelefon]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_DokumentArt_Papir] FOREIGN KEY([DokumentArtJournaliserPapirID])
REFERENCES [dbo].[DokumentArtOpslag] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_DokumentArt_Papir]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_DokumentArt_Scanning] FOREIGN KEY([DokumentArtJournaliserScanningID])
REFERENCES [dbo].[DokumentArtOpslag] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_DokumentArt_Scanning]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_DokumentArtOpslag] FOREIGN KEY([DokumentArtAvanceretFletID])
REFERENCES [dbo].[DokumentArtOpslag] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_DokumentArtOpslag]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_EmnePlan] FOREIGN KEY([EmneplanID])
REFERENCES [dbo].[EmnePlan] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_EmnePlan]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_ErindringType_Bemaerk] FOREIGN KEY([ErindringTypeBemaerkID])
REFERENCES [dbo].[ErindringTypeOpslag] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_ErindringType_Bemaerk]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_ErindringType_Laes] FOREIGN KEY([ErindringTypeLaesID])
REFERENCES [dbo].[ErindringTypeOpslag] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_ErindringType_Laes]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_ErindringType_Opfoelg] FOREIGN KEY([ErindringTypeOpfoelgID])
REFERENCES [dbo].[ErindringTypeOpslag] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_ErindringType_Opfoelg]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_ErindringType_RingTil] FOREIGN KEY([ErindringTypeRingTilID])
REFERENCES [dbo].[ErindringTypeOpslag] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_ErindringType_RingTil]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_Fagomraade] FOREIGN KEY([FagomraadeID])
REFERENCES [dbo].[FagOmraade] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_Fagomraade]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_KnownEksterntSystem] FOREIGN KEY([KnownEksterntSystemID])
REFERENCES [dbo].[KnownEksterntSystem] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_KnownEksterntSystem]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_SagsStatus] FOREIGN KEY([SagsStatusID])
REFERENCES [dbo].[SagsStatus] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_SagsStatus]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_Sekretariat] FOREIGN KEY([SekretariatID])
REFERENCES [dbo].[Sekretariat] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_Sekretariat]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_SkabelonGrundSkabelon] FOREIGN KEY([GrundskabelonID])
REFERENCES [dbo].[SkabelonGrundSkabelon] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_SkabelonGrundSkabelon]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_Stylesheet] FOREIGN KEY([PubliceringXslStylesheetID])
REFERENCES [dbo].[Stylesheet] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_Stylesheet]
GO
ALTER TABLE [dbo].[SystemDefaults]  WITH NOCHECK ADD  CONSTRAINT [FK_SystemDefaults_Stylesheet1] FOREIGN KEY([PubliceringCssStylesheetID])
REFERENCES [dbo].[Stylesheet] ([ID])
GO
ALTER TABLE [dbo].[SystemDefaults] CHECK CONSTRAINT [FK_SystemDefaults_Stylesheet1]
GO
ALTER TABLE [dbo].[TidsPostering]  WITH NOCHECK ADD  CONSTRAINT [FK_TidsPostering_TidsPosteringKategori] FOREIGN KEY([TidsPosteringKategoriID])
REFERENCES [dbo].[TidsPosteringKategori] ([Id])
GO
ALTER TABLE [dbo].[TidsPostering] CHECK CONSTRAINT [FK_TidsPostering_TidsPosteringKategori]
GO
ALTER TABLE [dbo].[TrustedAssembly]  WITH NOCHECK ADD  CONSTRAINT [TrustedAssembly_SystemConfiguration] FOREIGN KEY([SystemConfigurationID])
REFERENCES [dbo].[SystemConfiguration] ([ID])
GO
ALTER TABLE [dbo].[TrustedAssembly] CHECK CONSTRAINT [TrustedAssembly_SystemConfiguration]
GO
ALTER TABLE [dbo].[Udvalg]  WITH CHECK ADD  CONSTRAINT [FK_Udvalg_Bruger_CreatedBy] FOREIGN KEY([CreatedBy])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Udvalg] CHECK CONSTRAINT [FK_Udvalg_Bruger_CreatedBy]
GO
ALTER TABLE [dbo].[Udvalg]  WITH CHECK ADD  CONSTRAINT [FK_Udvalg_Bruger_LastChangedBy] FOREIGN KEY([LastChangedBy])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[Udvalg] CHECK CONSTRAINT [FK_Udvalg_Bruger_LastChangedBy]
GO
ALTER TABLE [dbo].[Udvalg]  WITH CHECK ADD  CONSTRAINT [FK_Udvalg_DagsordenpunktFelt_beslutning] FOREIGN KEY([BeslutningSkalKopieresTilFeltID])
REFERENCES [dbo].[DagsordenpunktFelt] ([ID])
GO
ALTER TABLE [dbo].[Udvalg] CHECK CONSTRAINT [FK_Udvalg_DagsordenpunktFelt_beslutning]
GO
ALTER TABLE [dbo].[Udvalg]  WITH CHECK ADD  CONSTRAINT [FK_Udvalg_DagsordenpunktFelt_Indstilling] FOREIGN KEY([IndstillingSkalKopieresTilFeltID])
REFERENCES [dbo].[DagsordenpunktFelt] ([ID])
GO
ALTER TABLE [dbo].[Udvalg] CHECK CONSTRAINT [FK_Udvalg_DagsordenpunktFelt_Indstilling]
GO
ALTER TABLE [dbo].[Udvalg]  WITH CHECK ADD  CONSTRAINT [FK_Udvalg_Sekretariat_Sekretariat] FOREIGN KEY([SekretariatID])
REFERENCES [dbo].[Sekretariat] ([ID])
GO
ALTER TABLE [dbo].[Udvalg] CHECK CONSTRAINT [FK_Udvalg_Sekretariat_Sekretariat]
GO
ALTER TABLE [dbo].[Udvalg]  WITH CHECK ADD  CONSTRAINT [FK_Udvalg_Udvalg_Udvalgsstruktur] FOREIGN KEY([UdvalgsstrukturID])
REFERENCES [dbo].[Udvalgsstruktur] ([ID])
GO
ALTER TABLE [dbo].[Udvalg] CHECK CONSTRAINT [FK_Udvalg_Udvalg_Udvalgsstruktur]
GO
ALTER TABLE [dbo].[Udvalgsmedlem]  WITH CHECK ADD  CONSTRAINT [FK_Udvaelgsmedlem_Udvaelgsmedlemmer_Udvalg] FOREIGN KEY([UdvalgID])
REFERENCES [dbo].[Udvalg] ([ID])
GO
ALTER TABLE [dbo].[Udvalgsmedlem] CHECK CONSTRAINT [FK_Udvaelgsmedlem_Udvaelgsmedlemmer_Udvalg]
GO
ALTER TABLE [dbo].[Udvalgsmedlem]  WITH NOCHECK ADD  CONSTRAINT [FK_Udvalgsmedlem_Udvalgsperson] FOREIGN KEY([UdvaelgspersonID])
REFERENCES [dbo].[Udvalgsperson] ([ID])
GO
ALTER TABLE [dbo].[Udvalgsmedlem] CHECK CONSTRAINT [FK_Udvalgsmedlem_Udvalgsperson]
GO
ALTER TABLE [dbo].[Udvalgsstruktur]  WITH NOCHECK ADD  CONSTRAINT [FK_Udvalgsstruktur_Parent_Udvalgsstruktur] FOREIGN KEY([ParentID])
REFERENCES [dbo].[Udvalgsstruktur] ([ID])
GO
ALTER TABLE [dbo].[Udvalgsstruktur] CHECK CONSTRAINT [FK_Udvalgsstruktur_Parent_Udvalgsstruktur]
GO
ALTER TABLE [dbo].[Vej]  WITH NOCHECK ADD  CONSTRAINT [Vej_Kommune] FOREIGN KEY([KommuneID])
REFERENCES [dbo].[KommuneOpslag] ([ID])
GO
ALTER TABLE [dbo].[Vej] CHECK CONSTRAINT [Vej_Kommune]
GO
ALTER TABLE [dbo].[WebWidgetBruger]  WITH CHECK ADD FOREIGN KEY([BrugerId])
REFERENCES [dbo].[Bruger] ([ID])
GO
ALTER TABLE [dbo].[WebWidgetBruger]  WITH CHECK ADD FOREIGN KEY([WebWidgetId])
REFERENCES [dbo].[WebWidget] ([ID])
GO
ALTER TABLE [dbo].[WebWidgetSagSkabelon]  WITH CHECK ADD FOREIGN KEY([SagskabelonId])
REFERENCES [dbo].[SagSkabelon] ([ID])
GO
ALTER TABLE [dbo].[WebWidgetSagSkabelon]  WITH CHECK ADD FOREIGN KEY([WebWidgetId])
REFERENCES [dbo].[WebWidget] ([ID])
GO
ALTER TABLE [dbo].[WebWidgetSagstype]  WITH CHECK ADD FOREIGN KEY([SagstypeID])
REFERENCES [dbo].[SagsType] ([Id])
GO
ALTER TABLE [dbo].[WebWidgetSagstype]  WITH CHECK ADD FOREIGN KEY([WebWidgetId])
REFERENCES [dbo].[WebWidget] ([ID])
GO
ALTER TABLE [dbo].[WordGeneratorDagsordenExtension]  WITH CHECK ADD  CONSTRAINT [FK_WordGeneratorDagsordenExtension_Dagsorden] FOREIGN KEY([DagsordenID])
REFERENCES [dbo].[Dagsorden] ([ID])
GO
ALTER TABLE [dbo].[WordGeneratorDagsordenExtension] CHECK CONSTRAINT [FK_WordGeneratorDagsordenExtension_Dagsorden]
GO
ALTER TABLE [dbo].[WordGeneratorUdvalgExtension]  WITH CHECK ADD  CONSTRAINT [FK_WordGeneratorUdvalgExtension_Udvalg] FOREIGN KEY([UdvalgID])
REFERENCES [dbo].[Udvalg] ([ID])
GO
ALTER TABLE [dbo].[WordGeneratorUdvalgExtension] CHECK CONSTRAINT [FK_WordGeneratorUdvalgExtension_Udvalg]
GO
ALTER TABLE [sts].[AnsaettelsesstedIdentitet]  WITH CHECK ADD  CONSTRAINT [FK_STSAnsaettelsesstedIdentitet_OrganisationIdentitet] FOREIGN KEY([OrganisationIdentitetID])
REFERENCES [sts].[OrganisationIdentitet] ([ID])
GO
ALTER TABLE [sts].[AnsaettelsesstedIdentitet] CHECK CONSTRAINT [FK_STSAnsaettelsesstedIdentitet_OrganisationIdentitet]
GO
ALTER TABLE [dbo].[Ansaettelsessted]  WITH CHECK ADD  CONSTRAINT [CK_AnsaettelsesstedUniqueCustomAdID] CHECK  (([dbo].[IsCustomAdIDUnique]([CustomAdID])='True'))
GO
ALTER TABLE [dbo].[Ansaettelsessted] CHECK CONSTRAINT [CK_AnsaettelsesstedUniqueCustomAdID]
GO
ALTER TABLE [dbo].[Beskedfordeling]  WITH CHECK ADD  CONSTRAINT [CK_Beskedfordeling_Column] CHECK  (((1)=(((case when [ForloebId] IS NULL then (0) else (1) end+case when [UsageLogId] IS NULL then (0) else (1) end)+case when [DokumentKonverteringBestillingId] IS NULL then (0) else (1) end)+case when [SendBOMBesvarelseBestillingId] IS NULL then (0) else (1) end)))
GO
ALTER TABLE [dbo].[Beskedfordeling] CHECK CONSTRAINT [CK_Beskedfordeling_Column]
GO
ALTER TABLE [dbo].[Bruger]  WITH CHECK ADD  CONSTRAINT [CK_Bruger_LogonAlgorithm] CHECK  (([LogonAlgorithm]='SHA512' OR [LogonAlgorithm]='SHA384' OR [LogonAlgorithm]='SHA256' OR [LogonAlgorithm]='MD5'))
GO
ALTER TABLE [dbo].[Bruger] CHECK CONSTRAINT [CK_Bruger_LogonAlgorithm]
GO
ALTER TABLE [dbo].[Bruger]  WITH CHECK ADD  CONSTRAINT [CK_Bruger_LogonIterations] CHECK  (([LogonAlgorithm]='MD5' AND [LogonIterations] IS NULL OR [LogonAlgorithm]<>'MD5' AND [LogonIterations] IS NOT NULL))
GO
ALTER TABLE [dbo].[Bruger] CHECK CONSTRAINT [CK_Bruger_LogonIterations]
GO
ALTER TABLE [dbo].[Bruger]  WITH CHECK ADD  CONSTRAINT [CK_Bruger_LogonSalt] CHECK  (([LogonAlgorithm]='MD5' AND [LogonSalt] IS NULL OR [LogonAlgorithm]<>'MD5' AND [LogonSalt] IS NOT NULL))
GO
ALTER TABLE [dbo].[Bruger] CHECK CONSTRAINT [CK_Bruger_LogonSalt]
GO
ALTER TABLE [dbo].[Bruger]  WITH CHECK ADD  CONSTRAINT [CK_BrugerUniqueObjectSid] CHECK  (([dbo].[IsObjectSidUnique]([ObjectSid])='True'))
GO
ALTER TABLE [dbo].[Bruger] CHECK CONSTRAINT [CK_BrugerUniqueObjectSid]
GO
ALTER TABLE [dbo].[Erindring]  WITH NOCHECK ADD  CONSTRAINT [CK_Erindring_Ikke_Tomt_Navn] CHECK  (([Navn]<>''))
GO
ALTER TABLE [dbo].[Erindring] CHECK CONSTRAINT [CK_Erindring_Ikke_Tomt_Navn]
GO
ALTER TABLE [dbo].[Person]  WITH NOCHECK ADD  CONSTRAINT [CK_Person_KontaktForm] CHECK  (([KontaktForm]>(0) AND [KontaktForm]<(4)))
GO
ALTER TABLE [dbo].[Person] CHECK CONSTRAINT [CK_Person_KontaktForm]
GO
ALTER TABLE [dbo].[SagSkabelonPart]  WITH CHECK ADD  CONSTRAINT [CK_SagSkabelonPart_BenytKorrektPartType] CHECK  (([FirmaID] IS NOT NULL AND [PartTypeID]=(0) OR [PersonID] IS NOT NULL AND [PartTypeID]=(1)))
GO
ALTER TABLE [dbo].[SagSkabelonPart] CHECK CONSTRAINT [CK_SagSkabelonPart_BenytKorrektPartType]
GO
ALTER TABLE [dbo].[SagSkabelonPart]  WITH CHECK ADD  CONSTRAINT [CK_SagSkabelonPart_RefererKunPersonEllerFirma] CHECK  (([FirmaID] IS NOT NULL AND [PersonID] IS NULL OR [FirmaID] IS NULL AND [PersonID] IS NOT NULL))
GO
ALTER TABLE [dbo].[SagSkabelonPart] CHECK CONSTRAINT [CK_SagSkabelonPart_RefererKunPersonEllerFirma]
GO
ALTER TABLE [dbo].[Sikkerhedsgruppe]  WITH NOCHECK ADD  CONSTRAINT [CK_SikkerhedsGruppeUniqueObjectSid] CHECK  (([dbo].[IsObjectSidUnique]([ObjectSid])='True'))
GO
ALTER TABLE [dbo].[Sikkerhedsgruppe] CHECK CONSTRAINT [CK_SikkerhedsGruppeUniqueObjectSid]
GO
ALTER TABLE [dbo].[StyringsreolHyldeFag]  WITH NOCHECK ADD  CONSTRAINT [CK_StyringsreolHyldeFag] CHECK  ((NOT ([NormtidDage] IS NULL AND [NormtidDato] IS NULL)))
GO
ALTER TABLE [dbo].[StyringsreolHyldeFag] CHECK CONSTRAINT [CK_StyringsreolHyldeFag]
GO
