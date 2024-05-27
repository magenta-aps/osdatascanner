USE [SbSysNetDrift]
GO

INSERT INTO [dbo].[Adresse]
           ([Adresse1]
           ,[Adresse2]
           ,[Adresse3]
           ,[Adresse4]
           ,[Adresse5]
           ,[PostNummer]
           ,[Bynavn]
           ,[HusNummer]
           ,[Etage]
           ,[DoerBetegnelse]
           ,[BygningsNummer]
           ,[Postboks]
           ,[PostDistrikt]
           ,[LandeKode]
           ,[ErUdlandsadresse]
           ,[ErBeskyttet]
           ,[AdresseIdentity]
           ,[AdgangsAdresseIdentity])
     VALUES (
             N'Vejstrand Huset', -- (<Adresse1, nvarchar(75),>
             Null, --<Adresse2, nvarchar(75),>
             Null, -- <Adresse3, nvarchar(75),>
             Null, -- <Adresse4, nvarchar(75),>
             Null, -- <Adresse5, nvarchar(75),>
             Null, -- <PostNummer, int,>
             Null, -- <Bynavn, nvarchar(80),>
             Null, -- <HusNummer, nvarchar(20),>
             Null, -- <Etage, nvarchar(10),>
             Null, -- <DoerBetegnelse, nvarchar(20),>
             Null, -- <BygningsNummer, nvarchar(20),>
             Null, -- <Postboks, nvarchar(10),>
             Null, -- <PostDistrikt, nvarchar(80),>
             Null, -- <LandeKode, nvarchar(3),>
             Null, -- <ErUdlandsadresse, bit,>
             0, -- <ErBeskyttet, bit,> NOT NULL
             Null, -- <AdresseIdentity, uniqueidentifier,>
             Null -- <AdgangsAdresseIdentity, uniqueidentifier,>)
            )
GO


