USE [SbSysNetDrift]
GO

INSERT INTO [dbo].[Bruger]
           ([LogonID]
           ,[LogonPassword]
           ,[LogonSalt]
           ,[LogonAlgorithm]
           ,[LogonIterations]
           ,[LogonFailedAttemptCount]
           ,[LogonTemporaryLockedExpiration]
           ,[Navn]
           ,[Titel]
           ,[Stilling]
           ,[KontorID]
           ,[FagomraadeID]
           ,[Lokale]
           ,[AdresseID]
           ,[AnsaettelsesstedID]
           ,[Status]
           ,[EksternID]
           ,[ObjectSid]
           ,[UserPrincipalName]
           ,[BrugerIdentity]
           ,[ErSystembruger])
     VALUES (
             1, --(<LogonID, nvarchar(50),> NOT NULL
             Null, -- <LogonPassword, nvarchar(88),>
             Null, -- ,<LogonSalt, nvarchar(88),>
             'SHA512', -- <LogonAlgorithm, nvarchar(6),> NOT NULL
             Null, -- <LogonIterations, int,>
             0, -- <LogonFailedAttemptCount, int,> NOT NULL
             Null, -- <LogonTemporaryLockedExpiration, datetime,>
             N'Dev', -- <Navn, nvarchar(50),> NOT NULL
             Null, -- <Titel, nvarchar(50),>
             Null, -- <Stilling, nvarchar(50),>
             Null, -- <KontorID, int,>
             1, -- <FagomraadeID, int,> NOT NULL
             Null, -- <Lokale, nvarchar(50),>
             Null, -- <AdresseID, int,>
             1, -- <AnsaettelsesstedID, int,> NOT NULL
             1, -- <Status, int,>     NOT NULL
             Null, -- <EksternID, nvarchar(50),>
             N'S-DIG', -- <ObjectSid, nvarchar(50),>
             N'dev@devsen.dk', -- <UserPrincipalName, nvarchar(254),>
             CAST(N'4321DCBA-A1B2-4CD6-BCF1-764909F244CE' AS UNIQUEIDENTIFIER),--<BrugerIdentity, uniqueidentifier,> NOT NULL
             0 -- <ErSystembruger, bit,>) NOT NULL
            )
GO


