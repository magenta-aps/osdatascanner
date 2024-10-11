from django.views.generic import ListView
from django.db.models import Count
from django.urls import reverse_lazy
from django.shortcuts import redirect

from ..models.documentreport import DocumentReport


class ScannerjobListView(ListView):
    model = DocumentReport
    template_name = "scannerjobs/scannerjob_list.html"

    def get_queryset(self):
        return DocumentReport.objects.filter(organization=self.kwargs["org"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["scannerjobs"] = self.object_list.values(
            "scanner_job_pk", "scanner_job_name", "source_type").order_by().annotate(
                count=Count("scanner_job_name"))
        return context

    def dispatch(self, request, *args, **kwargs):
        self.kwargs["org"] = request.user.account.organization
        return super().dispatch(request, *args, **kwargs)


class ScannerjobDeleteView(ListView):
    model = DocumentReport

    def get_queryset(self):
        all_reports = super().get_queryset().filter(organization=self.kwargs["org"])
        return all_reports.filter(scanner_job_pk=self.kwargs["pk"])

    def dispatch(self, request, *args, **kwargs):
        self.kwargs["org"] = request.user.account.organization
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        qs = self.get_queryset()
        qs.delete()
        return redirect(reverse_lazy('scannerjobs'))
