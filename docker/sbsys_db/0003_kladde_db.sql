CREATE DATABASE [SbSysNetDriftKladde0000]
GO
USE [SbSysNetDriftKladde0000]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [SbSysNetDriftKladde0000].dbo.KladdeData (
    [ID] [int] IDENTITY (1, 1) NOT NULL,
    [KladdeID] [int] NULL,
    [Data] [image] NULL,
    [Version] [int] NULL,
    [Created] [datetime] NULL
 CONSTRAINT [PK_KladdeData_ID] PRIMARY KEY NONCLUSTERED
(
    [ID]
) WITH FILLFACTOR = 90 ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

CREATE UNIQUE INDEX [IX_KladdeData_KladdeIDVersion]
ON [SbSysNetDriftKladde0000].[dbo].[KladdeData] ([KladdeID], [Version]) ON [PRIMARY]
GO