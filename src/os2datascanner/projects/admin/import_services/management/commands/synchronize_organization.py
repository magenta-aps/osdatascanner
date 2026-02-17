#!/usr/bin/env python
# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import structlog
from django.core.management import BaseCommand

from os2datascanner.projects.admin.import_services.models import ImportService
from os2datascanner.utils.system_utilities import time_now

"""
    This command should be run by a cron job at the desired time
    organizational synchronizations should take place.
"""

logger = structlog.get_logger("import_services")


class Command(BaseCommand):

    help = "Run organization synchronization for current configured type(s):"

    def add_arguments(self, parser):
        parser.add_argument(
            "-f", "--force",
            action="store_true",
            help="Ignore scheduling information and synchronize immediately.",
        )

    def handle(self, *args, force: bool = False, **kwargs):
        for conf in ImportService.objects.select_subclasses().all():
            if force or self.schedule_check(conf.organization):
                conf.start_import()
            else:
                logger.info(
                    f"Skipping import service {type(conf).__name__} as it is not scheduled now.")

    def schedule_check(self, org):

        if not org.synchronization_time:
            # Org doesn't have mail notifications scheduled/have disabled it.
            self.stdout.write(f"Organization {org.name} has no set synchronization hour.",
                              style_func=self.style.WARNING)
            return False

        else:
            current_hour = time_now().hour
            return current_hour == org.synchronization_time.hour
