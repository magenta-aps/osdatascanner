# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import IntegrityError, transaction

from ....core.models.client import Client
from ....organizations.models.organization import Organization, OrganizationSerializer
from ....organizations.models.account import Account, AccountSerializer
from ....organizations.models import SyncedPermission
from ....organizations.broadcast_bulk_events import BulkCreateEvent
from ....organizations.publish import publish_events
from ....adminapp.models.rules import Rule


def setup_user(username, password, email):
    user = User.objects.create(
        username=username,
        email=email)
    user.set_password(password)
    user.save()
    user.groups.add(Group.objects.get(name="superadmins"))
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
            metavar="SUPERADMIN_PASSWORD",
            help="Password for the superadmin",
            default=self.default_password,
        )
        parser.add_argument(
            "--username",
            type=str,
            metavar="SUPERADMIN_USERNAME",
            help="Username for the superadmin",
            default="os",
        )
        parser.add_argument(
            "--load-cpr-rule",
            help="Also loads in the CPR rule fixture",
            action="store_true"
        )

    @transaction.atomic
    def handle(self, *args, client_name, org_name, email, phone, password, username, load_cpr_rule,
               **options):
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

        self.stdout.write(f"Creating superadmin {username}")
        try:
            setup_user(username, password, email)
        except IntegrityError:
            self.stdout.write(self.style.NOTICE(
                f"User with name {username} already exists. Command failed"))
            return
        self.stdout.write(self.style.SUCCESS("Superadmin created succesfully"))
        if password == self.default_password:
            self.stdout.write(self.style.WARNING("Default password used. CHANGE THIS IMMEDIATELY"))

        self.stdout.write("Creating & synchronizing corresponding Account")
        account = Account.objects.create(username=username, organization=org)

        # Add all synced permissions to user
        account.permissions.add(*Permission.objects.filter(
                content_type__app_label=SyncedPermission._meta.app_label,
                content_type__model=SyncedPermission._meta.model_name
            ).exclude(codename__in=[
                "add_syncedpermission",
                "delete_syncedpermission",
                "change_syncedpermission",
                "view_syncedpermission"
            ]))

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

        if load_cpr_rule:
            self.stdout.write("Load CPR rule fixture...")
            call_command("loaddata", "rules-cpr-da")

            self.stdout.write("Add Organization to CPR rule...")
            rule = Rule.objects.get(pk=8880100)  # The "CPR regel"
            organization = Organization.objects.first()
            rule.organizations.add(organization)
            self.stdout.write(self.style.SUCCESS(f"{organization} added to CPR rule!"))

        self.stdout.write(self.style.SUCCESS("Done!"))
