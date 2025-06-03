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
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.experimental.cpr import TurboCPRRule
from os2datascanner.engine2.rules.experimental.health_rule import TurboHealthRule
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.engine2.rules.name import NameRule
from os2datascanner.engine2.rules.address import AddressRule
from os2datascanner.engine2.rules.links_follow import LinksFollowRule
from os2datascanner.engine2.rules.rule import Sensitivity
from os2datascanner.engine2.rules.wordlists import OrderedWordlistRule
from os2datascanner.engine2.rules.dict_lookup import EmailHeaderRule
from os2datascanner.engine2.rules.passport import PassportRule

from .utilities.ews_utilities import try_ews_delete
from .utilities.google_utilities import try_gmail_delete, try_gdrive_delete
from .utilities.smb_utilities import try_smb_delete_1
from .utilities.document_report_utilities import handle_report, get_deviations
from .utilities.msgraph_utilities import delete_email, delete_file
from ..models.documentreport import DocumentReport
from ...organizations.models.account import Account

logger = structlog.get_logger("reportapp")

RENDERABLE_RULES = (
    CPRRule.type_label, RegexRule.type_label, LinksFollowRule.type_label,
    OrderedWordlistRule.type_label, NameRule.type_label, AddressRule.type_label,
    TurboCPRRule.type_label, EmailHeaderRule.type_label, TurboHealthRule.type_label,
    PassportRule.type_label,
)


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

    def get_queryset_base(self):
        try:
            acct = self.request.user.account
            self.org = acct.organization
            report = acct.get_report(self.report_type, self.archive)

            if self.filter_types:
                report = report.filter(source_type__in=self.filter_types)
            if self.exclude_types:
                report = report.exclude(source_type__in=self.exclude_types)

            return report

        except Account.DoesNotExist:
            logger.warning(
                    "unexpected error in ReportView.get_queryset_base",
                    exc_info=True)
            return DocumentReport.objects.none()

    def get_queryset(self):
        self.all_reports = self.document_reports = self.get_queryset_base()
        self.apply_filters()
        self.order_queryset_by_property()

        return self.document_reports.only(
            "name",
            "resolution_status",
            "resolution_time",
            "last_opened_time",
            "raw_matches",
            "datasource_last_modified",
            "raw_problem",
            "number_of_matches"
        )

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

        # Check permissions for deleting shared files
        context["show_smb_delete_button"] = settings.SMB_ALLOW_WRITE
        context["show_smb_mass_delete_button"] = settings.SMB_ALLOW_WRITE and \
            self.all_reports_from_same_source("smbc", context["page_obj"])
        context["show_ews_delete_button"] = settings.EWS_ALLOW_WRITE
        context["show_ews_mass_delete_button"] = settings.EWS_ALLOW_WRITE and \
            self.all_reports_from_same_source("ews", context["page_obj"])
        context["show_gmail_delete_button"] = settings.GMAIL_ALLOW_WRITE
        context["show_gmail_mass_delete_button"] = settings.GMAIL_ALLOW_WRITE and \
            self.all_reports_from_same_source("gmail", context["page_obj"])
        context["show_gdrive_delete_button"] = settings.GDRIVE_ALLOW_WRITE
        context["show_gdrive_mass_delete_button"] = settings.GDRIVE_ALLOW_WRITE and \
            self.all_reports_from_same_source("googledrive", context["page_obj"])
        context["show_file_delete_button"] = (
            self.request.user.account.organization.has_file_delete_permission())
        context["show_file_mass_delete_button"] = (
            self.request.user.account.organization.has_file_delete_permission() and
            self.all_reports_from_same_source("msgraph-files", context["page_obj"]))

        # Retention policy details
        context["retention_policy"] = self.org.retention_policy
        context["retention_days"] = self.org.retention_days

        return context

    def apply_filters(self):
        if self.org.retention_policy and self.request.GET.get('retention') == 'false':
            older_than_ret_pol = time_now() - timedelta(days=self.org.retention_days)
            self.document_reports = self.document_reports.filter(
                datasource_last_modified__lte=older_than_ret_pol)

        if (scannerjob := self.request.GET.get('scannerjob')) and scannerjob != 'all':
            self.document_reports = self.document_reports.filter(
                scanner_job_pk=int(scannerjob))

        if (sensitivity := self.request.GET.get('sensitivities')) and sensitivity != 'all':
            self.document_reports = self.document_reports.filter(sensitivity=int(sensitivity))

        if (method := self.request.GET.get('resolution_status')) and method != 'all':
            self.document_reports = self.document_reports.filter(resolution_status=int(method))

        if (source_type := self.request.GET.get('source_type')) and source_type != 'all':
            self.document_reports = self.document_reports.filter(source_type=source_type)

    def order_queryset_by_property(self):
        """Checks if a sort key is allowed and orders the queryset"""
        allowed_sorting_properties = [
            'sort_key',
            'number_of_matches',
            'resolution_status',
            'datasource_last_modified']
        if (sort_key := self.request.GET.get('order_by')) and (
                order := self.request.GET.get('order')):

            if sort_key not in allowed_sorting_properties:
                return

            if order != 'ascending':
                sort_key = '-'+sort_key
            self.document_reports = self.document_reports.order_by(sort_key, 'pk')

    def add_form_context(self, context):
        sensitivity_filter = Q(sensitivity=self.request.GET.get('sensitivities')
                               ) if self.request.GET.get('sensitivities') not in \
            ['all', None] else Q()
        scannerjob_filter = Q(scanner_job_pk=self.request.GET.get('scannerjob')
                              ) if self.request.GET.get('scannerjob') not in \
            ['all', None] else Q()
        resolution_status_filter = Q(resolution_status=self.request.GET.get(
            'resolution_status')) if self.request.GET.get('resolution_status') not in \
            ['all', None] else Q()

        if self.scannerjob_filters is None:
            # Create select options
            self.scannerjob_filters = self.all_reports.order_by(
                'scanner_job_pk').values(
                'scanner_job_pk').annotate(
                filtered_total=Count('pk', distinct=True,
                                     filter=sensitivity_filter & resolution_status_filter),
                total=Count('pk', distinct=True)  # Todo: I'm not sure we're using this 'total'?
                ).values(
                    'scanner_job_name', 'total', 'filtered_total', 'scanner_job_pk'
                ).order_by('scanner_job_name')

        context['scannerjob_choices'] = self.scannerjob_filters
        context['chosen_scannerjob'] = self.request.GET.get('scannerjob', 'all')

        context['retention'] = self.request.GET.get('retention', 'true')

        sensitivities = self.all_reports.order_by(
                '-sensitivity').values(
                'sensitivity').annotate(
                total=Count('pk',
                            distinct=True, filter=scannerjob_filter & resolution_status_filter)
            ).values(
                'sensitivity', 'total'
            )

        context['sensitivity_choices'] = ((Sensitivity(s["sensitivity"]),
                                           s["total"]) for s in sensitivities)
        context['chosen_sensitivity'] = self.request.GET.get('sensitivities', 'all')

        context['source_type_choices'] = self.all_reports.order_by("source_type").values(
            "source_type"
        ).annotate(
            total=Count("pk", filter=sensitivity_filter & scannerjob_filter, distinct=True),
        ).values("source_type", "total")
        context['chosen_source_type'] = self.request.GET.get('source_type', 'all')

        resolution_status = self.all_reports.order_by(
                'resolution_status').values(
                'resolution_status').annotate(
                total=Count('pk', distinct=True,
                            filter=sensitivity_filter & scannerjob_filter),
                ).values('resolution_status', 'total',
                         )

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

    def all_reports_from_same_source(self, source_type: str, page_obj) -> bool:
        """Checks if all reports on the page stem from the source type. The source_type-argument
        is a string, and is checked against the source_type-field on DocumentReport."""
        # Check if the filtering option specifies this source type. In that case, all reports must
        # be from this type of source.
        filtered = self.request.GET.get("source_type") == source_type

        # Check if there is anything on the page.
        page_exists = page_obj.object_list.exists()

        # Check if all elements of the page stem from this source type
        all_from_source = not DocumentReport.objects.filter(
                pk__in=page_obj.object_list.values_list("pk")
            ).exclude(source_type=source_type).exists()

        return filtered or (page_exists and all_from_source)


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

        # show_delete_button is overwritten in the archive view.
        context["show_email_delete_button"] = (
            self.request.user.account.organization.has_email_delete_permission())
        context["show_email_mass_delete_button"] = (
            self.request.user.account.organization.has_email_delete_permission() and
            self.all_reports_from_same_source("msgraph-mail", context["page_obj"]))
        context["show_file_delete_button"] = (
            self.request.user.account.organization.has_file_delete_permission())
        context["show_file_mass_delete_button"] = (
            self.request.user.account.organization.has_file_delete_permission() and
            self.all_reports_from_same_source("msgraph-files", context["page_obj"]))
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
    permission_required = "os2datascanner_report.see_withheld_documentreport"
    template_name = "undistributed_content.html"

    def get_queryset_base(self):
        # This is the only ReportView subclass that doesn't use Aliases to get
        # results, so it doesn't use the Account.get_report() mechanism
        try:
            acct = self.request.user.account
            self.org = acct.organization
            return DocumentReport.objects.filter(
                    organization=self.org,
                    only_notify_superadmin=True,
                    number_of_matches__gte=1,
                    resolution_status__isnull=not self.archive)
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
        context = super().get_context_data(**kwargs)
        for report in context["page_obj"].object_list:
            report.deviations = get_deviations(report)

            report.kle_number = report.matches.handle.source.handle.relative_path
        return context

    def dispatch(self, request, *args, **kwargs):
        account = request.user.account

        # Access check:
        # 1) Org must have SBSYS enabled
        if not account.sbsystab_access:
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
        context["show_email_delete_button"] = False
        context["show_file_delete_button"] = False
        context["show_file_mass_delete_button"] = False
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
        print(request.headers)
        print(request.POST)
        self.is_htmx = request.headers.get('HX-Request')
        if self.is_htmx == "true":
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseBadRequest("HTMX endpoint called from non-HTMX source!")


class HandleMatchView(HTMXEndpointView, DetailView):
    """Endpoint for handling matches via HTMX."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
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
        reports = self.get_queryset()
        action = request.POST.get('action')
        self.handle_reports(reports, action)

        return response

    def handle_reports(self, reports, action):
        try:
            self.request.user.account.update_last_handle()
        except Exception as e:
            logger.warning("Exception raised while trying to update last_handle field "
                           f"of account belonging to user {self.request.user}:", e)

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
            if frag.rule.type_label in RENDERABLE_RULES:
                context['frag'] = frag

        # Serve the document report key
        context['pk'] = self.object.pk

        return context


class DistributeMatchesView(HTMXEndpointView, PermissionRequiredMixin, ListView):
    model = DocumentReport
    permission_required = "os2datascanner_report.distribute_withheld_documentreport"

    def get_queryset(self):
        qs = super().get_queryset()
        scanner_job_pk = self.request.POST.get('distribute-to')
        qs = qs.filter(scanner_job_pk=scanner_job_pk)
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
                error_message)
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
                    error_message)


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
                error_message)
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
                    error_message)


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
                error_message)

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
                error_message)


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
                error_message)

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
                error_message)


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
                error_message)

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
                error_message)


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
                error_message)

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
                error_message)
