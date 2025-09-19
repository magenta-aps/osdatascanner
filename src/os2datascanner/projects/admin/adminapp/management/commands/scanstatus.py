"""Presents information about a given ScanStatus"""

import termplotlib as tpl

from django.core.management.base import BaseCommand
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner_helpers import ScanStatus


def boolean_symbol(boolean):
    if boolean:
        return "✅"
    else:
        return "❌"


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "status_id",
            help="a scan_status primary key",
            type=int,
            metavar="PK"
        )

    def handle(self, status_id: int, *args, **kwargs):
        status = ScanStatus.objects.get(pk=status_id)

        print("===SCAN STATUS INFORMATION===")
        print("Scanner:", status.scanner)
        print("Start time:", status.start_time)

        print("---Current status---")
        if status.is_running:
            print("Scanner is still running!")
            print("Stage:", status.stage)
            print("Estimated completion time:", status.estimated_completion_time)
        else:
            print("Scanner is not running.")

        print("---Objects---")
        print("Fraction scanned:", str(round(status.fraction_scanned*100, 2)) + "%")
        print("Objects scanned:", status.scanned_objects)
        print("Total objects:", status.total_objects)
        print("Known objects skipped:", status.skipped_by_last_modified)
        print("Results found:", status.matches_found)
        print("Scanned size:", status.scanned_size, "bytes")

        print("---Settings---")
        print("Resolved:", boolean_symbol(status.resolved))
        print("Email sent:", boolean_symbol(status.email_sent))

        x_data, y_data = zip(*[(d["x"], d["y"]) for d in status.timeline()])

        fig = tpl.figure()
        fig.plot(x_data, y_data,
                 xlabel="Seconds since start time",
                 title="Percentage scanned over time")
        fig.show()
