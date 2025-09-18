import sys

from django.contrib.auth.models import User
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from recurrence import Recurrence

from os2datascanner.projects.grants.models import SMBGrant
from os2datascanner.projects.admin.adminapp.models.scannerjobs.filescanner import (
    FileScanner,
)
from os2datascanner.projects.admin.adminapp.models.scannerjobs.webscanner import (
    WebScanner,
)
from os2datascanner.projects.admin.adminapp.models.rules import (
    Rule,
)
from os2datascanner.projects.admin.organizations.models.account import (
    Account,
)
from os2datascanner.projects.admin.organizations.models.aliases import (
    Alias, AliasType,
)
from os2datascanner.projects.admin.organizations.models.organization import Organization
from os2datascanner.projects.admin.core.models.client import Client


def get_default_org_and_cprrule():
    """
    Retrieves the default organization along with an instance
    of the CPR rule for the dev environment.
    """

    default_org = Organization.objects.first()

    cpr = Rule.objects.filter(
        name="CPR regel",
        description="Denne regel finder alle gyldige CPR numre.",
        ).first()

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

        # Create development client and organization
        client, _ = Client.objects.get_or_create(name="Development Client",
                                                 contact_email="dev@dev.com",
                                                 contact_phone="12345678")
        Organization.objects.get_or_create(name="OSdatascanner", client=client,
                                           defaults={
                                            "outlook_delete_email_permission": True,
                                            "onedrive_delete_permission": True,
                                            "smb_delete_permission": True,
                                            "exchange_delete_permission": True,
                                            "gmail_delete_permission": True,
                                            "gdrive_delete_permission": True
                                           })

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
        org, cpr = get_default_org_and_cprrule()
        print("org:", org)
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

        self.stdout.write("Connecting CPR rule to organization ...")
        org.system_rules.add(cpr)

        alias, c2 = Alias.objects.get_or_create(
            account=account,
            _alias_type=AliasType.REMEDIATOR,
            _value="0",
        )
        if c2:
            self.stdout.write(self.style.SUCCESS("Remediator alias for account dev "
                                                 "created successfully!"))
        else:
            self.stdout.write("Remediator alias for account dev already exists!")

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
            rule=cpr
        )
        if created:
            smb_grant = SMBGrant(username=smb_user, password=smb_password, organization=org)
            smb_grant.save()
            share.smb_grant = smb_grant
            share.save()
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
            rule=cpr
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Webscanner created successfully!"))
        else:
            self.stdout.write("Webscanner already exists!")

        self.stdout.write(self.style.SUCCESS(
            "Done! Remember to run the same cmd in the Report module"))
