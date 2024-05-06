import structlog
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView

from os2datascanner.projects.admin.core.models import Administrator
from os2datascanner.projects.admin.organizations.models import Organization
from os2datascanner.projects.admin.adminapp.models.scannerjobs.analysisscanner import AnalysisJob
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import Scanner
from os2datascanner.projects.admin.adminapp.models.scannerjobs.msgraph import MSGraphMailScanner
from os2datascanner.projects.admin.adminapp.models.scannerjobs.exchangescanner import (
    ExchangeScanner)
from os2datascanner.projects.admin.core.models.background_job import JobState
import json

logger = structlog.get_logger("adminapp")


class AnalysisPageView(LoginRequiredMixin, TemplateView):
    template_name = "analysis.html"
    orgs = []

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            self.orgs = Organization.objects.all()
        else:
            try:
                self.orgs = [Administrator.objects.get(user=request.user).client.organizations]
            except Administrator.DoesNotExist:
                self.orgs = []

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        scanners = Scanner.objects.filter(organization__in=self.orgs).select_subclasses()
        context["scanners"] = scanners

        try:
            selected_scanner_pk = int(self.request.GET.get('scannerjob', 'none'))
            selected_scanner = scanners.get(pk=selected_scanner_pk)
        except ValueError:
            selected_scanner = None
        context["selected_scanner"] = selected_scanner

        if type(selected_scanner) in (MSGraphMailScanner, ExchangeScanner):
            context["supported_scannertype"] = False
        else:
            context["supported_scannertype"] = True

        if selected_scanner:
            analysis_job = selected_scanner.get_analysis_job()
            context["analysis_job"] = analysis_job
            if finished_analysis := selected_scanner.get_analysis_job(finished=True):
                type_stats = finished_analysis.types.all().order_by("mime_type")

                if type_stats:
                    context["chart_data"] = json.dumps([{"type": ts.mime_type,
                                                        "sizes": ts.sizes,
                                                         "n_files": ts.count,
                                                         "total_size": sum(ts.sizes)}
                                                        for ts in type_stats])

                    context["bar_list"] = [ts.mime_type for ts in type_stats]
                    context["pie_list"] = ["a", "b"]

        return context


def start_analysis_job(scanner: Scanner):
    """
    Function for starting an analysis job related to a given scanner
    """
    latest_job = AnalysisJob.objects.filter(scanner=scanner).first()
    # get latest import job
    if not latest_job \
            or latest_job.exec_state == JobState.FINISHED \
            or latest_job.exec_state == JobState.FAILED \
            or latest_job.exec_state == JobState.CANCELLED:
        AnalysisJob.objects.create(scanner=scanner)
        logger.info(f"Analysis job started for {scanner}")
    else:
        logger.info(f"It is not possible to start analysis job for {scanner}")


class AnalysisJobRunView(LoginRequiredMixin, DetailView):
    """Base class for view that handles starting of an analysis job"""

    model = Scanner

    def post(self, request, *args, **kwargs):
        """
        Handle a get request to the LDAPImportView.
        """
        start_analysis_job(self.get_object())

        # redirect back to organizations
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
