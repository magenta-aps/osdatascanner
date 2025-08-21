from django.core.management.base import BaseCommand

from ...models.scanner_reference import ScannerReference


class Command(BaseCommand):
    """ Lists all scannerjobs that the report module knows about.
    """

    help = "Lists all scannerjobs that the report module knows about."

    def handle(self, *args, **kwargs):
        scannerjobs = ScannerReference.objects.all()

        if scannerjobs.exists():
            self.stdout.write(self.style.SUCCESS("Scannerjobs:"))

            for job in scannerjobs:
                self.stdout.write(
                    f"{job.scanner_name} (PK: {job.scanner_pk})")

        else:
            self.stdout.write(self.style.NOTICE("No scannerjobs found."))
