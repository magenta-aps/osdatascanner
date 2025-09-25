import termplotlib as tpl
import termtables as tt

from django.core.management.base import BaseCommand
from os2datascanner.projects.report.organizations.models import Account


def boolean_symbol(boolean):
    if boolean:
        return "✅"
    else:
        return "❌"


def weeks_dict_to_table(d: dict):
    return [[w["weeknum"], w["matches"], w["new"], w["handled"]] for w in d]


class Command(BaseCommand):
    """Presents information about a specific account in the report module."""
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            help="an account username",
            type=str
        )

    def handle(self, username: str, *args, **kwargs):
        account = Account.objects.get(username=username)

        print("===USER OVERVIEW===")
        print("Account:", account)

        # Table with results per week the last three weeks
        # Structure:
        # | Week number | Unhandled results | Positive change | Negative change |
        three_weeks_dict = account.count_matches_by_week(weeks=3)
        three_weeks_table = weeks_dict_to_table(three_weeks_dict)

        tt.print(three_weeks_table,
                 header=["Week #", "Unhandled results", "+", "-"],
                 style=tt.styles.markdown,
                 alignment="cccc")

        # Figure with results per week the last year
        year_dict = account.count_matches_by_week()
        year_xdata = [i + 1 for i, w in enumerate(year_dict)]
        year_ydata = [w["matches"] for w in reversed(year_dict)]

        figure = tpl.figure()
        figure.plot(year_xdata, year_ydata,
                    xlim=[1, 53],
                    xlabel="Weeks since one year ago",
                    title="Unhandled results during the previous year")
        figure.show()

        print("False positive rate:", account.false_positive_percentage,
              "⚠️" if account.false_positive_alarm() else "", "\n")

        # Table with results per scanner job
        # Structure:
        # | Scanner name | Results |
        scannerjobs_queryset = account.get_scannerjobs_list()
        scanner_table = [[scanner.scanner_name, scanner.total] for scanner in scannerjobs_queryset]

        tt.print(scanner_table, header=["Scanner name", "Total results"],
                 style=tt.styles.markdown, alignment="lc")
