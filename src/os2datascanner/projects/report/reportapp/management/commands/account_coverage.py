"""Returns the account coverage of a given scan based on existing DocumentReports."""

from django.core.management.base import BaseCommand
from django.db.models import Count

from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
from os2datascanner.projects.report.reportapp.models.scanner_reference import ScannerReference
from os2datascanner.projects.report.organizations.models.aliases import AliasType
from os2datascanner.projects.report.organizations.models.organization import Organization
from os2datascanner.engine2.pipeline.messages import CoverageMessage
from os2datascanner.engine2.pipeline.utilities.pika import PikaPipelineThread


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "-s", "--scanner",
            type=int,
            help="the primary key of a scanner in the admin module")
        parser.add_argument(
            "-o", "--organization",
            type=str,
            help="the UUID of an organization"
        )

    def handle(self, scanner: int | None = None, organization: str | None = None, **kwargs):

        if organization:
            org = Organization.objects.get(uuid=organization)
        else:
            # If there is only one organization, grab that. Else fail
            org = Organization.objects.get()

        if scanner:
            assert ScannerReference.objects.filter(scanner_pk=scanner, organization=org).exists()
            reports = DocumentReport.objects.filter(scanner_job__scanner_pk=scanner)
        else:
            reports = DocumentReport.objects.filter(scanner_job__organization=org)

        reports = DocumentReport.objects.filter(
                # We don't want reports from scanners which don't use CoveredAccounts.
                scanner_job__org_units__isnull=False,
                alias_relations__account__isnull=False
            ).exclude(
                alias_relations___alias_type=AliasType.REMEDIATOR,
            ).values(
                "scanner_job__scanner_pk",
                "alias_relations__account",
                "scan_time"
                ).order_by("scan_time").annotate(count=Count("scan_time"))

        coverages = [{
                        "account": str(obj["alias_relations__account"]),
                        "time": obj["scan_time"].astimezone(tz=None).isoformat(),
                        "scanner_id": obj["scanner_job__scanner_pk"]
                    } for obj in reports]

        message = CoverageMessage(
            coverages=coverages
        )

        ppt = PikaPipelineThread(write=["os2ds_checkups"])
        ppt.start()

        ppt.enqueue_message(
            "os2ds_checkups", message.to_json_object()
        )

        print(
                "Enqueued messages, waiting for"
                " RabbitMQ thread to finish sending them...")

        ppt.synchronise()
        ppt.enqueue_stop()
        ppt.join()

        print("RabbitMQ thread finished. All done!")
