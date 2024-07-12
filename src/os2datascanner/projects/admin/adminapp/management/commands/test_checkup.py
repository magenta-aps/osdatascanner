import sys
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext, gettext_lazy as _

from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner_helpers import (
        ScheduledCheckup)

from os2datascanner.engine2.model.core.utilities import SourceManager
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import Scanner


class Command(BaseCommand):
    """Schedule a scanner job for execution by the pipeline, just as the user
    interface's "Run" button does."""
    help = gettext(__doc__)

    def add_arguments(self, parser):
        parser.add_argument(
            "id",
            type=int,
            help=_("the primary key of the scheduled checkup to touch"),
            default=None)
        parser.add_argument(
            "--print-metadata",
            help=_("print metadata of the touched checkup"),
            action="store_true",
            default=False
        )

    def handle(self, id, *args, print_metadata, **options):
        try:
            checkup = ScheduledCheckup.objects.get(pk=id)
        except ObjectDoesNotExist:
            print(_("no scheduled checkup exists with id {id}").format(id=id))
            sys.exit(1)

        # We need to uncensor the checkup handle, in case we need authentication
        # to reach the source.
        scanner = Scanner.objects.select_subclasses().get(pk=checkup.scanner_id)
        remap_dict = Scanner._make_remap_dict(scanner.generate_sources())
        changed, uncensored_handle = Scanner._uncensor_handle(remap_dict, checkup.handle)

        resource = uncensored_handle.follow(SourceManager())

        print("Could reach source:", resource.check())
        if print_metadata:
            print("Metadata:", resource.get_metadata())
