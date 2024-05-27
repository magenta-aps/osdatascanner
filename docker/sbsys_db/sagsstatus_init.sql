USE [SbSysNetDrift]
GO
DELETE FROM [dbo].[SagsStatus]
GO
SET IDENTITY_INSERT [dbo].[SagsStatus] ON
GO
INSERT [dbo].[SagsStatus] ([ID], [Navn], [Orden], [SagsTilstand], [RequireComments], [IsDeleted], [SagsForklaede]) VALUES (1, N'Opklaring', 2, 0, 0, 0, 0)
GO
INSERT [dbo].[SagsStatus] ([ID], [Navn], [Orden], [SagsTilstand], [RequireComments], [IsDeleted], [SagsForklaede]) VALUES (2, N'Afgjort_slettet', 3, 0, 0, 1, 0)
GO
INSERT [dbo].[SagsStatus] ([ID], [Navn], [Orden], [SagsTilstand], [RequireComments], [IsDeleted], [SagsForklaede]) VALUES (3, N'Afventer', 4, 0, 0, 0, 0)
GO
INSERT [dbo].[SagsStatus] ([ID], [Navn], [Orden], [SagsTilstand], [RequireComments], [IsDeleted], [SagsForklaede]) VALUES (4, N'Afsluttet', 5, 1, 0, 0, 2)
GO
INSERT [dbo].[SagsStatus] ([ID], [Navn], [Orden], [SagsTilstand], [RequireComments], [IsDeleted], [SagsForklaede]) VALUES (5, N'Arkiveret', 6, 1, 0, 0, 2)
GO
INSERT [dbo].[SagsStatus] ([ID], [Navn], [Orden], [SagsTilstand], [RequireComments], [IsDeleted], [SagsForklaede]) VALUES (6, N'Afsluttet fra GoPro', 7, 1, 0, 0, 2)
GO
INSERT [dbo].[SagsStatus] ([ID], [Navn], [Orden], [SagsTilstand], [RequireComments], [IsDeleted], [SagsForklaede]) VALUES (7, N'Endeligt_slettet', 8, 1, 0, 1, 2)
GO
INSERT [dbo].[SagsStatus] ([ID], [Navn], [Orden], [SagsTilstand], [RequireComments], [IsDeleted], [SagsForklaede]) VALUES (8, N'Opstået', 1, 0, 0, 0, 0)
GO
SET IDENTITY_INSERT [dbo].[SagsStatus] OFF
GO
