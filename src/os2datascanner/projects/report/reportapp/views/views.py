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
import datetime

from django.db.models import Count
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import View, TemplateView, ListView
from django.db.models import Q

from ..models.documentreport_model import DocumentReport
from ..models.roles.defaultrole_model import DefaultRole
from ..models.userprofile_model import UserProfile
from ..models.organization_model import Organization

from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.engine2.rules.rule import Sensitivity

logger = structlog.get_logger()

RENDERABLE_RULES = (CPRRule.type_label, RegexRule.type_label,)


class LoginRequiredMixin(View):
    """Include to require login."""
    roles = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """Check for login and dispatch the view."""
        return super().dispatch(*args, **kwargs)

    def get_user_roles(self):
        if self.roles is None:
            user = self.request.user
            self.roles = user.roles.select_subclasses() or [DefaultRole(user=user)]
        return self.roles


class LoginPageView(View):
    template_name = 'login.html'


class MainPageView(ListView, LoginRequiredMixin):
    template_name = 'index.html'
    paginate_by = 10  # Determines how many objects pr. page.
    context_object_name = "matches"  # object_list renamed to something more relevant
    model = DocumentReport
    matches = DocumentReport.objects.filter(
        data__matches__matched=True).filter(
        resolution_status__isnull=True)
    scannerjob_filters = None

    def get_queryset(self):
        # Filter by organization
        try:
            user_organization = self.request.user.profile.organization
            # Include matches without organization (backwards compatibility)
            self.matches = self.matches.filter(Q(organization=None) | Q(organization=user_organization))
        except UserProfile.DoesNotExist:
            # No UserProfile has been set on the request user
            # Default action depends on how many organization objects we have
            # If more than one exist, limit matches to ones without an organization (safety measure)
            if Organization.objects.count() > 1:
                self.matches = self.matches.filter(organization=None)

        # Filter matches by Default role. Remediator should no longer live when LDAP gets impl.
        self.matches = DefaultRole(user=self.request.user).filter(self.matches)

        if self.request.GET.get('scannerjob') \
                and self.request.GET.get('scannerjob') != 'all':
            # Filter by scannerjob
            self.matches = self.matches.filter(
                data__scan_tag__scanner__pk=int(
                    self.request.GET.get('scannerjob'))
            )
        if self.request.GET.get('sensitivities') \
                and self.request.GET.get('sensitivities') != 'all':
            # Filter by sensitivities
            self.matches = self.matches.filter(
                sensitivity=int(
                    self.request.GET.get('sensitivities'))
            )

        # matches are always ordered by sensitivity desc. and probability desc.
        return self.matches

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["renderable_rules"] = RENDERABLE_RULES

        if self.scannerjob_filters is None:
            # Create select options
            self.scannerjob_filters = self.matches.order_by(
                'data__scan_tag__scanner__pk').values(
                'data__scan_tag__scanner__pk').annotate(
                total=Count('data__scan_tag__scanner__pk')
            ).values(
                'data__scan_tag__scanner__name',
                'total',
                'data__scan_tag__scanner__pk'
            )

        context['scannerjobs'] = (self.scannerjob_filters,
                                  self.request.GET.get('scannerjob', 'all'))

        sensitivities = self.matches.order_by(
            '-sensitivity').values(
            'sensitivity').annotate(
            total=Count('sensitivity')
        ).values(
            'sensitivity', 'total'
        )

        context['sensitivities'] = (((Sensitivity(s["sensitivity"]),
                                      s["total"]) for s in sensitivities),
                                    self.request.GET.get('sensitivities', 'all'))

        return context


class StatisticsPageView(TemplateView, LoginRequiredMixin):
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

        # matches = DocumentReport.objects.filter(
        #     data__matches__matched=True)
        #
        # for role in self.get_user_roles():
        #     # TODO: filter either for the role dpo or leader, depending on the stats they are viewing.
        #     matches = role.filter(matches)

        # Contexts are done as a lists of tuples
        context['oldest_match'] = self.get_oldest_matches()
        
        context['data_sources'] = self.get_data_sources()

        context['sensitivities'], context['total_matches'] = self.get_sensitivities()

        context['handled_matches'], context['total_handled_matches'] = self.count_handled_matches()

        context['unhandled_matches'] = self.count_unhandled_matches()

        return context

    def count_handled_matches(self):
        # Counts the distribution of handled matches by sensitivity
        handled_matches = self.handled_matches.order_by(
            '-sensitivity').values(
            'sensitivity').annotate(
            total=Count('sensitivity')
        ).values(
            'sensitivity', 'total',
        )

        # For handling having no values - List defaults to 0
        handled_list = [
            [Sensitivity.CRITICAL.presentation, 0],
            [Sensitivity.PROBLEM.presentation, 0],
            [Sensitivity.WARNING.presentation, 0],
            [Sensitivity.NOTICE.presentation, 0],
        ]

        for hm in handled_matches:
            if (hm['sensitivity']) == 1000:
                handled_list[0][1] = hm['total']
            elif (hm['sensitivity']) == 750:
                handled_list[1][1] = hm['total']
            elif (hm['sensitivity']) == 500:
                handled_list[2][1] = hm['total']
            elif (hm['sensitivity']) == 250:
                handled_list[3][1] = hm['total']

        total = 0
        for hm in handled_list:
            total += hm[1]

        return handled_list, total

    def get_sensitivities(self):
        # Counts the distribution of matches by sensitivity
        sensitivities = self.matches.order_by(
            '-sensitivity').values(
            'sensitivity').annotate(
            total=Count('sensitivity')
        ).values(
            'sensitivity', 'total'
        )

        # For handling having no values - List defaults to 0
        sensitivity_list = [
            [Sensitivity.CRITICAL.presentation, 0],
            [Sensitivity.PROBLEM.presentation, 0],
            [Sensitivity.WARNING.presentation, 0],
            [Sensitivity.NOTICE.presentation, 0],
        ]
        
        for s in sensitivities:
            if (s['sensitivity']) == 1000:
                sensitivity_list[0][1] = s['total']
            elif (s['sensitivity']) == 750:
                sensitivity_list[1][1] = s['total']
            elif (s['sensitivity']) == 500:
                sensitivity_list[2][1] = s['total']
            elif (s['sensitivity']) == 250:
                sensitivity_list[3][1] = s['total']
            
        total = 0
        for s in sensitivity_list:
            total += s[1]

        return sensitivity_list, total

    def get_data_sources(self):
        # Counts the distribution of data sources by type
        data_sources = self.matches.order_by(
            'data__matches__handle__type').values(
            'data__matches__handle__type').annotate(
            total=Count('data__matches__handle__type')
        ).values(
            'data__matches__handle__type', 'total',
        )

        return [(ds['data__matches__handle__type'],
                ds['total']) for ds in data_sources]
        
    def count_unhandled_matches(self):
        # Counts the amount of unhandled matches
        unhandled_matches = self.unhandled_matches.order_by(
            'data__metadata__metadata').values(
            'data__metadata__metadata').annotate(
            total=Count('data__metadata__metadata')
        ).values(
            'data__metadata__metadata', 'total',
        )

        employee_unhandled_list = []
        for um in unhandled_matches:
            dict_values = list(um['data__metadata__metadata'].values())
            first_value = dict_values[0]
            employee_unhandled_list.append((first_value, um['total']))

        return employee_unhandled_list

    def get_oldest_matches(self):
        # TODO: Fiks så brugerne har deres egen værdi - Bug

        # Needs to be rewritten if a better 'time' is added(#41326)
        # Gets days since oldest unhandled matche for each user
        oldest_matches = []
        
        for org_user in self.users:
            org_roles = org_user.roles.select_subclasses() or [DefaultRole(user=org_user)]
            earliest_date = timezone.now()
            for match in self.unhandled_matches:
                if match.scan_time < earliest_date:
                    earliest_date = match.scan_time
                days_ago = timezone.now() - earliest_date
            tup = (org_user.first_name, days_ago.days)
            oldest_matches.append(tup)

        return oldest_matches


class LeaderStatisticsPageView(StatisticsPageView):
    template_name = 'statistics.html'


class DPOStatisticsPageView(StatisticsPageView):
    template_name = 'statistics.html'


class ApprovalPageView(TemplateView):
    template_name = 'approval.html'


class StatsPageView(TemplateView):
    template_name = 'stats.html'


class SettingsPageView(TemplateView):
    template_name = 'settings.html'


class AboutPageView(TemplateView):
    template_name = 'about.html'
