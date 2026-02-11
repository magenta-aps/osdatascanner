#!/usr/bin/env python
# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from typing import Any
import structlog

from django.db import transaction
from django.db.utils import DataError
from django.core.management.base import BaseCommand

from prometheus_client import Summary, start_http_server

from os2datascanner.utils import debug
from os2datascanner.engine2.model.core import Handle
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.pipeline.utilities.pika import PikaPipelineThread
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner_helpers import (
    cancel_scan_tag_messages, )

from ...models.scannerjobs.scanner import (
    Scanner, ScanStatus, ScheduledCheckup)
from ...models.usererrorlog import UserErrorLog
from ...models.scannerjobs.scanner_helpers import CoveredAccount
from ....organizations.models.account import Account
from ...utils import CoverageMessage

logger = structlog.get_logger("checkup_collector")
SUMMARY = Summary("os2datascanner_checkup_collector_admin",
                  "Messages through checkup collector")


def create_usererrorlog(
        message: messages.ProblemMessage, ss: ScanStatus):
    """Create a UserErrorLog object from a problem message."""

    try:
        scanner = Scanner.objects.get(pk=message.scan_tag.scanner.pk)
    except Scanner.DoesNotExist:
        # This is a residual message for a scanner that the administrator has
        # deleted. Throw it away
        return
    error_message = message.message
    # Different types of scans have different source classes, where the
    # source path is contained differently.
    if message.handle and message.handle.presentation_url:
        path = message.handle.presentation_url
    elif message.handle and str(message.handle):
        path = str(message.handle)
    elif message.handle and message.handle.presentation_name:
        path = message.handle.presentation_name
    else:
        path = ""

    logger.info("Logging the error!",
                error_message=error_message, scanner=ss.scanner.name)

    UserErrorLog.objects.create(
        scan_status=ss,
        error_message=error_message,
        path=path,
        organization=scanner.organization,
        is_new=True
    )


def checkup_message_received_raw(body):
    logger.info(
            "raw checkup message received", body=body)

    if "coverages" in body:  # CoverageMessage
        recreate_account_coverage(
                CoverageMessage.from_json_object(body).coverages)
        return

    handle: Handle | None = None
    scan_tag: messages.ScanTagFragment | None = None
    scan_tag_raw: dict[str, Any] | None = None
    message: (messages.Issue
              | messages.MatchesMessage
              | messages.ContentMissingMessage)
    if "message" in body:  # Problem message
        message = messages.ProblemMessage.from_json_object(body)
        handle = message.handle
        scan_tag = message.scan_tag
        scan_tag_raw = body["scan_tag"]
    elif "matches" in body:  # Matches message
        message = messages.MatchesMessage.from_json_object(body)
        handle = message.handle
        scan_tag = message.scan_spec.scan_tag
        scan_tag_raw = body["scan_spec"]["scan_tag"]
    elif messages.ContentMissingMessage.test(body):
        message = messages.ContentMissingMessage.from_json_object(body)
        handle = message.handle
        scan_tag = message.scan_tag
        scan_tag_raw = body["scan_tag"]
    else:
        # Note that we don't need to handle ContentIrrelevantMessage here; the
        # admin module emits this message for the report module's benefit and
        # then deletes the checkup directly without going through the collector
        return

    try:
        scanner = Scanner.objects.get(pk=scan_tag.scanner.pk)
        ss = ScanStatus.objects.get(scan_tag=scan_tag_raw, cancelled=False)
    except Scanner.DoesNotExist:
        # This is a residual message for a scanner that the administrator has
        # deleted. Throw it away and all subsequent messages from it.
        cancel_scan_tag_messages(scan_tag.to_json_object())
        return
    except ScanStatus.DoesNotExist:
        # This means that there is no corresponding ScanStatus object.
        # Likely, this means that the scan has been cancelled. Tell processes to throwaway messages.
        cancel_scan_tag_messages(scan_tag.to_json_object())
        return

    if not handle:
        if isinstance(message, messages.ProblemMessage) and message.source:
            # XXX: it might also be nice to set ScanStatus.message and
            # .message_is_error in this case, but that might mean lock fighting
            create_usererrorlog(message, ss)
        return

    scan_time = scan_tag.time

    # Some Handles carry a dict of hints: pieces of extra information uncovered
    # during exploration that can be used to speed Resource functions up (and
    # to provide extra presentation information). But this information may be
    # stale if we hold onto it until the next scan, so we need to clear it
    # before storing it
    for here in handle.walk_up():
        here.clear_hints()

    update_scheduled_checkup(
            handle.censor(), message, scan_time, scanner, ss)

    yield from []


def update_scheduled_checkup(  # noqa: CCR001 E501
        handle, message, scan_time, scanner, ss: ScanStatus):
    locked_qs = ScheduledCheckup.objects.select_for_update(
        of=('self',)
    ).filter(
        scanner=scanner,
        path=handle.crunch(hash=True)
    )
    # Queryset is evaluated immediately with .first() to lock the database entry.
    locked_qs.first()
    if locked_qs:
        # There was already a checkup object in the database. Let's take a
        # look at it
        if isinstance(message, messages.MatchesMessage):
            if not message.matched:
                if (len(message.matches) == 1
                        and isinstance(message.matches[0].rule,
                                       LastModifiedRule)):
                    # This object hasn't changed since the last scan.
                    # Update the checkup timestamp so we remember to check
                    # it again next time
                    logger.debug(
                            "LM/no change, updating timestamp",
                            handle=handle.presentation)
                    locked_qs.update(
                            interested_after=scan_time)
                else:
                    # This object has been changed and no longer has any
                    # matches. Hooray! Forget about it
                    logger.debug(
                            "Changed, no matches, deleting",
                            handle=handle.presentation)
                    locked_qs.delete()
            else:
                # This object has changed, but still has matches. Update
                # the checkup timestamp
                logger.debug(
                        "Changed, new matches, updating timestamp",
                        handle=handle.presentation)
                locked_qs.update(
                        interested_after=scan_time)
        elif isinstance(message, messages.ContentMissingMessage):
            logger.debug(
                    "Problem, deleted, deleting",
                    handle=handle.presentation)
            locked_qs.delete()
        elif isinstance(message, messages.ProblemMessage):
            # Transient error -- do nothing. In particular, don't update the
            # checkup timestamp; we don't want to forget about changes between
            # the last match and this error
            logger.debug(
                    "Problem, transient, doing nothing",
                    handle=handle.presentation)

    elif ((isinstance(message, messages.MatchesMessage) and message.matched)
          or isinstance(message, messages.ProblemMessage)):
        logger.debug(
                "Interesting, creating", handle=str(handle))
        # An object with a transient problem or with real matches is an
        # object we'll want to check up on again later
        ScheduledCheckup.objects.update_or_create(
                path=handle.crunch(hash=True),
                scanner=scanner,
                # XXX: ideally we'd detect if a LastModifiedRule is the
                # victim of a transient failure so that we can preserve
                # the date to scan the object properly next time, but
                # we don't (yet) get enough information out of the
                # pipeline for that
                defaults={
                    "handle_representation": handle.to_json_object(),
                    "interested_after": scan_time
                })
        if isinstance(message, messages.ProblemMessage):
            # For problems, we also create a UserErrorLog object to alert
            # the user that something did not go as expected.
            create_usererrorlog(message, ss)
    else:
        logger.debug(
                "Not interesting, doing nothing",
                handle=handle.presentation)


def recreate_account_coverage(coverages: list[dict[str, str]]):
    for obj in coverages:

        try:
            scanner = Scanner.objects.get(pk=obj["scanner_id"])
        except Scanner.DoesNotExist:
            logger.warning("Could not recreate account coverage: Scanner not found",
                           account_uuid=obj["account"],
                           scanner_id=obj["scanner_id"],
                           scan_time=obj["time"])
            continue

        try:
            account = Account.objects.get(uuid=obj["account"])
        except Account.DoesNotExist:
            logger.warning("Could not recreate account coverage: Account not found",
                           account_uuid=obj["account"],
                           scanner_id=obj["scanner_id"],
                           scan_time=obj["time"])
            continue

        try:
            status = ScanStatus.objects.get(scanner=scanner, scan_tag__time=obj["time"])
        except ScanStatus.DoesNotExist:
            logger.warning("Could not recreate account coverage: ScanStatus not found",
                           scanner_id=obj["scanner_id"],
                           scan_time=obj["time"],
                           account_uuid=obj["account"])
            continue

        # Make sure all objects are from the same organization
        if account.organization != scanner.organization:
            logger.warning("Could not recreate account coverage: Organization mismatch",
                           account=account,
                           scanner=scanner,
                           status=status)
            continue

        logger.info("Creating CoveredAccount",
                    scanner_id=obj["scanner_id"],
                    scan_time=obj["time"],
                    account_uuid=obj["account"])

        CoveredAccount.objects.get_or_create(
            scanner=scanner,
            scan_status=status,
            account=account)


class CheckupCollectorRunner(PikaPipelineThread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        start_http_server(9091)

    def handle_message(self, routing_key, body):
        with SUMMARY.time():
            logger.debug(
                "Checkup collector received a raw message",
                routing_key=routing_key,
                body=body
            )
            try:
                with transaction.atomic():
                    if routing_key == "os2ds_checkups":
                        yield from checkup_message_received_raw(body)
            except DataError as de:
                # DataError occurs when something went wrong trying to select
                # or create/update data in the database. Often regarding
                # ScheduledCheckups it is related to the json data. For now, we
                # only log the error message.
                logger.error(
                    "Could not get or create object, due to DataError",
                    error=de)


class Command(BaseCommand):
    """Command for starting a pipeline collector process."""
    help: str = __doc__

    def handle(self, *args, **options):
        debug.register_debug_signal()

        CheckupCollectorRunner(
            read=["os2ds_checkups"],
            prefetch_count=512).run_consumer()
