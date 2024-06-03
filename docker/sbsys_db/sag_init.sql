USE [SbSysNetDrift]
GO

-- Active case, less than a year since last edit
INSERT INTO [dbo].[Sag]
           ([SagIdentity]
           ,[Nummer]
           ,[Titel]
           ,[ErBeskyttet]
           ,[Kommentar]
           ,[BevaringID]
           ,[KommuneID]
           ,[BehandlerID]
           ,[SagsStatusID]
           ,[CreatedByID]
           ,[Created]
           ,[LastChangedByID]
           ,[LastChanged]
           ,[YderligereMaterialeFindes]
           ,[YderligereMaterialeBeskrivelse]
           ,[AmtID]
           ,[ErBesluttet]
           ,[Besluttet]
           ,[BeslutningsTypeID]
           ,[BeslutningNotat]
           ,[BeslutningDeadline]
           ,[BeslutningHarDeadline]
           ,[ErSamlesag]
           ,[FagomraadeID]
           ,[SecuritySetID]
           ,[SagsNummerID]
           ,[LastStatusChange]
           ,[LastStatusChangeComments]
           ,[Kassationsdato]
           ,[SagsPartID]
           ,[RegionID]
           ,[KommuneFoer2007ID]
           ,[Opstaaet]
           ,[AnsaettelsesstedID]
           ,[ArkivAfklaringStatusID]
           ,[ArkivNote]
           ,[StyringsreolHyldeID]
           ,[SkabelonID]
           ,[Sletningsdato])
     VALUES (
             CAST(N'1234ABCD-A1B2-4CD6-BCF1-764909F244CE' AS UNIQUEIDENTIFIER), -- SagsIdentity NOT NULL, uniqueidentifier
             N'06.13.01-K02-3-13', -- Nummer NOT NULL, nvarchar
             N'Opsætning af skilte: Skabet til Narnia', -- Titel NOT NULL, nvarchar
             1, -- ErBeskyttet  NOT NULL, bit
             Null, -- Kommentar, nvarchar
             Null, -- BevaringID, int
             Null, -- KommuneID, int
             1, -- Behandler ID NOT NULL, int, FORVIRRENDE, MEN DET ER "BRUGER" TABELLEN.
             8, -- SagsStatusID NOT NULL, int
             1, --CreatedByID NOT NULL, int
             CAST(N'2013-09-11 00:00:00.000' AS DATETIME), -- Created NOT NULL, datetime
             1, -- LastChangedByID NOT NULL, int
             CAST(N'2023-09-11 00:00:00.000' AS DATETIME), -- LastChanged, datetime
             Null, -- YderligereMaterialeFindes, bit
             Null, -- YderligereMaterialeBeskrivelse, nvarchar
             Null, -- AmtID, int
             Null, -- ErBesluttet, bit
             Null, -- Besluttet, datetime
             Null, -- BeslutningsTypeID, int
             Null, -- BeslutningNotat, nvarchar
             Null, -- BeslutningDeadline, datetime
             Null, -- BeslutningHarDeadline, bit
             Null, -- ErSamlesag, bit
             Null, -- FagomraadeID, int
             Null, -- SecuritySetID, int
             Null, -- SagsNummerID, int
             Null, -- LastStatusChange, datetime,
             Null, -- LastStatusChangeComments, nvarchar
             Null, -- Kassationsdato, datetime
             Null, -- SagsPartID, int
             Null, -- RegionID, int,
             Null, -- KommuneFoer2007ID, int
             Null, -- Opstaaet, datetime
             1, -- AnsaettelsesstedID, NOT NULL, int
             1, --ArkivAfklaringStatusID, NOT NULL, int
             Null, -- ArkivNote, ntext
             Null, -- StyringsreolHyldeID, int
             Null, -- SkabelonID, int
             Null -- Sletningsdato, datetime
            )
GO

-- Non-active case, more than a year since last edit
INSERT INTO [dbo].[Sag]
           ([SagIdentity]
           ,[Nummer]
           ,[Titel]
           ,[ErBeskyttet]
           ,[Kommentar]
           ,[BevaringID]
           ,[KommuneID]
           ,[BehandlerID]
           ,[SagsStatusID]
           ,[CreatedByID]
           ,[Created]
           ,[LastChangedByID]
           ,[LastChanged]
           ,[YderligereMaterialeFindes]
           ,[YderligereMaterialeBeskrivelse]
           ,[AmtID]
           ,[ErBesluttet]
           ,[Besluttet]
           ,[BeslutningsTypeID]
           ,[BeslutningNotat]
           ,[BeslutningDeadline]
           ,[BeslutningHarDeadline]
           ,[ErSamlesag]
           ,[FagomraadeID]
           ,[SecuritySetID]
           ,[SagsNummerID]
           ,[LastStatusChange]
           ,[LastStatusChangeComments]
           ,[Kassationsdato]
           ,[SagsPartID]
           ,[RegionID]
           ,[KommuneFoer2007ID]
           ,[Opstaaet]
           ,[AnsaettelsesstedID]
           ,[ArkivAfklaringStatusID]
           ,[ArkivNote]
           ,[StyringsreolHyldeID]
           ,[SkabelonID]
           ,[Sletningsdato])
     VALUES (
             CAST(N'0D468458-6F70-4B1C-9C6F-D7C49454A128' AS UNIQUEIDENTIFIER), -- SagsIdentity NOT NULL, uniqueidentifier
             N'07.13.01-K02-3-13', -- Nummer NOT NULL, nvarchar
             N'Eiffel Tower', -- Titel NOT NULL, nvarchar
             1, -- ErBeskyttet  NOT NULL, bit
             Null, -- Kommentar, nvarchar
             Null, -- BevaringID, int
             Null, -- KommuneID, int
             1, -- Behandler ID NOT NULL, int, FORVIRRENDE, MEN DET ER "BRUGER" TABELLEN.
             5, -- SagsStatusID NOT NULL, int, 5 = "AFSLUTTET" => non-active SagsTilstand
             1, --CreatedByID NOT NULL, int
             CAST(N'2013-09-11 00:00:00.000' AS DATETIME), -- Created NOT NULL, datetime
             1, -- LastChangedByID NOT NULL, int
             CAST(N'2022-09-11 00:00:00.000' AS DATETIME), -- LastChanged, datetime
             Null, -- YderligereMaterialeFindes, bit
             Null, -- YderligereMaterialeBeskrivelse, nvarchar
             Null, -- AmtID, int
             Null, -- ErBesluttet, bit
             Null, -- Besluttet, datetime
             Null, -- BeslutningsTypeID, int
             Null, -- BeslutningNotat, nvarchar
             Null, -- BeslutningDeadline, datetime
             Null, -- BeslutningHarDeadline, bit
             Null, -- ErSamlesag, bit
             Null, -- FagomraadeID, int
             Null, -- SecuritySetID, int
             Null, -- SagsNummerID, int
             Null, -- LastStatusChange, datetime,
             Null, -- LastStatusChangeComments, nvarchar
             Null, -- Kassationsdato, datetime
             Null, -- SagsPartID, int
             Null, -- RegionID, int,
             Null, -- KommuneFoer2007ID, int
             Null, -- Opstaaet, datetime
             1, -- AnsaettelsesstedID, NOT NULL, int
             1, --ArkivAfklaringStatusID, NOT NULL, int
             Null, -- ArkivNote, ntext
             Null, -- StyringsreolHyldeID, int
             Null, -- SkabelonID, int
             Null -- Sletningsdato, datetime
            )
GO

-- Active case, more than a year since last edit
INSERT INTO [dbo].[Sag]
           ([SagIdentity]
           ,[Nummer]
           ,[Titel]
           ,[ErBeskyttet]
           ,[Kommentar]
           ,[BevaringID]
           ,[KommuneID]
           ,[BehandlerID]
           ,[SagsStatusID]
           ,[CreatedByID]
           ,[Created]
           ,[LastChangedByID]
           ,[LastChanged]
           ,[YderligereMaterialeFindes]
           ,[YderligereMaterialeBeskrivelse]
           ,[AmtID]
           ,[ErBesluttet]
           ,[Besluttet]
           ,[BeslutningsTypeID]
           ,[BeslutningNotat]
           ,[BeslutningDeadline]
           ,[BeslutningHarDeadline]
           ,[ErSamlesag]
           ,[FagomraadeID]
           ,[SecuritySetID]
           ,[SagsNummerID]
           ,[LastStatusChange]
           ,[LastStatusChangeComments]
           ,[Kassationsdato]
           ,[SagsPartID]
           ,[RegionID]
           ,[KommuneFoer2007ID]
           ,[Opstaaet]
           ,[AnsaettelsesstedID]
           ,[ArkivAfklaringStatusID]
           ,[ArkivNote]
           ,[StyringsreolHyldeID]
           ,[SkabelonID]
           ,[Sletningsdato])
     VALUES (
             CAST(N'F6E6AD45-5ABB-44C0-AB76-D3863FC9C574' AS UNIQUEIDENTIFIER), -- SagsIdentity NOT NULL, uniqueidentifier
             N'05.13.01-K02-3-13', -- Nummer NOT NULL, nvarchar
             N'Den grimme ælling', -- Titel NOT NULL, nvarchar
             1, -- ErBeskyttet  NOT NULL, bit
             Null, -- Kommentar, nvarchar
             Null, -- BevaringID, int
             Null, -- KommuneID, int
             1, -- Behandler ID NOT NULL, int, FORVIRRENDE, MEN DET ER "BRUGER" TABELLEN.
             8, -- SagsStatusID NOT NULL, int, 8 = "OPSTÅET" => active SagsTilstand
             1, --CreatedByID NOT NULL, int
             CAST(N'2013-09-11 00:00:00.000' AS DATETIME), -- Created NOT NULL, datetime
             1, -- LastChangedByID NOT NULL, int
             CAST(N'2022-09-11 00:00:00.000' AS DATETIME), -- LastChanged, datetime
             Null, -- YderligereMaterialeFindes, bit
             Null, -- YderligereMaterialeBeskrivelse, nvarchar
             Null, -- AmtID, int
             Null, -- ErBesluttet, bit
             Null, -- Besluttet, datetime
             Null, -- BeslutningsTypeID, int
             Null, -- BeslutningNotat, nvarchar
             Null, -- BeslutningDeadline, datetime
             Null, -- BeslutningHarDeadline, bit
             Null, -- ErSamlesag, bit
             Null, -- FagomraadeID, int
             Null, -- SecuritySetID, int
             Null, -- SagsNummerID, int
             Null, -- LastStatusChange, datetime,
             Null, -- LastStatusChangeComments, nvarchar
             Null, -- Kassationsdato, datetime
             Null, -- SagsPartID, int
             Null, -- RegionID, int,
             Null, -- KommuneFoer2007ID, int
             Null, -- Opstaaet, datetime
             1, -- AnsaettelsesstedID, NOT NULL, int
             1, --ArkivAfklaringStatusID, NOT NULL, int
             Null, -- ArkivNote, ntext
             Null, -- StyringsreolHyldeID, int
             Null, -- SkabelonID, int
             Null -- Sletningsdato, datetime
            )
GO
