import structlog
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from os2datascanner.projects.admin.adminapp.models.scannerjobs.analysisscanner import (AnalysisJob,
                                                                                       TypeStats)
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import Scanner
from os2datascanner.projects.admin.core.models.background_job import JobState
import json

logger = structlog.get_logger(__name__)


class AnalysisPageView(LoginRequiredMixin, TemplateView):
    context_object_name = 'scanner_list'
    scanners = None
    template_name = "components/analysis.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.scanners is None:
            self.scanners = Scanner.objects.all()

        context["scanners"] = (self.scanners, self.request.GET.get('scannerjob', 'none'))

        pk = context["scanners"][1]
        if pk == 'none':
            context["selected_scanner"] = None
            context["selected_job"] = None
        else:
            selected_scanner = self.scanners.filter(pk=int(pk)).first()
            context["selected_scanner"] = selected_scanner
            analysis_job = AnalysisJob.objects.filter(scanner=selected_scanner).first()
            context["selected_job"] = analysis_job
            type_stats = TypeStats.objects.filter(analysis_job=analysis_job)  # noqa

            if not type_stats:  # If the queryset is empty, send nothing to frontend
                context["chart_data"] = None
            else:
                context["chart_data"] = json.dumps([{"type": ts.mime_type,
                                                     "sizes": ts.sizes,
                                                     "n_files": ts.count,
                                                     "total_size": sum(ts.sizes)}
                                                    for ts in type_stats])
        # print(f'Parent context: {context}')
        # print(f"Selected job: {context['selected_job']}")
        return context

    # def get_template_names(self):
    #     is_htmx = self.request.headers.get('HX-Request') == 'true'
    #     if is_htmx:
    #         htmx_trigger = self.request.headers.get("HX-Trigger-Name")
    #         print("TRIGGER:", htmx_trigger)
    #         return "components/analysis.html" #response-analysis-template
    #     else:
    #         return "components/analysis.html"


def start_analysis_job(scanner: Scanner):
    """
    Function for starting an analysis job related to a given scanner
    """
    try:
        latest_job = AnalysisJob.objects.filter(scanner=scanner).first()
        # get latest import job
        if not latest_job \
                or latest_job.exec_state == JobState.FINISHED \
                or latest_job.exec_state == JobState.FAILED \
                or latest_job.exec_state == JobState.CANCELLED:
            logger.info(f"Analysis job startet for {scanner}")
        else:
            logger.info(f"It is not possible to start analysis job for {scanner}")

    except AnalysisJob.DoesNotExist:
        AnalysisJob.objects.create(scanner=scanner)


class AnalysisJobRunView(LoginRequiredMixin, DetailView):
    """Base class for view that handles starting of an analysis job"""

    model = AnalysisJob

    def __init__(self):
        self.object = None

    def get(self, request, *args, **kwargs):
        """
        Handle a get request to the LDAPImportView.
        """
        start_analysis_job(self.get_object().scanner)

        # redirect back to organizations
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ResponseAnalysisView(AnalysisPageView):
    template_name = "components/response-analysis-template.html"

    def get(self, request, uuid):
        print("Get method")
        print(uuid)
        print(request.GET.get("uuid"))
        return uuid

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        analysis_job = AnalysisJob.objects.filter(
            pk="uuid").first()  # How to get uuid from get to here?
        context["selected_job"] = analysis_job

    def get_template_names(self):
        return "components/response-analysis-template.html"
