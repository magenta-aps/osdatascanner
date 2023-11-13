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

import os
from typing import Iterator
import datetime
import structlog

from django.db import models
from django.conf import settings
from django.core.validators import validate_comma_separated_integer_list
from django.db.models.signals import post_delete
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver

from model_utils.managers import InheritanceManager
from recurrence.fields import RecurrenceField

from os2datascanner.utils.system_utilities import time_now
from os2datascanner.engine2.model.core import Source
from os2datascanner.engine2.rules.meta import HasConversionRule
from os2datascanner.engine2.rules.logical import OrRule, AndRule, AllRule, make_if
from os2datascanner.engine2.rules.dimensions import DimensionsRule
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
import os2datascanner.engine2.pipeline.messages as messages
from os2datascanner.engine2.pipeline.utilities.pika import PikaPipelineThread
from os2datascanner.engine2.conversions.types import OutputType
from os2datascanner.engine2.pipeline.headers import get_exchange, get_headers
from mptt.models import TreeManyToManyField

from .scanner_helpers import (  # noqa (interface backwards compatibility)
        ScanStatus, CoveredAccount, ScheduledCheckup, ScanStatusSnapshot)
from ..rules.rule import Rule
from ..authentication import Authentication


logger = structlog.get_logger(__name__)
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
        verbose_name=_('name')
    )

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='scannerjob',
        verbose_name=_('organization'),
        default=None,
        null=True,
    )

    org_unit = TreeManyToManyField(
        "organizations.OrganizationalUnit",
        related_name="scanners",
        blank=True,
        verbose_name=_("organizational unit"),
    )

    schedule = RecurrenceField(
        max_length=1024,
        null=True,
        blank=True,
        verbose_name=_('planned execution')
    )

    do_ocr = models.BooleanField(
        default=False,
        verbose_name=_('scan images')
    )

    do_last_modified_check = models.BooleanField(
        default=True,
        verbose_name=_('check date of last modification'),
    )

    only_notify_superadmin = models.BooleanField(
        default=False,
        verbose_name=_('only notify superadmin'),
    )

    keep_false_positives = models.BooleanField(
        default=True,
        verbose_name=_('keep false positives'),
        help_text=_('Retain false positives in the report module, regardless '
                    'of the current state of the matched sources.')
    )

    columns = models.CharField(validators=[validate_comma_separated_integer_list],
                               max_length=128,
                               null=True,
                               blank=True
                               )

    rules = models.ManyToManyField(Rule,
                                   blank=True,
                                   verbose_name=_('rules'),
                                   related_name='scanners')

    VALID = 1
    INVALID = 0

    validation_choices = (
        (INVALID, _('Unverified')),
        (VALID, _('Verified')),
    )

    authentication = models.OneToOneField(Authentication,
                                          null=True,
                                          related_name='%(app_label)s_%(class)s_authentication',
                                          verbose_name=_('username'),
                                          on_delete=models.SET_NULL)

    validation_status = models.IntegerField(choices=validation_choices,
                                            default=INVALID,
                                            verbose_name=_('validation status'))

    exclusion_rules = models.ManyToManyField(Rule,
                                             blank=True,
                                             verbose_name=_('exclusion rules'),
                                             related_name='scanners_ex_rules')

    covered_accounts = models.ManyToManyField(
            'organizations.Account',
            blank=True, through=CoveredAccount,
            verbose_name=_('covered accounts'),
            related_name='covered_by_scanner')

    def verify(self) -> bool:
        """Method documentation"""
        raise NotImplementedError("Scanner.verify")

    @property
    def needs_revalidation(self) -> bool:
        """Used to check if the url on a form object differs from the
        corresponding field on the model object."""
        return False

    @property
    def schedule_date(self) -> datetime.date | None:
        """Returns the date for the next scheduled execution of this scanner,
        if there is one."""
        today = time_now().date()
        for oc in self.schedule.occurrences():
            # Check that the date is at least today -- otherwise we might pick
            # an old one-off scan and declare that the next scan will have been
            # yesterday
            if (date := oc.date()) >= today:
                return date
        return None

    @property
    def schedule_time(self):
        """Returns the time for the next scheduled execution of this scanner,
        if there is one."""
        if self.schedule_date is not None:
            return self.get_start_time()

    # Run error messages
    HAS_NO_RULES = (
        _("The scanner job could not be started because it has no assigned rules.")
    )
    NOT_VALIDATED = (
        _("The scanner job could not be started because it is not validated.")
    )
    ALREADY_RUNNING = (
        _("The scanner job could not be started because it is already running.")
    )

    # First possible start time
    FIRST_START_TIME = datetime.time(hour=19, minute=0)
    # Amount of quarter-hours that can be added to the start time
    STARTTIME_QUARTERS = 5 * 4

    def get_start_time(self) -> datetime.time:
        """Returns the time of day at which this scanner can be considered for
        scheduled execution.

        The current implementation of this method always returns a time between
        7pm and midnight; this time is not configurable, but is derived from
        the primary key of the scanner in an attempt to spread executions
        out."""
        # add (minutes|hours) in intervals of 15m depending on `pk`, so each
        # scheduled job start at different times after 19h00m
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

    def local_or_rules(self) -> list:
        """Returns a list of OR rules specific for the scanner model
        """
        return []

    def local_and_rules(self) -> list:
        """Returns a list of AND rules specific for the scanner model
        """
        return []

    def local_all_rules(self) -> list:
        """Returns a list of ALL rules specific for the scanner model
        """
        return []

    def _construct_scan_tag(self, user=None):
        """Builds a scan tag fragment that describes a scan (started now) under
        this scanner."""
        return messages.ScanTagFragment(
                time=time_now(),
                user=user.username if user else None,
                scanner=messages.ScannerFragment(
                        pk=self.pk,
                        name=self.name,
                        test=self.only_notify_superadmin,
                        keep_fp=self.keep_false_positives),
                organisation=messages.OrganisationFragment(
                        name=self.organization.name,
                        uuid=self.organization.uuid))

    def _construct_configuration(self):
        """Builds a configuration dictionary based on the parameters of this
        scanner."""
        return {} if self.do_ocr else {"skip_mime_types": ["image/*"]}

    def _construct_rule(self, force: bool) -> Rule:
        """Builds an object that represents the rules configured for this
        scanner."""
        rule = OrRule.make(
                *[r.make_engine2_rule()
                  for r in self.rules.all().select_subclasses()])

        prerules = []
        if not force and self.do_last_modified_check:
            last = self.get_last_successful_run_at()
            if last:
                prerules.append(LastModifiedRule(last))

        if self.do_ocr:
            # If we're doing OCR, then filter out any images smaller than
            # 128x32 (or 32x128)
            cr = make_if(
                    HasConversionRule(OutputType.ImageDimensions),
                    DimensionsRule(
                            width_range=range(32, 16385),
                            height_range=range(32, 16385),
                            min_dim=128),
                    True)
            prerules.append(cr)

        # append any model-specific rules. Order matters!
        # AllRule will evaluate all rules, no matter the outcome of current rule
        # AndRule will only evaluate next rule, if current rule have match
        # OrRule will stop evaluating as soon as one rule have match
        rule = AllRule.make(*self.local_all_rules(), rule)
        rule = OrRule.make(*self.local_or_rules(), rule)
        rule = AndRule.make(*self.local_and_rules(), rule)

        # prerules includes: do_ocr, LastModifiedRule
        return AndRule.make(*prerules, rule)

    def _construct_filter_rule(self) -> Rule:
        try:
            return OrRule.make(
                *[er.make_engine2_rule()
                  for er in self.exclusion_rules.all().select_subclasses()])
        except ValueError:
            pass
        return None

    def _construct_scan_spec_template(self, user, force: bool) -> (
            messages.ScanSpecMessage):
        """Builds a scan specification template for this scanner. This template
        has no associated Source, so make sure you put one in with the _replace
        or _deep_replace methods before trying to scan with it."""
        rule = self._construct_rule(force)
        filter_rule = self._construct_filter_rule()
        scan_tag = self._construct_scan_tag(user)
        configuration = self._construct_configuration()

        return messages.ScanSpecMessage(
                scan_tag=scan_tag, rule=rule, configuration=configuration,
                filter_rule=filter_rule, source=None, progress=None)

    def _add_sources(
            self, spec_template: messages.ScanSpecMessage,
            outbox: list) -> int:
        """Creates scan specifications, based on the provided scan
        specification template, for every Source covered by this scanner, and
        puts them into the provided outbox list. Returns the number of sources
        added."""
        source_count = 0
        for source in self.generate_sources():
            outbox.append((
                settings.AMQP_PIPELINE_TARGET,
                spec_template._replace(source=source)))
            source_count += 1
        return source_count

    def _add_checkups(
            self, spec_template: messages.ScanSpecMessage,
            outbox: list,
            force: bool,
            queue_suffix=None) -> int:
        """Creates instructions to rescan every object covered by this
        scanner's ScheduledCheckup objects (in the process deleting objects no
        longer covered by one of this scanner's Sources), and puts them into
        the provided outbox list. Returns the number of checkups added."""
        uncensor_map = {
                source.censor(): source for source in self.generate_sources()}

        conv_template = messages.ConversionMessage(
                scan_spec=spec_template,
                handle=None,
                progress=messages.ProgressFragment(
                    rule=None,
                    matches=[]))
        checkup_count = 0
        for reminder in self.checkups.iterator():
            rh = reminder.handle

            # for/else is one of the more obscure Python loop constructs, but
            # it is precisely what we want here: the else clause is executed
            # only when the for loop *isn't* stopped by a break statement
            for handle in rh.walk_up():
                if handle.source in uncensor_map:
                    # One of the Sources that contains this checkup's Handle is
                    # still relevant for us. Abort the walk up the tree
                    break
            else:
                # This checkup refers to a Source that we no longer care about
                # (for example, an account that's been removed from the scan).
                # Delete it
                reminder.delete()
                continue

            rh = rh.remap(uncensor_map)

            # XXX: we could be adding LastModifiedRule twice
            ib = reminder.interested_before
            rule_here = AndRule.make(
                    LastModifiedRule(ib) if ib and not force else True,
                    spec_template.rule)
            outbox.append((settings.AMQP_CONVERSION_TARGET,
                           conv_template._deep_replace(
                               scan_spec__source=rh.source,
                               handle=rh,
                               progress__rule=rule_here),
                           ),)
            checkup_count += 1
        return checkup_count

    def run(
            self, user=None,
            explore: bool = True,
            checkup: bool = True,
            force: bool = False):  # noqa: CCR001
        """Schedules a scan to be run by the pipeline. Returns the scan tag of
        the resulting scan on success.

        If the @explore flag is False, no ScanSpecMessages will be emitted for
        this Scanner's Sources. If the @checkup flag is False, no
        ConversionMessages will be emitted for this Scanner's
        ScheduledCheckups. (If both of these flags are False, then this method
        will have nothing to do and will raise an exception.)

        If the @force flag is True, then no Last-Modified checks will be
        requested, not even for ScheduledCheckup objects.

        An exception will be raised if the underlying source is not available,
        and a pika.exceptions.AMQPError (or a subclass) will be raised if it
        was not possible to communicate with the pipeline."""

        spec_template = self._construct_scan_spec_template(user, force)
        scan_tag = spec_template.scan_tag

        outbox = []

        source_count = 0
        if explore:
            source_count = self._add_sources(spec_template, outbox)

            if source_count == 0:
                raise ValueError(f"{self} produced 0 explorable sources")

        checkup_count = 0
        if checkup:
            checkup_count = self._add_checkups(
                spec_template,
                outbox,
                force,
                queue_suffix=self.organization.name)

        if source_count == 0 and checkup_count == 0:
            raise ValueError(f"nothing to do for {self}")

        # Synchronize the 'covered_accounts'-field with accounts, which are
        # about to be scanned.
        self.sync_covered_accounts()

        self.save()

        # Use the name of an appropriate organization as queue_suffix for
        # headers-based routing.
        queue_suffix = self.organization.name

        # Create a model object to track the status of this scan...
        ScanStatus.objects.create(
                scanner=self, scan_tag=scan_tag.to_json_object(),
                last_modified=scan_tag.time, total_sources=source_count,
                total_objects=checkup_count)

        # ... and dispatch the scan specifications to the pipeline!
        with PikaPipelineThread(
                queue_suffix=queue_suffix,
                write={queue for queue, _ in outbox}) as sender:

            for queue, message in outbox:
                sender.enqueue_message(queue,
                                       message.to_json_object(),
                                       exchange=get_exchange(rk=queue),
                                       **get_headers(organisation=queue_suffix))
            sender.enqueue_stop()
            sender.start()
            sender.join()

        logger.info(
            "Scan submitted",
            scan=self,
            pk=self.pk,
            scan_type=self.get_type(),
            organization=self.organization,
            rules=spec_template.rule.presentation,
        )
        return scan_tag.to_json_object()

    def get_last_successful_run_at(self) -> datetime:
        query = ScanStatus.objects.filter(scanner=self)
        finished = (status for status in query if status.finished)
        last = max(finished, key=lambda status: status.start_time, default=None)
        return last.start_time if last else None

    def generate_sources(self) -> Iterator[Source]:
        """Yields one or more engine2 Sources corresponding to the target of
        this Scanner."""
        # (this can't use the @abstractmethod decorator because of metaclass
        # conflicts with Django, but subclasses should override this method!)
        raise NotImplementedError("Scanner.generate_sources")
        yield from []

    def get_covered_accounts(self):
        """Return all accounts which would be scanned by this scannerjob, if
        run at this moment."""
        # Avoid circular import
        from os2datascanner.projects.admin.organizations.models import Account
        if self.org_unit.exists():
            return Account.objects.filter(units__in=self.org_unit.all())
        else:
            return Account.objects.all()

    def get_new_covered_accounts(self):
        """Return all accounts, which will be scanned by this scannerjob on the
        next scan, but are not present in the 'covered_accounts'-field."""
        return self.get_covered_accounts().difference(self.covered_accounts.all())

    def sync_covered_accounts(self):
        """Adds the accounts, which have not previously been scanned by this
        scanner, but will be scanned if run now, to the 'covered_accounts'-
        field."""
        return self.covered_accounts.add(*self.get_new_covered_accounts())

    def get_stale_accounts(self):
        """Return all accounts, which are included in the scanner's
        'covered_accounts' field, but are not associated with any org units
        linked to the scanner."""
        return self.covered_accounts.all().difference(self.get_covered_accounts())

    def remove_stale_accounts(self, accounts: list = None):
        """Removes all stale accounts from the object's 'covered_accounts'
        relation."""
        if accounts:
            self.covered_accounts.remove(*accounts)
        else:
            self.covered_accounts.remove(*self.get_stale_accounts())

    class Meta:
        abstract = False
        ordering = ['name']


@receiver(post_delete)
def post_delete_callback(sender, instance, using, **kwargs):
    """Signal handler for post_delete. Requests that all running pipeline
    components blacklist and ignore the scan tag of the now-deleted scan."""
    if not isinstance(instance, ScanStatus):
        return

    msg = messages.CommandMessage(
            abort=messages.ScanTagFragment.from_json_object(
                    instance.scan_tag))
    with PikaPipelineThread() as p:
        p.enqueue_message(
                "", msg.to_json_object(),
                "broadcast", priority=10)
        p.enqueue_stop()
        p.run()
