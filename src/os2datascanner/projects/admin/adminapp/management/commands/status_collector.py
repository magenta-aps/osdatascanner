# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.
from typing import override

import math
import structlog

from django.conf import settings
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.db.models import F
from django.db.utils import DataError
from django.core.management.base import BaseCommand

from prometheus_client import Summary, start_http_server

from os2datascanner.utils import debug
from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.pipeline.utilities.pika import ANON_QUEUE, PikaPipelineThread


from ...models.scannerjobs.scanner import (
    Scanner, ScanStatus, ScanStatusSnapshot)
from ...models.scannerjobs.scanner_helpers import (
        MIMETypeProcessStat, DuplicationStat, HashCache, delete_per_scan_queue,
        notify_new_conversion_queues_batch)
from ...notification import FinishedScannerNotificationEmail
from datetime import timedelta

logger = structlog.get_logger("status_collector")
SUMMARY = Summary("os2datascanner_scan_status_collector_admin",
                  "Messages through ScanStatus collector")


def status_message_received_raw(body):  # noqa: CCR001, C901 complexity
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

        if message.content_identifier:
            try:
                with transaction.atomic():
                    # Try to store the hash in the cache.
                    HashCache.objects.create(
                        scan_status=scan_status,
                        content_identifier=message.content_identifier,
                        file_size=message.object_size,
                        mime_type=message.object_type
                    )
            except IntegrityError:
                try:
                    with transaction.atomic():
                        # If the hash was not created, it's a duplicate.
                        DuplicationStat.objects.create(
                            scan_status=scan_status,
                            content_identifier=message.content_identifier,
                            file_size=message.object_size,
                            mime_type=message.object_type,
                            occurrences=2,
                            process_time=timedelta(seconds=message.process_time_worker)
                        )
                except IntegrityError:
                    # The duplication was already recorded. Increment the occurrence count.
                    DuplicationStat.objects.filter(
                        scan_status=scan_status,
                        content_identifier=message.content_identifier,
                        file_size=message.object_size,
                        mime_type=message.object_type
                    ).update(occurrences=F('occurrences') + 1,
                             process_time=F('process_time') + timedelta(
                                 seconds=message.process_time_worker))

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
                # Clean up the hash cache for this scan
                HashCache.objects.filter(scan_status=scan_status).delete()

                # Clean up the per-scan conversion queue now that all work is done.
                delete_per_scan_queue(scan_status.scan_tag)
            else:
                logger.warning(
                    "BUG: received status message for a ScanStatus marked as complete!",
                    scan_status=scan_status, message=message)

    yield from []


_REBROADCAST_INTERVAL_TICKS = 600  # ~60 seconds at 0.1s/tick


class StatusCollectorRunner(PikaPipelineThread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        start_http_server(9091)

    # TODO: Re-broadcasting of queues may not really belong in StatusCollector, consider moving
    # it / creating another service for this type of work

    @override
    def make_channel(self):
        channel = super().make_channel()
        anon_queue = channel.queue_declare(
                ANON_QUEUE,
                passive=False, durable=False, exclusive=False,
                auto_delete=True, arguments={"x-max-priority": 10})
        channel.queue_bind(
                exchange="broadcast", queue=anon_queue.method.queue)
        return channel

    @override
    def _basic_consume(self, *, exclusive=False):
        consumer_tags = super()._basic_consume(exclusive=exclusive)
        consumer_tags["anon"] = self.channel.basic_consume(
                ANON_QUEUE, self.handle_message_raw, exclusive=False)
        return consumer_tags

    @override
    def _processing_complete(self, tick):
        if tick and tick % _REBROADCAST_INTERVAL_TICKS == 0:
            self._rebroadcast_active_queues()
        return super()._processing_complete(tick)

    def _rebroadcast_active_queues(self, target_queue: str = None):
        """Sends all active per-scan conversion queue names to workers so they
        can subscribe to any ongoing scans they may have missed.

        If target_queue is given, each message is sent directly to that single
        worker's anonymous command queue (worker_hello response). Otherwise,
        messages are broadcast to all workers (periodic re-broadcast).

        All messages are sent in a single RabbitMQ connection to avoid the
        overhead of one connection per active scan."""
        active = ScanStatus.objects.exclude(
                ScanStatus._completed_or_cancelled_Q).values_list(
                "scan_tag", "conversion_queue_tag", "conversion_queue_name")
        queues = [
            (conversion_queue_name, tag)
            for scan_tag, tag, conversion_queue_name in active
            if conversion_queue_name
        ]
        if queues:
            notify_new_conversion_queues_batch(queues, target_queue=target_queue)
            logger.debug(
                    "Sent active per-scan queues to worker",
                    count=len(queues),
                    target=target_queue or "broadcast")

    @override
    def handle_message(self, routing_key, body):
        with SUMMARY.time():
            logger.debug(
                "Status collector received a raw message",
                routing_key=routing_key,
                body=body
            )
            if routing_key == "":
                command = messages.CommandMessage.from_json_object(body)
                if command.worker_hello:
                    logger.info(
                            "Worker hello received, sending active queues directly",
                            target=command.worker_hello)
                    self._rebroadcast_active_queues(target_queue=command.worker_hello)
                yield from []
                return

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
