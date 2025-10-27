import datetime
from django.core.management.base import BaseCommand

from os2datascanner.projects.grants.models import GraphGrant
from os2datascanner.projects.admin.adminapp.notification import GraphGrantExpiryNotificationEmail


def is_expiring_soon(exp_date, today):
    """Determine if the expiry date is soon or overdue."""
    if exp_date:
        days_until_expiry = (exp_date - today).days
        return exp_date <= today or days_until_expiry <= 7
    return False


class Command(BaseCommand):
    def handle(self, *args, **options):  # noqa
        today = datetime.date.today()

        for graph_grant in GraphGrant.objects.all():
            exp_date = graph_grant.expiry
            if is_expiring_soon(exp_date, today):
                GraphGrantExpiryNotificationEmail(graph_grant).notify()
