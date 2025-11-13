import datetime
from django.core.management.base import BaseCommand

from os2datascanner.projects.grants.models import GraphGrant
from os2datascanner.projects.admin.adminapp.notification import GraphGrantExpiryNotificationEmail
from os2datascanner.projects.admin.adminapp.utils import is_expiring_soon


class Command(BaseCommand):
    def handle(self, *args, **options):  # noqa
        today = datetime.date.today()

        for graph_grant in GraphGrant.objects.all():
            exp_date = graph_grant.expiry
            if is_expiring_soon(exp_date, today):
                GraphGrantExpiryNotificationEmail(graph_grant).notify()
