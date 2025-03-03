from django.core.management.base import BaseCommand
from ...models.documentreport import DocumentReport


class Command(BaseCommand):
    """ Deletes all DocumentReport objects related to the provided scanner job
    primary key.
    """

    help = "Deletes all reports for the scanner job with the provided primary key"

    def add_arguments(self, parser):
        parser.add_argument(
            "pk",
            type=int,
            help="Primary key of scanner job",
            default=None,
        )

    def handle(self, pk, *args, **options):  # noqa: CCR001, too high cognitive complexity
        reports = DocumentReport.objects.filter(scanner_job_pk=pk)

        if not reports.exists():
            self.stderr.write(self.style.NOTICE(
                f"Did not find any DocumentReport-objects related to scanner job with pk {pk}."))
            return

        else:
            out = reports.delete()
            self.stdout.write(self.style.SUCCESS(
                f"Deleted {out[0]} objects:"
            ))
            for key, val in out[1].items():
                self.stdout.write(
                    f"* {key}: {val}"
                )
