# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import sys
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext, gettext_lazy as _

from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import (
        Scanner)


class Command(BaseCommand):
    """Schedule a scanner job for execution by the pipeline, just as the user
    interface's "Run" button does."""
    help = gettext(__doc__)

    def add_arguments(self, parser):
        parser.add_argument(
            "id",
            type=int,
            help=_("the primary key of the scanner job to start"),
            default=None)
        parser.add_argument(
            "--checkups-only",
            help=_("only scan objects previously scheduled for a checkup"),
            action="store_true")
        parser.add_argument(
            "--force",
            help=_("disable the last modification date check for everything"
                   " in this scan"),
            action="store_true")

    def handle(self, id, *args, checkups_only, force, **options):
        try:
            scanner = Scanner.objects.select_subclasses().get(pk=id)
        except ObjectDoesNotExist:
            print(_("no scanner job exists with id {id}").format(id=id))
            sys.exit(1)

        print(scanner.run(explore=not checkups_only, force=force))
