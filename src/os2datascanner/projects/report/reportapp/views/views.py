#!/usr/bin/env python
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
# OS2datascanner was developed by Magenta in collaboration with OS2 the
# Danish community of open source municipalities (https://os2.eu/).
#
# The code is currently governed by OS2 the Danish community of open
# source municipalities ( https://os2.eu/ )
import structlog

from datetime import timedelta
from calendar import month_abbr
from collections import deque
from urllib.parse import urlencode
from django.conf import settings

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.views.generic import View, TemplateView, ListView

from os2datascanner.utils.system_utilities import time_now
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.engine2.rules.rule import Sensitivity
from os2datascanner.projects.report.reportapp.models.roles.role_model import Role

from ..utils import user_is
from ..models.documentreport_model import DocumentReport
from ..models.roles.defaultrole_model import DefaultRole
from ..models.userprofile_model import UserProfile
from ..models.organization_model import Organization
from ..models.roles.remediator_model import Remediator

# For permissions
from ..models.roles.dpo_model import DataProtectionOfficer
from ..models.roles.leader_model import Leader

#DRF
from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from ..serializers import DocumentReportSerializers
from ..pagination import StandardResultsSetPagination


logger = structlog.get_logger()

RENDERABLE_RULES = (CPRRule.type_label, RegexRule.type_label,)


class LoginPageView(View):
    template_name = 'login.html'


class LogoutPageView(TemplateView, View):
    template_name = 'logout.html'


class MainPageView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

class ReportListing(LoginRequiredMixin, ListAPIView):

    # set the pagination and serializer class

    pagination_class = StandardResultsSetPagination
    serializer_class = DocumentReportSerializers

    def get_queryset(self):
    # filter the queryset based on the filters applied

        queryList = DocumentReport.objects.filter(
                data__matches__matched=True).filter(
                resolution_status__isnull=True)
        sensitivity = self.request.query_params.get('sensitivity', None)
        scannerjob = self.request.query_params.get('scannerjob', None)
        thirty_day_rule = self.request.query_params.get('30-day-rule', None)
        # region = self.request.query_params.get('region', None)
        # sort_by = self.request.query_params.get('sort_by', None)

        if sensitivity:
            queryList = queryList.filter(sensitivity = sensitivity)
        if scannerjob:
            queryList = queryList.filter(
                    data__scan_tag__scanner__pk = int(scannerjob))
        if thirty_day_rule == 'false':
            time_threshold = time_now() - timedelta(days=30)
            print(queryList.filter(datasource_last_modified__gte=time_threshold))
            queryList = queryList.filter(
                datasource_last_modified__lte=time_threshold)
            print(queryList.count())
        # if region:
        #     queryList = queryList.filter(region = region)    

        # sort it if applied on based on price/points

        # if sort_by == "price":
        #     queryList = queryList.order_by("price")
        # elif sort_by == "points":
        #     queryList = queryList.order_by("points")
        return queryList

def getSensitivities(request):
    if request.method == "GET" and request.is_ajax():
        documentreports = DocumentReport.objects.filter(
                data__matches__matched=True).filter(
                resolution_status__isnull=True)
        sensitivities = documentreports.exclude(sensitivity__isnull=True).\
                order_by('sensitivity').\
                values_list('sensitivity').distinct()
        sensitivities = [i[0] for i in list(sensitivities)]
        data = {
            "sensitivities": sensitivities, 
        }
        return JsonResponse(data, status = 200)


def getScannerjobs(request):
    if request.method == "GET" and request.is_ajax():
        documentreports = DocumentReport.objects.filter(
                data__matches__matched=True).filter(
                resolution_status__isnull=True)
        scannerjobs = documentreports.exclude(data__scan_tag__scanner__pk__isnull=True).\
                order_by('data__scan_tag__scanner__pk').\
                values_list('data__scan_tag__scanner__pk').distinct()
        scannerjobs = [i[0] for i in list(scannerjobs)]
        data = {
        "scannerjobs": scannerjobs, 
        }
        return JsonResponse(data, status = 200)


class StatisticsPageView(LoginRequiredMixin, TemplateView):
    template_name = 'statistics.html'
    context_object_name = "matches"  # object_list renamed to something more relevant
    model = DocumentReport
    users = UserProfile.objects.all()
    matches = DocumentReport.objects.filter(
        data__matches__matched=True)
    handled_matches = matches.filter(
        resolution_status__isnull=False)
    unhandled_matches = matches.filter(
        resolution_status__isnull=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now()

        # Contexts are done as lists of tuples
        context['sensitivities'], context['total_matches'] = \
            self.count_all_matches_grouped_by_sensitivity()

        context['handled_matches'], context['total_handled_matches'] = \
            self.count_handled_matches_grouped_by_sensitivity()

        context['source_types'] = self.count_by_source_types()

        context['new_matches_by_month'] = self.count_new_matches_by_month(today)

        return context

    def count_handled_matches_grouped_by_sensitivity(self):
        """Counts the distribution of handled matches grouped by sensitivity"""
        handled_matches = self.handled_matches.order_by(
            '-sensitivity').values(
            'sensitivity').annotate(
            total=Count('sensitivity')
        ).values(
            'sensitivity', 'total',
        )

        return self.create_sensitivity_list(handled_matches)

    def count_all_matches_grouped_by_sensitivity(self):
        """Counts the distribution of matches grouped by sensitivity"""
        sensitivities = self.matches.order_by(
            '-sensitivity').values(
            'sensitivity').annotate(
            total=Count('sensitivity')
        ).values(
            'sensitivity', 'total'
        )

        return self.create_sensitivity_list(sensitivities)

    def create_sensitivity_list(self, matches):
        """Helper method which groups the totals by sensitivities
        and also takes the sum of the totals"""
        # For handling having no values - List defaults to 0
        sensitivity_list = [
            [Sensitivity.CRITICAL.presentation, 0],
            [Sensitivity.PROBLEM.presentation, 0],
            [Sensitivity.WARNING.presentation, 0],
            [Sensitivity.NOTICE.presentation, 0],
        ]
        for match in matches:
            if (match['sensitivity']) == Sensitivity.CRITICAL.value:
                sensitivity_list[0][1] = match['total']
            elif (match['sensitivity']) == Sensitivity.PROBLEM.value:
                sensitivity_list[1][1] = match['total']
            elif (match['sensitivity']) == Sensitivity.WARNING.value:
                sensitivity_list[2][1] = match['total']
            elif (match['sensitivity']) == Sensitivity.NOTICE.value:
                sensitivity_list[3][1] = match['total']

        # Sum of the totals
        total = 0
        for match in sensitivity_list:
            total += match[1]

        return sensitivity_list, total

    def count_by_source_types(self):
        """Counts all matches grouped by source types"""
        matches_counted_by_sources = self.matches.order_by(
            'source_type').values(
            'source_type').annotate(
            total=Count('source_type')
        ).values(
            'source_type', 'total'
        )

        source_count_gen = ((m['source_type'], m['total'])
                            for m in matches_counted_by_sources)

        formatted_counts = [
            [_('Other'), 0],
            [_('Webscan'), 0],
            [_('Filescan'), 0],
            [_('Mailscan'), 0],
        ]

        # Places source_types from generator to formatted_counts
        for s in source_count_gen:
            if s[0] == 'web':
                formatted_counts[1][1] = s[1]
            elif s[0] == 'smbc':
                formatted_counts[2][1] = s[1]
            elif s[0] == 'ews':
                formatted_counts[3][1] = s[1]
            else:
                formatted_counts[0][1] += s[1]

        return formatted_counts
        
    def count_unhandled_matches(self):
        # Counts the amount of unhandled matches
        # TODO: Optimize queries by reading from relational db
        unhandled_matches = self.unhandled_matches.order_by(
            'data__metadata__metadata').values(
            'data__metadata__metadata').annotate(
            total=Count('data__metadata__metadata')
        ).values(
            'data__metadata__metadata', 'total',
        )

        # TODO: Optimize queries by reading from relational db
        employee_unhandled_list = []
        for um in unhandled_matches:
            dict_values = list(um['data__metadata__metadata'].values())
            first_value = dict_values[0]
            employee_unhandled_list.append((first_value, um['total']))

        return employee_unhandled_list

    def get_oldest_matches(self):
        # TODO: Needs to be rewritten if a better 'time' is added(#41326)
        # Gets days since oldest unhandled match for each user
        oldest_matches = []
        now = time_now

        for org_user in self.users:
            org_roles = Role.get_user_roles_or_default(org_user)
            earliest_date = now
            for match in self.unhandled_matches:
                if match.scan_time < earliest_date:
                    earliest_date = match.scan_time
                days_ago = now - earliest_date
            tup = (org_user.first_name, days_ago.days)
            oldest_matches.append(tup)

        return oldest_matches

    def count_new_matches_by_month(self, current_date):
        """Counts matches by months for the last year
        and rotates them by the current month"""
        a_year_ago = current_date - timedelta(days=365)

        # Truncates months with their match counts
        matches_by_month = self.matches.filter(
            created_timestamp__range=(a_year_ago, current_date)).annotate(
            month=TruncMonth('created_timestamp')).values(
            'month').annotate(
            total=Count('data')
        ).order_by('month')

        # Generator with the months as integers and the total
        matches_by_month_gen = ((int(m['month'].strftime('%m')), m['total'])
                                for m in matches_by_month)

        # Double-ended queue with all months abbreviated and a starting value
        deque_of_months = deque([[month_abbr[x + 1], 0] for x in range(12)])

        # Places totals from Generator to the correct months
        for m in matches_by_month_gen:
            deque_of_months[m[0] - 1][1] = m[1]

        # Rotates the current month to index 11
        current_month = int(current_date.strftime('%m'))
        deque_of_months.rotate(-current_month)

        return list(deque_of_months)


class LeaderStatisticsPageView(StatisticsPageView):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not user_is(Role.get_user_roles_or_default(request.user),
                           Leader):
                return HttpResponseForbidden()
        return super(LeaderStatisticsPageView, self).dispatch(
            request, *args, **kwargs)


class DPOStatisticsPageView(StatisticsPageView):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not user_is(Role.get_user_roles_or_default(request.user),
                           DataProtectionOfficer):
                return HttpResponseForbidden()
        return super(DPOStatisticsPageView, self).dispatch(
            request, *args, **kwargs)


class ApprovalPageView(TemplateView):
    template_name = 'approval.html'


class StatsPageView(TemplateView):
    template_name = 'stats.html'


class SettingsPageView(TemplateView):
    template_name = 'settings.html'


class AboutPageView(TemplateView):
    template_name = 'about.html'


# Logic separated to function to allow usability in send_notifications.py
def filter_inapplicable_matches(user, matches, roles):
    """ Filters matches by organization
    and role. """

    # Filter by organization
    try:
        user_organization = user.profile.organization
        # Include matches without organization (backwards compatibility)
        matches = matches.filter(Q(organization=None) | Q(organization=user_organization))
    except UserProfile.DoesNotExist:
        # No UserProfile has been set on the request user
        # Default action depends on how many organization objects we have
        # If more than one exist, limit matches to ones without an organization (safety measure)
        if Organization.objects.count() > 1:
            matches = matches.filter(organization=None)
    
    if user_is(roles, Remediator):
        # Filter matches by role.
        matches = Remediator(user=user).filter(matches)
    else:
        matches = DefaultRole(user=user).filter(matches)

    return matches


def oidc_op_logout_url_method(request):
    logout_url = settings.LOGOUT_URL
    return_to_url = settings.LOGOUT_REDIRECT_URL
    return logout_url + '?' + urlencode({'redirect_uri': return_to_url,
                                         'client_id': settings.OIDC_RP_CLIENT_ID})
