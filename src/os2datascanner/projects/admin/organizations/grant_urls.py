# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.urls import path
from os2datascanner.projects.admin.organizations import views

urlpatterns = [
    path('msgraph/request/',
         views.MSGraphGrantRequestView.as_view(
             redirect_token="admin:grants_graphgrant_changelist"),
         name='msgraphgrant-request'),
    path('msgraph/receive/',
         views.MSGraphGrantReceptionView.as_view(),
         name='msgraphgrant-receive'),
    path('<uuid:org>/ews/',
         views.EWSGrantCreateView.as_view(),
         name='ewsgrant-create'),
    path('<uuid:org>/msgraphgrant/',
         views.MSGraphGrantCreateView.as_view(),
         name='msgraphgrant-create'),
    path('<uuid:org>/smb/',
         views.SMBGrantCreateView.as_view(),
         name='smbgrant-create'),
    path('<uuid:org>/googleapigrant/',
         views.GoogleApiGrantCreateView.as_view(),
         name='googleapigrant-create'),
    path('msgraph/<uuid:pk>/',
         views.MSGraphGrantUpdateView.as_view(),
         name='msgraphgrant-update'),
    path('smb/<uuid:pk>/',
         views.SMBGrantUpdateView.as_view(),
         name='smbgrant-update'),
    path('ews/<uuid:pk>/',
         views.EWSGrantUpdateView.as_view(),
         name='ewsgrant-update'),
    path('googleapi/<uuid:pk>/',
         views.GoogleApiGrantUpdateView.as_view(),
         name='googleapigrant-update'),
]
