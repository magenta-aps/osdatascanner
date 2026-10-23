# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.core.management.base import BaseCommand

from ....organizations.broadcast_bulk_events import BulkUpdateEvent
from ....organizations.publish import publish_events
from ...models.scannerjobs.scanner import Scanner, ScannerSerializer


class Command(BaseCommand):
    """Publishes an update event for every scanner, so the report module creates any missing
    ScannerReference."""

    help = __doc__

    def handle(self, *args, **options):
        scanners = Scanner.objects.unfiltered().filter(organization__isnull=False)
        events = [
            BulkUpdateEvent({"Scanner": [ScannerSerializer(scanner).data]})
            for scanner in scanners
        ]
        publish_events(events)
        self.stdout.write(f"Published update events for {len(events)} scanner(s).")
