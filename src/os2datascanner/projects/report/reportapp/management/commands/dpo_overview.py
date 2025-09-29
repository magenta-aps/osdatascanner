"""Presents information about a given ScanStatus"""

import termplotlib as tpl
import termtables as tt

from django.core.management.base import BaseCommand

from os2datascanner.projects.report.organizations.models import (
    Organization, OrganizationalUnit)
from os2datascanner.projects.report.reportapp.models.scanner_reference import ScannerReference
from os2datascanner.projects.report.reportapp.views.statistics_views import DPOStatisticsPageView


def boolean_symbol(boolean):
    if boolean:
        return "✅"
    else:
        return "❌"


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "organization_id",
            help="an organization UUID",
            type=str,
            metavar="PK"
        )

        parser.add_argument(
            "--unit",
            help="an organizational unit UUID",
            type=str,
            metavar="PK"
        )

        parser.add_argument(
            "--scanner",
            help="a scanner primary key",
            type=int,
            metavar="PK"
        )

    def handle(self, organization_id: str, *args,
               unit: str | None = None,
               scanner: int | None = None, **kwargs):
        org = Organization.objects.get(uuid=organization_id)

        print("===DPO Overview===")
        print("Organization:", org)

        reports = DPOStatisticsPageView.base_query().filter(scanner_job__organization=org)

        if unit:
            org_unit = OrganizationalUnit.objects.get(organization=org, pk=unit)
            reports = DPOStatisticsPageView.filter_by_unit(reports, org_unit)
            print("Organizational unit:", org_unit)
        if scanner:
            scannerjob = ScannerReference.objects.get(organization=org, scanner_pk=scanner)
            reports = reports.filter(scanner_job=scannerjob)
            print("Scanner:", scannerjob)

        match_data, source_type_data, resolution_status, created_month, resolved_month = \
            DPOStatisticsPageView.make_data_structures(reports)
        progress_dict = DPOStatisticsPageView.source_type_progress(source_type_data)

        # Source type table
        src_type_table = [
            [
                progress_dict["unhandled_by_source"][src_type]["label"],
                progress_dict["unhandled_by_source"][src_type]["count"],
                progress_dict[f"{src_type}_monthly_progress"]
            ] for src_type in [
                "webscan",
                "filescan",
                "mailscan",
                "teamsscan",
                "calendarscan",
                "other"
                ]
        ]

        print("\nUnhandled results from source types")
        tt.print(src_type_table,
                 header=["Source type", "Unhandled results", "30 day delta"],
                 style=tt.styles.markdown,
                 alignment="lcc")

        # Percentage of results handled
        print("\nHandled results")
        print(
            round(
                match_data["handled"]["count"] /
                (match_data["handled"]["count"]+match_data["unhandled"]["count"])*100, 2),
            "% handled")

        print(match_data["handled"]["count"],
              "of",
              match_data["handled"]["count"] + match_data["unhandled"]["count"], "handled")

        # Distribution of results on source types
        print("\nDistribution of results by source type")
        x_data, y_data = ([d["count"] for d in progress_dict["total_by_source"].values()],
                          [d["label"] for d in progress_dict["total_by_source"].values()])

        fig = tpl.figure()
        fig.barh(x_data, y_data)
        fig.show()

        # Distribution of results on resolution status
        print("\nDistribution of results by resolution status")
        x_data, y_data = ([d["count"] for d in resolution_status.values()],
                          [d["label"] for d in resolution_status.values()])
        fig = tpl.figure()
        fig.barh(x_data, y_data)
        fig.show()

        # Development overview -- accumulated unhandled results per month
        print("\nAccumulated unhandled results per month")
        unhandled_matches_by_month = \
            DPOStatisticsPageView.count_unhandled_matches_by_month(reports, created_month,
                                                                   resolved_month)

        x_data, y_data = (
            [i for i in range(len(unhandled_matches_by_month))],
            [data_point[1] for data_point in unhandled_matches_by_month]
        )

        fig = tpl.figure()
        fig.plot(x_data, y_data, xlabel=f"Months since {unhandled_matches_by_month[0][0]}")
        fig.show()

        # Development overview -- new results per month
        print("\nNew results per month")
        new_matches_by_month = DPOStatisticsPageView.count_new_matches_by_month(reports,
                                                                                created_month)
        x_data, y_data = (
            [data_point[1] for data_point in new_matches_by_month],
            [data_point[0] for data_point in new_matches_by_month]
        )

        fig = tpl.figure()
        fig.barh(x_data, y_data)
        fig.show()
