#!/usr/bin/env python
# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.core.management.base import BaseCommand

from ...utils import create_alias_and_match_relations
from os2datascanner.projects.report.organizations.models import Alias


def update_match_alias_relations():
    aliases = Alias.objects.all()
    print("Found {0} aliases.".format(aliases.count()))

    approximate_count = 0

    for alias in aliases:
        ac = create_alias_and_match_relations(alias)
        if ac != 0:
            print(f"{alias}: approx. {ac}")
        approximate_count += ac

    print(
            f"Approximately {approximate_count}"
            " DocumentReport/Alias relations created.")


class Command(BaseCommand):
    """Sends emails."""
    help = __doc__

    def handle(self, **options):
        """This command will look for all DocumentReport matches and make
        a relation between the match and the alias if any, and not already
        present.
        """
        update_match_alias_relations()
