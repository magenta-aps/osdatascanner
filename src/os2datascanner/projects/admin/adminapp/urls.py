# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2datascanner is developed by Magenta in collaboration with the OS2 public
# sector open source network <https://os2.eu/>.
#
"""URL mappings."""

import django.contrib.auth.views
from django.conf.urls.static import static
from django.urls import re_path, path
from django.http import HttpResponse
from django.views.i18n import JavaScriptCatalog
from django.views.generic.base import TemplateView
from os2datascanner import __version__, __commit__, __tag__, __branch__
from os2datascanner.projects.admin.adminapp.views.analysis_views import (AnalysisPageView,
                                                                         AnalysisJobRunView)

from os2datascanner.projects.admin import settings

from .views.api import JSONAPIView
from .views.views import GuideView, DialogSuccess

import inspect
from .views import (exchangescanner_views, filescanner_views, dropboxscanner_views,
                    googledrivescanner_views, gmailscanner_views, sbsysscanner_views,
                    webscanner_views, msgraph_views)
from .views.exchangescanner_views import OrganizationalUnitListing
from .views.webscanner_views import WebScannerList

from .views.rule_views import (RuleList, CustomRuleCreate,
                               CustomRuleUpdate, CustomRuleDelete,
                               CustomRuleConnect)

from .views.scanner_views import (StatusOverview, StatusCompletedView, StatusCompletedCSVView,
                                  StatusDelete, StatusTimeline, UserErrorLogView,
                                  UserErrorLogCSVView, RemovedScannersView, RecreateScannerView,
                                  DeleteRemovedScannerView)


from .views.miniscanner_views import MiniScanner, execute_mini_scan, CustomRuleCreateMiniscan

from .views.scanner_views import (ScannerAskRun, ScannerCleanupStaleAccounts, ScannerCopy,
                                  ScannerCreate, ScannerDelete, ScannerList, ScannerRemove,
                                  ScannerRun, ScannerUpdate)
from .views.user_views import MyUserView, UserDetailView, UserUpdateView

urlpatterns = [
    # App URLs
    re_path(r'^$', WebScannerList.as_view(), name='index'),
    re_path(r'^api/openapi.yaml$', TemplateView.as_view(
        template_name="openapi.yaml", content_type="application/yaml"),
        name="json-api"),
    re_path(r'^api/(?P<path>.*)$', JSONAPIView.as_view(), name="json-api"),
    re_path(r'^analysis/overview/$',  AnalysisPageView.as_view(), name='analysis'),
    re_path(r'^analysis/overview/(?P<pk>\d+)/run/$',
            AnalysisJobRunView.as_view(), name='run-analysis-job'),
    # App URLs
    re_path(r'^status/$', StatusOverview.as_view(), name='status'),
    re_path(r'^status-completed/$', StatusCompletedView.as_view(), name='status-completed'),
    re_path(r'^status-completed/csv/$',
            StatusCompletedCSVView.as_view(), name='export-status-completed'),
    re_path(r'^status-completed/timeline/(?P<pk>\d+)/$',
            StatusTimeline.as_view(), name='status-timeline'),
    re_path(r'^error-log/$', UserErrorLogView.as_view(), name='error-log'),
    re_path(r'^error-log/csv/$', UserErrorLogCSVView.as_view(), name='export-error-log'),
    re_path(r'^status/(?P<pk>\d+)/delete/$', StatusDelete.as_view(), name='status-delete'),
    re_path(r'^help/guide/$', GuideView.as_view(), name='guide'),
    re_path(r'^org-units-listing/', OrganizationalUnitListing.as_view(), name='org-units-listing'),
    path("scanners/removed/", RemovedScannersView.as_view(), name="removed_scanners"),
    path("scanners/removed/<int:pk>/recreate", RecreateScannerView.as_view(),
         name="recreate_scanner"),
    path("scanners/removed/<int:pk>/delete", DeleteRemovedScannerView.as_view(),
         name="delete_removed_scanner"),


    re_path(r'^(msgraphcalendarscanners|msgraphmailscanners|msgraphfilescanners|'
            r'msgraphteamsfilescanners)/(\d+)/(created|saved)/$',
            DialogSuccess.as_view()),

    # Rules
    re_path(r'^rules/$', RuleList.as_view(), name='rules'),
    re_path(r'^rules/custom/add/$', CustomRuleCreate.as_view(), name='customrule_add'),
    re_path(r'^rules/custom/(?P<pk>\d+)/$', CustomRuleUpdate.as_view(),
            name='customrule_update'),
    re_path(r'^rules/custom/(?P<pk>\d+)/delete/$', CustomRuleDelete.as_view(),
            name='customrule_delete'),
    re_path(r'^rules/custom/(?P<pk>\d+)/connect/$', CustomRuleConnect.as_view(),
            name='connect-rule-to-org'),
    # Login/logout stuff
    re_path(r'^accounts/login/',
            django.contrib.auth.views.LoginView.as_view(
                template_name='components/user/login.html',
            ),
            name='login'),
    re_path(r'^accounts/logout/',
            django.contrib.auth.views.LogoutView.as_view(
                template_name='components/user/logout.html',
            ),
            name='logout'),
    re_path(r'^accounts/password_change/',
            django.contrib.auth.views.PasswordChangeView.as_view(
                template_name='components/password/password_change.html',
            ),
            name='password_change'),
    re_path(r'^accounts/password_change_done/',
            django.contrib.auth.views.PasswordChangeDoneView.as_view(
                template_name='components/password/password_change_done.html',
            ),
            name='password_change_done'),
    re_path(r'^accounts/password_reset/$',
            django.contrib.auth.views.PasswordResetView.as_view(
                template_name='components/password/password_reset_form.html',
            ),
            name='password_reset'),
    re_path(r'^accounts/password_reset/done/',
            django.contrib.auth.views.PasswordResetDoneView.as_view(
                template_name='components/password/password_reset_done.html',
            ),
            name='password_reset_done'),
    re_path(r'^accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/' +
            '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]*)/',
            django.contrib.auth.views.PasswordResetConfirmView.as_view(
                template_name='components/password/password_reset_confirm.html',
            ),
            name='password_reset_confirm'),
    re_path(r'^accounts/reset/complete',
            django.contrib.auth.views.PasswordResetCompleteView.as_view(
                template_name='components/password/password_reset_complete.html',
            ),
            name='password_reset_complete'),

    # User handlers
    path("users/me", MyUserView.as_view(), name="my-user"),
    path("users/<int:pk>", UserDetailView.as_view(), name="user"),
    path("users/<int:pk>/edit", UserUpdateView.as_view(), name="user-edit"),

    # General success handler
    re_path(r'^(webscanners|filescanners|exchangescanners|dropboxscanners|googledrivescanners|gmailscanners|sbsysscanners)/(\d+)/(created)/$',  # noqa
            DialogSuccess.as_view()),
    re_path(r'^(webscanners|filescanners|exchangescanners|dropboxscanners|googledrivescanners|gmailscanners|sbsysscanners)/(\d+)/(saved)/$',  # noqa
            DialogSuccess.as_view()),
    re_path(r'^(rules/regex|rules/cpr)/(\d+)/(created)/$',
            DialogSuccess.as_view()),
    re_path(r'^(rules/regex|rules/cpr)/(\d+)/(saved)/$',
            DialogSuccess.as_view()),

    re_path(r'^jsi18n/$',
            JavaScriptCatalog.as_view(
                packages=('os2datascanner.projects.admin.adminapp', 'recurrence')),
            name="jsi18n"),

    re_path(r'^health/', lambda r: HttpResponse()),
    re_path(r'^version/?$', lambda r: HttpResponse(
        f"""
        Version:   {__version__}<br/>
        Commit-ID: {__commit__}<br/>
        Tag:       {__tag__}<br/>
        Branch:    {__branch__}
        """)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.ENABLE_MINISCAN:
    urlpatterns.extend([
        path("miniscan/", MiniScanner.as_view(), name="miniscan"),
        path("miniscan/run/", execute_mini_scan, name="miniscan_run"),
        path("miniscan/rule/create", CustomRuleCreateMiniscan.as_view(),
             name="miniscan_customrule_create"),
    ])

# Iteratively add all scanner urls for consistent naming
for module in [exchangescanner_views,
               filescanner_views,
               dropboxscanner_views,
               googledrivescanner_views,
               gmailscanner_views,
               sbsysscanner_views,
               webscanner_views,
               msgraph_views]:
    imported = inspect.getmembers(module)
    for _, data in imported:

        type_to_action = {
            ScannerList: "list",
            ScannerCreate: "add",
            ScannerUpdate: "update",
            ScannerRemove: "remove",
            ScannerDelete: "delete",
            ScannerCopy: "copy",
            ScannerAskRun: "askrun",
            ScannerRun: "run",
            ScannerCleanupStaleAccounts: "cleanup",
        }

        action: str = None
        for superclass, act_label in type_to_action.items():
            if inspect.isclass(data) and issubclass(data, superclass) and data is not superclass:
                action = act_label
                break
        else:
            # No special treatment for this type
            continue

        stype: str = data.model.get_type().lower()

        # There are some special case patterns
        if action == "list":
            pattern = f"{stype}scanners/"
            name = f"{stype}scanners"
        elif action == "add":
            pattern = f"{stype}scanners/{action}/"
            name = f"{stype}scanner_{action}"
        else:
            pattern = f"{stype}scanners/<int:pk>/{action}/"
            name = f"{stype}scanner_{action}"

        urlpatterns.append(path(pattern, data.as_view(), name=name))
