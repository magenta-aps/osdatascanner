import django_saml2_auth.views
import django.contrib.auth.views as auth_views
from django.urls import re_path
from django.http import HttpResponse
from django.urls import include
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from django.views.i18n import JavaScriptCatalog
from os2datascanner import __version__

from .views.api import JSONAPIView
from .views.saml import metadata
from .views.statistics_views import (
    LeaderStatisticsPageView, LeaderStatisticsCSVView, DPOStatisticsPageView, DPOStatisticsCSVView,
    UserStatisticsPageView, EmployeeView)
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

urlpatterns = [
    re_path(r'^$',      UserReportView.as_view(),     name="index"),
    re_path(r'^reports$', UserReportView.as_view(), name="reports"),
    re_path(r'^remediator$', RemediatorView.as_view(), name="remediator"),
    re_path(r'^undistributed$', UndistributedView.as_view(), name="undistributed"),
    re_path(r'^archive/reports', UserArchiveView.as_view(), name="reports-archive"),
    re_path(r'^archive/remediator', RemediatorArchiveView.as_view(), name="remediator-archive"),
    re_path(r'^archive/undistributed', UndistributedArchiveView.as_view(),
         name="undistributed-archive"),  # noqa
    re_path(r'^sbsys/personal', SBSYSPersonalView.as_view(), name="sbsys-personal"),
    re_path(r'^sbsys/remediator', SBSYSRemediatorView.as_view(), name="sbsys-remediator"),
    re_path(r'^sbsys/archive/personal', SBSYSPersonalArchiveView.as_view(),
         name="sbsys-archive-personal"),   # noqa
    re_path(r'^sbsys/archive/remediator', SBSYSRemediatorArchiveView.as_view(),
         name="sbsys-archive-remediator"),   # noqa
    re_path('api$',     JSONAPIView.as_view(),     name="json-api"),
    path('account/<uuid:pk>', AccountView.as_view(), name="account"),
    path('account/', AccountView.as_view(), name="account-me"),
    path("account/outlook-category-settings/", AccountOutlookSettingView.as_view(),
         name="outlook-category-settings"),
    re_path(r'^statistics/leader/$', LeaderStatisticsPageView.as_view(), name='statistics-leader'),
    re_path(r'^statistics/leader/csv/$', LeaderStatisticsCSVView.as_view(), name='statistics-leader-export'),  # noqa
    re_path(r'^statistics/dpo/$', DPOStatisticsPageView.as_view(), name='statistics-dpo'),
    re_path(r'^statistics/dpo/csv/$', DPOStatisticsCSVView.as_view(), name='statistics-dpo-export'),
    path('statistics/user/', UserStatisticsPageView.as_view(),
         name='statistics-user-me'),
    path('statistics/user/<uuid:pk>', UserStatisticsPageView.as_view(),
         name='statistics-user-id'),
    path('statistics/employee/<uuid:pk>', EmployeeView.as_view(), name='employee'),
    path('scannerjobs/', ScannerjobListView.as_view(), name="scannerjobs"),
    path('scannerjobs/<int:pk>/delete', ScannerjobDeleteView.as_view(), name="delete_scannerjob"),
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
                               auth_views.PasswordResetView.as_view(
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


def setup_saml2_login_urls():
    urlpatterns.append(re_path(r"^saml2_auth/metadata.xml$", metadata, name="saml_metadata"))
    urlpatterns.append(re_path(r"^saml2_auth/", include("django_saml2_auth.urls")))
    urlpatterns.append(re_path(r"^accounts/sso_login/$", django_saml2_auth.views.signin,
                               name="login"))
    urlpatterns.append(
        re_path(
            r'^accounts/sso_logout/$',
            django_saml2_auth.views.signout,
            name="logout"))


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
    if settings.SAML2_ENABLED:
        setup_saml2_login_urls()

    if settings.KEYCLOAK_ENABLED:
        settings.LOGIN_URL = "oidc_authentication_init"
        setup_keycloak_login_urls()
    else:
        setup_username_password_login_urls()
