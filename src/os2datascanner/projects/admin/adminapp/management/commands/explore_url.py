# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Performs URL exploration on one or more Sources."""

from django.core.management.base import BaseCommand

from os2datascanner.engine2.commands import url_explorer
from os2datascanner.engine2.model.core import (
        Source,
        SourceManager,
        UnknownSchemeError,
)


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        url_explorer.add_arguments(parser)

    def handle(self, **kwargs):
        urls = kwargs['urls']
        guess, summarise = kwargs['guess'], kwargs['summarise']
        with SourceManager() as sm:
            for i in urls:
                try:
                    s = Source.from_url(i)
                    url_explorer.print_source(
                            sm, s, guess=guess, summarise=summarise)
                except UnknownSchemeError:
                    pass
