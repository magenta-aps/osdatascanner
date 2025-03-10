"""URL patterns for Organizations"""
from django.urls import path

# Must be full path import to allow including url patterns in project urls
from os2datascanner.projects.admin.organizations import views

urlpatterns = [
    path('', views.OrganizationListView.as_view(), name='organization-list'),
    path('add', views.AddOrganizationView.as_view(), name='add-organization'),
    path('add_for/<uuid:client_id>', views.AddOrganizationView.as_view(),
         name='add-organization-for'),
    path('<slug:slug>/edit', views.UpdateOrganizationView.as_view(), name='edit-organization'),
    path('<slug:org_slug>/units', views.OrganizationalUnitListView.as_view(), name='orgunit-list'),
    path('<slug:org_slug>/units/edit-visibility', views.OrganizationalUnitEditVisibility.as_view(),
         name='edit-orgunit-visibility-view'),
    path('<slug:org_slug>/units/<uuid:pk>/manager-dropdown', views.ManagerDropdownView.as_view(),
         name='manager-dropdown'),
    path('<slug:org_slug>/units/<uuid:pk>/dpo-dropdown', views.DPODropdownView.as_view(),
         name='dpo-dropdown'),
    path('<slug:org_slug>/uni-dpo-dropdown', views.OrgDPODropdownView.as_view(),
         name='uni-dpo-dropdown'),
    path('<slug:slug>/delete', views.DeleteOrganizationView.as_view(), name='delete-organization'),
    path('<slug:slug>/org_delete_blocked', views.OrganizationDeletionBlocked.as_view(),
         name='org_delete_block'),
    path('<slug:org_slug>/accounts/', views.AccountListView.as_view(), name='accounts'),
    path('<slug:org_slug>/accounts/<uuid:pk>', views.AccountDetailView.as_view(), name='account'),
    path('<slug:org_slug>/accounts/<uuid:acc_uuid>/alias/create',
         views.AliasCreateView.as_view(), name='create-alias'),
    path('<slug:org_slug>/accounts/<uuid:acc_uuid>/alias/<uuid:pk>/delete',
         views.AliasDeleteView.as_view(), name='delete-alias'),
    path('<uuid:org_id>/sso/add/', views.SSOCreateView.as_view(), name='add-sso'),
    path('<uuid:org_id>/sso/edit/', views.SSOUpdateView.as_view(), name='edit-sso'),
    path('sso/error', views.SSOErrorView.as_view(), name='sso-error'),
    path('grants/', views.GrantListView.as_view(), name='grant-list'),
    path('grants/<str:type>/<int:pk>/edit/',
         views.GrantRedirectUpdateView.as_view(),
         name='edit-grant'),
]
