# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from django.db.models import Case, Count, DateField, F, Q, When
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ...models.documentreport import DocumentReport
from ....organizations.models.account import Account
from ....organizations.models.organizational_unit import OrganizationalUnit
from ....organizations.models.position import Position


def month_delta(series_start: date, here: date):
    """Returns the (zero-based) month index of @here relative to
    @series_start."""

    def _months(date: date):
        return date.year * 12 + date.month

    return _months(here) - _months(series_start)


def sort_by_keys(d: dict) -> dict:
    return dict(sorted(d.items(), key=lambda t: t[0]))


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
                    ).annotate(count=Count('pk', distinct=True)).order_by()


def filter_by_unit(reports, unit: OrganizationalUnit):
    descendant_units = unit.get_descendants(include_self=True)
    positions = Position.employees.filter(unit__in=descendant_units)
    accounts = Account.objects.filter(positions__in=positions).distinct()

    return (
        reports.annotate(
            total_relations=Count(
                'alias_relations',
                distinct=True
            ),
            shared_relations=Count(
                'alias_relations',
                filter=Q(alias_relations__shared=True),
                distinct=True
            )
        )
        # Ensure at least one relation is to these accounts
        .filter(alias_relations__account__in=accounts)
        # Keep only if not all relations are shared (i.e., at least one is not shared)
        .filter(~Q(total_relations=F('shared_relations')))
    )


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
