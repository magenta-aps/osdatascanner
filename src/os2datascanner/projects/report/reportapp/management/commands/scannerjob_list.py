# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

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
