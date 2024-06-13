from django.urls import path

from os2datascanner.projects.grants.views import msgraph_views


urlpatterns = [
    path('msgraph/request/',
         msgraph_views.MSGraphGrantRequestView.as_view(
                redirect_token="admin:grants_graphgrant_changelist"),
         name='msgraphgrant-request'),
    path('msgraph/receive/',
         msgraph_views.MSGraphGrantReceptionView.as_view(),
         name='msgraphgrant-receive'),
]
