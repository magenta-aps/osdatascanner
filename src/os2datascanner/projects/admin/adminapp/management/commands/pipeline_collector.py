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

from django.core.management.base import BaseCommand

from os2datascanner.utils.system_utilities import parse_isoformat_timestamp
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.pipeline.utilities.pika import PikaPipelineRunner
from ...models.scannerjobs.scanner_model import (Scanner, ScanStatus,
        ScheduledCheckup)


def status_message_received_raw(body):
    message = messages.StatusMessage.from_json_object(body)

    status = ScanStatus.objects.filter(scan_tag=body["scan_tag"]).first()
    if not status:
        return

    if message.total_objects is not None:
        status.total_objects = (status.total_objects or 0) + message.total_objects
        status.explored_sources = (status.explored_sources or 0) + 1
    elif message.object_size is not None and message.object_type is not None:
        status.scanned_size = (status.scanned_size or 0) + message.object_size
        status.scanned_objects = (status.scanned_objects or 0) + 1

    status.save()

    yield from []


def checkup_message_received_raw(body):
    handle = None
    scan_tag = None
    matches = None
    problem = None
    if "message" in body:  # Problem message
        problem = messages.ProblemMessage.from_json_object(body)
        handle = problem.handle
        scan_tag = problem.scan_tag
    elif "matches" in body:  # Matches message
        matches = messages.MatchesMessage.from_json_object(body)
        handle = matches.handle
        scan_tag = matches.scan_spec.scan_tag

    if not scan_tag or not handle:
        return
    scanner = Scanner.objects.get(pk=scan_tag["scanner"]["pk"])
    scan_time = parse_isoformat_timestamp(scan_tag["time"])

    try:
        checkup = ScheduledCheckup.objects.get(
                handle_representation=handle.to_json_object(),
                scanner=scanner)

        # If we get here, then there was already a checkup object in the
        # database. Let's take a look at it

        if matches:
            if not matches.matched:
                if (len(matches.matches) == 1
                        and isinstance(matches.matches[0].rule,
                                LastModifiedRule)):
                    # This object hasn't changed since the last scan. Update
                    # the checkup timestamp so we remember to check it again
                    # next time
                    print(handle.presentation,
                            "LM/no change, updating timestamp")
                    checkup.interested_before = scan_time
                    checkup.save()
                else:
                    # This object has been changed and no longer has any
                    # matches. Hooray! Forget about it
                    print(handle.presentation,
                            "Changed, no matches, deleting")
                    checkup.delete()
            else:
                # This object has changed, but still has matches. Update the
                # checkup timestamp
                print(handle.presentation,
                        "Changed, new matches, updating timestamp")
                checkup.interested_before = scan_time
                checkup.save()
        elif problem:
            if problem.missing:
                # Permanent error, so this object has been deleted. Forget
                # about it
                print(handle.presentation, "Problem, deleted, deleting")
                checkup.delete()
            else:
                # Transient error -- do nothing. In particular, don't update
                # the checkup timestamp; we don't want to forget about changes
                # between the last match and this error
                print(handle.presentation, "Problem, transient, doing nothing")
    except ScheduledCheckup.DoesNotExist:
        if ((matches and matches.matched)
                or (problem and not problem.missing)):
            print(handle.presentation, "Interesting, creating")
            # An object with a transient problem or with real matches is an
            # object we'll want to check up on again later
            ScheduledCheckup.objects.create(
                    handle_representation=handle.to_json_object(),
                    scanner=scanner,
                    # XXX: ideally we'd detect if a LastModifiedRule is the
                    # victim of a transient failure so that we can preserve the
                    # date to scan the object properly next time, but we don't
                    # (yet) get enough information out of the pipeline for that
                    interested_before=scan_time)
        else:
            print(handle.presentation, "Not interesting, doing nothing")

    yield from []


class AdminCollector(PikaPipelineRunner):
    def handle_message(self, message_body, *, channel=None):
        if channel == "os2ds_status":
            return status_message_received_raw(message_body)
        elif channel == "os2ds_checkups":
            return checkup_message_received_raw(message_body)


class Command(BaseCommand):
    """Command for starting a pipeline collector process."""
    help = __doc__

    def handle(self, *args, **options):
        with AdminCollector(
                read=["os2ds_status", "os2ds_checkups"],
                heartbeat=6000) as runner:
            try:
                print("Start")
                runner.run_consumer(exclusive=True)
            finally:
                print("Stop")
