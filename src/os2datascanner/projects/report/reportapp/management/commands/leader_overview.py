"""Presents information about a given ScanStatus"""

# import termplotlib as tpl
import termtables as tt

from django.core.management.base import BaseCommand

from os2datascanner.projects.report.organizations.models import (
    Organization, Account, OrganizationalUnit)


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

    def handle(self, organization_id: int, *args, unit: int | None = None, **kwargs):
        org = Organization.objects.get(pk=organization_id)

        # It would probably be nice if this tool uses the exact same logic as the view.
        if unit:
            org_unit = OrganizationalUnit.objects.get(organization=org, pk=unit)
            accounts = Account.objects.filter(organization=org, positions__unit=org_unit)
        else:
            accounts = Account.objects.filter(organization=org)

        accounts = accounts.distinct().with_result_stats().with_status()

        print("===LEADER OVERVIEW===")
        print("Organization:", org)
        if org_unit:
            print("Organizational unit:", org_unit)
        print("Number of employees:", accounts.count())

        headers = ["Username", "Name", "Results", "Withheld", "Status"]
        table_rows = [[acc.username,
                       acc.get_full_name(),
                       acc.unhandled_results,
                       acc.withheld_results,
                       acc.status] for acc in accounts]

        tt.print(table_rows, style=tt.styles.markdown, header=headers)
