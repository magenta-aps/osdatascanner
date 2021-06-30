# -*- coding: utf-8 -*-
# encoding: utf-8
# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2Webscanner was developed by Magenta in collaboration with OS2 the
# Danish community of open source municipalities (http://www.os2web.dk/).
#
# The code is currently governed by OS2 the Danish community of open
# source municipalities ( http://www.os2web.dk/ )

"""Contains Django model for the scanner types."""

import datetime
import os
import re

from typing import Iterator

from django.db import models
from django.conf import settings
from django.core.validators import validate_comma_separated_integer_list
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _

from model_utils.managers import InheritanceManager
from recurrence.fields import RecurrenceField

from os2datascanner.utils.system_utilities import time_now
from os2datascanner.engine2.model.core import Handle, Source
from os2datascanner.engine2.rules.meta import HasConversionRule
from os2datascanner.engine2.rules.logical import OrRule, AndRule, make_if
from os2datascanner.engine2.rules.dimensions import DimensionsRule
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
import os2datascanner.engine2.pipeline.messages as messages
from os2datascanner.engine2.pipeline.utilities.pika import PikaPipelineSender
from os2datascanner.engine2.conversions.types import OutputType

from ..authentication_model import Authentication
from ..rules.rule_model import Rule

base_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class Scanner(models.Model):

    """A scanner, i.e. a template for actual scanning jobs."""
    objects = InheritanceManager()

    linkable = False

    name = models.CharField(
        max_length=256,
        unique=True,
        null=False,
        db_index=True,
        verbose_name='Navn'
    )

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='scannerjob',
        verbose_name=_('organization'),
        default=None,
        null=True,
    )

    schedule = RecurrenceField(
        max_length=1024,
        null=True,
        blank=True,
        verbose_name='Planlagt afvikling'
    )

    do_ocr = models.BooleanField(
        default=False,
        verbose_name='Scan billeder'
    )

    do_last_modified_check = models.BooleanField(
        default=True,
        verbose_name='Tjek dato for sidste ændring',
    )

    columns = models.CharField(validators=[validate_comma_separated_integer_list],
                               max_length=128,
                               null=True,
                               blank=True
                               )

    rules = models.ManyToManyField(Rule,
                                   blank=True,
                                   verbose_name='Regler',
                                   related_name='scanners')

    # Spreadsheet annotation and replacement parameters

    # Save a copy of any spreadsheets scanned with annotations
    # in each row where matches were found. If this is enabled and any of
    # the replacement parameters are enabled (e.g. do_cpr_replace), matches
    # will also be replaced with the specified text (e.g. cpr_replace_text).
    output_spreadsheet_file = models.BooleanField(default=False)

    # Replace CPRs?
    do_cpr_replace = models.BooleanField(default=False)

    # Text to replace CPRs with
    cpr_replace_text = models.CharField(max_length=2048, null=True,
                                        blank=True)

    # Replace names?
    do_name_replace = models.BooleanField(default=False)

    # Text to replace names with
    name_replace_text = models.CharField(max_length=2048, null=True,
                                         blank=True)
    # Replace addresses?
    do_address_replace = models.BooleanField(default=False)

    # Text to replace addresses with
    address_replace_text = models.CharField(max_length=2048, null=True,
                                            blank=True)

    VALID = 1
    INVALID = 0

    validation_choices = (
        (INVALID, "Ugyldig"),
        (VALID, "Gyldig"),
    )

    url = models.CharField(max_length=2048, blank=False, verbose_name='URL')

    authentication = models.OneToOneField(Authentication,
                                          null=True,
                                          related_name='%(app_label)s_%(class)s_authentication',
                                          verbose_name='Brugernavn',
                                          on_delete=models.SET_NULL)

    validation_status = models.IntegerField(choices=validation_choices,
                                            default=INVALID,
                                            verbose_name='Valideringsstatus')

    exclusion_rules = models.TextField(blank=True,
                                       default="",
                                       verbose_name='Ekskluderingsregler')

    e2_last_run_at = models.DateTimeField(null=True)

    def verify(self) -> bool:
        """Method documentation"""
        raise NotImplementedError("Scanner.verify")

    def exclusion_rule_list(self):
        """Return the exclusion rules as a list of strings or regexes."""
        REGEX_PREFIX = "regex:"
        rules = []
        for line in self.exclusion_rules.splitlines():
            line = line.strip()
            if line.startswith(REGEX_PREFIX):
                rules.append(re.compile(line[len(REGEX_PREFIX):],
                                        re.IGNORECASE))
            else:
                rules.append(line)
        return rules

    @property
    def schedule_description(self):
        """A lambda for creating schedule description strings."""
        if any(self.schedule.occurrences()):
            return u"Ja"
        else:
            return u"Nej"

    # Run error messages
    HAS_NO_RULES = (
        "Scannerjobbet kunne ikke startes," +
        " fordi det ingen tilknyttede regler har."
    )
    NOT_VALIDATED = (
        "Scannerjobbet kunne ikke startes," +
        " fordi det ikke er blevet valideret."
    )
    ALREADY_RUNNING = (
        "Scannerjobbet kunne ikke startes," +
        " da dette scan er igang."
    )

    process_urls = JSONField(null=True, blank=True)

    # Booleans for control of scanners run from web service.
    do_run_synchronously = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)

    # First possible start time
    FIRST_START_TIME = datetime.time(hour=18, minute=0)
    # Amount of quarter-hours that can be added to the start time
    STARTTIME_QUARTERS = 6 * 4

    def get_start_time(self):
        """The time of day the Scanner should be automatically started."""
        # add (minutes|hours) in intervals of 15m depending on `pk`, so each
        # scheduled job start at different times after 18h00m
        added_minutes = 15 * (self.pk % self.STARTTIME_QUARTERS)
        added_hours = int(added_minutes / 60)
        added_minutes -= added_hours * 60
        return self.FIRST_START_TIME.replace(
            hour=self.FIRST_START_TIME.hour + added_hours,
            minute=self.FIRST_START_TIME.minute + added_minutes
        )

    @classmethod
    def modulo_for_starttime(cls, time):
        """Convert a datetime.time object to the corresponding modulo value.

        The modulo value can be used to search the database for scanners that
        should be started at the given time by filtering a query with:
            (WebScanner.pk % WebScanner.STARTTIME_QUARTERS) == <modulo_value>
        """
        if(time < cls.FIRST_START_TIME):
            return None
        hours = time.hour - cls.FIRST_START_TIME.hour
        minutes = 60 * hours + time.minute - cls.FIRST_START_TIME.minute
        return int(minutes / 15)

    @property
    def display_name(self):
        """The name used when displaying the scanner on the web page."""
        return "WebScanner '%s'" % self.name

    def __str__(self):
        """Return the name of the scanner."""
        return self.name

    def run(self, user=None):
        """Schedules a scan to be run by the pipeline. Returns the scan tag of
        the resulting scan on success.

        An exception will be raised if the underlying source is not available,
        and a pika.exceptions.AMQPError (or a subclass) will be raised if it
        was not possible to communicate with the pipeline."""
        now = time_now()

        # Create a new engine2 scan specification
        rule = OrRule.make(
                *[r.make_engine2_rule()
                        for r in self.rules.all().select_subclasses()])

        configuration = {}

        prerules = []
        if self.do_last_modified_check:
            last = self.e2_last_run_at
            if last:
                prerules.append(LastModifiedRule(last))

        if self.do_ocr:
            # If we are doing OCR, then filter out any images smaller than
            # 128x32 (or 32x128)...
            cr = make_if(
                    HasConversionRule(OutputType.ImageDimensions),
                    DimensionsRule(
                            width_range=range(32, 16385),
                            height_range=range(32, 16385),
                            min_dim=128),
                    True)
            prerules.append(cr)
        else:
            # ... and, if we're not, then skip all of the image files
            configuration["skip_mime_types"] = ["image/*"]

        rule = AndRule.make(*prerules, rule)

        scan_tag = messages.ScanTagFragment(
                time=now,
                user=user.username if user else None,
                scanner=messages.ScannerFragment(
                        pk=self.pk,
                        name=self.name),
                organisation=messages.OrganisationFragment(
                        name=self.organization.name,
                        uuid=self.organization.uuid))

        # Build ScanSpecMessages for all Sources
        message_template = messages.ScanSpecMessage(scan_tag=scan_tag,
                rule=rule, configuration=configuration, source=None,
                progress=None)
        outbox = []
        source_count = 0
        for source in self.generate_sources():
            outbox.append((settings.AMQP_PIPELINE_TARGET,
                    message_template._replace(source=source)))
            source_count += 1

        if source_count == 0:
            raise ValueError(f"{self} produced 0 explorable sources")

        # Also build ConversionMessages for the objects that we should try to
        # scan again (our pipeline_collector is responsible for eventually
        # deleting these reminders)
        message_template = messages.ConversionMessage(
                scan_spec=message_template,
                handle=None, progress=messages.ProgressFragment(
                        rule=None,
                        matches=[]))
        for reminder in self.checkups.all():
            ib = reminder.interested_before
            rule_here = AndRule.make(
                    LastModifiedRule(ib) if ib else True,
                    rule)
            outbox.append((settings.AMQP_CONVERSION_TARGET,
                    message_template._deep_replace(
                            scan_spec__source=reminder.handle.source,
                            handle=reminder.handle,
                            progress__rule=rule_here)))

        self.e2_last_run_at = now
        self.save()

        # OK, we're committed now! Create a model object to track the status of
        # this scan...
        ScanStatus.objects.create(
                scanner=self, scan_tag=scan_tag.to_json_object(),
                total_sources=source_count,
                total_objects=self.checkups.count())

        # ... and dispatch the scan specifications to the pipeline
        with PikaPipelineSender(write={queue for queue, _ in outbox}) as pps:
            for queue, message in outbox:
                pps.publish_message(queue, message.to_json_object())

        return scan_tag.to_json_object()

    def path_for(self, uri):
        return uri

    def generate_sources(self) -> Iterator[Source]:
        """Yields one or more engine2 Sources corresponding to the target of
        this Scanner."""
        # (this can't use the @abstractmethod decorator because of metaclass
        # conflicts with Django, but subclasses should override this method!)
        raise NotImplementedError("Scanner.generate_sources")
        yield from []

    class Meta:
        abstract = False
        ordering = ['name']


class ScheduledCheckup(models.Model):
    """A ScheduledCheckup is a reminder to the administration system to test
    the availability of a specific Handle in the next scan.

    These reminders serve two functions: to make sure that objects that were
    transiently unavailable will eventually be included in a scan, and to make
    sure that the report module has a chance to resolve matches associated with
    objects that are later removed."""

    handle_representation = JSONField(verbose_name="Reference")
    """The handle to test again."""
    interested_before = models.DateTimeField(null=True)
    """The Last-Modified cutoff date to attach to the test."""
    scanner = models.ForeignKey(Scanner, related_name="checkups",
                                verbose_name="Tilknyttet scannerjob",
                                on_delete=models.CASCADE)
    """The scanner job that produced this handle."""

    @property
    def handle(self):
        return Handle.from_json_object(self.handle_representation)


class ScanStatus(models.Model):
    """A ScanStatus object collects the status messages received from the
    pipeline for a given scan."""

    scan_tag = JSONField(verbose_name=_("scan tag"), unique=True)

    scanner = models.ForeignKey(Scanner, related_name="statuses",
                                verbose_name=_("associated scanner job"),
                                on_delete=models.CASCADE)

    total_sources = models.IntegerField(verbose_name=_("total sources"),
                                       null=True)
    explored_sources = models.IntegerField(verbose_name=_("explored sources"),
                                         null=True)

    total_objects = models.IntegerField(verbose_name=_("total objects"),
                                        null=True)
    scanned_objects = models.IntegerField(verbose_name=_("scanned objects"),
                                          null=True)
    scanned_size = models.BigIntegerField(
            verbose_name=_("size of scanned objects"),
            null=True)

    @property
    def finished(self) -> bool:
        return (self.total_sources is not None
                and self.total_sources == self.explored_sources
                and self.total_objects is not None
                and self.total_objects == self.scanned_objects)

    @property
    def fraction_explored(self) -> float:
        """Returns the fraction of the sources in this scan that has been
        explored, or None if this is not yet computable."""
        if self.total_sources:
            return (self.explored_sources or 0) / self.total_sources
        else:
            return None

    @property
    def fraction_scanned(self) -> float:
        """Returns the fraction of this scan that has been scanned, or None if
        this is not yet computable."""
        if self.fraction_explored == 1.0 and self.total_objects:
            return (self.scanned_objects or 0) / self.total_objects
        else:
            return None

    @property
    def estimated_completion_time(self) -> datetime.datetime:
        """Returns the linearly interpolated completion time of this scan
        based on the return value of ScannerStatus.fraction_scanned (or None,
        if that function returns None).

        Note that the return value of this function is only meaningful if
        fraction_scanned is less than 1.0: at that point, it always returns the
        current time."""
        fraction_scanned = self.fraction_scanned
        if (fraction_scanned is not None
                and fraction_scanned >= settings.ESTIMATE_AFTER):
            start = self.start_time
            so_far = time_now() - start
            total_duration = so_far / fraction_scanned
            return start + total_duration
        else:
            return None

    @property
    def start_time(self) -> datetime.datetime:
        """Returns the start time of this scan."""
        return messages.ScanTagFragment.from_json_object(self.scan_tag).time

    class Meta:
        verbose_name = _("scan status")
        verbose_name_plural = _("scan statuses")
