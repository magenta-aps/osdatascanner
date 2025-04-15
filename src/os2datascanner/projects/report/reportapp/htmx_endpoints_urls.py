from django.urls import path
from django.conf import settings

from .views.report_views import (
    HandleMatchView, MassHandleView, OpenMatchView, ShowMoreMatchesView,
    DistributeMatchesView,
    DeleteMailView, MassDeleteMailView,
    DeleteFileView, MassDeleteFileView,
    DeleteSMBFileView, MassDeleteSMBFileView,
    DeleteEWSMailView, MassDeleteEWSMailView,
    DeleteGmailView, MassDeleteGmailView)

urlpatterns = [
    path('handle_match/<int:pk>/', HandleMatchView.as_view(), name='handle-match'),
    path('mass_handle/', MassHandleView.as_view(), name='mass-handle'),
    path('open_match/<int:pk>/', OpenMatchView.as_view(), name='open-match'),
    path('show_more_matches/<int:pk>/', ShowMoreMatchesView.as_view(), name='show-more-matches'),
    path('distribute/', DistributeMatchesView.as_view(), name='distribute'),
    path('delete_mail/<int:pk>', DeleteMailView.as_view(), name='delete-mail'),
    path('mass_delete_mail/', MassDeleteMailView.as_view(), name="mass-delete-mail"),
    path('delete_file/<int:pk>', DeleteFileView.as_view(), name="delete-file"),
    path('mass_delete_file/', MassDeleteFileView.as_view(), name="mass-delete-file"),
]


if settings.SMB_ALLOW_WRITE:
    urlpatterns.extend([
        path('delete_smb_file/<int:pk>', DeleteSMBFileView.as_view(), name="delete-smb-file"),
        path('mass_delete_smb_file/', MassDeleteSMBFileView.as_view(), name="mass-delete-smb-file"),
    ])

if settings.EWS_ALLOW_WRITE:
    urlpatterns.extend([
        path('delete_ews_mail/<int:pk>', DeleteEWSMailView.as_view(), name="delete-ews-mail"),
        path('mass_delete_ews_mail/', MassDeleteEWSMailView.as_view(), name="mass-delete-ews-mail"),
    ])

if settings.GMAIL_ALLOW_WRITE:
    urlpatterns.extend([
        path('delete_gmail/<int:pk>', DeleteGmailView.as_view(), name="delete-gmail"),
        path('mass_delete_gmail/', MassDeleteGmailView.as_view(), name="mass-delete-gmail"),
    ])
