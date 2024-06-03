USE [SbSysNetDrift]
GO

INSERT INTO [dbo].[FagOmraade]
           ([Navn]
           ,[FagomraadeIdentity])
     VALUES
    (
        N'Veje og strande', -- (<Navn, nvarchar(50),>
        CAST('5678DCBA-A1B2-4CD6-BCF1-764909F244CE' AS UNIQUEIDENTIFIER) -- <FagomraadeIdentity, uniqueidentifier,>)
    )
GO


