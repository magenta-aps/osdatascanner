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
# OS2Webscanner was developed by Magenta in collaboration with OS2 the
# Danish community of open source municipalities (http://www.os2web.dk/).
#
# The code is currently governed by OS2 the Danish community of open
# source municipalities ( http://www.os2web.dk/ )

import structlog
import datetime

from django.core.management.base import BaseCommand

from os2datascanner.utils.system_utilities import time_now
from ...models.scannerjobs.scanner import Scanner, ScanStatus
from ...notification import InvalidScannerNotificationEmail

logger = structlog.get_logger("adminapp")


def scheduled_for_now(scanner: Scanner,
                      current_qhr: datetime.datetime,
                      next_qhr: datetime.datetime,
                      now: bool = False):
    schedule_datetime = scanner.schedule_datetime
    return (schedule_datetime is not None
            and (current_qhr <= schedule_datetime < next_qhr or now))


def should_scanner_start(scanner: Scanner,
                         current_qhr: datetime.datetime,
                         next_qhr: datetime.datetime,
                         now: bool = False):
    return scheduled_for_now(scanner, current_qhr, next_qhr, now)\
            and scanner.validation_status


class Command(BaseCommand):
    help = __doc__

    current_qhr = time_now().replace(second=0)
    current_qhr = current_qhr.replace(
        minute=current_qhr.minute - current_qhr.minute % 15
    )

    next_qhr = current_qhr + datetime.timedelta(minutes=15)

    def add_arguments(self, parser):
        parser.add_argument(
            "--now",
            action="store_true",
            help="If scannerjob is validated, run the scanner now if scheduled for today")

    def handle(self, *args, now, **options):

        # Loop through all scanners
        for scanner in Scanner.objects.exclude(schedule="").select_subclasses():

            start = should_scanner_start(scanner=scanner,
                                         current_qhr=self.current_qhr,
                                         next_qhr=self.next_qhr,
                                         now=now)

            if start:

                # In principle, we should start this scanner now. Check that
                # it's not already running, though
                ScanStatus.clean_defunct()

                last_status = scanner.statuses.last()
                if last_status is None or last_status.finished:
                    scanner.run()
                else:
                    logger.warning("Scanner is already running, not starting it again!",
                                   scanner=scanner)

            else:
                # Why not?
                if scheduled_for_now(scanner, current_qhr=self.current_qhr, next_qhr=self.next_qhr,
                                     now=now) and not scanner.validation_status:
                    # If the scanner _is_ scheduled for now, but is not validated, send a
                    # notification to someone who can do something about that.
                    logger.warning("Scanner is not validated, sending email notification.",
                                   scanner=scanner)
                    InvalidScannerNotificationEmail(scanner).notify()
