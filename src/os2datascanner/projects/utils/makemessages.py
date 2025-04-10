# XXX: The true (project-relative) path of this file is src/os2datascanner/
# projects/utils/makemessages.py; the administration system and report module
# reference it by relative symbolic links. Don't edit it through the symbolic
# links, as that might break them!


from django.core.management.commands import makemessages


class Command(makemessages.Command):
    def run_from_argv(self, argv):
        return super().run_from_argv(argv + ["--add-location=file"])
