import structlog
from django.db import transaction

from django.views.generic import ListView
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from ..models.documentreport import DocumentReport
from os2datascanner.projects.report.organizations.models import Alias


logger = structlog.get_logger()


# TODO: Change to use ScannerReference
class ScannerjobListView(PermissionRequiredMixin, ListView):
    model = DocumentReport
    template_name = "scannerjobs/scannerjob_list.html"
    permission_required = 'os2datascanner_report.delete_documentreport'

    def get_queryset(self):
        return DocumentReport.objects.filter(
            number_of_matches__gte=1,
            scanner_job__organization=self.kwargs["org"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = self.kwargs['org']
        context["scannerjobs"] = org.scanners.annotate(
                count=Count(
                    'document_reports',
                    filter=Q(document_reports__in=self.object_list),
                )
            )
        return context

    def dispatch(self, request, *args, **kwargs):

        self.kwargs["org"] = request.user.account.organization
        return super().dispatch(request, *args, **kwargs)


# TODO: Change to use ScannerReference
class ScannerjobDeleteView(PermissionRequiredMixin, ListView):
    model = DocumentReport
    permission_required = 'os2datascanner_report.delete_documentreport'

    def get_queryset(self):
        all_reports = super().get_queryset().filter(scanner_job__organization=self.kwargs["org"])
        return all_reports.filter(scanner_job__scanner_pk=self.kwargs["pk"]).only("pk")

    def dispatch(self, request, *args, **kwargs):
        self.kwargs["org"] = request.user.account.organization
        return super().dispatch(request, *args, **kwargs)

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
