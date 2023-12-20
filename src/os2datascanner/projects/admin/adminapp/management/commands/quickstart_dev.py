import sys

from django.contrib.auth.models import User
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from recurrence import Recurrence

from ....organizations.broadcast_bulk_events import BulkCreateEvent
from ....organizations.publish import publish_events
from os2datascanner.projects.admin.adminapp.models.sensitivity_level import (
    Sensitivity,
)
from os2datascanner.projects.admin.adminapp.models.authentication import (
    Authentication,
)
from os2datascanner.projects.admin.adminapp.models.scannerjobs.filescanner import (
    FileScanner,
)
from os2datascanner.projects.admin.adminapp.models.scannerjobs.webscanner import (
    WebScanner,
)
from os2datascanner.projects.admin.adminapp.models.rules.cprrule import (
    CPRRule,
)
from os2datascanner.projects.admin.organizations.models.account import (
    Account,
)
from os2datascanner.projects.admin.organizations.models.organization import (
    Organization, OrganizationSerializer
)


def get_default_org_and_cprrule():
    """
    Sets up the default organization along with an instance
    of the CPR rule for the dev environment.
    """
    default_org = Organization.objects.get_or_create(
        name="OS2datascanner",
        contact_email="info@magenta-aps.dk",
        contact_phone="+45 3336 9696")

    cpr = CPRRule.objects.get_or_create(
        name="CPR regel",
        description="Denne regel finder alle gyldige CPR numre.",
        sensitivity=Sensitivity.CRITICAL,
        do_modulus11=True,
        ignore_irrelevant=True,
        examine_context=True,
        organization=default_org)

    return default_org, cpr


class Command(BaseCommand):
    """Configure the admin app as a dev environment. This includes:

    * Creating a superuser called "dev" with password "dev"
    * Setting up the samba share from the docker-compose dev env as a file scan
    """

    help = __doc__

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG or settings.PRODUCTION:
            self.stdout.write(self.style.NOTICE("Aborting! This may not be a developer machine."))
            sys.exit(1)

        # If the need arise, feel free to add these as parameters. For now we
        # just KISS
        username = password = "dev"
        email = "dev@example.org"
        smb_user = "os2"
        smb_password = "swordfish"
        smb_name = "Lille Samba"
        smb_unc = "//samba/e2test"
        web_name = "Local nginx"
        web_url = "http://nginx/"

        self.stdout.write("Synchronizing Organization to Report module ...")
        creation_dict = {"Organization": OrganizationSerializer(
            Organization.objects.all(), many=True).data,
                         }
        event = BulkCreateEvent(creation_dict)
        publish_events([event])
        self.stdout.write(self.style.SUCCESS(f"Sent Organization create message!:"
                                             f" \n {creation_dict}"))

        self.stdout.write("Creating superuser dev/dev!")
        user, created = User.objects.get_or_create(
            username=username,
            email=email,
            is_superuser=True,
            is_staff=True,
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS("Superuser dev/dev created successfully!"))
        else:
            self.stdout.write("Superuser dev/dev already exists!")

        self.stdout.write("Creating & synchronizing corresponding dev Account")
        org = Organization.objects.first()
        account, c = Account.objects.get_or_create(
            username=username,
            first_name="dev",
            last_name="devsen",
            organization=org,
            is_superuser=True,
        )
        if c:
            self.stdout.write(self.style.SUCCESS("Account dev created successfully!"))
        else:
            self.stdout.write("Account for dev already exists!")

        self.stdout.write("Synchronizing Organization to Report module")
        org, cpr = get_default_org_and_cprrule()
        creation_dict = {"Organization": OrganizationSerializer(
            Organization.objects.all(), many=True).data}
        event = BulkCreateEvent(creation_dict)
        publish_events([event])
        self.stdout.write(self.style.SUCCESS(f"Sent Organization create message!:"
                                             f" \n {creation_dict}"))

        self.stdout.write("Creating file scanner for samba share")
        recurrence = Recurrence()
        share, created = FileScanner.objects.get_or_create(
            name=smb_name,
            unc=smb_unc,
            do_ocr=True,
            validation_status=True,
            do_last_modified_check=False,
            organization=org,
            schedule=recurrence,
        )
        if created:
            auth = Authentication(username=smb_user)
            auth.set_password(smb_password)
            auth.save()
            share.authentication = auth
            share.save()
            share.rules.set([cpr])
            self.stdout.write(self.style.SUCCESS("Samba share file scanner created successfully!"))
        else:
            self.stdout.write("Samba share file scanner already exists!")

        self.stdout.write("Creating webscanner for local nginx")
        webscanner, created = WebScanner.objects.get_or_create(
            name=web_name,
            url=web_url,
            validation_status=True,
            do_last_modified_check=False,
            organization=org,
            schedule=recurrence,
            download_sitemap=False,
        )
        if created:
            webscanner.rules.set([cpr])
            self.stdout.write(self.style.SUCCESS("Webscanner created successfully!"))
        else:
            self.stdout.write("Webscanner already exists!")

        self.stdout.write(self.style.SUCCESS(
            "Done! Remember to run the same cmd in the Report module"))
