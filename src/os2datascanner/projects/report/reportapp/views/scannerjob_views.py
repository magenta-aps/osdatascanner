import structlog
from django.db import transaction

from django.views.generic import ListView
from django.db.models import Count
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

from ..models.documentreport import DocumentReport
from os2datascanner.projects.report.organizations.models import Alias


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
        return all_reports.filter(scanner_job_pk=self.kwargs["pk"]).only("pk")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            self.kwargs["org"] = request.user.account.organization
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def post(self, request, *args, **kwargs):
        qs = self.get_queryset()

        # TODO: Ideal solution would be using a background job or alike, to perform deletion using
        # Django's delete() without halting a web worker.
        with transaction.atomic():
            # Using private method _raw_delete to avoid using Django's CASCADE handling, as it's
            # very slow when fast pathing is unavailable (i.e. there are relations to consider.)
            # However, it means we have to handle Alias relations ourselves.
            alias_through_relations = Alias.match_relation.through.objects.filter(
                documentreport_id__in=qs
            )
            alias_relations = alias_through_relations._raw_delete(alias_through_relations.db)
            drs = qs._raw_delete(qs.db)

            logger.info(
                "Deletion of results issued.",
                deleted_alias_relation=alias_relations,
                deleted_document_reports=drs
            )
        return redirect(reverse_lazy('scannerjobs'))
