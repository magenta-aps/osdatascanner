"""URL patterns for Directory Services"""
from django.urls import path

# Must be full path import to allow including url patterns in project urls
from os2datascanner.projects.admin.directory_services import views

urlpatterns = [
    path('ldap/configure/<uuid:org_id>', views.LDAPEditView.as_view(), name='add-ldap'),
]
