import structlog
from django.db import transaction

from django.views.generic import ListView
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin

from ..models.scanner_reference import ScannerReference
from ..models.documentreport import DocumentReport
from os2datascanner.projects.report.organizations.models import Alias


logger = structlog.get_logger()


class ScannerjobListView(PermissionRequiredMixin, ListView):
    model = ScannerReference
    template_name = "scannerjobs/scannerjob_list.html"
    permission_required = 'os2datascanner_report.delete_documentreport'
    context_object_name = "scannerjobs"

    def get_queryset(self):
        org = self.kwargs['org']
        return super().get_queryset().filter(organization=org).annotate(
            count=Count(
                'document_reports',
                filter=Q(document_reports__number_of_matches__gte=1),
            )
        )

    def dispatch(self, request, *args, **kwargs):
        self.kwargs["org"] = request.user.account.organization
        return super().dispatch(request, *args, **kwargs)


class ScannerjobDeleteView(PermissionRequiredMixin, ListView):
    model = DocumentReport
    permission_required = 'os2datascanner_report.delete_documentreport'

    def get_queryset(self):
        scanner = get_object_or_404(
            ScannerReference,
            pk=self.kwargs["pk"],
            organization=self.kwargs["org"],
        )
        return scanner.document_reports.all()

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
            alias_through_relations = Alias.reports.through.objects.filter(
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
