"""Returns the account coverage of a given scan based on existing DocumentReports."""

from django.core.management.base import BaseCommand
from django.db.models import Count

from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
from os2datascanner.engine2.pipeline.messages import CoverageMessage
from os2datascanner.engine2.pipeline.utilities.pika import PikaPipelineThread


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "scanner_id",
            type=int,
            help="the primary key of a scanner in the admin module")

    def handle(self, scanner_id, **kwargs):
        reports = DocumentReport.objects.filter(
            alias_relations__account__isnull=False,
            scanner_job__scanner_pk=scanner_id).values(
                "alias_relations__account",
                "scan_time"
                ).order_by("scan_time").annotate(count=Count("scan_time"))

        coverages = [{
                        "account": str(obj["alias_relations__account"]),
                        "time": obj["scan_time"].astimezone(tz=None).isoformat()
                    } for obj in reports]

        message = CoverageMessage(
            coverages=coverages,
            scanner_id=int(scanner_id)
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
