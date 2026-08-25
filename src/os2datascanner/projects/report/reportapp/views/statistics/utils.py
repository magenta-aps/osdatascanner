# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import structlog

from abc import abstractmethod, ABC
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.conf import settings
from django.db.models import Case, Count, DateField, Exists, OuterRef, QuerySet, When
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ...models.documentreport import DocumentReport
from ...models.scanner_reference import ScannerReference
from ....organizations.models.account import Account
from ....organizations.models.aliases import Alias
from ....organizations.models.organizational_unit import OrganizationalUnit
from ....organizations.models.position import Position
from .....utils.view_mixins import CSVExportMixin


logger = structlog.get_logger("reportapp")


month_abbr = {1: _("Jan"), 2: _("Feb"), 3: _("Mar"), 4: _("Apr"),
              5: _("May"), 6: _("Jun"), 7: _("Jul"), 8: _("Aug"),
              9: _("Sep"), 10: _("Oct"), 11: _("Nov"), 12: _("Dec")}


def base_query():
    placeholder_time = timezone.make_aware(timezone.datetime(1970, 1, 1))
    today = timezone.now()
    a_month_ago = today - timedelta(days=30)

    return DocumentReport.objects.filter(number_of_matches__gte=1).annotate(
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
                resolution_status__isnull=False,
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
                    ).annotate(count=Count('pk')).order_by()


def accounts_under_units(units: QuerySet[OrganizationalUnit]) -> QuerySet[Account]:
    """Returns the Accounts holding an employee position in any of @units or
    in any of their descendant units."""
    descendant_units = units.get_descendants()
    positions = Position.employees.filter(unit__in=descendant_units)
    return Account.objects.filter(positions__in=positions).distinct()


def filter_by_accounts(
        reports: QuerySet[DocumentReport], accounts: QuerySet[Account]) -> QuerySet[DocumentReport]:
    """Restricts @reports to those with a relation to one of @accounts, but
    excludes reports whose only relations are shared aliases (e.g. a shared
    mailbox or universal remediator) -- shared-only isn't a personal match."""
    # Both conditions are EXISTS semi-joins rather than joins on the
    # multi-valued alias_relations, so a report is never multiplied into the
    # aggregation - which is what lets base_query count without DISTINCT.
    return reports.filter(
        # Related to at least one account in @accounts.
        Exists(Alias.objects.filter(reports=OuterRef('pk'), account__in=accounts)),
        # Not related only through shared aliases (has a non-shared relation).
        Exists(Alias.objects.filter(reports=OuterRef('pk'), shared=False)),
    )


def filter_by_unit(
        reports: QuerySet[DocumentReport], unit: OrganizationalUnit) -> QuerySet[DocumentReport]:
    """Like filter_by_accounts(), but scoped to the Accounts employed in
    @unit or any of its descendant units."""
    descendant_units = unit.get_descendants(include_self=True)
    positions = Position.employees.filter(unit__in=descendant_units)
    accounts = Account.objects.filter(positions__in=positions).distinct()

    return filter_by_accounts(reports, accounts)


def month_delta(series_start: date, here: date):
    """Returns the (zero-based) month index of @here relative to
    @series_start."""

    def _months(date: date):
        return date.year * 12 + date.month

    return _months(here) - _months(series_start)


def sort_by_keys(d: dict) -> dict:
    return dict(sorted(d.items(), key=lambda t: t[0]))


def count_new_matches_by_month(matches, created_month: dict,
                               current_date=timezone.now(), num_months=12):
    """Counts matches by months for the last year
    and rotates them by the current month

    The "created_month" input variable should contain a dict on the form:

    {
        <date>: <count>,
        <date>: <count>,
        ...
    }"""

    matches_by_month = sort_by_keys(created_month)

    # We only want data from the last <num_months> months
    cutoff_day = ((current_date - relativedelta(months=num_months-1)).replace(day=1)).date()
    earlier_months = [month for month in matches_by_month.keys() if month < cutoff_day]
    for month in earlier_months:
        del matches_by_month[month]

    a_year_ago: date = (
            current_date - timedelta(days=365)).date().replace(day=1)

    if matches.exists() and matches_by_month:
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


def count_unhandled_matches_by_month(matches, created_month: dict, resolved_month: dict,
                                     current_date=timezone.now(), num_months=12):
    """Counts new matches and resolved matches by month for the last year,
    rotates the current month to the end of the list, inserts and subtracts using the counts
    and then makes a running total.

    The "created_month" and "resolved_month" input variables should contain dicts on the form:

    {
        <date>: <count>,
        <date>: <count>,
        ...
    }"""
    a_year_ago: date = (
            current_date - timedelta(days=365)).date().replace(day=1)

    new_matches_by_month = sort_by_keys(created_month)

    resolved_matches_by_month = sort_by_keys(resolved_month)

    if matches.exists():
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


def make_data_structures(matches):  # noqa C901, CCR001
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
        'other':        {'label': _('other source')},
        'webscan':      {'label': _('web scan')},
        'filescan':     {'label': _('file scan')},
        'mailscan':     {'label': _('mail scan')},
        'teamsscan':    {'label': _('Teams scan')},
        'sbsys_db':     {'label': _('SBSYS scan')},
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
            case {'source_type': 'msgraph-calendar' | 'ews-calendar'}:
                source_category = 'calendarscan'
            case {'source_type': 'sbsys-db'}:
                source_category = 'sbsys_db'
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


def source_type_progress(source_type_data: dict):
    progress_dict = {}
    progress_dict["total_by_source"] = {}
    progress_dict["unhandled_by_source"] = {}

    for src_type, values in source_type_data.items():
        # The progress is calculated by subtracting the number of recently handled matches
        # from the number of recently created matches
        progress_dict[f'{src_type}_monthly_progress'] = \
            values['created_recent'] - values['handled_recent']

        progress_dict['total_by_source'][src_type] = {
            'label': values['label'], 'count': values['total']}
        progress_dict['unhandled_by_source'][src_type] = {
            'label': values['label'], 'count': values['unhandled']}

    return progress_dict


class ResultsStatisticsPageView(LoginRequiredMixin, TemplateView, ABC):
    """Shared scaffolding for the DPO and leader-results statistics pages:
    both render aggregate charts over a base_query() queryset, scoped to a
    unit chosen via ?orgunit= (or a subclass-specific default scope
    otherwise).

    Subclasses implement _get_own_units(); _confirm_orgunit_access(),
    _default_scope_accounts(), _extra_context() and _scannerjob_choices()
    are optional overrides for page-specific access rules and context."""

    context_object_name = "matches"  # object_list renamed to something more relevant
    model = DocumentReport
    scannerjob_filters = None

    @abstractmethod
    def _get_own_units(self):
        """The organizational units this (non-superuser) user has access to,
        before ordering."""

    def _confirm_orgunit_access(self, orgunit_uuid):
        """Whether the user may filter down to @orgunit_uuid. Defaults to
        checking self.user_units; override when access is broader than that
        set implies (see DPOStatisticsPageView's universal-DPO case)."""
        return self.user_units.filter(uuid=orgunit_uuid).exists()

    def _default_scope_accounts(self):
        """The Accounts to scope matches to when no ?orgunit= is chosen, or
        None for no extra scoping (the whole organization); override to
        restrict further."""
        return None

    def _extra_context(self, context):
        """Hook for subclass-specific context keys. No-op by default."""
        return context

    def _scannerjob_choices(self, org, accounts):
        """Scannerjob dropdown options for the current scope (@accounts is
        None when unscoped). Defaults to every scanner in @org (or every
        scanner, for a superuser); override to narrow further."""
        return org.scanners.all() if org else ScannerReference.objects.all()

    def _check_access(self, request):
        if not self.request.user.account:
            raise Account.DoesNotExist(_("The user does not have an account."))

        if self.request.user.is_superuser:
            self.user_units = OrganizationalUnit.objects.all().order_by("name")
        else:
            # Only allow the user to see reports and units from their own
            # organization
            org = request.user.account.organization
            self.kwargs["org"] = org
            self.matches = self.matches.filter(scanner_job__organization=org)
            self.user_units = self._get_own_units().order_by("name")

    def get(self, request, *args, **kwargs):
        self.matches = base_query()

        self._check_access(request)

        response = super().get(request, *args, **kwargs)

        return response

    def get_context_data(self, number_of_months=12, **kwargs):  # noqa CCR001
        context = super().get_context_data(**kwargs)
        today = timezone.now()

        accounts = None
        if (orgunit := self.request.GET.get('orgunit')) and orgunit != 'all':
            if self.request.user.is_superuser or self._confirm_orgunit_access(orgunit):
                accounts = accounts_under_units(self.user_units.filter(uuid=orgunit))
            else:
                raise OrganizationalUnit.DoesNotExist(
                    _("An organizational unit with the UUID '{0}' was not found.".format(orgunit)))
        elif not self.request.user.is_superuser:
            accounts = self._default_scope_accounts()

        if accounts is not None:
            self.matches = filter_by_accounts(self.matches, accounts)

        if self.scannerjob_filters is None:
            self.scannerjob_filters = self._scannerjob_choices(self.kwargs.get("org"), accounts)

        if (scannerjob := self.request.GET.get('scannerjob')) and scannerjob != 'all':
            self.matches = self.matches.filter(
                scanner_job__scanner_pk=scannerjob)

        (context['match_data'],
         source_type_data,
         context['resolution_status'],
         created_month,
         resolved_month) = make_data_structures(self.matches)

        context['unhandled_matches_by_month'] = \
            count_unhandled_matches_by_month(self.matches, created_month,
                                             resolved_month, current_date=today,
                                             num_months=number_of_months)

        context['new_matches_by_month'] = \
            count_new_matches_by_month(self.matches, created_month,
                                       current_date=today, num_months=number_of_months)

        context = context | source_type_progress(source_type_data)

        context['scannerjob_choices'] = self.scannerjob_filters
        context['chosen_scannerjob'] = self.request.GET.get('scannerjob', 'all')

        allowed_orgunits = self.user_units.filter(hidden=False)

        context['orgunit_choices'] = allowed_orgunits.order_by("name").values("name", "uuid")
        context['chosen_orgunit'] = self.request.GET.get('orgunit', 'all')

        return self._extra_context(context)


class StatisticsCSVExportMixin(CSVExportMixin):
    """Shared CSV-export behaviour for the DPO and leader-results statistics
    pages: identical context data and row layout, differing only in which
    feature flag gates the export and what filename prefix is used.
    Subclasses set @exported_filename and @feature_flag_setting (the
    settings attribute name that gates this export)."""

    feature_flag_setting = None

    def get(self, request, *args, **kwargs):
        if not getattr(settings, self.feature_flag_setting):
            raise PermissionDenied

        self.matches = base_query()

        self._check_access(request)

        # Adds scannername and orgunit to name of csv file
        scanner = None
        if (scanner_pk := request.GET.get('scannerjob')) and scanner_pk != 'all':
            if ScannerReference.objects.filter(scanner_pk=scanner_pk).exists():
                scanner = ScannerReference.objects.get(scanner_pk=scanner_pk)
            else:
                logger.debug("Scanner doesn't exists", scanner_pk=scanner_pk)
        self.exported_filename += f"_scannerjob_{scanner.scanner_name}" if scanner else ''

        orgunit = None
        if (orgunit_id := request.GET.get('orgunit')) and orgunit_id != 'all':
            orgunit = self.user_units.get(uuid=orgunit_id)
        self.exported_filename += f"_orgunit_{orgunit.name}" if orgunit else ''

        # Gets Response from CSVExportMixin
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
                    f"Unbalanced months in {self.exported_filename} data: "
                    f"{month_new} != {month_unhandled}")
                break

            if earlier_month or count_unhandled or count_new:
                # Only add month if it, or an earlier month, has matches
                earlier_month = True
                monthly.append([month_new, count_unhandled, count_new])

        return match_data, source_types, resolution_status, monthly

    def get_rows(self, qs=None):
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
