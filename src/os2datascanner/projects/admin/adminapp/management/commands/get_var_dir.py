# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Command for dispatching summary reports from crontab."""

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    """Print this installation's VAR directory."""

    help = "Print the path to the VAR directory"

    def handle(self, *args, **options):
        """Execute the command."""
        from django.conf import settings
        print((settings.VAR_DIR))
