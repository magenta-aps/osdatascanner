from django.core.management.base import BaseCommand, CommandError
from os2datascanner.projects.grants.models import GraphGrant

from os2datascanner.projects.report.organizations.models import Organization


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            "-org", "--organization",
            help="Organization PK to update GraphGrant for"
        )
        parser.add_argument(
            "-cl_sec", "--client_secret",
            type=str,
            help="Client secret",
            required=True,
        )

    # TODO: This command might become obsolete when/if we implement broadcast on GraphGrant
    def handle(self, *args, organization, client_secret, **options):
        if Organization.objects.count() > 1 and not organization:
            raise CommandError("Can't run without providing -org <pk> "
                               "when there are multiple organizations in the system!")

        if organization:
            org = Organization.objects.get(pk=organization)
        else:
            org = Organization.objects.first()

        try:
            gc = GraphGrant.objects.get(organization=org)
            gc.client_secret = client_secret
            gc.save()
        except GraphGrant.MultipleObjectsReturned:
            raise CommandError(
                f"Organization has {GraphGrant.objects.filter(organization=org).count()} GraphGrant"
                " objects! Command expects exactly 1")
        except GraphGrant.DoesNotExist:
            raise CommandError("Organization has 0 GraphGrant objects! Command expects exactly 1")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully updated GraphGrant! {gc} "
                               f"for {org}")
        )
