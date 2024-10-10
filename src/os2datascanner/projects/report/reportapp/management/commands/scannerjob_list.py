from django.core.management.base import BaseCommand
from django.db.models import Count

from ...models.documentreport import DocumentReport


class Command(BaseCommand):
    """ Lists all scannerjobs that the report module knows about.
    """

    help = "Lists all scannerjobs that the report module knows about."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Scannerjobs:"))

        scannerjobs = DocumentReport.objects.values(
            'scanner_job_pk', 'scanner_job_name').order_by().annotate(
            count=Count('scanner_job_name'))

        for job in scannerjobs:
            self.stdout.write(f"{job['scanner_job_name']} (PK: {job['scanner_job_pk']})")
