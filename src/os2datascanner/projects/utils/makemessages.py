# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

# XXX: The true (project-relative) path of this file is src/os2datascanner/
# projects/utils/makemessages.py; the administration system and report module
# reference it by relative symbolic links. Don't edit it through the symbolic
# links, as that might break them!


from django.core.management.commands import makemessages


class Command(makemessages.Command):
    def run_from_argv(self, argv):
        return super().run_from_argv(argv + ["--add-location=file"])
