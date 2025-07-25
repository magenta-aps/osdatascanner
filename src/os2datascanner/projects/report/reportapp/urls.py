import django.contrib.auth.views as auth_views
from django.urls import re_path, include, path
from django.http import HttpResponse
from django.conf.urls.static import static
from django.conf import settings
from django.views.i18n import JavaScriptCatalog
from django.views.generic import RedirectView

from os2datascanner import __version__

from .views.api import JSONAPIView
from .views.statistics_views import (
    LeaderUnitsStatisticsPageView, LeaderStatisticsRedirectView,
    DPOStatisticsPageView, DPOStatisticsCSVView,
    UserStatisticsPageView, EmployeeView, LeaderAccountsStatisticsPageView,
    LeaderAccountsStatisticsCSVView, LeaderUnitsStatisticsCSVView)
from .views.report_views import (
    UserReportView, UserArchiveView,
    RemediatorView, RemediatorArchiveView,
    UndistributedView, UndistributedArchiveView,
    SBSYSPersonalView, SBSYSPersonalArchiveView,
    SBSYSRemediatorView, SBSYSRemediatorArchiveView)
from .views.user_views import AccountView, AccountOutlookSettingView
from .views.scannerjob_views import ScannerjobListView, ScannerjobDeleteView
from .views.manual_views import ManualMainView
from .views.support_views import SupportButtonView
from os2datascanner.projects.shared.views import CustomPasswordResetView

reports_patterns = [
    # Pages related to unhandled reports:
    path("personal/",         UserReportView.as_view(),      name="personal"),
    path("remediator/",       RemediatorView.as_view(),      name="remediator"),
    path("undistributed/",    UndistributedView.as_view(),   name="undistributed"),
    path("sbsys-personal/",   SBSYSPersonalView.as_view(),   name="sbsys-personal"),
    path("sbsys-remediator/", SBSYSRemediatorView.as_view(), name="sbsys-remediator"),
]

archive_patterns = [
    # Pages related to archived reports:
    path("personal/",         UserArchiveView.as_view(),            name="personal"),
    path("remediator/",       RemediatorArchiveView.as_view(),      name="remediator"),
    path("undistributed/",    UndistributedArchiveView.as_view(),   name="undistributed"),
    path("sbsys-personal/",   SBSYSPersonalArchiveView.as_view(),   name="sbsys-personal"),
    path("sbsys-remediator/", SBSYSRemediatorArchiveView.as_view(), name="sbsys-remediator"),
]

urlpatterns = [
    # Document Report views
    path("",            UserReportView.as_view(),               name="index"),
    path("reports/",    include((reports_patterns, "reports"),  namespace="reports")),
    path("archive/",    include((archive_patterns, "archive"),  namespace="archive")),

    # LEGACY --> NEW MAPPINGS:
    # “/reports/” --> /reports/personal/
    re_path(
        r"^reports/?$",
        RedirectView.as_view(
            pattern_name="reports:personal",
            permanent=True,
            query_string=True
        )
    ),
    # “/remediator/” --> /reports/remediator/
    re_path(
        r"^remediator/?$",
        RedirectView.as_view(
            pattern_name="reports:remediator",
            permanent=True,
            query_string=True
        )
    ),
    # “/undistributed/” --> /reports/undistributed/
    re_path(
        r"^undistributed/?$",
        RedirectView.as_view(
            pattern_name="reports:undistributed",
            permanent=True,
            query_string=True
        )
    ),
    # "/archive/reports/" --> /archive/personal/
    re_path(
        r"^archive/reports/?$",
        RedirectView.as_view(
            pattern_name="archive:personal",
            permanent=True,
            query_string=True
        )
    ),

    # Scannerjob view
    path('scannerjobs/', ScannerjobListView.as_view(), name="scannerjobs"),
    path('scannerjobs/<int:pk>/delete', ScannerjobDeleteView.as_view(), name="delete_scannerjob"),

    # Statistics views
    path('statistics/leader', LeaderStatisticsRedirectView.as_view(), name='statistics-leader'),
    path('statistics/leader/units', LeaderUnitsStatisticsPageView.as_view(),
         name='statistics-leader-units'),
    path("statistics/leader/accounts", LeaderAccountsStatisticsPageView.as_view(),
         name='statistics-leader-accounts'),
    path('statistics/leader/accounts/csv', LeaderAccountsStatisticsCSVView.as_view(),
         name='statistics-leader-accounts-export'),
    path('statistics/leader/units/csv', LeaderUnitsStatisticsCSVView.as_view(),
         name='statistics-leader-units-export'),
    re_path(r'^statistics/dpo/$', DPOStatisticsPageView.as_view(), name='statistics-dpo'),
    re_path(r'^statistics/dpo/csv/$', DPOStatisticsCSVView.as_view(), name='statistics-dpo-export'),
    path('statistics/user/', UserStatisticsPageView.as_view(), name='statistics-user-me'),
    path('statistics/user/<uuid:pk>', UserStatisticsPageView.as_view(), name='statistics-user-id'),
    path('statistics/employee/<uuid:pk>', EmployeeView.as_view(), name='employee'),

    # Account view
    path('account/<uuid:pk>', AccountView.as_view(), name="account"),
    path('account/', AccountView.as_view(), name="account-me"),
    path("account/outlook-category-settings/", AccountOutlookSettingView.as_view(),
         name="outlook-category-settings"),

    re_path('api$',     JSONAPIView.as_view(),     name="json-api"),
    re_path(r'^health/', lambda r: HttpResponse()),
    re_path(r'^version/?$', lambda r: HttpResponse(__version__)),
    re_path(r'^help/$', ManualMainView.as_view(), name="guide"),
    re_path(r'^support/$', SupportButtonView.as_view(), name="support_button"),
    re_path(r'^jsi18n/$',
            JavaScriptCatalog.as_view(
                packages=(['os2datascanner.projects.report.reportapp'])),
            name="jsi18n"),
    path('htmx_endpoints/', include('os2datascanner.projects.report.reportapp.htmx_endpoints_urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


def setup_username_password_login_urls(**extra_context):
    urlpatterns.append(re_path(r'^accounts/login/',
                               auth_views.LoginView.as_view(
                                   template_name='components/user/login.html',
                                   extra_context=extra_context),
                               name='login'))
    urlpatterns.append(re_path(r'^accounts/logout/',
                               auth_views.LogoutView.as_view(
                                   template_name='components/user/logout.html'
                                   ),
                               name='logout'))
    urlpatterns.append(re_path(r'^accounts/password_change/',
                               auth_views.PasswordChangeView.as_view(
                                   template_name='components/password/password_change.html',
                                   ),
                               name='password_change'))
    urlpatterns.append(re_path(r'^accounts/password_change_done/',
                               auth_views.PasswordChangeDoneView.as_view(
                                   template_name='components/password/password_change_done.html',
                                   ),
                               name='password_change_done'))
    urlpatterns.append(re_path(r'^accounts/password_reset/$',
                               CustomPasswordResetView.as_view(
                                   template_name='components/password/password_reset_form.html',
                                   ),
                               name='password_reset'))
    urlpatterns.append(re_path(r'^accounts/password_reset/done/',
                               auth_views.PasswordResetDoneView.as_view(
                                   template_name='components/password/password_reset_done.html',
                                   ),
                               name='password_reset_done'))
    urlpatterns.append(re_path(r'^accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/' +
                               '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]*)/',
                               auth_views.PasswordResetConfirmView.as_view(
                                   template_name='components/password/password_reset_confirm.html',
                                   ),
                               name='password_reset_confirm'))
    urlpatterns.append(re_path(r'^accounts/reset/complete',
                               auth_views.PasswordResetCompleteView.as_view(
                                   template_name='components/password/password_reset_complete.html',
                                   ),
                               name='password_reset_complete'))


def setup_keycloak_login_urls():
    urlpatterns.append(path('oidc/', include('mozilla_django_oidc.urls'))),
    urlpatterns.append(re_path(r'^accounts/sso_logout/',
                               auth_views.LogoutView.as_view(
                                    template_name='components/user/logout.html'
                               ),
                               name='logout'))


if settings.HYBRID_LOGIN:
    setup_username_password_login_urls(keycloak_sso_enabled=settings.KEYCLOAK_ENABLED)
    settings.LOGIN_URL = "login"

    if settings.KEYCLOAK_ENABLED:
        setup_keycloak_login_urls()

else:
    if settings.KEYCLOAK_ENABLED:
        settings.LOGIN_URL = "oidc_authentication_init"
        setup_keycloak_login_urls()
    else:
        setup_username_password_login_urls()
