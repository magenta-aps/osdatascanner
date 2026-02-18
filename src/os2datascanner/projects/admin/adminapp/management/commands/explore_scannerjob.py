# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Explore the Sources that a given scanner job represents."""

from django.core.management.base import BaseCommand

from os2datascanner.engine2.commands import url_explorer
from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner \
        import Scanner


def model_pk(model, constructor=int):
    def _pk(s):
        return model.objects.select_subclasses().get(pk=constructor(s))
    return _pk


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
                "scanners",
                help="a scanner job primary key to summarise",
                type=model_pk(Scanner),
                metavar="PK",
                nargs="+")
        url_explorer.add_control_arguments(parser)
        parser.add_argument(
                "-F", "--full",
                dest="full",
                action="store_true",
                help="Don't use SmartDelta to filter irrelevant handles out.")

    def handle(
            self, scanners, *,
            guess, summarise, metadata, max_depth, hints, censor, full,
            **kwargs):
        with SourceManager() as sm:
            for scanner in scanners:
                sst = scanner._construct_scan_spec_template(None, force=full)
                for scan_spec in scanner._yield_sources(sst, None):
                    url_explorer.print_source(
                            sm, scan_spec.source,
                            guess=guess,
                            summarise=summarise,
                            metadata=metadata,
                            max_depth=max_depth,
                            hints=hints,
                            censor=censor,

                            rule=scan_spec.rule if not full else None)
                    print("--")
