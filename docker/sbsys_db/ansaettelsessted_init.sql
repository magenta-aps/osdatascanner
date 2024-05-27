USE [SbSysNetDrift]
GO

INSERT INTO [dbo].[Ansaettelsessted]
           ([Navn]
           ,[CustomAdID]
           ,[Beskrivelse]
           ,[PostAdresseID]
           ,[FysiskAdresseID]
           ,[Aabningstider]
           ,[EanNummer]
           ,[Leder]
           ,[CvrNummer]
           ,[PNummer]
           ,[Fritekst1]
           ,[Fritekst2]
           ,[FagomraadeID]
           ,[Indjournaliseringsfolder]
           ,[DefaultEmneplanID]
           ,[HierakiMedlemID]
           ,[Webside]
           ,[DefaultSagSecuritySetID]
           ,[VisAdgangsListeVedOpretSag]
           ,[TilladBrugerAtSkiftePassword]
           ,[TilladPublicering]
           ,[EksterneAdviseringer]
           ,[AutomatiskErindringVedJournalisering]
           ,[StandardAktindsigtVedJournalisering]
           ,[VisCPR]
           ,[AnsaettelsesstedIdentity]
           ,[VisCVR])
     VALUES
           (
           N'Vejstrand vej-afdeling', -- (<Navn, nvarchar(100),> NOT NULL
           Null, -- <CustomAdID, nvarchar(50),>
           Null, -- <Beskrivelse, nvarchar(300),>
           1, -- <PostAdresseID, int,> NOT NULL
           1, -- <FysiskAdresseID, int,> NOT NULL
           Null, -- <Aabningstider, nvarchar(200),>
           Null, -- <EanNummer, nvarchar(15),>
           Null, -- <Leder, nvarchar(100),>
           Null, -- <CvrNummer, nvarchar(12),>
           Null,  -- <PNummer, nvarchar(12),>
           Null,  -- <Fritekst1, nvarchar(200),>
           Null,  -- <Fritekst2, nvarchar(200),>
           Null, -- <FagomraadeID, int,>
           Null, -- <Indjournaliseringsfolder, nvarchar(300),>
           Null, -- <DefaultEmneplanID, int,>
           1, -- <HierakiMedlemID, int,> NOT NULL
           Null, -- <Webside, nvarchar(300),>
           Null, -- <DefaultSagSecuritySetID, int,>
           Null, -- <VisAdgangsListeVedOpretSag, bit,>
           1, -- <TilladBrugerAtSkiftePassword, bit,> NOT NULL
           1, -- <TilladPublicering, bit,> NOT NULL
           0, -- <EksterneAdviseringer, int,> NOT NULL
           1, -- <AutomatiskErindringVedJournalisering, bit,> NOT NULL
           1, -- <StandardAktindsigtVedJournalisering, bit,> NOT NULL
           1,  -- <VisCPR, bit,> NOT NULL
           CAST(N'1011DAAA-A1B2-4CD6-BCF1-764909F244CE' AS UNIQUEIDENTIFIER), -- <AnsaettelsesstedIdentity, uniqueidentifier,> NOT NULL
           1 -- <VisCVR, bit,>) NOT NULL
    )
GO


