from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


def setup_user(username, password):
    user = User.objects.get(username=username)
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()
    return user


class Command(BaseCommand):
    """Finishes superuser created by initial_setup from the admin module
    """

    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            type=str,
            metavar="Password for superuser",
            default="setup",
        )

        parser.add_argument(
            "--username",
            type=str,
            metavar="Username for superuser User and Account",
            default="os",
        )

    def handle(self, *args, password, username, **options):
        self.stdout.write(f"Looking for superuser \'{username}\'..")
        try:
            setup_user(username, password)
            self.stdout.write(self.style.SUCCESS(
                f"Superuser {username} updated successfully!"))
            if password == "setup":
                self.stdout.write(
                    self.style.WARNING("Default password used. CHANGE THIS IMMEDIATELY"))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"User \'{username}\' does not exist! "
                                                 "Did you run this command in the admin module?"))
