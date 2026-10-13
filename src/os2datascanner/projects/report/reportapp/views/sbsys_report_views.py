from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from os2datascanner.core_organizational_structure.models.organization import SBSYSTabConfigChoices
from os2datascanner.projects.report.reportapp.models.scanner_reference import ScannerReference
from ..models.documentreport import DocumentReport
from ..models.container_report import ContainerReport
from django.utils.translation import gettext_lazy as _
from ...organizations.models.account import Account
from .report_views import EmptyPagePaginator, HandledMixin
from django.db.models import F, Count, Prefetch
import structlog

logger = structlog.get_logger("reportapp")


class SBSYSReportView(LoginRequiredMixin, ListView):
    template_name = 'index.html'
    paginator_class = EmptyPagePaginator
    paginate_by = 10
    context_object_name = 'container_reports'
    model = ContainerReport
    paginate_by_options = [10, 20, 50, 100, 250]

    report_type: Account.ReportType | None = None
    handled: bool = False

    scannerjob_filters = None

    def get_base_queryset(self):
        return self.request.user.account.get_report(self.report_type, self.handled)

    def get_queryset(self):
        try:
            reports = self.get_base_queryset()
        except Account.DoesNotExist:
            logger.warning("unexpected error", exc_info=True)
            return ContainerReport.objects.none()

        if (scannerjob := self.request.GET.get("scannerjob", "all")) != "all":
            reports = reports.filter(scanner_job__scanner_pk=int(scannerjob))

        queryset = ContainerReport.objects.filter(
            source_type="sbsys-db",
            pk__in=reports.values_list("container_id", flat=True),
        ).prefetch_related(
            Prefetch("document_reports", queryset=reports, to_attr="visible_reports"),
        ).annotate(
            dr_count=Count("document_reports"),
            # Gives the case number a real field name, so it sorts like the others
            case_number=F("handle__path"),
        )

        allowed_sorting_properties = [
            "case_number",
            "datasource_creation_time",
            "datasource_last_modified",
        ]

        sort_key = self.request.GET.get("order_by")

        if sort_key not in allowed_sorting_properties:
            sort_key = "case_number"  # Fallback to case number

        match self.request.GET.get("order"):
            case "descending":
                return queryset.order_by(F(sort_key).desc(nulls_last=True), "pk")
            case _:
                return queryset.order_by(F(sort_key).asc(nulls_last=True), "pk")

    def get_paginate_by(self, queryset):
        # Allows changing the page size in the template with ?paginate_by=xx
        return self.request.GET.get('paginate_by', self.paginate_by)

    def _allow_handle(self):
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["is_handled"] = self.handled

        context['paginate_by'] = int(self.request.GET.get('paginate_by', self.paginate_by))
        context['paginate_by_options'] = self.paginate_by_options

        context["scannerjob_choices"] = ScannerReference.objects.filter(
            container_reports__source_type="sbsys-db",
            container_reports__in=self.object_list.values("pk"),
        ).annotate(
            total=Count("container_reports", distinct=True),
        ).order_by("scanner_name")
        context["chosen_scannerjob"] = self.request.GET.get("scannerjob", "all")
        context["order_by"] = self.request.GET.get("order_by", "case_number")
        context["order"] = self.request.GET.get("order", "ascending")

        # Possibility to restrict permission to handle reports
        context["allow_handle"] = self._allow_handle()

        return context

    def dispatch(self, request, *args, **kwargs):
        # The account lookup below would fail before LoginRequiredMixin gets to run
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        account = request.user.account

        # Access check:
        # 1) Org must have SBSYS enabled
        if not account.sbsystab_access:
            access_setting = SBSYSTabConfigChoices(account.organization.sbsystab_access)

            # If user doesn't have access, then redirect and show a message:
            match access_setting:
                # Visible only with permission:
                case SBSYSTabConfigChoices.WITH_PERMISSION:
                    message_text = _(
                        "The SBSYS tab is enabled for your organization, "
                        "but you do not have the required permission to view it."
                    )
                    message_theme = messages.WARNING

                # Hidden for all:
                case SBSYSTabConfigChoices.NONE:
                    message_text = _("The SBSYS tab is not enabled for your organization.")
                    message_theme = messages.WARNING

                # Invalid or unexpected value:
                case _:
                    message_text = _(
                        "Unexpected error: The system is unable to verify your SBSYS tab access "
                        "at this time.")
                    message_theme = messages.ERROR

            messages.add_message(
                request,
                message_theme,
                message_text,
                extra_tags="manual_close"
            )
            return redirect(reverse_lazy("index"))

        # 2) For RemediatorView it will then go through RemediatorView.dispatch,
        # which checks .is_remediator or superuser.
        return super().dispatch(request, *args, **kwargs)


class SBSYSPersonalView(SBSYSReportView):
    """Presents the user with their personal unhandled SBSYS results."""

    type = "sbsys-personal"
    template_name = "report_content--personal_sbsys.html"
    report_type = Account.ReportType.PERSONAL_AND_SHARED


class SBSYSPersonalHandledView(HandledMixin, SBSYSPersonalView):
    """Presents the user with their personal handled SBSYS results."""


class SBSYSRemediatorView(SBSYSReportView):
    """Presents a remediator with relevant unhandled SBSYS results."""

    type = "sbsys-remediator"
    template_name = "report_content--remediator_sbsys.html"
    report_type = Account.ReportType.REMEDIATOR

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        try:
            if request.user.account.is_remediator or request.user.is_superuser:
                return response
        except Exception as e:
            logger.warning("Exception raised while trying to dispatch to user "
                           f"{request.user}: {e}")
        return redirect(reverse_lazy("index"))


class SBSYSRemediatorHandledView(HandledMixin, SBSYSRemediatorView):
    """Presents the remediator with all relevant handled SBSYS results."""


class SBSYSUndistributedView(PermissionRequiredMixin, SBSYSReportView):
    """Presents a superuser with all undistributed unhandled SBSYS results."""

    type = "sbsys-undistributed"
    template_name = "report_content--undistributed_sbsys.html"
    permission_required = "organizations.view_withheld_results"

    def get_base_queryset(self):
        # Same filter as UndistributedView, which doesn't go through Aliases
        return DocumentReport.objects.filter(
            scanner_job__organization=self.request.user.account.organization,
            only_notify_superadmin=True,
            number_of_matches__gte=1,
            resolution_status__isnull=not self.handled,
        )

    def _allow_handle(self):
        return self.request.user.has_perm("organizations.handle_withheld_results")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # The "distribute results" modal lists these
        context["undistributed_scannerjobs"] = context["scannerjob_choices"]
        return context


class SBSYSUndistributedHandledView(HandledMixin, SBSYSUndistributedView):
    """Presents a superuser with all undistributed handled SBSYS results."""
