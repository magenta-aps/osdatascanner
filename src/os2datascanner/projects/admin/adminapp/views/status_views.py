from django.db import transaction
from django.db.models import Q, Max, Min
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from os2datascanner.projects.utils.pagination import EmptyPagePaginator

from .user_error_log_views import count_new_errors
from .views import RestrictedListView, RestrictedDetailView, RestrictedDeleteView
from ..models.scannerjobs.scanner import ScanStatus
from ....utils.view_mixins import CSVExportMixin


class StatusBase(RestrictedListView):
    def get_queryset(self):
        return super().get_queryset(org_path="scanner__organization")

    def get_context_data(self, **kwargs):
        ScanStatus.clean_defunct()

        context = super().get_context_data(**kwargs)
        context["new_error_logs"] = count_new_errors(self.request.user)
        return context


class StatusOverview(StatusBase):
    template_name = "scan_status.html"
    model = ScanStatus

    def get_queryset(self):

        # Only get ScanStatus objects that are not deemed "finished" (see
        # ScanStatus._completed_Q object above) and objects which are not cancelled.
        # That way we avoid manual filtering in the template and only get the data we
        # intend to display.

        return super().get_queryset().order_by("-pk").exclude(ScanStatus._completed_or_cancelled_Q
                                                              ).prefetch_related("scanner")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Tell the poll element to reload the entire table when a scan starts or finishes.
        running_jobs_count = self.object_list.count()
        old_scans_length = int(self.request.GET.get("scans", running_jobs_count))
        reload_table = running_jobs_count == 0 or running_jobs_count != old_scans_length
        context["reload"] = ".scan-status-table" if reload_table else "#status_table_poll"

        context['delay'] = "every 1s" if self.object_list.exists(
            ) or self.object_list.count() != old_scans_length else "every 5s"

        is_htmx = self.request.headers.get("HX-Request", False) == 'true'
        if is_htmx:
            htmx_trigger = self.request.headers.get("HX-Trigger-Name")
            if htmx_trigger == "status_tabs_poll":
                context["page"] = "scan-status"
        return context

    def get_template_names(self):
        is_htmx = self.request.headers.get("HX-Request", False) == 'true'
        if is_htmx:
            htmx_trigger = self.request.headers.get("HX-Trigger-Name")
            if htmx_trigger == "status_tabs_poll":
                return "components/navigation/scanner_tabs.html"
            elif htmx_trigger == "status_table_poll":
                return "components/scanstatus/scan_status_table.html"
        else:
            return "scan_status.html"


class StatusCompletedView(StatusBase):
    paginate_by = 10
    paginator_class = EmptyPagePaginator
    template_name = "components/scanner/scan_completed.html"
    model = ScanStatus
    paginate_by_options = [10, 20, 50, 100, 250]

    def get_queryset(self):
        """Returns a queryset of Scannerjobs that are finished.

        The queryset consists only of completed scans and is ordered by start time.
        """

        qs = super().get_queryset()
        qs = qs.filter(ScanStatus._completed_or_cancelled_Q, resolved=False).order_by(
                '-scan_tag__time').prefetch_related('scanner')

        # The runtime of the scan is calculated from the last snapshot and the first snapshot
        # that has recorded a scanned object (or more) to exclude time spent idle -
        # f.e. due to multiple running jobs resulting in a large message queue.
        qs = qs.annotate(
            scan_time=Max('snapshots__time_stamp')
            - Min('snapshots__time_stamp', filter=Q(snapshots__scanned_objects__gte=1))
        )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['paginate_by'] = int(self.request.GET.get('paginate_by', self.paginate_by))
        context['paginate_by_options'] = self.paginate_by_options

        return context

    def get_paginate_by(self, queryset):
        # Overrides get_paginate_by to allow changing it in the template
        # as url param paginate_by=xx
        return self.request.GET.get('paginate_by', self.paginate_by)

    def post(self, request, *args, **kwargs):
        is_htmx = self.request.headers.get("HX-Request", False) == "true"
        htmx_trigger = self.request.headers.get('HX-Trigger-Name')
        self.object_list = self.get_queryset()

        if is_htmx:
            if htmx_trigger == "status-resolved":
                resolve_pk = self.request.POST.get('pk')
                self.object_list.filter(pk=resolve_pk).update(resolved=True)
            elif htmx_trigger == "status-resolved-selected":
                self.object_list.filter(pk__in=self.request.POST.getlist(
                    'table-checkbox')).update(resolved=True)
            elif htmx_trigger == "status-resolved-all":
                self.object_list.update(resolved=True)

        return self.render_to_response(self.get_context_data())


class StatusCompletedCSVView(CSVExportMixin, PermissionRequiredMixin, StatusCompletedView):
    columns = [
        {
            'name': 'scanner__name',
            'label': _("Scanner name"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
        {
            'name': 'scan_tag__time',
            'label': _("Start time"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
        {
            'name': 'total_objects',
            'label': _("Objects found"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
        {
            'name': 'matches_found',
            'label': _("Matches found"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
        {
            'name': 'scan_time',
            'label': _("Scanning time"),
            'type': CSVExportMixin.ColumnType.FIELD,
        },
    ]
    exported_filename = 'os2datascanner_completed_scans'
    permission_required = 'os2datascanner.export_completed_scanstatus'


class StatusTimeline(RestrictedDetailView):
    model = ScanStatus
    template_name = "components/scanstatus/status_timeline.html"
    context_object_name = "status"
    fields = "__all__"

    def get_queryset(self):
        return super().get_queryset(org_path="scanner__organization")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        status = context['status']
        context['snapshot_data'] = status.timeline()

        return context


class StatusDelete(PermissionRequiredMixin, RestrictedDeleteView):
    model = ScanStatus
    fields = []
    success_url = reverse_lazy("status")
    permission_required = "os2datascanner.delete_scanstatus"

    def get_queryset(self):
        return super().get_queryset(org_path="scanner__organization")

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        return super().get_form(form_class)

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        # We need to take a lock on the status object here so our background
        # processes can't retrieve it before deletion, update it, and then save
        # it back to the database again
        pk = self.kwargs.get(self.pk_url_kwarg)
        self.get_queryset().filter(pk=pk).select_for_update().first()
        return super().delete(request, *args, **kwargs)


class StatusCancel(PermissionRequiredMixin, RestrictedDetailView):
    model = ScanStatus
    success_url = reverse_lazy("status")
    permission_required = "os2datascanner.cancel_scanstatus"

    def get_queryset(self):
        return super().get_queryset(org_path="scanner__organization")

    def post(self, request, *args, **kwargs):
        status = self.get_object(self.get_queryset())
        status.cancel(request.user)

        return redirect(self.success_url)
