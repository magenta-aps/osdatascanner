# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from enum import Enum
import datetime
from datetime import timedelta
import structlog
from statistics import linear_regression

from django.db import models
from django.db.models import F, Q
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User

from os2datascanner.utils.system_utilities import time_now
from os2datascanner.engine2.model.core import Handle
import os2datascanner.engine2.pipeline.messages as messages
import pika.exceptions
from os2datascanner.engine2.pipeline.utilities.pika import (
        PikaPipelineThread, PikaConnectionHolder)


logger = structlog.get_logger("adminapp")


class ScheduledCheckup(models.Model):
    """A ScheduledCheckup is a reminder to the administration system to test
    the availability of a specific Handle in the next scan.

    These reminders serve two functions: to make sure that objects that were
    transiently unavailable will eventually be included in a scan, and to make
    sure that the report module has a chance to resolve matches associated with
    objects that are later removed."""

    handle_representation = models.JSONField(verbose_name="Reference")
    """The (censored) Handle to revisit."""

    interested_after = models.DateTimeField(null=True)
    """The Last-Modified cutoff date to attach to the test."""

    scanner = models.ForeignKey('Scanner', related_name="checkups",
                                verbose_name=_('connected scanner job'),
                                on_delete=models.CASCADE)
    """The scanner job that produced this Handle."""

    # This field has a length of 256 for (bad) historic reasons. The thing we
    # store in it nowadays is a 64-byte SHA-512 hash
    path = models.CharField(max_length=256, verbose_name=_('path'))
    """A hashed form of the censored Handle. (Also the form used by the report
    module to uniquely identify a scanned object.)"""

    @property
    def handle(self) -> Handle:
        return Handle.from_json_object(self.handle_representation)

    def __str__(self):
        return f"{self.scanner}: {self.handle} ({self.pk})"

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.handle} ({self.pk}) from {self.scanner}>"

    class Meta:
        indexes = (
            models.Index(
                    fields=("path",),
                    name="scheduled_checkup_path_index"),
        )


class ScanStage(Enum):
    INDEXING = 0
    INDEXING_SCANNING = 1
    SCANNING = 2
    EMPTY = 3
    FAILED = 4


class AbstractScanStatus(models.Model):
    """
    Abstract base class for models relating to the status of a scanner job.
    """

    total_sources = models.IntegerField(
        verbose_name=_("total sources"),
        default=0,
    )

    explored_sources = models.IntegerField(
        verbose_name=_("explored sources"),
        default=0,
    )

    total_objects = models.IntegerField(
        verbose_name=_("total objects"),
        default=0,
    )

    scanned_objects = models.IntegerField(
        verbose_name=_("scanned objects"),
        default=0,
    )

    scanned_size = models.BigIntegerField(
            verbose_name=_("size of scanned objects"),
            default=0,
    )

    message = models.TextField(
        blank=True,
        verbose_name=_('message'),
    )

    status_is_error = models.BooleanField(
        default=False,
    )

    matches_found = models.IntegerField(
        verbose_name=_("matches found"),
        default=0,
        null=True,
        blank=True
    )

    skipped_by_last_modified = models.IntegerField(
        verbose_name=_("files skipped by last modified check"),
        default=0,
        null=True,
        blank=True
    )

    cancelled = models.BooleanField(default=False, verbose_name=_("cancelled"))

    @property
    def stage(self) -> int:
        # Something has gone wrong
        if self.status_is_error:
            return ScanStage.FAILED
        # Workers have not begun scanning any objects yet
        if self.fraction_scanned is None:
            if self.explored_sources >= 0 and self.fraction_explored < 1.0:
                # The explorer is definitely running
                if self.scanned_objects == 0:
                    # The explorer is running, but the scanner is waiting
                    return ScanStage.INDEXING
                # The explorer and worker are running in parallel
                return ScanStage.INDEXING_SCANNING
            elif self.fraction_explored == 1.0:
                # The explorer has finished and did not find any objects
                return ScanStage.EMPTY

        # Workers are scanning objects. Everything is good.
        return ScanStage.SCANNING

    @property
    def finished(self) -> bool:
        return self.fraction_explored == 1.0 and self.fraction_scanned == 1.0

    @property
    def is_running(self) -> bool:
        return (not self.finished and not self.cancelled)

    @property
    def fraction_explored(self) -> float | None:
        """Returns the fraction of the sources in this scan that has been
        explored, or None if this is not yet computable.

        This value is clamped, and can never exceed 1.0."""
        if self.total_sources > 0:
            return min(
                    (self.explored_sources or 0) / self.total_sources, 1.0)
        elif self.explored_sources == 0 and self.total_objects != 0:
            # We've explored zero of zero sources, but there are some objects?
            # This scan must consist only of checkups
            return 1.0
        else:
            return None

    @property
    def fraction_scanned(self) -> float | None:
        """Returns the fraction of this scan that has been scanned, or None if
        this is not yet computable.

        This value is clamped, and can never exceed 1.0."""
        if self.fraction_explored == 1.0 and self.total_objects > 0:
            return min(
                    (self.scanned_objects or 0) / self.total_objects, 1.0)
        else:
            return None

    @property
    def new_objects(self) -> int:
        return self.total_objects - self.skipped_by_last_modified

    class Meta:
        abstract = True


def inv_linear_func(y, a, b):
    return (y - b)/a if a != 0 else None


class ScanStatus(AbstractScanStatus):
    """A ScanStatus object collects the status messages received from the
    pipeline for a given scan."""

    _completed_Q = (
            Q(total_objects__gt=0)
            & Q(explored_sources=F('total_sources'))
            & Q(scanned_objects__gte=F('total_objects')))

    _completed_or_cancelled_Q = _completed_Q | Q(cancelled=True)

    last_modified = models.DateTimeField(
        verbose_name=_("last modified"),
        default=timezone.now,
    )

    scan_tag = models.JSONField(
        verbose_name=_("scan tag"),
        unique=True,
    )

    scanner = models.ForeignKey(
        'Scanner',
        related_name="statuses",
        verbose_name=_("associated scanner job"),
        on_delete=models.CASCADE,
    )

    resolved = models.BooleanField(
        verbose_name=_("resolved"),
        default=False
    )

    email_sent = models.BooleanField(
        verbose_name=_("has an email notification been sent"),
        default=False
    )

    @property
    def estimated_completion_time(self) -> datetime.datetime | None:
        """Returns an estimate of the completion time of the scan, based on a
        linear fit to the last 20% of the existing ScanStatusSnapshot objects."""

        if (self.fraction_scanned is None
                or self.fraction_scanned < settings.ESTIMATE_AFTER):
            return None
        else:
            snapshots = list(ScanStatusSnapshot.objects.filter(
                scan_status=self, total_objects__isnull=False).values(
                "time_stamp", "scanned_objects", "total_objects").order_by("time_stamp"))

            # To give an estimate of completion, the number of snapshots _must_
            # be 2 or more.
            if len(snapshots) < 2:
                return None

            width = 0.2  # Percentage of all data points

            # The window function needs to include at least two points, but it's
            # better to include at least ten, to iron out the worst local
            # phenomena.
            window = max([int(len(snapshots)*width), 10])

            time_data = [(obj.get("time_stamp") - self.start_time).total_seconds()
                         for obj in snapshots[-window:]]
            frac_scanned = [obj.get("scanned_objects")/obj.get("total_objects")
                            for obj in snapshots[-window:]]

            a, b = linear_regression(time_data, frac_scanned)

            try:
                end_time_guess = timedelta(
                    seconds=inv_linear_func(
                        1.0, a, b)) + self.start_time
            except Exception as e:
                logger.exception(
                    f'Exception while calculating end time for scan {self.scanner}: {e}')
                return None

            if end_time_guess > time_now():
                return end_time_guess
            else:
                return None

    @property
    def start_time(self) -> datetime.datetime:
        """Returns the start time of this scan."""
        return messages.ScanTagFragment.from_json_object(self.scan_tag).time
    start_time.fget.short_description = _('Start time')

    class Meta:
        verbose_name = _("scan status")
        verbose_name_plural = _("scan statuses")

        indexes = [
            models.Index(
                    fields=("scanner", "scan_tag",),
                    name="ss_pc_lookup"),
        ]

        get_latest_by = "scan_tag__time"

        permissions = [
            ("resolve_scanstatus", _("Can resolve scan statuses")),
            ("export_completed_scanstatus", _("Can export history of completed scans")),
            ("cancel_scanstatus", _("Can cancel running scan"))
        ]

    def __str__(self):
        return f"{self.scanner}: {self.start_time}"

    @classmethod
    def clean_defunct(cls) -> set['ScanStatus']:
        """Updates all defunct ScanStatus objects to appear as though they
        completed normally. (A defunct ScanStatus is one that's at least 99.5%
        complete but that hasn't received any new status messages in the last
        hour.)

        Returns a set of all the ScanStatus objects modified by this
        function."""
        now = time_now()
        rv = set()
        for ss in cls.objects.exclude(
                cls._completed_Q).filter(
                last_modified__lte=now - timedelta(hours=1)).iterator():
            if (ss.fraction_scanned is not None
                    and ss.fraction_scanned >= 0.995):
                # This ScanStatus is essentially complete but hasn't been
                # updated in the last hour; a status message or two must have
                # gone missing. Mark it as done to avoid cluttering the UI
                logger.warning(
                        "marking defunct ScanStatus as complete",
                        scan_status=ss,
                        total_objects=ss.total_objects,
                        scanned_objects=ss.scanned_objects)
                ss.scanned_objects = ss.total_objects
                rv.add(ss)
                ss.save()
        return rv

    def cancel(self, cancelled_by: User | None = None):
        """Queues a message to RabbitMQ, telling all pipeline processes to throw away all
        future messages from this job."""
        if self.is_running:
            # Instruct the pipeline to throw out all future messages from this scan
            cancel_scan_tag_messages(self.scan_tag, purge_queue=True)

            # Remove CoveredAccounts for this scan to make sure no accounts are skipped during next
            # scan on account of this scan.
            CoveredAccount.objects.filter(scan_status=self).delete()

            # Update this object to correctly reflect that it has been cancelled
            self.cancelled = True
            self.save()
            logger.info(
                "ScanStatus cancelled.",
                status=self,
                cancelled_by=cancelled_by if cancelled_by else "unknown")
        else:
            logger.warning("Tried to cancel a scannerjob which is not running. Doing nothing.")

    def timeline(self) -> list[dict]:
        """Returns a timeline of percentage scanned over time in the format:
            [
                {"x": <float>, "y": <float>},
                {"x": <float>, "y": <float>},
                ...
            ]
            where "x" denoted the time since scan start time in seconds and "y" denotes the
            percentage of all objects scanned at the given time.

            Snapshots are filtered for at least one scanned object, to be in line with presented
            run time. (See StatusCompletedView)

            Ordered by time_stamp to ensure chartjs receives data in logical order.
            """
        snapshot_data = []
        for snapshot in ScanStatusSnapshot.objects.filter(
                scan_status=self, scanned_objects__gte=1).order_by('time_stamp').iterator():
            seconds_since_start = (snapshot.time_stamp - self.start_time).total_seconds()
            # Calculating a new fraction, due to early versions of
            # snapshots not knowing the total number of objects.
            fraction_scanned = snapshot.scanned_objects/self.total_objects
            snapshot_data.append({"x": seconds_since_start, "y": fraction_scanned*100})
        return snapshot_data

    def data_types(self) -> dict:
        """Return a dict of size and time spent scanning different MIME types covered by scan."""
        stats = {}
        for stat in self.process_stats.iterator():
            stats[stat.file_type] = {"size": stat.total_size, "time": stat.total_time}
        return stats


class ScanStatusSnapshot(AbstractScanStatus):
    """
    Snapshot of a ScanStatus object, where the attributes of ScanStatus
    are copied and stored for analysis.
    """

    scan_status = models.ForeignKey(
        ScanStatus,
        on_delete=models.CASCADE,
        related_name="snapshots"
    )

    time_stamp = models.DateTimeField(
        verbose_name=_("timestamp"),
        default=timezone.now,
    )

    def __str__(self):
        return f"{self.scan_status.scanner}: {self.time_stamp}"

    class Meta:
        verbose_name = _("scan status snapshot")
        verbose_name_plural = _("scan status snapshots")


class CoveredAccount(models.Model):
    scanner = models.ForeignKey(
            'os2datascanner.Scanner', null=False, on_delete=models.CASCADE)
    account = models.ForeignKey(
            'organizations.Account', null=False, on_delete=models.CASCADE)
    scan_status = models.ForeignKey(
            ScanStatus, null=False, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                    fields=['scanner', 'account', 'scan_status'],
                    name='%(app_label)s_%(class)s_no_exact_dupes'),
        ]
        # Ordering by scan tag start time lets you get the most recent
        # CoveredAccount for a given Account/Scanner pair with
        #
        #     CoveredAccount.objects.filter(account=..., scanner=...).latest()
        get_latest_by = "scan_status__scan_tag__time"


mime_to_file_map = {
    "application/javascript": _("javascript file"),
    "application/json": _("JSON file"),
    "application/msonenote": _("OneNote"),
    "application/msword": _("Word document (.doc)"),
    "application/octet-stream": pgettext_lazy("MIME type", "unknown file type"),
    "application/vnd.ms-excel": _("Excel workbook (.xls)"),
    "application/vnd.ms-excel.addin.macroEnabled.12": _("Excel add-in (.xlam)"),
    "application/vnd.ms-excel.sheet.binary.macroEnabled.12": _("Excel binary workbook (.xlsb)"),
    "application/vnd.ms-excel.sheet.macroEnabled.12": _("Excel macro-enabled workbook (.xlsm)"),
    "application/vnd.ms-excel.template.macroEnabled.12": _("Excel macro-enabled template (.xltm)"),
    "application/vnd.ms-powerpoint.addin.macroEnabled.12": _("PowerPoint add-in (.ppam)"),
    "application/vnd.ms-powerpoint.presentation.macroEnabled.12": _(
        "PowerPoint macro-enabled presentation (.pptm)"),
    "application/vnd.ms-powerpoint.slide.macroEnabled.12": _(
        "PowerPoint macro-enabled slide (.sldm)"),
    "application/vnd.ms-powerpoint.slideshow.macroEnabled.12": _(
        "PowerPoint macro-enabled slide show (.ppsm)"),
    "application/vnd.ms-powerpoint.template.macroEnabled.12": _(
        "PowerPoint macro-enabled template (.potm)"),
    "application/vnd.magenta.osds.sbsys-case": _("SBSYS case"),
    "application/vnd.ms-word.document.macroEnabled.12": _("Word macro-enabled document (.docm)"),
    "application/vnd.oasis.opendocument.base": _("OpenDocument database (.odb)"),
    "application/vnd.oasis.opendocument.chart": _("OpenDocument chart (.odc)"),
    "application/vnd.oasis.opendocument.chart-template": _("OpenDocument chart template (.otc)"),
    "application/vnd.oasis.opendocument.graphics": _("OpenDocument drawing (.odg)"),
    "application/vnd.oasis.opendocument.graphics-template": _(
        "OpenDocument drawing template (.otg)"),
    "application/vnd.oasis.opendocument.formula": _("OpenDocument formula (.odf)"),
    "application/vnd.oasis.opendocument.formula-template": _(
        "OpenDocument formula template (.otf)"),
    "application/vnd.oasis.opendocument.image": _("OpenDocument image (.odi)"),
    "application/vnd.oasis.opendocument.image-template": _("OpenDocument image template (.oti)"),
    "application/vnd.oasis.opendocument.presentation": _("OpenDocument presentation (.odp)"),
    "application/vnd.oasis.opendocument.presentation-template": _(
        "OpenDocument presentation template (.otp)"),
    "application/vnd.oasis.opendocument.spreadsheet": _("OpenDocument spreadsheet (.ods)"),
    "application/vnd.oasis.opendocument.spreadsheet-template": _(
        "OpenDocument spreadsheet template (.ots)"),
    "application/vnd.oasis.opendocument.text": _("OpenDocument text file (.odt)"),
    "application/vnd.oasis.opendocument.text-master": _("OpenDocument master file (.odm)"),
    "application/vnd.oasis.opendocument.text-template": _("OpenDocument text template (.ott)"),
    "application/vnd.oasis.opendocument.text-web": _("OpenDocument web page template (.oth)"),
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": _(
        "PowerPoint presentation (.pptx)"),
    "application/vnd.openxmlformats-officedocument.presentationml.slide": _(
        "PowerPoint slide (.sldx)"),
    "application/vnd.openxmlformats-officedocument.presentationml.slideshow": _(
        "PowerPoint slide show (.ppsx)"),
    "application/vnd.openxmlformats-officedocument.presentationml.template": _(
        "PowerPoint template (.potx)"),
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": _(
        "Excel workbook (.xlsx)"),
    "application/vnd.openxmlformats-officedocument.spreadsheetml.template": _(
        "Excel template (.xltx)"),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": _(
        "Word document (.docx)"),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.template": _(
        "Word template (.dotm)"),
    "application/pdf": _("PDF file"),
    "application/xml": _("XML file"),
    "application/xml-sitemap": _("XML sitemap"),
    "application/zip": _("ZIP file"),
    "image/gif": _("GIF image"),
    "image/jpeg": _("JPEG image"),
    "image/jpg": _("JPG image"),
    "image/png": _("PNG image"),
    "image/svg+xml": _("SVG image"),
    "image/webp": _("WEPB image"),
    "image/x-icon": _("icon (.ico)"),
    "message/rfc822": _("email message"),
    "text/css": _("CSS file"),
    "text/csv": _("CSV file"),
    "text/html": _("HTML file"),
    "text/javascript": _("javascript file"),
    "text/plain": _("text file"),
    "text/xml": _("XML file"),
}


class MIMETypeProcessStat(models.Model):
    scan_status = models.ForeignKey(
        ScanStatus,
        on_delete=models.CASCADE,
        related_name="process_stats"
    )

    mime_type = models.CharField(
        max_length=256,
        verbose_name=_("MIME type"),
    )

    total_time = models.DurationField(
        default=0
    )

    total_size = models.PositiveBigIntegerField(
        default=0,
        verbose_name=_("Total size in bytes")
    )

    object_count = models.PositiveIntegerField(
        default=0,
    )

    @property
    def file_type(self):
        return mime_to_file_map.get(self.mime_type, self.mime_type)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['scan_status', 'mime_type'],
                name='unique_MIME_type_scan_status'
            )
        ]


def _per_scan_queue_name(tag: dict) -> str | None:
    """Returns the per-scan conversion queue name for the given scan tag dict,
    or None if the tag is too old/incomplete to derive one."""
    tag_obj = messages.ScanTagFragment.from_json_object(tag)
    if tag_obj.scanner and tag_obj.time:
        safe_time = tag_obj.time.strftime("%Y%m%dT%H%M%S")
        return f"os2ds_conversions.{tag_obj.scanner.pk}_{safe_time}"
    return None


def _purge_queue(queue_name: str):
    """Purges all messages from the named RabbitMQ queue if it exists."""
    try:
        with PikaConnectionHolder() as conn:
            conn.channel.queue_purge(queue_name)
            logger.info("Purged per-scan conversion queue", queue=queue_name)
    except pika.exceptions.ChannelClosedByBroker:
        # Queue doesn't exist — scan may have already completed and been cleaned up
        logger.debug("Per-scan queue not found during purge", queue=queue_name)
    except Exception:
        logger.warning(
                "Could not purge per-scan queue",
                queue=queue_name, exc_info=True)


def notify_new_conversion_queue(queue_name: str):
    """Declares the per-scan conversion queue on the broker and broadcasts a
    CommandMessage telling all pipeline workers to subscribe to it. Must be
    called before dispatching any ScanSpecMessages that route to that queue,
    so the queue exists before the explorer starts publishing to it."""
    msg = messages.CommandMessage(new_queue=queue_name)
    with PikaPipelineThread(write={queue_name}) as p:
        p.enqueue_message("", msg.to_json_object(), "broadcast", priority=10)
        p.enqueue_stop()
        p.run()


def cancel_scan_tag_messages(tag: dict, purge_queue: bool = False):
    """Requests that all running pipeline components blacklist and ignore
    messages from the scan tag.

    If purge_queue is True, also instantly purges the per-scan conversion
    queue so workers do not need to drain it message-by-message. Only pass
    True for explicit user-initiated cancellation — not for error recovery
    or cleanup paths, where the scan may still be producing valid results."""
    msg = messages.CommandMessage(
            abort=messages.ScanTagFragment.from_json_object(tag))
    with PikaPipelineThread() as p:
        p.enqueue_message(
                "", msg.to_json_object(),
                "broadcast", priority=10)
        p.enqueue_stop()
        p.run()

    if purge_queue:
        # Fast path: discard all queued conversion messages server-side in one
        # operation, instead of each being individually dequeued and rejected.
        if queue_name := _per_scan_queue_name(tag):
            _purge_queue(queue_name)


@receiver(post_delete)
def post_delete_callback(sender, instance, using, **kwargs):
    """Signal handler for post_delete."""
    if not isinstance(instance, ScanStatus):
        return

    cancel_scan_tag_messages(instance.scan_tag, purge_queue=True)
    logger.info("ScanStatus deleted. Sending abort message to message queue.", instance=instance)
