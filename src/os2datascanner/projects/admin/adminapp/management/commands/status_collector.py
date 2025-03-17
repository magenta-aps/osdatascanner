import math
import structlog

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.db.models import F
from django.db.utils import DataError
from django.core.management.base import BaseCommand

from prometheus_client import Summary, start_http_server

from os2datascanner.utils import debug
from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.pipeline.utilities.pika import PikaPipelineThread


from ...models.scannerjobs.scanner import (
    Scanner, ScanStatus, ScanStatusSnapshot)
from ...models.scannerjobs.scanner_helpers import MIMETypeProcessStat
from ...notification import FinishedScannerNotificationEmail
from datetime import timedelta

logger = structlog.get_logger("status_collector")
SUMMARY = Summary("os2datascanner_scan_status_collector_admin",
                  "Messages through ScanStatus collector")


def status_message_received_raw(body):  # noqa: CCR001 complexity
    """A status message for a scannerjob is created in Scanner.run().
    Therefore, this method can focus merely on updating the ScanStatus object."""
    message = messages.StatusMessage.from_json_object(body)

    try:
        scanner = Scanner.objects.get(pk=message.scan_tag.scanner.pk)
    except Scanner.DoesNotExist:
        # This is a residual message for a scanner that the administrator has
        # deleted. Throw it away
        return

    locked_qs = ScanStatus.objects.select_for_update(
        of=('self',)
    ).filter(
        scanner=scanner,
        scan_tag=body["scan_tag"]
    )
    # Queryset is evaluated immediately with .first() to lock the database entry.
    scan_status = locked_qs.first()

    if message.total_objects is not None:
        # An explorer has finished exploring a Source
        locked_qs.update(
                message=message.message,
                last_modified=timezone.now(),
                status_is_error=message.status_is_error,
                total_objects=F('total_objects') + message.total_objects,
                total_sources=F('total_sources') + (message.new_sources or 0),
                explored_sources=F('explored_sources') + 1)

    elif message.object_size is not None and message.object_type is not None:
        # A worker has finished processing a Handle
        locked_qs.update(
                message=message.message,
                last_modified=timezone.now(),
                status_is_error=message.status_is_error,
                scanned_size=F('scanned_size') + message.object_size,
                scanned_objects=F('scanned_objects') + 1)

    if message.skipped_by_last_modified:
        locked_qs.update(skipped_by_last_modified=F("skipped_by_last_modified") +
                         message.skipped_by_last_modified)

    if message.matches_found is not None:
        locked_qs.update(matches_found=F('matches_found') + message.matches_found)

    # Get the frequency setting and decide whether to create a snapshot
    snapshot_param = settings.SNAPSHOT_PARAMETER

    if scan_status:
        if message.process_time_worker is not None and message.object_type is not None:
            # select for update to lock
            locked_stat_qs = MIMETypeProcessStat.objects.select_for_update(
                ).filter(
                scan_status=scan_status,
                mime_type=message.object_type
                )
            mime_type_process_stats = locked_stat_qs.first()

            if mime_type_process_stats:
                locked_stat_qs.update(
                    total_time=F('total_time') + timedelta(seconds=message.process_time_worker),
                    total_size=F('total_size') + message.object_size,
                    object_count=F('object_count') + 1
                )
            else:
                MIMETypeProcessStat.objects.create(
                    scan_status=scan_status,
                    mime_type=message.object_type,
                    total_size=message.object_size,
                    object_count=1,
                    total_time=timedelta(seconds=message.process_time_worker)
                    )

        # We've just updated using locked_qs, refresh our saved instance before proceeding.
        scan_status.refresh_from_db()
        n_total = scan_status.total_objects
        if n_total and n_total > 0:
            # Calculate a frequency for how often to take a snapshot.
            # n_total must be at least 2 for this to work.
            frequency = n_total * math.log(snapshot_param, max(n_total, 2))
            # Decide whether it is time to take a snapshot.
            take_snap = scan_status.scanned_objects % max(1, math.floor(frequency))
            if take_snap == 0:
                ScanStatusSnapshot.objects.create(
                    scan_status=scan_status,
                    time_stamp=timezone.now(),
                    total_sources=scan_status.total_sources,
                    explored_sources=scan_status.explored_sources,
                    total_objects=scan_status.total_objects,
                    scanned_objects=scan_status.scanned_objects,
                    scanned_size=scan_status.scanned_size,
                    skipped_by_last_modified=scan_status.skipped_by_last_modified,
                )

        # TODO: No mails are sent when scans are cancelled -- should they?
        if scan_status.finished:
            if not scan_status.email_sent:
                # Send email upon scannerjob completion
                logger.info("Sending notification mail for finished scannerjob.")
                FinishedScannerNotificationEmail(scanner, scan_status).notify()
                scan_status.email_sent = True
                scan_status.save()
            else:
                logger.warning(
                    "BUG: received status message for a ScanStatus marked as complete!",
                    scan_status=scan_status, message=message)

    yield from []


class StatusCollectorRunner(PikaPipelineThread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        start_http_server(9091)

    def handle_message(self, routing_key, body):
        with SUMMARY.time():
            logger.debug(
                "Status collector received a raw message",
                routing_key=routing_key,
                body=body
            )
            try:
                with transaction.atomic():
                    if routing_key == "os2ds_status":
                        yield from status_message_received_raw(body)
            except DataError as de:
                # DataError occurs when something went wrong trying to select
                # or create/update data in the database. For now, we
                # only log the error message.
                logger.error(
                    "Could not get or create object, due to DataError",
                    error=de)


class Command(BaseCommand):
    """Command for starting a ScanStatus collector process."""
    help = __doc__

    def handle(self, *args, **options):
        debug.register_debug_signal()

        StatusCollectorRunner(
            read=["os2ds_status"],
            prefetch_count=1024).run_consumer()
