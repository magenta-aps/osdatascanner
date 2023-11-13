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
from django.contrib.postgres.indexes import HashIndex

from os2datascanner.utils.system_utilities import time_now
from os2datascanner.engine2.model.core import Handle
import os2datascanner.engine2.pipeline.messages as messages


logger = structlog.get_logger(__name__)


class ScheduledCheckup(models.Model):
    """A ScheduledCheckup is a reminder to the administration system to test
    the availability of a specific Handle in the next scan.

    These reminders serve two functions: to make sure that objects that were
    transiently unavailable will eventually be included in a scan, and to make
    sure that the report module has a chance to resolve matches associated with
    objects that are later removed."""

    handle_representation = models.JSONField(verbose_name="Reference")
    # The handle to test again.
    interested_before = models.DateTimeField(null=True)
    # The Last-Modified cutoff date to attach to the test.
    scanner = models.ForeignKey('Scanner', related_name="checkups",
                                verbose_name=_('connected scanner job'),
                                on_delete=models.CASCADE)
    # The scanner job that produced this handle.

    @property
    def handle(self) -> Handle:
        return Handle.from_json_object(self.handle_representation)

    def __str__(self):
        return f"{self.scanner}: {self.handle} ({self.pk})"

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.handle} ({self.pk}) from {self.scanner}>"

    class Meta:
        indexes = (
            HashIndex(
                    fields=("handle_representation",),
                    name="sc_cc_lookup"),
        )


class ScanStage(Enum):
    INDEXING = 0
    INDEXING_SCANNING = 1
    SCANNING = 2
    EMPTY = 3


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

    @property
    def stage(self) -> int:
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

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['scanner', 'account'],
            name='os2datascanner_scanner_c_scanner_id_account_id_ec9ff164_uniq')]
