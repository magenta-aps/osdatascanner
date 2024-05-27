USE [SbSysNetDrift]
GO
DELETE FROM [dbo].[ArkivAfklaringStatus]
GO
SET IDENTITY_INSERT [dbo].[ArkivAfklaringStatus] ON
GO
INSERT [dbo].[ArkivAfklaringStatus] ([ID], [Navn]) VALUES (1, N'Mangler bekræftelse')
GO
INSERT [dbo].[ArkivAfklaringStatus] ([ID], [Navn]) VALUES (2, N'Skal arkiveres')
GO
SET IDENTITY_INSERT [dbo].[ArkivAfklaringStatus] OFF
GO
