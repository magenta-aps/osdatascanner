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

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count, DateField, When, Case
from django.db.models.functions import Coalesce, TruncMonth
from django.http import HttpResponseForbidden, Http404, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.views.generic import TemplateView, DetailView, ListView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.conf import settings

from ..models.documentreport import DocumentReport
from ...organizations.models.account import Account
from ...organizations.models.aliases import AliasType
from ...organizations.models.position import Position
from ...organizations.models.organizational_unit import OrganizationalUnit
from ....utils.view_mixins import CSVExportMixin
from .report_views import EmptyPagePaginator


logger = structlog.get_logger("reportapp")


def month_delta(series_start: date, here: date):
    """Returns the (zero-based) month index of @here relative to
    @series_start."""

    def _months(date: date):
        return date.year * 12 + date.month

    return _months(here) - _months(series_start)


class DPOStatisticsPageView(LoginRequiredMixin, TemplateView):
    context_object_name = "matches"  # object_list renamed to something more relevant
    template_name = "statistics.html"
    model = DocumentReport
    scannerjob_filters = None

    # TODO: We need to figure out multi tenancy. I.e. only view stuff from your organization

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholder_time = timezone.make_aware(timezone.datetime(1970, 1, 1))
        today = timezone.now()
        a_month_ago = today - timedelta(days=30)

        self.matches = DocumentReport.objects.filter(number_of_matches__gte=1).annotate(
            created_recently=Case(
                When(
                    created_timestamp__gte=a_month_ago,
                    then=True
                ),
                default=False
            ),
            handled_recently=Case(
                When(
                    resolution_time__gte=a_month_ago,
                    then=True,
                ),
                default=False
            ),
            created_month=TruncMonth(
                        # If created_timestamp isn't set on a DocumentReport
                        # the timestamp is set to a default time value.
                        Coalesce('created_timestamp', placeholder_time),
                        output_field=DateField()),
            resolved_month=TruncMonth(
                        # If resolution_time isn't set on a report that has been
                        # handled, then assume it was handled in the same month it
                        # was created
                        Coalesce('resolution_time', 'created_timestamp'),
                        output_field=DateField())).values(
                            'resolution_status',
                            'source_type',
                            'created_month',
                            'resolved_month',
                            'created_recently',
                            'handled_recently',
                        ).annotate(count=Count('source_type')).order_by()

    def _check_access(self, request):
        if self.request.user.account:

            if self.request.user.is_superuser:
                self.user_units = OrganizationalUnit.objects.all().order_by("name")
            else:
                # Only allow the user to see reports and units from their own
                # organization
                org = request.user.account.organization
                self.matches = self.matches.filter(organization=org)
                self.user_units = self.request.user.account.get_dpo_units().order_by("name")

        else:
            raise Account.DoesNotExist(_("The user does not have an account."))

    def get(self, request, *args, **kwargs):
        self._check_access(request)

        response = super().get(request, *args, **kwargs)

        return response

    def get_context_data(self, number_of_months=12, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now()

        if (scannerjob := self.request.GET.get('scannerjob')) and scannerjob != 'all':
            self.matches = self.matches.filter(
                scanner_job_pk=scannerjob)

        if (orgunit := self.request.GET.get('orgunit')) and orgunit != 'all':
            confirmed_dpo = self.request.user.account.get_dpo_units().filter(uuid=orgunit).exists()
            if self.request.user.is_superuser or confirmed_dpo:
                selected_unit = self.user_units.get(uuid=orgunit)
                descendant_units = selected_unit.get_descendants(include_self=True)
                positions = Position.employees.filter(unit__in=descendant_units)
                accounts = Account.objects.filter(positions__in=positions).distinct()
                self.matches = self.matches.filter(
                    alias_relation__account__in=accounts).exclude(
                    alias_relation__shared=True)
            else:
                raise OrganizationalUnit.DoesNotExist(
                    _("An organizational unit with the UUID '{0}' was not found.".format(orgunit)))

        if self.scannerjob_filters is None:
            # Create select options
            self.scannerjob_filters = DocumentReport.objects.filter(
                number_of_matches__gte=1).order_by('scanner_job_pk').values(
                "scanner_job_name", "scanner_job_pk").distinct()

        (context['match_data'],
         source_type_data,
         context['resolution_status'],
         self.created_month,
         self.resolved_month) = self.make_data_structures(self.matches)

        context['unhandled_matches_by_month'] = \
            self.count_unhandled_matches_by_month(today, num_months=number_of_months)

        context['new_matches_by_month'] = \
            self.count_new_matches_by_month(today, num_months=number_of_months)

        # This is removed, until we make some structural changes, which should
        # prevent clients from having stupid amounts of organizational data.
        # if self.request.GET.get('orgunit') is None:
        #     highest_unhandled_ou, highest_handled_ou, highest_total_ou = (
        #         self.count_match_status_by_org_unit())

        #     context['matches_by_org_unit_unhandled'] = highest_unhandled_ou
        #     context['matches_by_org_unit_handled'] = highest_handled_ou
        #     context['matches_by_org_unit_total'] = highest_total_ou

        context['total_by_source'] = {}
        context['unhandled_by_source'] = {}

        for src_type, values in source_type_data.items():
            # The progress is calculated by subtracting the number of recently handled matches
            # from the number of recently created matches
            context[f'{src_type}_monthly_progress'] = \
                values['created_recent'] - values['handled_recent']

            context['total_by_source'][src_type] = {
                'label': values['label'], 'count': values['total']}
            context['unhandled_by_source'][src_type] = {
                'label': values['label'], 'count': values['unhandled']}

        context['scannerjobs'] = (self.scannerjob_filters,
                                  self.request.GET.get('scannerjob', 'all'))

        allowed_orgunits = self.user_units

        context['orgunits'] = (allowed_orgunits.order_by("name").values("name", "uuid"),
                               self.request.GET.get('orgunit', 'all'))

        return context

    def dispatch(self, request, *args, **kwargs):

        response = super().dispatch(request, *args, **kwargs)

        try:
            # Allow the user access, if they are a superuser or has a DPO relation
            # to at least one organizational unit.
            if request.user.is_superuser or request.user.account.is_dpo:
                return response
        except Exception as e:
            logger.warning("Exception raised while trying to dispatch to user "
                           f"{request.user}: {e}")
        return redirect(reverse_lazy('index'))

    def make_data_structures(self, matches):  # noqa C901, CCR001
        """To avoid making multiple separate queries to the DocumentReport
        table, we instead use the one call defined previously, then packages
        data into separate structures, which can then be used for statistical
        presentations."""

        handled_unhandled = {
            'handled': {'count': 0, 'label': _('handled')},
            'unhandled': {'count': 0, 'label': _('unhandled')},
        }

        resolution_status = {choice.value: {'label': choice.label, 'count': 0}
                             for choice in DocumentReport.ResolutionChoices}

        source_type = {
            'other': {'label': _('other source')},
            'webscan': {'label': _('web scan')},
            'filescan': {'label': _('file scan')},
            'mailscan': {'label': _('mail scan')},
            'teamsscan': {'label': _('Teams scan')},
            'calendarscan': {'label': _('calendar scan')},
        }
        for key in source_type.keys():
            for field in ['total', 'unhandled', 'created_recent', 'handled_recent']:
                source_type[key][field] = 0

        created_month = {}

        resolved_month = {}

        for obj in matches:
            count = obj.get('count', 0)
            match obj:
                case {'source_type': 'smb' | 'smbc' | 'msgraph-files' | 'googledrive'}:
                    source_category = 'filescan'
                case {'source_type': 'web'}:
                    source_category = 'webscan'
                case {'source_type': 'ews' | 'msgraph-mail' | 'mail' | 'gmail'}:
                    source_category = 'mailscan'
                case {'source_type': 'msgraph-teams-files'}:
                    source_category = 'teamsscan'
                case {'source_type': 'msgraph-calendar'}:
                    source_category = 'calendarscan'
                case _:
                    source_category = 'other'

            status = obj.get('resolution_status')
            key = 'handled' if status is not None else 'unhandled'

            source_type[source_category]['total'] += count
            source_type[source_category]['unhandled'] += count if key == 'unhandled' else 0
            source_type[source_category]['created_recent'] += count if obj.get(
                'created_recently') else 0
            source_type[source_category]['handled_recent'] += count if obj.get(
                'handled_recently') else 0

            if status is not None:
                resolution_status[status]['count'] += count
                month_resolved = obj['resolved_month']
                resolved_month[month_resolved] = resolved_month.get(month_resolved, 0) + count

            handled_unhandled[key]['count'] += count

            month_created = obj['created_month']
            created_month[month_created] = created_month.get(month_created, 0) + count

        return handled_unhandled, source_type, resolution_status, created_month, resolved_month

    def count_unhandled_matches_by_month(self, current_date, num_months=12):
        """Counts new matches and resolved matches by month for the last year,
        rotates the current month to the end of the list, inserts and subtracts using the counts
        and then makes a running total"""
        a_year_ago: date = (
                current_date - timedelta(days=365)).date().replace(day=1)

        new_matches_by_month = sort_by_keys(self.created_month)

        resolved_matches_by_month = sort_by_keys(self.resolved_month)

        if self.matches.exists():
            earliest_month = min(
                    key
                    for key in new_matches_by_month.keys() | resolved_matches_by_month.keys())
            # The range of the graph should be at least a year
            earliest_month = min(earliest_month, a_year_ago)
        else:
            # ... even if we don't have /any/ data at all
            earliest_month = a_year_ago
        number_of_months = 1 + month_delta(earliest_month, current_date)

        # This series needs to have a slot for every month, not just those in
        # which something actually happened
        delta_by_month: dict[date, int] = {
                earliest_month + relativedelta(months=k): 0
                for k in range(number_of_months)}

        for month, total in new_matches_by_month.items():
            delta_by_month[month] += total
        for month, total in resolved_matches_by_month.items():
            delta_by_month[month] -= total

        def _make_running_total():
            total = 0
            for month_start, delta in delta_by_month.items():
                total += delta
                yield month_start, total

        total_of_months = 0
        for _month_start, total in list(_make_running_total())[-num_months:]:
            total_of_months += total

        # If there are no matches, return empty list
        if total_of_months == 0:
            return []

        return [[month_abbr[month_start.month] + " " + str(month_start.year), total]
                for month_start, total in list(_make_running_total())[-num_months:]]

    def count_new_matches_by_month(self, current_date, num_months=12):
        """Counts matches by months for the last year
        and rotates them by the current month"""

        matches_by_month = sort_by_keys(self.created_month)

        # We only want data from the last <num_months> months
        cutoff_day = ((current_date - relativedelta(months=num_months-1)).replace(day=1)).date()
        earlier_months = [month for month in matches_by_month.keys() if month < cutoff_day]
        for month in earlier_months:
            del matches_by_month[month]

        a_year_ago: date = (
                current_date - timedelta(days=365)).date().replace(day=1)

        if self.matches.exists() and matches_by_month:
            earliest_month = min(
                    key
                    for key in matches_by_month.keys())
            # The range of the graph should be at least a year
            earliest_month = min(earliest_month, a_year_ago)
        else:
            # ... even if we don't have /any/ data at all
            earliest_month = a_year_ago
        number_of_months = 1 + month_delta(earliest_month, current_date)

        # This series needs to have a slot for every month, not just those in
        # which something actually happened
        matches_by_month: dict[date, int] = {
                (month := earliest_month + relativedelta(months=k)): matches_by_month.get(month, 0)
                for k in range(number_of_months)}

        # If there are no matches, return empty list
        if not any(total > 0 for total in matches_by_month.values()):
            return []

        labelled_values_by_month = list([month_abbr[month.month] + " " + str(month.year), total]
                                        for month, total in matches_by_month.items())

        return labelled_values_by_month[-num_months:]

    def count_match_status_by_org_unit(self):

        stats = OrganizationalUnit.objects.with_match_counts().filter(
            organization=self.request.user.account.organization
        ).values(
            "name", "total_ou_matches", "handled_ou_matches"
        )

        def get_matches(match_type):
            match match_type:
                case "unhandled":
                    props = ("name", "handled_ou_matches", "total_ou_matches")
                case "handled":
                    props = ("name", "handled_ou_matches")
                case "total":
                    props = ("name", "total_ou_matches")

            return [[ou.get(prop) for prop in props] for ou in stats]

        def sort_OU(array, match_type: str):
            def _key(x):
                match match_type, x:
                    case "unhandled", [_, handled_matches, match_count] if (
                            handled_matches is not None and match_count is not None):
                        return match_count - handled_matches
                    case "handled", [_, handled_matches] if handled_matches is not None:
                        return handled_matches
                    case "total", [_, match_count] if match_count is not None:
                        return match_count
                    case _:
                        return 0
            return sorted(array, key=_key)

        return tuple(list(reversed(sort_OU(get_matches(mt), match_type=mt)[-10:]))
                     for mt in ("unhandled", "handled", "total"))


class DPOStatisticsCSVView(CSVExportMixin, DPOStatisticsPageView):
    exported_filename = 'osdatascanner_dpo_statistics'

    def get(self, request, *args, **kwargs):
        if not settings.DPO_CSV_EXPORT:
            raise PermissionDenied

        self._check_access(request)

        # Adds scannername and orgunit to name of csv file
        scanner = None
        if (scanner_pk := request.GET.get('scannerjob')) and scanner_pk != 'all':
            scanner = DocumentReport.objects.filter(scanner_job_pk=scanner_pk).first()
        self.exported_filename += f"_scannerjob_{scanner.scanner_job_name}" if scanner else ''

        orgunit = None
        if (orgunit_id := request.GET.get('orgunit')) and orgunit_id != 'all':
            orgunit = self.user_units.get(uuid=orgunit_id)
        self.exported_filename += f"_orgunit_{orgunit.name}" if orgunit else ''

        # Gets Respone from CSVExportMixin
        response = super().get(request)

        return response

    def stream_queryset(self, rows):
        # Overwrites CSVExportMixin.stream_queryset
        self.prepare_stream()

        for row in rows:
            yield self.writer.writerow(row)

    def unpack_context_data(self):
        # Takes the data form get_context_data, and restructures it for use in get_rows
        context_data = self.get_context_data(number_of_months=100)

        match_data = [[values["label"], values["count"]]
                      for (_key, values) in context_data["match_data"].items()]
        source_types = [[values["label"], values["count"]]
                        for (_source, values) in context_data["total_by_source"].items()]
        resolution_status = [[values["label"], values["count"]]
                             for (_status, values) in context_data["resolution_status"].items()]

        monthly = []
        earlier_month = False
        for ([month_new, count_new], [month_unhandled, count_unhandled]) in zip(
                context_data["new_matches_by_month"], context_data["unhandled_matches_by_month"]):
            if (month_new != month_unhandled):
                logger.warning(
                    f"Unbalanced months in dpo-statisticsdata: {month_new} != {month_unhandled}")
                break

            if earlier_month or count_unhandled or count_new:
                # Only add month if it, or an earlier month, has matches
                earlier_month = True
                monthly.append([month_new, count_unhandled, count_new])

        return match_data, source_types, resolution_status, monthly

    def get_rows(self):
        # Since this isn't a ListView, the data isn't a queryset.
        # So CSVExportMixin.get_rows is overwritten,
        # and instead we unpack get_context_data manually

        match_data, source_types, resolutions, monthly = self.unpack_context_data()

        rows = []
        row_i = -1
        row = [_("Handled/Unhandled"), _("Matches by Handled/Unhandled"), _("Source Type"),
               _("Matches by Source Type"), _("Resolution Status"),
               _("Matches by Resolution Status"), _("Month"), _("Unhandled Matches by Month"),
               _("New Matches by Month")]

        # If latest row only contains empty cells, we're done
        while any(value != "" for value in row):
            rows.append(row)
            row_i += 1
            row = []

            # If a column doesn't contain any more data, make empty cells
            row.extend(match_data[row_i]) if row_i < len(match_data) else row.extend(["", ""])
            row.extend(source_types[row_i]) if row_i < len(source_types) else row.extend(["", ""])
            row.extend(resolutions[row_i]) if row_i < len(resolutions) else row.extend(["", ""])
            row.extend(monthly[row_i]) if row_i < len(monthly) else row.extend(["", "", ""])

        return rows


class LeaderStatisticsPageView(LoginRequiredMixin, ListView):
    template_name = "statistics.html"
    paginator_class = EmptyPagePaginator
    paginate_by = 200
    model = Account
    context_object_name = "employees"

    def get_queryset(self):
        qs = super().get_queryset()

        if self.org_unit:
            all_units = self.org_unit.get_descendants(include_self=True)
            positions = Position.employees.filter(unit__in=all_units)
            qs = qs.filter(positions__in=positions).distinct()
        else:
            qs = Account.objects.none()

        if search_field := self.request.GET.get('search_field', None):
            qs = qs.filter(
                Q(first_name__icontains=search_field) |
                Q(last_name__icontains=search_field) |
                Q(username__istartswith=search_field))

        qs = self.order_employees(qs)

        self.employee_count = qs.count()

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user_units'] = self.user_units

        context["org_unit"] = self.org_unit

        context["employee_count"] = self.employee_count

        context['order_by'] = self.request.GET.get('order_by', 'first_name')
        context['order'] = self.request.GET.get('order', 'ascending')

        return context

    def order_employees(self, qs):
        """Checks if a sort key is allowed and orders the employees queryset"""
        allowed_sorting_properties = [
            'first_name',
            'match_count',
            'match_status']
        if (sort_key := self.request.GET.get('order_by', 'first_name')) and (
                order := self.request.GET.get('order', 'ascending')):

            if sort_key not in allowed_sorting_properties:
                return

            if sort_key == "match_count":
                # Trigger recomputation of match_count by saving
                # all the objects again. FIXME FIXME FIXME!!!
                for acc in qs:
                    acc.save()

            if order != 'ascending':
                sort_key = '-'+sort_key
            qs = qs.order_by(sort_key, 'pk').distinct(
                sort_key if sort_key[0] != "-" else sort_key[1:], "pk")

        return qs

    def get(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            self.user_units = OrganizationalUnit.objects.all().order_by("name")
        else:
            self.user_units = self.request.user.account.get_managed_units().order_by("name")

        if unit_uuid := request.GET.get('org_unit', None):
            self.org_unit = self.user_units.get(uuid=unit_uuid)
        else:
            self.org_unit = self.user_units.first() or None

        response = super().get(request, *args, **kwargs)

        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_superuser and not request.user.account.is_manager:
                return HttpResponseForbidden(
                    "Only managers and superusers have access to this page.")
        return super(LeaderStatisticsPageView, self).dispatch(
            request, *args, **kwargs)


class UserStatisticsPageView(LoginRequiredMixin, DetailView):
    template_name = "statistics.html"
    model = Account
    context_object_name = "account"

    def get_object(self, queryset=None):
        if self.kwargs.get(self.pk_url_kwarg) is None:
            try:
                self.kwargs[self.pk_url_kwarg] = self.request.user.account.uuid
            except Account.DoesNotExist:
                raise Http404()
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        account = context["account"]
        matches_by_week = account.count_matches_by_week()
        context["matches_by_week"] = matches_by_week
        scannerjobs = (
            filter_inapplicable_matches(
                user=account.user,
                matches=DocumentReport.objects.filter(
                        number_of_matches__gte=1,
                        resolution_status__isnull=True
                    ),
                only_personal=True)
            .order_by(
                "scanner_job_pk"
            ).values(
                "scanner_job_pk",
                "scanner_job_name"
            ).annotate(
                total=Count("scanner_job_pk")
            ).values(
                "scanner_job_pk",
                "scanner_job_name",
                "total"
            ))
        context["scannerjobs"] = scannerjobs
        return context

    def post(self, request, *args, **kwargs):

        pk = kwargs.get("pk")
        self.verify_access(request.user, pk)

        scannerjob_pk = request.POST.get("pk")
        scannerjob_name = request.POST.get("name")
        account = Account.objects.get(pk=pk)

        reports = filter_inapplicable_matches(
            user=account.user,
            matches=DocumentReport.objects.filter(
                scanner_job_pk=scannerjob_pk,
                resolution_status__isnull=True,
                number_of_matches__gte=1),
            only_personal=True)

        response_string = _('You deleted all results from {0} associated with {1}.'.format(
                scannerjob_name, account.get_full_name()))

        reports.delete()

        response = HttpResponse(
            "<li>" +
            response_string +
            "</li>")

        response.headers["HX-Trigger"] = "reload-htmx"
        return response

    def get(self, request, *args, **kwargs):
        try:
            # If the URL has specified a primary key for the Account whose
            # statistics we want to see, then use that
            pk = kwargs.get("pk") or request.user.account.pk
        except Account.DoesNotExist:
            raise Http404()

        self.verify_access(request.user, pk)

        return super().get(request, *args, **kwargs)

    def verify_access(self, user, pk):
        target_account = get_object_or_404(Account, pk=pk)
        try:
            user_account = user.account
        except Account.DoesNotExist:
            user_account = None

        # (Note that accessing Account.user can't raise a DoesNotExist in the
        # way that User.account can, so we don't need to wrap this line)
        owned = target_account.user == user
        managed = user_account and target_account.managed_by(user_account)

        if user.is_superuser or owned or managed:
            return
        else:
            raise PermissionDenied


class EmployeeView(LoginRequiredMixin, DetailView):
    model = Account
    context_object_name = "employee"
    template_name = "components/statistics/employee_template.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.save()
        return response

# Logic separated to function to allow usability in send_notifications.py


def filter_inapplicable_matches(user, matches, account=None, only_personal=False):
    """ Filters matches by organization
    and role. """

    # Filter by organization
    try:
        user_organization = user.account.organization
        if user_organization:
            matches = matches.filter(organization=user_organization)
    except Account.DoesNotExist:
        # No Account has been set on the request user
        # Check if we have received an account as arg (from send_notifications.py) and use
        # its organization to locate matches.
        if account:
            matches = matches.filter(organization=account.organization)

    if not only_personal and user.is_superuser:
        hidden_matches = matches.filter(only_notify_superadmin=True)
        user_matches = matches.filter(
            alias_relation__in=user.aliases.exclude(_alias_type=AliasType.REMEDIATOR),
            only_notify_superadmin=False)

        matches_all = hidden_matches | user_matches
    elif only_personal:
        matches_all = matches.filter(
            alias_relation__in=user.aliases.exclude(
                _alias_type=AliasType.REMEDIATOR, shared=True),
            only_notify_superadmin=False)
    else:
        matches_all = matches.filter(
            alias_relation__in=user.aliases.exclude(_alias_type=AliasType.REMEDIATOR),
            only_notify_superadmin=False)

    if not only_personal and user.account.is_remediator:
        matches = matches.filter(
            alias_relation__in=user.aliases.all(),
            only_notify_superadmin=False)
    else:
        matches = matches_all

    return matches


def sort_by_keys(d: dict) -> dict:
    return dict(sorted(d.items(), key=lambda t: t[0]))


month_abbr = {1: _("Jan"), 2: _("Feb"), 3: _("Mar"), 4: _("Apr"),
              5: _("May"), 6: _("Jun"), 7: _("Jul"), 8: _("Aug"),
              9: _("Sep"), 10: _("Oct"), 11: _("Nov"), 12: _("Dec")}
