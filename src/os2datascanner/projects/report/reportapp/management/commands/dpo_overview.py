"""Presents information about a given ScanStatus"""

import termplotlib as tpl
import termtables as tt

from django.core.management.base import BaseCommand
from django.db.models import Q

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
            "--organization",
            help="an organization UUID or name (case insensitive)",
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

    def handle(self, *args,
               organization: str | None = None,
               unit: str | None = None,
               scanner: int | None = None, **kwargs):

        if not organization:
            org = Organization.objects.get()
        else:
            for lookup in [Q(uuid=organization),
                           Q(name__iexact=organization)]:
                try:
                    org = Organization.objects.get(lookup)
                    break
                except Organization.DoesNotExist:
                    continue
            else:
                print(f"No organization with the name or UUID '{organization}' found.")
                return

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
        handled_results = match_data["handled"]["count"]
        total_results = (match_data["handled"]["count"]+match_data["unhandled"]["count"])*100
        print(
            round(handled_results / total_results, 2) if total_results > 0 else "0",
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
        if unhandled_matches_by_month:
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
        if new_matches_by_month:
            x_data, y_data = (
                [data_point[1] for data_point in new_matches_by_month],
                [data_point[0] for data_point in new_matches_by_month]
            )

            fig = tpl.figure()
            fig.barh(x_data, y_data)
            fig.show()
