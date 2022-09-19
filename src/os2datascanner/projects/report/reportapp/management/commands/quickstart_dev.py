import sys

from django.contrib.auth.models import User
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from os2datascanner.projects.report.reportapp.models.roles.remediator import (
    Remediator,
)
from os2datascanner.projects.report.reportapp.models.userprofile import UserProfile


class Command(BaseCommand):
    """Configure the report app as a dev environment. This includes:

    * Creating a superuser called "dev" with password "dev"
    * Making "dev" a remediator, so they can see all matches
    """

    help = __doc__

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.NOTICE("Aborting! This may not be a developer machine."))
            sys.exit(1)

        username = password = "dev"
        email = "dev@example.org"

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
            self.stdout.write("Making dev remediator")
            Remediator.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS("Superuser dev/dev created successfully!"))
        else:
            self.stdout.write("Superuser dev/dev already exists!")

        self.stdout.write("Creating user profile!")
        profile, created = UserProfile.objects.get_or_create(
            user=user
        )

        self.stdout.write(self.style.SUCCESS(
            "Done! Remember to run the same cmd in the Admin module"))
