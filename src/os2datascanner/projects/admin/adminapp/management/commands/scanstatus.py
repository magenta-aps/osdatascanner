"""Presents information about a given ScanStatus"""

import termplotlib as tpl
import termtables as tt

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

        print("\n---Current status---")
        if status.is_running:
            print("Scanner is still running!")
            print("Stage:", status.stage)
            print("Estimated completion time:", status.estimated_completion_time)
        else:
            print("Scanner is not running.")

        if status.status_is_error:
            print("Error:", status.message)

        print("\n---Objects---")
        tt.print([
            ["Fraction scanned",
             str(round(status.fraction_scanned*100, 2) if status.fraction_scanned else 0.0) + "%"],
            ["Objects scanned", status.scanned_objects],
            ["Total objects", status.total_objects],
            ["Known objects skipped", status.skipped_by_last_modified],
            ["Results found", status.matches_found],
            ["Scanned size", str(status.scanned_size) + " bytes"]
            ],
            style=tt.styles.markdown,
        )

        print("\n---Settings---")
        tt.print([
            ("Resolved", boolean_symbol(status.resolved)),
            ("Email sent", boolean_symbol(status.email_sent))],
            style=tt.styles.markdown
        )

        timeline = status.timeline()
        if timeline:
            x_data, y_data = zip(*[(d["x"], d["y"]) for d in timeline])

            fig = tpl.figure()
            fig.plot(x_data, y_data,
                     xlabel="Seconds since start time",
                     title="Percentage scanned over time")
            fig.show()

        data_types = status.data_types()
        if data_types:
            mime_types, sizes, times = zip(*[(k, p["size"], p["time"].seconds)
                                             for k, p in data_types.items()])

            print("\n---Total size of scanned mime types [bytes]---")
            s, m = zip(*sorted(zip(sizes, mime_types), reverse=True))
            fig_size = tpl.figure()
            fig_size.barh(s, m)
            fig_size.show()

            print("\n---Total time spent scanning mime types in seconds---")
            t, m = zip(*sorted(zip(times, mime_types), reverse=True))
            fig_times = tpl.figure()
            fig_times.barh(t, m)
            fig_times.show()
