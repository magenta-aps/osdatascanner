"""Replay messages from the report module to the administration system in order
to (re-)create ScheduledCheckup objects."""

import sys
from django.db.models import Q
from django.core.management.base import BaseCommand
import functools
import structlog

from os2datascanner.engine2.pipeline.utilities.pika import PikaPipelineThread

from ...models.documentreport import DocumentReport
from .print_objects import build_queryset_from, CollectorActionFactory


logger = structlog.get_logger(__name__)


eprint = functools.partial(print, file=sys.stderr)


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        caf = CollectorActionFactory()

        parser.add_argument(
            '--exclude',
            dest="filt_ops",
            metavar="FL",
            type=str,
            action=caf.make_collector_action("exclude"),
            help="a Django field lookup to exclude objects")
        parser.add_argument(
            '--filter',
            dest="filt_ops",
            metavar="FL",
            type=str,
            action=caf.make_collector_action("filter"),
            help="a Django field lookup to filter objects")
        parser.add_argument(
            '--annotate',
            dest="filt_ops",
            metavar="FL",
            type=str,
            action=caf.make_collector_action("annotate"),
            help="a Django field lookup describing an annotation to add to the"
                 " query set")

        parser.add_argument(
            "-f",
            "--force",
            dest="force",
            action="store_true",
            help="don't prompt for confirmation")

    def handle(  # noqa CCR001
            self, *,
            filt_ops, force, **kwargs):
        queryset = build_queryset_from(DocumentReport, filt_ops)

        queryset = queryset.filter(
                # We are only interested in a report if it has not been handled ...
                Q(resolution_status__isnull=True),
                # ... and it contains either a match or a problem.
                Q(raw_problem__isnull=False) | Q(raw_matches__isnull=False))

        queryset = queryset.order_by("-pk")

        print(f" unhandled:    {queryset.count()} row(s)")

        if not queryset.exists():
            print("Nothing to do. Exiting.")

        if not force:
            try:
                proceed = input("Do you want to proceed? [yN] ")
            except EOFError:
                print("n")
                proceed = "n"
            if proceed != "y":
                print("Exiting.")
                sys.exit(0)

        ppt = PikaPipelineThread(write=["os2ds_checkups"])
        ppt.start()

        for dr in queryset.iterator():
            ppt.enqueue_message(
                    "os2ds_checkups", dr.raw_matches or dr.raw_problem)

        print(
                "Enqueued messages, waiting for"
                " RabbitMQ thread to finish sending them...")

        ppt.synchronise()
        ppt.enqueue_stop()
        ppt.join()

        print("RabbitMQ thread finished. All done!")
