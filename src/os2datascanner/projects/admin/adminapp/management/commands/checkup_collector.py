#!/usr/bin/env python
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
# OS2datascanner was developed by Magenta in collaboration with OS2 the
# Danish community of open source municipalities (https://os2.eu/).
#
# The code is currently governed by OS2 the Danish community of open
# source municipalities ( https://os2.eu/ )

import structlog

from django.db import transaction
from django.db.utils import DataError
from django.core.management.base import BaseCommand

from prometheus_client import Summary, start_http_server

from os2datascanner.utils import debug
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.pipeline.utilities.pika import PikaPipelineThread
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner_helpers import (
    cancel_scan_tag_messages, )

from ...models.scannerjobs.scanner import (
    Scanner, ScanStatus, ScheduledCheckup)
from ...models.usererrorlog import UserErrorLog

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
    handle = None
    scan_tag = None
    scan_tag_raw = None
    matches = None
    problem = None
    if "message" in body:  # Problem message
        problem = messages.ProblemMessage.from_json_object(body)
        handle = problem.handle
        scan_tag = problem.scan_tag
        scan_tag_raw = body["scan_tag"]
    elif "matches" in body:  # Matches message
        matches = messages.MatchesMessage.from_json_object(body)
        handle = matches.handle
        scan_tag = matches.scan_spec.scan_tag
        scan_tag_raw = body["scan_spec"]["scan_tag"]

    if not scan_tag or not handle:
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

    scan_time = scan_tag.time

    # Some Handles carry a dict of hints: pieces of extra information uncovered
    # during exploration that can be used to speed Resource functions up (and
    # to provide extra presentation information). But this information may be
    # stale if we hold onto it until the next scan, so we need to clear it
    # before storing it
    here = handle
    while here:
        here.clear_hints()
        here = here.source.handle

    update_scheduled_checkup(
            handle.censor(), matches, problem, scan_time, scanner, ss)

    yield from []


def update_scheduled_checkup(  # noqa: CCR001 E501
        handle, matches, problem, scan_time, scanner, ss: ScanStatus):
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
        if matches:
            if not matches.matched:
                if (len(matches.matches) == 1
                        and isinstance(matches.matches[0].rule,
                                       LastModifiedRule)):
                    # This object hasn't changed since the last scan.
                    # Update the checkup timestamp so we remember to check
                    # it again next time
                    logger.debug(
                            "LM/no change, updating timestamp",
                            handle=handle.presentation)
                    locked_qs.update(
                            interested_before=scan_time)
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
                        interested_before=scan_time)
        elif problem:
            if problem.missing:
                # Permanent error, so this object has been deleted. Forget
                # about it
                logger.debug(
                        "Problem, deleted, deleting",
                        handle=handle.presentation)
                locked_qs.delete()
            else:
                # Transient error -- do nothing. In particular, don't
                # update the checkup timestamp; we don't want to forget
                # about changes between the last match and this error
                logger.debug("Problem, transient, doing nothing",
                             handle=handle.presentation)

    elif ((matches and matches.matched)
            or (problem and not problem.missing)):
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
                    "interested_before": scan_time
                })
        if problem and not problem.missing:
            # For problems, we also create a UserErrorLog object to alert
            # the user that something did not go as expected.
            create_usererrorlog(problem, ss)
    else:
        logger.debug(
                "Not interesting, doing nothing",
                handle=handle.presentation)


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
    help = __doc__

    def handle(self, *args, **options):
        debug.register_debug_signal()

        CheckupCollectorRunner(
            read=["os2ds_checkups"],
            prefetch_count=512).run_consumer()
