from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction

from ....core.models.client import Client
from ....organizations.models.organization import Organization, OrganizationSerializer
from ....organizations.models.account import Account, AccountSerializer
from ....organizations.broadcast_bulk_events import BulkCreateEvent
from ....organizations.publish import publish_events


def setup_user(username, password, email):
    user = User.objects.create(
        username=username,
        email=email,
        is_superuser=True,
        is_staff=True)
    user.set_password(password)
    user.save()
    return user


class Command(BaseCommand):
    """ Makes the initial setup for new instances. This includes:

    * Creating a Client
    * Creating an Organization
    * Creating a superuser
    """

    help = __doc__

    default_password = "setup"

    def add_arguments(self, parser):
        parser.add_argument(
            "--client-name",
            type=str,
            metavar="CLIENT_NAME",
            help="Desired name of client",
            default=settings.NOTIFICATION_INSTITUTION,
        )
        parser.add_argument(
            "--org-name",
            type=str,
            metavar="ORGANIZATION_NAME",
            help="Desired name of organization",
            default=settings.NOTIFICATION_INSTITUTION,
        )
        parser.add_argument(
            "--email",
            type=str,
            metavar="CONTACT_EMAIL",
            help="Email for contacting client",
            default="",
        )
        parser.add_argument(
            "--phone",
            type=str,
            metavar="CONTACT_PHONE_NUMBER",
            help="Phone number for contacting client",
            default="",
        )
        parser.add_argument(
            "--password",
            type=str,
            metavar="SUPERUSER_PASSWORD",
            help="Password for the superuser",
            default=self.default_password,
        )
        parser.add_argument(
            "--username",
            type=str,
            metavar="SUPERUSER_USERNAME",
            help="Username for the superuser",
            default="os",
        )

    @transaction.atomic
    def handle(self, *args, client_name, org_name, email, phone, password, username, **options):
        self.stdout.write(f"Creating Client {client_name}")
        try:
            client = Client.objects.create(name=client_name,
                                           contact_email=email, contact_phone=phone)
        except IntegrityError:
            self.stdout.write(self.style.NOTICE(
                f"Client with name {client_name} already exists. Command failed"))
            return
        self.stdout.write(self.style.SUCCESS("Client created succesfully"))

        self.stdout.write(f"Creating Organization {org_name}")
        try:
            org = Organization.objects.create(name=org_name, client=client)
        except IntegrityError:
            self.stdout.write(self.style.NOTICE(
                f"Organization with name {org_name} already exists. Command failed"))
            return
        self.stdout.write(self.style.SUCCESS("Organization created succesfully"))

        self.stdout.write(f"Creating superuser {username}")
        try:
            setup_user(username, password, email)
        except IntegrityError:
            self.stdout.write(self.style.NOTICE(
                f"User with name {username} already exists. Command failed"))
            return
        self.stdout.write(self.style.SUCCESS("Superuser created succesfully"))
        if password == self.default_password:
            self.stdout.write(self.style.WARNING("Default password used. CHANGE THIS IMMEDIATELY"))

        self.stdout.write("Creating & synchronizing corresponding Account")
        account = Account.objects.create(username=username, organization=org)
        account.is_superuser = True
        account.save()
        self.stdout.write(self.style.SUCCESS("Account created successfully!"))

        self.stdout.write("Synchronizing Organization and Account to Report module ...")
        creation_dict = {"Organization": OrganizationSerializer(
            Organization.objects.filter(pk=org.pk), many=True).data,
                         "Account": AccountSerializer(
            Account.objects.filter(pk=account.pk), many=True).data,
                         }
        publish_events([BulkCreateEvent(creation_dict)])
        self.stdout.write(self.style.SUCCESS("Sent Organization and Account create message!:"))
        self.stdout.write(f"{creation_dict}")

        self.stdout.write(self.style.SUCCESS(
            "Done! Run initial_setup in the Report module to create superuser there"))
