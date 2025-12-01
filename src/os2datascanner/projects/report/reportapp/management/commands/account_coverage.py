"""Returns the account coverage of a given scan based on existing DocumentReports."""

from django.core.management.base import BaseCommand
from django.db.models import Q, F, DateTimeField
from django.db.models.functions import Cast
from django.db.models.fields.json import KeyTextTransform

from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
from os2datascanner.projects.report.reportapp.models.scanner_reference import ScannerReference
from os2datascanner.projects.report.organizations.models.aliases import AliasType
from os2datascanner.projects.report.organizations.models.organization import Organization
from os2datascanner.projects.admin.adminapp.utils import CoverageMessage
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
            scan_ref = ScannerReference.objects.get(scanner_pk=scanner, organization=org)
            reports = DocumentReport.objects.filter(scanner_job=scan_ref)
        else:
            reports = DocumentReport.objects.filter(scanner_job__organization=org)

        reports = reports.filter(
                # We don't want reports from scanners which don't use CoveredAccounts.
                Q(scanner_job__org_units__isnull=False) |
                Q(scanner_job__scan_entire_org=True)
            ).filter(
                alias_relations__account__isnull=False
            ).exclude(
                alias_relations___alias_type=AliasType.REMEDIATOR,
            )

        st_reports = reports.annotate(
                    scan_tag_time_str=KeyTextTransform("time", "raw_scan_tag"),
                    scan_tag_time=Cast("scan_tag_time_str", DateTimeField()),
                ).exclude(
                    scan_time=F("scan_tag_time")
                ).values(
                    "scanner_job__scanner_pk",
                    "alias_relations__account",
                    "scan_time"
                ).distinct().order_by("scan_time")

        rstt_reports = reports.values(
                "scanner_job__scanner_pk",
                "alias_relations__account",
                "raw_scan_tag__time"
                ).distinct().order_by("raw_scan_tag__time")

        st_coverages = [{
                        # The queryset has been converted to a dict, so the
                        # "alias_relations__account" value here is a UUID, not an Account.
                        "account": str(obj["alias_relations__account"]),
                        "time": obj["scan_time"].astimezone(tz=None).isoformat(),
                        "scanner_id": obj["scanner_job__scanner_pk"]
                        } for obj in st_reports]

        rstt_coverages = [{
                        # The queryset has been converted to a dict, so the
                        # "alias_relations__account" value here is a UUID, not an Account.
                        "account": str(obj["alias_relations__account"]),
                        "time": obj["raw_scan_tag__time"],
                        "scanner_id": obj["scanner_job__scanner_pk"]
                        } for obj in rstt_reports]

        coverages = st_coverages + rstt_coverages

        if coverages:
            message = CoverageMessage(
                coverages=coverages
            )

            ppt = PikaPipelineThread(write=["os2ds_checkups"])

            ppt.enqueue_message(
                "os2ds_checkups", message.to_json_object()
            )

            print(
                    "Enqueued messages, waiting for"
                    " RabbitMQ thread to finish sending them...")

            ppt.enqueue_stop()
            ppt.run()

            print("RabbitMQ thread finished. All done!")
        else:
            print("Nothing to recreate, no messages enqueued.")
