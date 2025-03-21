from django.urls import path

from os2datascanner.projects.grants.views import msgraph_views, smb_views, ews_views, googleapi_views  # noqa


urlpatterns = [
    path('msgraph/request/',
         msgraph_views.MSGraphGrantRequestView.as_view(
                redirect_token="admin:grants_graphgrant_changelist"),
         name='msgraphgrant-request'),
    path('msgraph/receive/',
         msgraph_views.MSGraphGrantReceptionView.as_view(),
         name='msgraphgrant-receive'),
    path('<uuid:org>/ews/',
         ews_views.EWSGrantCreateView.as_view(),
         name='ewsgrant-create'),
    path('<uuid:org>/msgraphgrant/',
         msgraph_views.MSGraphGrantCreateView.as_view(),
         name='msgraphgrant-create'),
    path('<uuid:org>/smb/',
         smb_views.SMBGrantCreateView.as_view(),
         name='smbgrant-create'),
    path('<uuid:org>/googleapigrant/',
         googleapi_views.GoogleApiGrantCreateView.as_view(),
         name='googleapigrant-create'),
    path('msgraph/<int:pk>/',
         msgraph_views.MSGraphGrantUpdateView.as_view(),
         name='msgraphgrant-update'),
    path('smb/<int:pk>/',
         smb_views.SMBGrantUpdateView.as_view(),
         name='smbgrant-update'),
    path('ews/<int:pk>/',
         ews_views.EWSGrantUpdateView.as_view(),
         name='ewsgrant-update'),
    path('googleapi/<int:pk>/',
         googleapi_views.GoogleApiGrantUpdateView.as_view(),
         name='googleapigrant-update'),
]
