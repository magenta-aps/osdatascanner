import structlog
import sys

from django.core.management.base import BaseCommand

from ....core.models.client import Client
from ....organizations.broadcast_bulk_events import BulkCreateEvent, BulkUpdateEvent
from ....organizations.publish import publish_events
from ....organizations.models.organization import Organization, OrganizationSerializer

logger = structlog.get_logger("adminapp")


class Command(BaseCommand):
    """ Helper command for setting up new installations.

        Running setup_org --name 'Magenta ApS' will rename existing Client and
        Organization to Magenta ApS, set Organization contact info to None and send a
        BulkCreateEvent with the Organization to the report module.

        If an Organization already exist in both admin and report, run with the --update flag
        to instead send a BulkUpdateEvent.
      """

    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "-n", "--name",
            type=str,
            metavar="Name",
            help="Desired name of client & organization",
            default=False,
            required=True
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "-u", "--update",
            default=False,
            action="store_true",
            help="Update Client and Organization name in the admin module and "
                 "send an update message for Organization to the report module."
        )
        group.add_argument(
            "-c", "--create",
            default=False,
            action="store_true",
            help="Create a new Client and Organization in the admin module and "
                 "synchronize created Organization to the report module."
        )

    def handle(self, *args, name, update, create, **options):
        if (Client.objects.count() > 1 or Organization.objects.count() > 1) and not create:
            logger.warning("Can't run command when multiple Clients or Organizations exist!")
            sys.exit(1)

        if create:
            client = Client.objects.create(name=name,
                                           contact_email="info@magenta.dk",
                                           contact_phone="+45 3336 9696")
            org = Organization.objects.create(name=name, client=client)

            creation_dict = {"Organization": OrganizationSerializer(
                Organization.objects.filter(pk=org.pk), many=True).data}
            publish_events([BulkCreateEvent(creation_dict)])
            logger.info(f"Created Client and Organization {name} and sent create"
                        f"message of Organization")

        elif update:
            client = Client.objects.first()
            org = Organization.objects.first()

            client.name = name
            org.name = name

            client.save()
            org.save()

            update_dict = {"Organization": OrganizationSerializer(
                Organization.objects.all(), many=True).data}
            publish_events([BulkUpdateEvent(update_dict)])
            logger.info(f"Sent update message for Organization {name} to the report module.")

        else:
            client = Client.objects.first()
            org = Organization.objects.first()

            client.name = name
            org.name = name
            org.contact_email = None
            org.contact_phone = None

            client.save()
            org.save()
            logger.info(f"Saved Client & Org with name: {name}")

            creation_dict = {"Organization": OrganizationSerializer(
                Organization.objects.all(), many=True).data}
            publish_events([BulkCreateEvent(creation_dict)])
            logger.info("Sent create message for Organization to the report module. \n"
                        "Be aware that this is NOT an update message.")
