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
from dateutil.tz import gettz
import structlog

from django.db import models
from django.conf import settings
from django.core.validators import validate_comma_separated_integer_list
from django.db.models.signals import post_delete
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver

from model_utils.managers import InheritanceManager, InheritanceQuerySet
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
from os2datascanner.projects.admin.adminapp.utils import CleanProblemMessage

from ..rules import Rule
from .scanner_helpers import (  # noqa (interface backwards compatibility)
        ScanStatus, CoveredAccount, ScheduledCheckup, ScanStatusSnapshot)
from ..authentication import Authentication

logger = structlog.get_logger(__name__)
base_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class ScannerQuerySet(InheritanceQuerySet):
    def delete(self):
        scanners = self.values_list("pk", flat=True)
        CleanProblemMessage.send(scanners, publisher="Scanner.objects.delete()")
        logger.info('CleanProblemMessage published to the events_queue with '
                    f'the list of scanners: {scanners}')
        return super().delete()


class ScannerManager(InheritanceManager):
    def get_queryset(self):
        return ScannerQuerySet(self.model, using=self._db, hints=self._hints)


class Scanner(models.Model):

    """A scanner, i.e. a template for actual scanning jobs."""
    objects = ScannerManager()

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

    rule = models.ForeignKey(Rule,
                             verbose_name=_('rule'),
                             related_name='scanners',
                             on_delete=models.PROTECT)

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

    exclusion_rule = models.ForeignKey(Rule,
                                       blank=True,
                                       null=True,
                                       verbose_name=_('exclusion rule'),
                                       related_name='scanners_ex_rule',
                                       on_delete=models.PROTECT)

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

    # First possible start time
    FIRST_START_TIME = datetime.time(hour=19, minute=0)
    # Amount of quarter-hours that can be added to the start time
    STARTTIME_QUARTERS = 5 * 4

    @property
    def schedule_datetime(self) -> datetime.datetime | None:
        """Returns the timestamp for the next scheduled execution of this
        scanner, if there is one.

        The current implementation of this method always returns a time between
        7pm and midnight; this time is not configurable, but is derived from
        the primary key of the scanner in an attempt to spread executions
        out."""
        if (schedule_date := self.schedule_date) is not None:
            added_minutes = 15 * (self.pk % self.STARTTIME_QUARTERS)
            return (datetime.datetime.combine(schedule_date,
                                              self.FIRST_START_TIME,
                                              tzinfo=gettz())
                    + datetime.timedelta(minutes=added_minutes))

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
        rule = self.rule.customrule.make_engine2_rule()

        prerules = []
        if not force and self.do_last_modified_check:
            if self._supports_account_annotations:
                # _add_sources will add a per-Source LastModifiedRule, so we
                # don't need to do anything here
                pass
            else:
                # Create a single LastModifiedRule for the whole scan
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
            return self.exclusion_rule.customrule.make_engine2_rule()\
                if self.exclusion_rule else None
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

    @property
    def _supports_account_annotations(self) -> bool:
        return hasattr(self, "generate_sources_with_accounts")

    def _add_sources(
            self, spec_template: messages.ScanSpecMessage,
            outbox: list, force: bool) -> int:
        """Creates scan specifications, based on the provided scan
        specification template, for every Source covered by this scanner, and
        puts them into the provided outbox list. Returns the number of sources
        added."""
        source_count = 0
        if (self.do_last_modified_check
                and not force
                and self._supports_account_annotations):
            # CoveredAccount-aware scanner!
            # TODO: If an account has more than one Alias, we'll try to scan both.
            # This is an issue when it comes to service accounts/shared mailboxes.
            for account, source in self.generate_sources_with_accounts():
                rule = spec_template.rule
                try:
                    cva = CoveredAccount.objects.filter(
                            account=account, scanner=self).latest()
                    # OK, this Account has been covered by this Scanner before,
                    # so make a custom LastModifiedRule for them
                    rule = AndRule.make(
                            LastModifiedRule(cva.scan_status.start_time),
                            rule)
                    logger.info(
                            f"{self}: account {account} last scanned at"
                            f" {cva.scan_status.start_time}")
                except CoveredAccount.DoesNotExist:
                    # This Account is new to this Scanner, so do nothing -- the
                    # default rule is fine
                    logger.info(
                            f"{self}: account {account} not previously"
                            " scanned")
                outbox.append((
                    settings.AMQP_PIPELINE_TARGET,
                    spec_template._replace(source=source, rule=rule)))
                source_count += 1
            return source_count
        else:
            # The scanner isn't CoveredAccount-aware, or we're running without
            # the Last-Modified check. In either case, we just put Sources into
            # the queue without fiddling around with the rule
            for source in self.generate_sources():
                outbox.append((
                    settings.AMQP_PIPELINE_TARGET,
                    spec_template._replace(source=source)
                ))
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

        source_list = list(self.generate_sources())
        uncensor_map = {}
        for source in source_list:
            censored = source.censor()
            match (censored, uncensor_map.get(source)):
                case (s, None):
                    # Our map doesn't know about this Source yet, so put it in
                    # there
                    uncensor_map[source] = censored
                case (s, t) if s == t:
                    # We've ended up with two references to the same Source
                    # (presumably through two different Accounts?), but that's
                    # harmless in this context
                    pass
                case (s, t):
                    # Something weird has happened
                    raise ValueError(
                            "Conflicting censored representations for "
                            f"{source}: {s.crunch()} / {t.crunch()}")

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
            source_count = self._add_sources(spec_template, outbox, force)

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

        self.save()

        # Use the name of an appropriate organization as queue_suffix for
        # headers-based routing.
        queue_suffix = self.organization.name

        # Create a model object to track the status of this scan...
        new_status = ScanStatus.objects.create(
                scanner=self, scan_tag=scan_tag.to_json_object(),
                last_modified=scan_tag.time, total_sources=source_count,
                total_objects=checkup_count)

        # Synchronize the 'covered_accounts'-field with accounts, which are
        # about to be scanned.
        self.record_covered_accounts(new_status)

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

    def compute_covered_accounts(self):
        """Return all accounts which would be scanned by this scannerjob, if
        run at this moment."""
        from os2datascanner.projects.admin.organizations.models import Account, OrganizationalUnit  # noqa: avoid circular import
        if self.org_unit.exists():
            return Account.objects.filter(
                    units__in=self.org_unit.all()).distinct()
        elif self._supports_account_annotations:
            relevant_units = OrganizationalUnit.objects.filter(
                    organization=self.organization)
            return Account.objects.filter(
                    units__in=relevant_units).distinct()
        else:
            # We can't assume that everyone is covered, but we can conclude
            # that we can't know who's covered. (Scan might use a user-list file)
            return Account.objects.none()

    def compute_stale_accounts(self):
        """Computes all accounts that have previously been included in this
        scanner job, but which are no longer covered."""
        from os2datascanner.projects.admin.organizations.models import Account  # noqa: avoid circular import

        all_caccs = CoveredAccount.objects.filter(scanner=self)
        all_accs = Account.objects.filter(
                pk__in=all_caccs.values_list("account_id", flat=True))
        return all_accs.difference(self.compute_covered_accounts())

    def record_covered_accounts(self, scan_status: ScanStatus):
        """Creates CoveredAccount relations for accounts covered
        by current run of scannerjob.
        I.e. connects a scannerjob, an account and a scanner status
        """
        objects = [
            CoveredAccount(
                    account=account, scanner=self, scan_status=scan_status)
            for account in self.compute_covered_accounts()
        ]
        # ignore_conflicts shouldn't be needed here -- but it's harmless, so
        # let's err on the side of letting the scan actually start
        CoveredAccount.objects.bulk_create(objects, ignore_conflicts=True)

    def get_remediators(self):
        """Returns the accounts with a remediator-alias for this scannerjob.
        Disregards universal remediator aliases."""
        # Avoid circular import
        from ....organizations.models import Account
        from ....organizations.models.aliases import AliasType
        return Account.objects.filter(
            aliases___alias_type=AliasType.REMEDIATOR,
            aliases___value=self.pk)

    def delete(self, **kwargs):
        CleanProblemMessage.send([self.pk], publisher="Scanner.delete()")
        logger.info('CleanProblemMessage published to the events_queue with '
                    f'the scanner: {self.name} ({self.pk})')
        return super().delete(**kwargs)

    def get_analysis_job(self, finished=False):
        """Returns the last analysis job, if any exists."""
        from .analysisscanner import AnalysisJob
        if finished:
            from os2datascanner.projects.admin.core.models.background_job import JobState
            job = AnalysisJob.objects.filter(scanner=self, _exec_state=JobState.FINISHED.value
                                             ).order_by("-created_at"
                                                        ).prefetch_related("types").first()
        else:
            job = AnalysisJob.objects.filter(scanner=self).order_by(
                "-created_at").prefetch_related("types").first()
        return job

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
