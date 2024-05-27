USE [SbSysNetDrift]
GO

INSERT INTO [dbo].[HierakiMedlem]
           ([Navn]
           ,[HierakiID]
           ,[ParentID]
           ,[EksternID]
           ,[SortIndex])
     VALUES
           (
            N'Vejstrand Hieraki Medlem', -- (<Navn, nvarchar(100),>
            1, -- <HierakiID, int,> NOT NULL
            Null, -- <ParentID, int,>
            Null, -- <EksternID, nvarchar(50),>
            Null -- <SortIndex, int,>)
           )
GO


