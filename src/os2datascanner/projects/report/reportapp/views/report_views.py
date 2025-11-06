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
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Count, Q
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.utils.translation import gettext_lazy as _
from django.views.generic import View, ListView, DetailView

from os2datascanner.utils.system_utilities import time_now
from os2datascanner.engine2.rules.rule import Sensitivity

from .utilities.ews_utilities import try_ews_delete
from .utilities.google_utilities import try_gmail_delete, try_gdrive_delete
from .utilities.smb_utilities import try_smb_delete_1
from .utilities.document_report_utilities import handle_report, get_deviations
from .utilities.msgraph_utilities import delete_email, delete_file
from ..models.documentreport import DocumentReport, RENDERABLE_RULES
from ..models.scanner_reference import ScannerReference
from ...organizations.models.account import Account

from os2datascanner.core_organizational_structure.models.organization import SBSYSTabConfigChoices

logger = structlog.get_logger("reportapp")


class EmptyPagePaginator(Paginator):
    def validate_number(self, number):
        try:
            return super(EmptyPagePaginator, self).validate_number(number)
        except EmptyPage:
            if number > 1:
                return self.num_pages
            else:
                raise Http404(_('The page does not exist'))


class ReportView(LoginRequiredMixin, ListView):
    template_name = 'index.html'
    paginator_class = EmptyPagePaginator
    paginate_by = 10
    context_object_name = 'document_reports'
    model = DocumentReport
    scannerjob_filters = None
    paginate_by_options = [10, 20, 50, 100, 250]

    report_type: Account.ReportType = None
    archive: bool = False

    filter_types: list[str] = []
    exclude_types: list[str] = ["sbsys-db"]

    def get_base_queryset(self):
        try:
            acct = self.request.user.account
            self.org = acct.organization
            reports = acct.get_report(self.report_type, self.archive)

            if self.filter_types:
                reports = reports.filter(source_type__in=self.filter_types)
            if self.exclude_types:
                reports = reports.exclude(source_type__in=self.exclude_types)

            return reports

        except Account.DoesNotExist:
            logger.warning(
                    "unexpected error in ReportView.get_queryset_base",
                    exc_info=True)
            return DocumentReport.objects.none()

    def get_queryset(self):
        reports = self.get_base_queryset()
        reports = self.apply_get_param_filters(self.request, self.org, reports)

        return reports.only(
            "name",
            "resolution_status",
            "resolution_time",
            "last_opened_time",
            "raw_matches",
            "datasource_last_modified",
            "raw_problem",
            "number_of_matches"
            )

    @staticmethod
    def apply_get_param_filters(request, org, reports):
        """Called by get_queryset(), filters and orders DocumentReport queryset according
        to request.GET parameters. """

        sort_key, order = None, None
        # Filtering logic - and stores sort_key and order, if present, for the ordering logic.
        for key, value in request.GET.items():
            if value == "all":  # skip no-op filters early.
                continue
            match key:
                case "order_by":
                    sort_key = value
                case "order":
                    order = value
                case "scannerjob":
                    reports = reports.filter(
                        scanner_job__scanner_pk=int(value))
                case "sensitivities":
                    reports = reports.filter(
                        sensitivity=int(value))
                case "resolution_status":
                    reports = reports.filter(
                        resolution_status=int(value))
                case "source_type":
                    reports = reports.filter(
                        source_type=value)
                case "retention":
                    if org.retention_policy and value == "false":
                        older_than_ret_pol = time_now() - timedelta(
                            days=org.retention_days)
                        reports = reports.filter(
                            datasource_last_modified__lte=older_than_ret_pol)
                case _:
                    # Unknown param
                    pass

        # Ordering logic - by allowed properties and sets ascending or descending order.
        allowed_sorting_properties = [
            'sort_key',
            'number_of_matches',
            'resolution_status',
            'datasource_last_modified']
        if (sort_key in allowed_sorting_properties) and order:
            match order:
                case 'ascending':
                    reports = reports.order_by(sort_key, 'pk')
                case 'descending':
                    reports = reports.order_by(f'-{sort_key}', 'pk')
        return reports

    def _allow_handle(self):
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["renderable_rules"] = RENDERABLE_RULES

        # We do this at the request of a customer to change the structure of resolution choices.
        choices = DocumentReport.ResolutionChoices.choices
        context["resolution_choices"] = [choices[i] for i in [3, 2, 1, 0]]  # No False Positive
        context["mass_resolution_choices"] = [choices[i] for i in [3, 2, 4, 1, 0]]  # Has FP

        self.add_form_context(context)

        # Define popover data for error messages
        context["popover_data"] = {
            'status': _("No action required:"),
            'title': _(
                "A temporary error occurred during the latest check of this result. "
                "OSdatascanner will automatically check this result again as part of the next scan."
            ),
            'subtitle': "",
        }

        # Might be slightly over-optimizing - but the evaluation of object_list can be expensive,
        # and there's no reason to do so, if we know in advance that there's no relevant permission
        # f.e. in a WebScanner-only environment.
        org = self.request.user.account.organization
        has_delete_permission = any(
            check() for check in [
                org.has_smb_file_delete_permission,
                org.has_exchange_email_delete_permission,
                org.has_gmail_email_delete_permission,
                org.has_gdrive_file_delete_permission,
                org.has_msgraph_email_delete_permission,
                org.has_msgraph_file_delete_permission,
            ]
        )
        if has_delete_permission:
            filtered_source_type = self.request.GET.get("source_type", None)

            # If GET param is provided (i.e. filtered by source type) use that
            if filtered_source_type:
                source_types = [filtered_source_type]
            else:
                # Otherwise, check what's on the page.
                source_types = list(set(
                    context["page_obj"].object_list.values_list("source_type", flat=True)))

            match source_types:
                case s if len(s) > 1:
                    logger.debug(
                        "More than one source type on page. Mass deletion button not applicable.",
                        source=s
                    )
                case ["smbc"]:
                    context["show_smb_mass_delete_button"] = (
                        self.request.user.account.organization.has_smb_file_delete_permission()
                    )
                case ["ews"]:
                    context["show_ews_mass_delete_button"] = (
                       self.request.user.account.organization.has_exchange_email_delete_permission()
                    )
                case ["gmail"]:
                    context["show_gmail_mass_delete_button"] = (
                        self.request.user.account.organization.has_gmail_email_delete_permission()
                    )
                case ["googledrive"]:
                    context["show_gdrive_mass_delete_button"] = (
                        self.request.user.account.organization.has_gdrive_file_delete_permission()
                    )
                case ["msgraph-mail"]:
                    context["show_msgraph_email_mass_delete_button"] = (
                        self.request.user.account.organization.has_msgraph_email_delete_permission()
                    )
                case ["msgraph-files"]:
                    context["show_msgraph_file_mass_delete_button"] = (
                        self.request.user.account.organization.has_msgraph_file_delete_permission()
                    )
                case _:
                    logger.info("Mass deletion not applicable", source=s)

        # Check permissions for deleting shared files
        context["show_smb_delete_button"] = (
            self.request.user.account.organization.has_smb_file_delete_permission())
        context["show_ews_delete_button"] = (
            self.request.user.account.organization.has_exchange_email_delete_permission())
        context["show_gmail_delete_button"] = (
            self.request.user.account.organization.has_gmail_email_delete_permission())
        context["show_gdrive_delete_button"] = (
            self.request.user.account.organization.has_gdrive_file_delete_permission())
        context["show_msgraph_email_delete_button"] = (
            self.request.user.account.organization.has_msgraph_email_delete_permission())
        context["show_msgraph_file_delete_button"] = (
            self.request.user.account.organization.has_msgraph_file_delete_permission())

        # Retention policy details
        context["retention_policy"] = self.org.retention_policy
        context["retention_days"] = self.org.retention_days

        # Possibility to restrict permission to handle reports
        context["allow_handle"] = self._allow_handle()

        return context

    def add_form_context(self, context):
        sensitivity_filter = Q(sensitivity=self.request.GET.get('sensitivities')
                               ) if self.request.GET.get('sensitivities') not in \
            ['all', None] else Q()
        scannerjob_filter = Q(scanner_job__scanner_pk=self.request.GET.get('scannerjob')
                              ) if self.request.GET.get('scannerjob') not in \
            ['all', None] else Q()
        resolution_status_filter = Q(resolution_status=self.request.GET.get(
            'resolution_status')) if self.request.GET.get('resolution_status') not in \
            ['all', None] else Q()

        # Aggregate counts from DocumentReport queryset.
        # DR PK's must be distinct, because one person can have multiple alias relations, to the
        # same result: Think UPN and Email.
        scanner_counts = (
            self.object_list.filter(
                scanner_job__organization_id=self.org.pk
            )
            .values('scanner_job_id').order_by()
            .annotate(
                total=Count('pk',

                            distinct=True),
            )
        )

        # Map scanner counts
        scanner_counts_map = {row['scanner_job_id']: row for row in scanner_counts}
        scanner_ids = [scanner_id for scanner_id, counts in scanner_counts_map.items()]

        # Fetch ScannerReference objects
        self.scannerjob_filters = (
            ScannerReference.objects.filter(pk__in=scanner_ids)
            .order_by('scanner_name')
        )

        # Attach counts from the DocumentReport aggregation
        for scanner in self.scannerjob_filters:
            counts = scanner_counts_map.get(scanner.pk, {})
            scanner.total = counts.get('total', 0)

        context['scannerjob_choices'] = self.scannerjob_filters
        context['chosen_scannerjob'] = self.request.GET.get('scannerjob', 'all')

        context['retention'] = self.request.GET.get('retention', 'true')

        sensitivities = self.object_list.values(
                'sensitivity').annotate(
                total=Count('pk',
                            distinct=True, filter=scannerjob_filter & resolution_status_filter)
            ).values(
                'sensitivity', 'total'
            ).order_by(
                '-sensitivity')
        context['sensitivity_choices'] = ((Sensitivity(s["sensitivity"]), s["total"]) for s in
                                          sensitivities)
        context['chosen_sensitivity'] = self.request.GET.get('sensitivities', 'all')
        context['source_type_choices'] = self.object_list.order_by("source_type").values(
            "source_type"
        ).annotate(
            total=Count("pk", filter=sensitivity_filter & scannerjob_filter, distinct=True),
        ).values("source_type", "total")
        context['chosen_source_type'] = self.request.GET.get('source_type', 'all')

        resolution_status = self.object_list.values(
                'resolution_status').annotate(
                total=Count('pk', distinct=True,
                            filter=sensitivity_filter & scannerjob_filter),
                ).values('resolution_status', 'total',
                         ).order_by(
                'resolution_status')

        for method in resolution_status:
            method['resolution_label'] = DocumentReport.ResolutionChoices(
                method['resolution_status']).label if method['resolution_status'] \
                or method['resolution_status'] == 0 else None

        context['resolution_status_choices'] = resolution_status
        context['chosen_resolution_status'] = self.request.GET.get('resolution_status', 'all')

        context['paginate_by'] = int(self.request.GET.get('paginate_by', self.paginate_by))
        context['paginate_by_options'] = self.paginate_by_options

        context['order_by'] = self.request.GET.get('order_by', 'sort_key')
        context['order'] = self.request.GET.get('order', 'ascending')

    def get_paginate_by(self, queryset):
        # Overrides get_paginate_by to allow changing it in the template
        # as url param paginate_by=xx
        return self.request.GET.get('paginate_by', self.paginate_by)


class UserReportView(ReportView):
    """Presents the user with their personal unhandled results."""
    type = "personal"
    template_name = "user_content.html"

    @property
    def report_type(self):
        if self.request.GET.get("include-shared", "true") == "true":
            return Account.ReportType.PERSONAL_AND_SHARED
        else:
            return Account.ReportType.PERSONAL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["include_shared"] = self.request.GET.get('include-shared', 'true')

        return context


class RemediatorView(ReportView):
    """Presents a remediator with relevant unhandled results."""

    type = "remediator"
    template_name = "remediator_content.html"
    report_type = Account.ReportType.REMEDIATOR

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        try:
            if self.request.user.account.is_remediator or request.user.is_superuser:
                return response
        except Exception as e:
            logger.warning("Exception raised while trying to dispatch to user "
                           f"{request.user}: {e}")
        return redirect(reverse_lazy('index'))


class UndistributedView(PermissionRequiredMixin, ReportView):
    """Presents a superuser with all undistributed unhandled results."""

    type = "undistributed"
    permission_required = "organizations.view_withheld_results"
    template_name = "undistributed_content.html"

    def get_base_queryset(self):
        # This is the only ReportView subclass that doesn't use Aliases to get
        # results, so it doesn't use the Account.get_report() mechanism
        try:
            acct = self.request.user.account
            self.org = acct.organization
            reports = DocumentReport.objects.filter(
                    scanner_job__organization=self.org,
                    only_notify_superadmin=True,
                    number_of_matches__gte=1,
                    resolution_status__isnull=not self.archive)

            return reports
        except Account.DoesNotExist:
            logger.warning(
                    "unexpected error in UndistributedView.get_queryset_base",
                    exc_info=True)
            return DocumentReport.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['undistributed_scannerjobs'] = self.scannerjob_filters

        context["show_smb_delete_button"] = False
        context["show_smb_mass_delete_button"] = False
        context["show_ews_delete_button"] = False
        context["show_ews_mass_delete_button"] = False
        context["show_gmail_delete_button"] = False
        context["show_gmail_mass_delete_button"] = False
        context["show_drive_delete_button"] = False
        context["show_gdrive_mass_delete_button"] = False
        return context

    def _allow_handle(self):
        return self.request.user.has_perm("organizations.handle_withheld_results")


class SBSYSMixin:
    """
    - Opt into source_type='sbsys-db' via filter_types/exclude_types on ReportView.
    - Attaches these onto each report in the page:
        - `deviations`
        - `kle_number`
    """

    filter_types = ["sbsys-db"]
    exclude_types = []

    def get_context_data(self, **kwargs):
        from os2datascanner.engine2.model._staging import sbsysdb  # noqa

        context = super().get_context_data(**kwargs)
        for report in context["page_obj"].object_list:
            report.deviations = get_deviations(report)

            for h in report.matches.handle.walk_up():
                if isinstance(h, sbsysdb.SBSYSDBHandles.Case):
                    report.kle_number = h.relative_path
                    break
            else:
                report.kle_number = None
        return context

    def dispatch(self, request, *args, **kwargs):
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


class SBSYSPersonalView(SBSYSMixin, ReportView):
    """Presents the user with their personal unhandled SBSYS results."""

    type = "sbsys-personal"
    template_name = "sbsys_content.html"
    report_type = Account.ReportType.PERSONAL_AND_SHARED


class SBSYSRemediatorView(SBSYSMixin, RemediatorView):
    """Presents a remediator with relevant unhandled SBSYS results."""

    type = "sbsys-remediator"
    template_name = "sbsys_remediator_content.html"
    report_type = Account.ReportType.REMEDIATOR


class ArchiveMixin:
    """This mixin is able to overwrite some logic on children of the ReportView-
    class, most notably changing the queryset to query for handled results
    instead of unhandled results."""

    archive = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["show_msgraph_email_delete_button"] = False
        context["show_msgraph_email_mass_delete_button"] = False
        context["show_msgraph_file_delete_button"] = False
        context["show_msgraph_file_mass_delete_button"] = False
        context["show_smb_delete_button"] = False
        context["show_smb_mass_delete_button"] = False
        context["show_ews_delete_button"] = False
        context["show_ews_mass_delete_button"] = False
        context["show_gmail_delete_button"] = False
        context["show_gmail_mass_delete_button"] = False
        context["show_drive_delete_button"] = False
        context["show_gdrive_mass_delete_button"] = False
        return context

    def dispatch(self, request, *args, **kwargs):
        if settings.ARCHIVE_TAB:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect(reverse_lazy('index'))


class UserArchiveView(ArchiveMixin, UserReportView):
    """Presents the user with their personal handled results."""


class RemediatorArchiveView(ArchiveMixin, RemediatorView):
    """Presents the remediator with all relevant handled results."""


class UndistributedArchiveView(ArchiveMixin, UndistributedView):
    """Presents a superuser with all undistributed handled results."""


class SBSYSPersonalArchiveView(ArchiveMixin, SBSYSPersonalView):
    """Presents the user with their personal handled SBSYS results."""


class SBSYSRemediatorArchiveView(ArchiveMixin, SBSYSRemediatorView):
    """Presents the remediator with all relevant handled SBSYS results."""


class HTMXEndpointView(LoginRequiredMixin, View):
    """A view for sending POST-requests via HTMX to the backend."""

    model = DocumentReport

    def post(self, request, *args, **kwargs):

        # Add a header value to the response before returning to initiate reload of some elements.
        response = HttpResponse()
        response.headers["HX-Trigger"] = "reload-htmx"

        return response

    def dispatch(self, request, *args, **kwargs):
        self.is_htmx = request.headers.get('HX-Request')
        if self.is_htmx == "true":
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseBadRequest("HTMX endpoint called from non-HTMX source!")


class HandleMatchView(HTMXEndpointView, DetailView):
    """Endpoint for handling matches via HTMX."""

    def get_queryset(self):
        qs = self.account.get_report(Account.ReportType.RAW) | \
            self.account.get_report(Account.ReportType.RAW, archived=True)

        # Include withheld reports if the user has permission to handle those.
        # TODO: Check for permission here instead of superuser status.
        if self.request.user.is_superuser:
            qs |= DocumentReport.objects.filter(only_notify_superadmin=True).distinct()

        return qs

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        self.account = request.user.account
        report = self.get_object()
        action = request.POST.get('action')
        handle_report(self.request.user.account, report, action)

        return response


class BaseMassView(ListView):
    """
    Base class for Mass-related views.
    A ListView, defining get_queryset, returning queryset of items checked in table-checkbox.
    Not for any use alone.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        pks = self.request.POST.getlist("table-checkbox", [])
        reports = qs.filter(pk__in=pks)
        return reports


class MassHandleView(HTMXEndpointView, BaseMassView):
    """Endpoint for mass handling matches via HTMX."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        self.account = request.user.account
        reports = self.get_queryset()
        action = request.POST.get('action')
        self.handle_reports(reports, action)

        return response

    def handle_reports(self, reports, action):
        try:
            self.account.update_last_handle()
        except Exception as e:
            logger.warning("Exception raised while trying to update last_handle field "
                           f"of account belonging to user {self.request.user}:", e)

        # Make sure all reports belong to the account -- otherwise raise 404 error
        account_reports = self.account.get_report(Account.ReportType.RAW)

        # Include all withheld reports in the queryset of account reports if the user has permission
        # to handle those.
        # TODO: Check for permission here instead of superuser status
        if self.request.user.is_superuser:
            account_reports = account_reports.union(
                DocumentReport.objects.filter(only_notify_superadmin=True))

        if account_reports.intersection(reports).count() != reports.count():
            # At least some of the reports are not accessible by the account. Raise the alarm!
            raise Http404("At least one of the specified reports not found!")

        for report in reports:
            report.resolution_status = action
            report.raw_problem = None
            report.save()
        logger.info(
            f"Successfully handled DocumentReports "
            f"{', '.join([str(report) for report in reports])} with "
            f"resolution_status {action}.")


class OpenMatchView(HTMXEndpointView, DetailView):
    """Endpoint for marking matches as opened."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        report = self.get_object()

        report.update_opened()

        request.session["last_opened"] = str(report.pk)

        return response


class ShowMoreMatchesView(HTMXEndpointView, DetailView):
    template_name = "components/reports/show_more_matches.html"
    model = DocumentReport

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Increase number of shown matches
        last_index = int(self.request.GET.get('last_match', '10'))
        interval = [last_index, last_index + 10]
        context['interval'] = interval

        # Serve the fragments associated with the document report
        frags = self.object.matches.matches
        for frag in frags:
            if (not frag.rule.synthetic
                    and frag.rule.type_label in RENDERABLE_RULES):
                context['frag'] = frag

        # Serve the document report key
        context['pk'] = self.object.pk

        return context


class DistributeMatchesView(HTMXEndpointView, PermissionRequiredMixin, ListView):
    model = DocumentReport
    permission_required = "organizations.distribute_withheld_results"

    def get_queryset(self):
        qs = super().get_queryset()
        scanner_job_pks = self.request.POST.getlist('distribute-to')
        qs = qs.filter(scanner_job__in=scanner_job_pks)
        return qs

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        object_list = self.get_queryset()

        update_output = object_list.update(only_notify_superadmin=False)

        logger.info(f"Updated DocumetReport objects: {update_output}")

        return response


class DeleteMailView(HTMXEndpointView, DetailView):
    """ View for sending a delete request for an email
    through the MSGraph message API. """
    model = DocumentReport

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        report = self.get_object()

        try:
            delete_email(report, request.user.account)
        except PermissionDenied as e:
            error_message = _("Failed to delete {pn}: {e}").format(
                pn=report.matches.handle.presentation_name, e=e)
            messages.add_message(
                request,
                messages.WARNING,
                error_message,
                extra_tags="manual_close"
            )
        return response


class MassDeleteMailView(HTMXEndpointView, BaseMassView):
    """ View for sending delete requests for multiple emails
     through the MSGraph message API. """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        reports = self.get_queryset()
        self.delete_emails(reports)

        return response

    def delete_emails(self, document_reports):
        for report in document_reports:
            try:
                delete_email(report, self.request.user.account)
            except PermissionDenied as e:
                error_message = _("Failed to delete {pn}: {e}").format(
                    pn=report.matches.handle.presentation_name, e=e)
                messages.add_message(
                    self.request,
                    messages.WARNING,
                    error_message,
                    extra_tags="manual_close"
                )


class DeleteFileView(HTMXEndpointView, DetailView):
    """ View for sending a delete request for a file
    through the MSGraph API. """
    model = DocumentReport

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        report = self.get_object()

        try:
            delete_file(report, request.user.account)
        except PermissionDenied as e:
            error_message = _("Failed to delete {pn}: {e}").format(
                pn=report.matches.handle.presentation_name, e=e)
            messages.add_message(
                request,
                messages.WARNING,
                error_message,
                extra_tags="manual_close"
            )
        return response


class MassDeleteFileView(HTMXEndpointView, BaseMassView):
    """ View for sending delete requests for multiple files
     through the MSGraph API. """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        reports = self.get_queryset()
        self.delete_files(reports)

        return response

    def delete_files(self, document_reports):
        for report in document_reports:
            try:
                delete_file(report, self.request.user.account)
            except PermissionDenied as e:
                error_message = _("Failed to delete {pn}: {e}").format(
                    pn=report.matches.handle.presentation_name, e=e)
                messages.add_message(
                    self.request,
                    messages.WARNING,
                    error_message,
                    extra_tags="manual_close"
                )


class DeleteSMBFileView(HTMXEndpointView, DetailView):
    """ View for sending a delete request for a file
    on an SMB share."""
    model = DocumentReport

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        report = self.get_object()

        deleted, problem = try_smb_delete_1(request, [report.pk])
        if not deleted:
            error_message = _("Failed to delete {pn}: {e}").format(
                pn=report.matches.handle.presentation_name, e=problem)
            messages.add_message(
                request,
                messages.WARNING,
                error_message,
                extra_tags="manual_close"
            )

        return response


class MassDeleteSMBFileView(HTMXEndpointView, BaseMassView):
    """View for sending delete requests for multiple files
    on an SMB share."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        reports = self.get_queryset()
        self.delete_files(reports)

        return response

    def delete_files(self, document_reports):
        deleted, problem = try_smb_delete_1(
            self.request, document_reports.values_list(
                "pk", flat=True))

        if not deleted:
            error_message = _("Failed to delete some reports: {e}").format(
                e=problem)
            messages.add_message(
                self.request,
                messages.WARNING,
                error_message,
                extra_tags="manual_close"
            )


class DeleteEWSMailView(HTMXEndpointView, DetailView):
    """ View for sending a delete request for an EWS mail."""
    model = DocumentReport

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        report = self.get_object()

        deleted, problem = try_ews_delete(request, [report.pk])
        if not deleted:
            error_message = _("Failed to delete {pn}: {e}").format(
                pn=report.matches.handle.presentation_name, e=problem)
            messages.add_message(
                request,
                messages.WARNING,
                error_message,
                extra_tags="manual_close"
            )

        return response


class MassDeleteEWSMailView(HTMXEndpointView, BaseMassView):
    """View for sending delete requests for multiple EWS mails."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        reports = self.get_queryset()
        self.delete_ews_mails(reports)

        return response

    def delete_ews_mails(self, document_reports):
        deleted, problem = try_ews_delete(
            self.request, document_reports.values_list(
                "pk", flat=True))

        if not deleted:
            error_message = _("Failed to delete some reports: {e}").format(
                e=problem)
            messages.add_message(
                self.request,
                messages.WARNING,
                error_message,
                extra_tags="manual_close"
            )


class DeleteGmailView(HTMXEndpointView, DetailView):
    """ View for sending a delete request for a gmail."""
    model = DocumentReport

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        report = self.get_object()

        deleted, problem = try_gmail_delete(request, [report.pk])
        if not deleted:
            error_message = _("Failed to delete {pn}: {e}").format(
                pn=report.matches.handle.presentation_name, e=problem)
            messages.add_message(
                request,
                messages.WARNING,
                error_message,
                extra_tags="manual_close"
            )

        return response


class MassDeleteGmailView(HTMXEndpointView, BaseMassView):
    """View for sending delete requests for multiple Gmails."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        reports = self.get_queryset()
        self.delete_gmails(reports)

        return response

    def delete_gmails(self, document_reports):
        deleted, problem = try_gmail_delete(
            self.request, document_reports.values_list(
                "pk", flat=True))

        if not deleted:
            error_message = _("Failed to delete some reports: {e}").format(
                e=problem)
            messages.add_message(
                self.request,
                messages.WARNING,
                error_message,
                extra_tags="manual_close"
            )


class DeleteGoogleDriveView(HTMXEndpointView, DetailView):
    """ View for sending a delete request for a Google Drive file."""
    model = DocumentReport

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        report = self.get_object()

        deleted, problem = try_gdrive_delete(request, [report.pk])
        if not deleted:
            error_message = _("Failed to delete {pn}: {e}").format(
                pn=report.matches.handle.presentation_name, e=problem)
            messages.add_message(
                request,
                messages.WARNING,
                error_message,
                extra_tags="manual_close"
            )

        return response


class MassDeleteGoogleDriveView(HTMXEndpointView, BaseMassView):
    """View for sending delete requests for multiple Google Drive files."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        reports = self.get_queryset()
        self.delete_gdrive_files(reports)

        return response

    def delete_gdrive_files(self, document_reports):
        deleted, problem = try_gdrive_delete(
            self.request, document_reports.values_list(
                "pk", flat=True))
        if not deleted:
            error_message = _("Failed to delete some reports: {e}").format(
                e=problem)
            messages.add_message(
                self.request,
                messages.WARNING,
                error_message,
                extra_tags="manual_close"
            )
