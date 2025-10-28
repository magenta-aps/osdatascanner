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
    model = DocumentReport
    template_name = "scannerjobs/scannerjob_list.html"
    permission_required = 'organizations.view_scannerjob_list'
    context_object_name = "scannerjobs"

    def get_queryset(self):
        org = self.kwargs['org']
        # TODO: Provide help text #66955
        # TODO: Show Scannerjobs with 0 result / determine responsibility #66960
        return super().get_queryset().filter(scanner_job__organization=org,
                                             number_of_matches__gte=1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # We shouldn't need distinct=True here, since pk is already unique in this context.
        # (No alias relations involved)
        scanner_counts = self.get_queryset().values('scanner_job_id'
                                                    ).order_by().annotate(
            total_reports=Count('pk'),
            handled_reports=Count('pk', filter=Q(resolution_status__isnull=False)),
            unhandled_reports=Count('pk', filter=Q(resolution_status__isnull=True))
        )
        scanner_counts_map = {row['scanner_job_id']: row for row in scanner_counts}
        scanner_ids = [scanner_id for scanner_id, counts in scanner_counts_map.items()]

        scanner_refs = ScannerReference.objects.filter(
                pk__in=scanner_ids).order_by('scanner_name')

        for scanner in scanner_refs:
            counts = scanner_counts_map.get(scanner.pk, {})
            scanner.total = counts.get('total_reports', 0)
            scanner.handled = counts.get('handled_reports', 0)
            scanner.unhandled = counts.get('unhandled_reports', 0)

        context["scannerjobs"] = scanner_refs
        return context

    def dispatch(self, request, *args, **kwargs):
        self.kwargs["org"] = request.user.account.organization
        return super().dispatch(request, *args, **kwargs)


class ScannerjobDeleteView(PermissionRequiredMixin, ListView):
    model = DocumentReport
    permission_required = 'organizations.delete_documentreports'

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
