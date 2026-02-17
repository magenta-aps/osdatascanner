# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.core.management.base import BaseCommand
from os2datascanner.projects.utils.checkdb import waitdb


class Command(BaseCommand):
    help = "Check the connection to the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "-w",
            "--wait",
            default=1,
            type=int,
            help="Retry the connection for every second for WAIT seconds.",
        )

    def handle(self, *args, **options):
        wait = options["wait"]
        return waitdb(wait)
