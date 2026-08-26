#!/usr/bin/env python
# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from abc import abstractmethod, ABC

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.aggregates import StringAgg
from django.core.exceptions import PermissionDenied
from django.db.models import (Q, When, Case, CharField, Value, F, Subquery, OuterRef, Sum,
                              IntegerField, FloatField, ExpressionWrapper)
from django.db.models.functions import Coalesce
from django.http import HttpResponseForbidden
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, RedirectView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.conf import settings

from .utils import accounts_under_units, ResultsStatisticsPageView, StatisticsCSVExportMixin
from ...models.documentreport import DocumentReport
from ...models.scanner_reference import ScannerReference
from ...models.leader_statistic_snapshot import LeaderStatisticSnapshot, AccountResultSnapshot
from ....organizations.models.account import Account, StatusChoices
from ....organizations.models.position import Position
from ....organizations.models.organizational_unit import OrganizationalUnit
from ......core_organizational_structure.models.organization import LeaderTabConfigChoices
from .....utils.view_mixins import CSVExportMixin


class LeaderStatisticsRedirectView(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        org = self.request.user.account.organization
        if org.leadertab_config in [LeaderTabConfigChoices.UNITS, LeaderTabConfigChoices.BOTH]:
            return reverse_lazy("statistics-leader-units")
        elif org.leadertab_config == LeaderTabConfigChoices.ACCOUNTS:
            return reverse_lazy("statistics-leader-accounts")
        else:
            raise PermissionDenied(f"An incorrect setting was found on the organization {org}!")


class LeaderStatisticsPageView(LoginRequiredMixin, TemplateView, ABC):
    template_name = "leader_statistics_template.html"
    max_objects = 200

    @abstractmethod
    def get_account_queryset(self):
        """Override this in child classes"""

    @staticmethod
    def annotate_account_queryset(qs, reports=None, retention_days=None):

        # This might be optimization for nobody, but there's no reason to do further queries
        # if the account_qs is empty here. It'll add a lot of overhead to display an empty page.
        if qs:
            qs = qs.with_result_stats(reports=reports,
                                      retention_policy=retention_days)
            qs = qs.with_status()
            qs = qs.with_fp_ratio()
        else:
            # Tests require these fields though, so we'll just set them to zero, we really
            # don't want to attempt any calculations we know will yield nothing.
            qs = Account.objects.none().annotate(
                old_results=Value(0),
                unhandled_results=Value(0),
                withheld_results=Value(0),
            )

        return qs

    @staticmethod
    def annotate_account_queryset_from_snapshot(qs, snapshot_ids, scanner_pk=None,
                                                source_type=None):
        """Annotates an account queryset with the same fields as
        annotate_account_queryset, but reads the pre-aggregated
        AccountResultSnapshot rows of @snapshot_ids instead of computing the
        aggregates live.

        @snapshot_ids is the set of snapshots to read from — normally the latest
        snapshot per organization, so each account is summed from its own
        organization's snapshot (the live aggregation likewise scopes each
        account's counts to its own organization, which matters when a superuser
        views accounts across several organizations).

        Known limitation: an account whose organization has no snapshot in
        @snapshot_ids (a brand-new organization not yet reached by the cron, or
        one with snapshotting disabled) sums to zero here. This only surfaces for
        a superuser viewing accounts across organizations; an ordinary leader
        sees a single organization, which either has a snapshot (all its accounts
        are covered) or falls back to the live aggregation in get_context_data.

        The result counts (unhandled/withheld/old) are summed over the buckets
        matching the current scannerjob/source_type filter, mirroring the live
        with_result_stats(reports=...). 'handle_status' and 'fp_ratio' are summed
        over ALL of the account's buckets, mirroring the live with_status() and
        with_fp_ratio(), which are never scoped to the filter."""
        all_detail = AccountResultSnapshot.objects.filter(
            snapshot_id__in=snapshot_ids, account=OuterRef("pk"))
        filtered_detail = all_detail
        if scanner_pk and scanner_pk != "all":
            filtered_detail = filtered_detail.filter(scanner_job__scanner_pk=scanner_pk)
        if source_type and source_type != "all":
            filtered_detail = filtered_detail.filter(source_type=source_type)

        def summed(detail, field):
            return Coalesce(
                Subquery(
                    detail.values("account").annotate(_s=Sum(field)).values("_s")[:1],
                    output_field=IntegerField()),
                0)

        qs = qs.annotate(
            unhandled_results=summed(filtered_detail, "unhandled_results"),
            withheld_results=summed(filtered_detail, "withheld_results"),
            old_results=summed(filtered_detail, "old_results"),
            _unhandled_all=summed(all_detail, "unhandled_results"),
            _handled_recent=summed(all_detail, "handled_recent"),
            _new_recent=summed(all_detail, "new_recent"),
            _handled_total=summed(all_detail, "handled_total"),
            _fp_total=summed(all_detail, "fp_total"),
        )
        qs = qs.annotate(
            handle_status=Case(
                When(_unhandled_all=0, then=Value(StatusChoices.GOOD)),
                When(_handled_recent=0, then=Value(StatusChoices.BAD)),
                When(Q(_new_recent__gt=0)
                     & Q(_handled_recent__lt=F("_new_recent") * 0.75),
                     then=Value(StatusChoices.BAD)),
                default=Value(StatusChoices.OK),
                output_field=IntegerField()),
            fp_ratio=Case(
                When(_handled_total__gt=0,
                     then=F("_fp_total") * 1.0 / F("_handled_total")),
                default=0.0,
                output_field=FloatField()),
        )
        return qs.annotate(
            fp_percentage=ExpressionWrapper(
                F("fp_ratio") * 100, output_field=FloatField()))

    @staticmethod
    def latest_snapshot_ids():
        """The primary key of the most recent snapshot of each organization, so
        every account can be read from its own organization's snapshot."""
        return list(
            LeaderStatisticSnapshot.objects
            .order_by("organization_id", "-created_at")
            .distinct("organization_id")
            .values_list("pk", flat=True))

    @staticmethod
    def snapshot_scanner_ids(snapshot_ids, base_qs):
        """The scanner_job ids that produced matches for @base_qs accounts,
        read from the snapshot instead of joining through every report."""
        return (AccountResultSnapshot.objects
                .filter(snapshot_id__in=snapshot_ids, account__in=base_qs)
                .values_list("scanner_job_id", flat=True).distinct())

    def get_context_data(self, **kwargs):  # noqa CCR001
        context = super().get_context_data(**kwargs)
        base_qs = self.get_account_queryset()

        scanner_pk_filter = None
        if (self.request.user.has_perm('organizations.filter_scannerjob_leader_overview') and
                (scanner_pk := self.request.GET.get('scannerjob')) and scanner_pk != "all"):
            sr = get_object_or_404(ScannerReference, scanner_pk=scanner_pk)
            reports = sr.document_reports.all()
            scanner_pk_filter = scanner_pk
        else:
            reports = DocumentReport.objects.all()

        # Serve the leader overview from the most recent snapshot; fall back to
        # the (much slower) live aggregation when the organization has disabled
        # snapshotting (interval 0) or has no snapshot yet. self.snapshot_ids is
        # exposed for the subclasses' scannerjob dropdowns; None signals the
        # live fallback.
        snapshot = None
        if self.org.leader_snapshot_interval:
            snapshot = LeaderStatisticSnapshot.objects.filter(
                organization=self.org).order_by('-created_at').first()
        self.snapshot_ids = self.latest_snapshot_ids() if snapshot is not None else None

        if self.snapshot_ids is not None:
            snapshot_buckets = AccountResultSnapshot.objects.filter(
                snapshot_id__in=self.snapshot_ids, account__in=base_qs)
            if scanner_pk_filter:
                snapshot_buckets = snapshot_buckets.filter(
                    scanner_job__scanner_pk=scanner_pk_filter)
            source_type_choices = snapshot_buckets.order_by(
                'source_type').values('source_type').distinct()
        else:
            source_type_choices = reports.filter(
                alias_relations__account__in=base_qs,
                alias_relations__shared=False,
                number_of_matches__gte=1,
            ).order_by('source_type').values('source_type').distinct()
        context['source_type_choices'] = source_type_choices

        source_type = self.request.GET.get('source_type', 'all')
        if source_type != 'all':
            if source_type_choices.filter(source_type=source_type).exists():
                reports = reports.filter(source_type=source_type)
            else:
                source_type = 'all'

        retention_days = self.org.retention_days if self.org.retention_policy else None

        if self.snapshot_ids is not None:
            qs = self.annotate_account_queryset_from_snapshot(
                base_qs, self.snapshot_ids,
                scanner_pk=scanner_pk_filter, source_type=source_type)
        else:
            qs = self.annotate_account_queryset(base_qs, reports, retention_days)
        context['snapshot_created_at'] = snapshot.created_at if snapshot else None

        if self.request.GET.get('only_with_results'):
            qs = qs.filter(unhandled_results__gt=0)

        qs = self.order_employees(qs)
        context["employees"] = qs[:self.max_objects]
        context["base_qs"] = base_qs

        context['order_by'] = self.request.GET.get('order_by', 'first_name')
        context['order'] = self.request.GET.get('order', 'ascending')
        context['show_retention_column'] = self.org.retention_policy
        context['show_withheld_column'] = self.request.user.has_perm(
            "organizations.view_withheld_results")
        context['retention_days'] = self.org.retention_days
        context['show_units_tab'] = self.org.leadertab_config in [
            LeaderTabConfigChoices.UNITS, LeaderTabConfigChoices.BOTH]
        context['show_accounts_tab'] = self.org.leadertab_config in [
            LeaderTabConfigChoices.ACCOUNTS, LeaderTabConfigChoices.BOTH]
        context['chosen_scannerjob'] = self.request.GET.get('scannerjob', 'all')
        context['chosen_source_type'] = source_type
        context['only_with_results'] = self.request.GET.get('only_with_results')
        context['2org_fp_rate'] = 2 * self.org.false_positive_rate
        context['max_objects'] = self.max_objects

        # Determine number of columns from context
        context['num_cols'] = 4 + context['show_retention_column'] + self.request.user.has_perm(
            "organizations.view_withheld_results")

        return context

    def order_employees(self, qs):
        """Checks if a sort key is allowed and orders the employees queryset"""
        allowed_sorting_properties = [
            'first_name',
            'unhandled_results',
            'withheld_results',
            'old_results',
            'handle_status']
        if (sort_key := self.request.GET.get('order_by', 'first_name')) and (
                order := self.request.GET.get('order', 'ascending')):

            if sort_key not in allowed_sorting_properties:
                return

            if order != 'ascending':
                sort_key = '-'+sort_key
            qs = qs.order_by(sort_key, 'pk')

        return qs

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_superuser and not request.user.account.is_manager:
                return HttpResponseForbidden(
                    "Only managers and superusers have access to this page.")
        self.org = request.user.account.organization
        return super(LeaderStatisticsPageView, self).dispatch(
            request, *args, **kwargs)


class LeaderAccountsStatisticsPageView(LeaderStatisticsPageView):

    def get_account_queryset(self):
        account_qs = self.request.user.account.managed_accounts.all()
        if search_field := self.request.GET.get('search_field', None):
            account_qs = account_qs.filter(
                Q(first_name__icontains=search_field) |
                Q(last_name__icontains=search_field) |
                Q(username__istartswith=search_field))

        return account_qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_tab"] = "accounts"
        context["view_url"] = reverse_lazy("statistics-leader-accounts")
        context["export_url"] = reverse_lazy("statistics-leader-accounts-export")
        if self.snapshot_ids is not None:
            scannerjobs = self.org.scanners.filter(
                pk__in=self.snapshot_scanner_ids(self.snapshot_ids, context['base_qs']))
        else:
            scannerjobs = self.org.scanners.filter(
                document_reports__number_of_matches__gte=1,
                document_reports__alias_relations__account__in=context['base_qs'],
                document_reports__alias_relations__shared=False,
            ).distinct()
        if not self.request.user.has_perm(
                "organizations.view_withheld_results"):
            scannerjobs = scannerjobs.exclude(only_notify_superadmin=True).exclude(
                document_reports__only_notify_remediators=True)

        context['scannerjob_choices'] = scannerjobs

        return context

    def get(self, request, *args, **kwargs):
        org = request.user.account.organization
        if org.leadertab_config not in [LeaderTabConfigChoices.ACCOUNTS,
                                        LeaderTabConfigChoices.BOTH]:
            return redirect(reverse_lazy("statistics-leader"))
        else:
            return super().get(request, *args, **kwargs)


class LeaderUnitsStatisticsPageView(LeaderStatisticsPageView):

    def get_account_queryset(self):
        qs = Position.employees.all().distinct("account")
        qs = self.filter_positions(qs)

        if search_field := self.request.GET.get('search_field', None):
            qs = qs.filter(
                Q(account__first_name__icontains=search_field) |
                Q(account__last_name__icontains=search_field) |
                Q(account__username__istartswith=search_field))

        account_qs = Account.objects.filter(pk__in=qs.values_list("account", flat=True))
        return account_qs

    def filter_positions(self, qs):
        if self.request.GET.get("org_unit") == 'all':
            self.descendant_units = self.user_units.get_descendants()
            qs = qs.filter(unit__in=self.descendant_units)
        elif self.org_unit:
            # Note that AL_Node.get_descendants returns a list _not_ a queryset.
            self.descendant_units = self.org_unit.get_descendants(include_self=True)
            qs = qs.filter(unit__in=self.descendant_units)
        else:
            self.descendant_units = OrganizationalUnit.objects.none()
            qs = Position.objects.none()

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_tab"] = "units"
        context['user_units'] = self.user_units.filter(hidden=False)
        context["org_unit"] = self.org_unit
        context["view_url"] = reverse_lazy("statistics-leader-units")
        context["export_url"] = reverse_lazy("statistics-leader-units-export")

        if self.snapshot_ids is not None:
            scannerjobs = self.org.scanners.filter(
                Q(org_units__in=self.descendant_units)
                | Q(pk__in=self.snapshot_scanner_ids(self.snapshot_ids, context['base_qs']))
            ).distinct()
        else:
            scannerjobs = self.org.scanners.filter(
                Q(org_units__in=self.descendant_units)
                | Q(
                    document_reports__number_of_matches__gte=1,
                    document_reports__alias_relations__account__in=context['base_qs'],
                    document_reports__alias_relations__shared=False,
                )
            ).distinct()
        if not self.request.user.has_perm(
                "organizations.view_withheld_results"):
            scannerjobs = scannerjobs.exclude(only_notify_superadmin=True).exclude(
                document_reports__only_notify_remediators=True)

        context['scannerjob_choices'] = scannerjobs

        return context

    def set_user_units_and_org_unit(self, request):
        if self.request.user.is_superuser:
            self.user_units = OrganizationalUnit.objects.all().order_by("name")
        else:
            self.user_units = self.request.user.account.get_managed_units().order_by("name")

        unit_uuid = request.GET.get('org_unit', None)
        if unit_uuid and unit_uuid != 'all':
            self.org_unit = self.user_units.get(uuid=unit_uuid)
        elif unit_uuid == 'all':
            self.org_unit = None
        else:
            self.org_unit = self.user_units.first() or None

    def get(self, request, *args, **kwargs):
        org = request.user.account.organization
        if org.leadertab_config not in [LeaderTabConfigChoices.UNITS,
                                        LeaderTabConfigChoices.BOTH]:
            return redirect(reverse_lazy("statistics-leader"))
        else:
            self.set_user_units_and_org_unit(request)
            response = super().get(request, *args, **kwargs)

            return response


class LeaderStatisticsCSVMixin(CSVExportMixin):
    columns = [
        {
            'name': 'first_name',
            'label': _("First name"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
        {
            'name': 'last_name',
            'label': _("Last name"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
        {
            'name': 'username',
            'label': _("Username"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
        {
            'name': 'unhandled_results',
            'label': _("Matches"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
        {
            'name': 'handle_status',
            'label': _("Status"),
            'type': CSVExportMixin.ColumnType.FUNCTION,
            'function': lambda acc: StatusChoices(acc.handle_status).label,
        },
    ]
    exported_filename = 'os2datascanner_leaderpage_statistics'
    max_objects = None

    def order_employees(self, qs):
        # Overriding order_employees of parent class, because it is super slow.
        # The user can always sort the data themselves in their own spreadsheet editor
        return qs

    def add_conditional_colums(self, request):
        columns = self.columns.copy()
        if self.request.user.has_perm("organizations.view_withheld_results"):
            columns = columns + [{
                'name': 'withheld_results',
                'label': _("Withheld matches"),
                'type': CSVExportMixin.ColumnType.FIELD,
            }]

        if self.org.retention_policy:
            # Don't use '.append()' to avoid shallow copies
            columns = columns + [{
                    'name': 'old_results',
                    'label': _("Results older than %(days)s days") % {"days": self.org.retention_days},  # noqa
                    'type': CSVExportMixin.ColumnType.FIELD,
                }]
        self.columns = columns

    def get(self, request, *args, **kwargs):
        if not settings.LEADER_CSV_EXPORT:
            raise PermissionDenied
        response = super().get(request, *args, **kwargs)
        return response

    def get_rows(self, qs=None):
        # Since this isn't a ListView, there's no get_queryset method.
        # So CSVExportMixin.get_rows is overwritten

        scanner_pk_filter = None
        if (self.request.user.has_perm('organizations.filter_scannerjob_leader_overview') and
                (scanner_pk := self.request.GET.get('scannerjob')) and scanner_pk != "all"):
            sr = get_object_or_404(ScannerReference, scanner_pk=scanner_pk)
            reports = sr.document_reports.all()
            scanner_pk_filter = scanner_pk
        else:
            reports = DocumentReport.objects.all()

        source_type = self.request.GET.get('source_type', 'all')
        if source_type and source_type != 'all':
            reports = reports.filter(source_type=source_type)

        retention_days = self.org.retention_days if self.org.retention_policy else None
        account_qs = self.get_account_queryset()

        snapshot = None
        if self.org.leader_snapshot_interval:
            snapshot = LeaderStatisticSnapshot.objects.filter(
                organization=self.org).order_by('-created_at').first()
        if snapshot is not None:
            account_qs = LeaderStatisticsPageView.annotate_account_queryset_from_snapshot(
                account_qs, LeaderStatisticsPageView.latest_snapshot_ids(),
                scanner_pk=scanner_pk_filter, source_type=source_type)
        else:
            account_qs = LeaderStatisticsPageView.annotate_account_queryset(
                qs=account_qs, reports=reports, retention_days=retention_days
            )

        if self.request.GET.get('only_with_results'):
            account_qs = account_qs.filter(unhandled_results__gt=0)

        account_qs = self.order_employees(account_qs)

        if hasattr(self, "descendant_units"):
            # descendant_units is only available (and relevant), when using the
            # unit based overview - not when it's Account / manager based.
            account_qs = account_qs.annotate(
                unit_list=Coalesce(
                    StringAgg(
                        'units__name',
                        delimiter=', ',
                        ordering='units__name',
                        output_field=CharField(),
                        filter=Q(units__in=self.descendant_units),
                        distinct=True,
                    ),
                    Value('')
                )
            )

        return super().get_rows(account_qs)


class LeaderAccountsStatisticsCSVView(LeaderStatisticsCSVMixin, LeaderAccountsStatisticsPageView):
    pass


class LeaderUnitsStatisticsCSVView(LeaderStatisticsCSVMixin, LeaderUnitsStatisticsPageView):
    columns = [
        {
            'name': 'first_name',
            'label': _("First name"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
        {
            'name': 'last_name',
            'label': _("Last name"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
        {
            'name': 'username',
            'label': _("Username"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
        {
            'name': 'unhandled_results',
            'label': _("Matches"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
        {
            'name': 'handle_status',
            'label': _("Status"),
            'type': CSVExportMixin.ColumnType.FUNCTION,
            'function': lambda acc: StatusChoices(acc.handle_status).label,
        },
    ]

    def __init__(self, *args, **kwargs):
        self.columns = self.columns + [
            {
                'name': 'unit_list',
                'label': _("Organizational units"),
                'type': CSVExportMixin.ColumnType.FIELD,
            },
        ]
        return super().__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.set_user_units_and_org_unit(request)
        return super().get(request, *args, **kwargs)


class LeaderResultsStatisticsPageView(ResultsStatisticsPageView):
    template_name = "leader_results_statistics_template.html"

    def _get_own_units(self):
        return self.request.user.account.get_managed_units()

    def _default_scope_accounts(self):
        # No unit chosen: aggregate the leader's managed units plus any
        # accounts they manage directly (the only scope for leaders with no
        # unit position at all) -- never the whole organization.
        return Account.objects.filter(
            Q(pk__in=accounts_under_units(self.user_units))
            | Q(pk__in=self.request.user.account.managed_accounts.all()))

    def _extra_context(self, context):
        org = self.request.user.account.organization
        context['show_units_tab'] = org.leadertab_config in [
            LeaderTabConfigChoices.UNITS, LeaderTabConfigChoices.BOTH]
        context['show_accounts_tab'] = org.leadertab_config in [
            LeaderTabConfigChoices.ACCOUNTS, LeaderTabConfigChoices.BOTH]
        context['active_tab'] = "results"
        return context

    def _scannerjob_choices(self, org, accounts):
        if org is None:
            return super()._scannerjob_choices(org, accounts)
        return org.scanners.filter(
            document_reports__number_of_matches__gte=1,
            document_reports__alias_relations__account__in=accounts,
            document_reports__alias_relations__shared=False,
        ).distinct()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_superuser and not request.user.account.is_manager:
                return HttpResponseForbidden(
                    "Only managers and superusers have access to this page.")
        return super().dispatch(request, *args, **kwargs)


class LeaderResultsStatisticsCSVView(StatisticsCSVExportMixin, LeaderResultsStatisticsPageView):
    exported_filename = 'osdatascanner_leader_results_statistics'
    feature_flag_setting = 'LEADER_CSV_EXPORT'
