"""Presents the same information as the leader overview in the report module."""

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

        parser.add_argument(
            "--leader",
            help="an account username for the manager",
            type=str,
        )

    def handle(self, organization_id: int, *args,
               unit: int | None = None,
               leader: str | None = None,
               **kwargs):
        org = Organization.objects.get(pk=organization_id)

        accounts = Account.objects.filter(organization=org)

        if unit:
            org_unit = OrganizationalUnit.objects.get(organization=org, pk=unit)
            accounts = accounts.filter(positions__unit=org_unit)
        elif leader:
            manager = Account.objects.get(username=leader, organization=org)
            accounts = accounts.filter(manager=manager)

        accounts = accounts.distinct().with_result_stats().with_status()

        print("===LEADER OVERVIEW===")
        print("Organization:", org)
        if unit:
            print("Organizational unit:", org_unit)
        if leader:
            print("Manager:", manager)
        print("Number of employees:", accounts.count())

        headers = ["Username", "Name", "Results", "Withheld", "Status"]
        table_rows = [[acc.username,
                       acc.get_full_name(),
                       acc.unhandled_results,
                       acc.withheld_results,
                       acc.status] for acc in accounts]

        tt.print(table_rows, style=tt.styles.markdown, header=headers)
