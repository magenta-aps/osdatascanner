import structlog

from django.views.generic import ListView
from django.db.models import Count
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

from ..models.documentreport import DocumentReport


logger = structlog.get_logger()


class ScannerjobListView(ListView):
    model = DocumentReport
    template_name = "scannerjobs/scannerjob_list.html"

    def get_queryset(self):
        return DocumentReport.objects.filter(
            number_of_matches__gte=1,
            organization=self.kwargs["org"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["scannerjobs"] = self.object_list.values(
            "scanner_job_pk", "scanner_job_name", "source_type").order_by().annotate(
                count=Count("scanner_job_name"))
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            self.kwargs["org"] = request.user.account.organization
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


class ScannerjobDeleteView(ListView):
    model = DocumentReport

    def get_queryset(self):
        all_reports = super().get_queryset().filter(organization=self.kwargs["org"])
        return all_reports.filter(scanner_job_pk=self.kwargs["pk"])

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            self.kwargs["org"] = request.user.account.organization
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def post(self, request, *args, **kwargs):
        qs = self.get_queryset()
        out = qs.delete()
        logger.info(
            f"Delete issued to {self.__class__.__name__}: {out[0]} objects deleted: {out[1]}"
        )
        return redirect(reverse_lazy('scannerjobs'))
