import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

from os2datascanner.projects.grants.models import GraphGrant
from os2datascanner.projects.admin.adminapp.notification import GraphGrantExpiryNotificationEmail
from os2datascanner.projects.admin.adminapp.utils import is_expiring_soon


class Command(BaseCommand):
    def handle(self, *args, **options):  # noqa
        today = datetime.date.today()

        for graph_grant in GraphGrant.objects.all():
            exp_date = graph_grant.expiry
            days_since_last_email = (
                today - graph_grant.last_email_date).days\
                if graph_grant.last_email_date else float('inf')
            if (is_expiring_soon(exp_date, today) and
                    days_since_last_email >= settings.EXPIRATION_WARNING_THRESHOLD):
                GraphGrantExpiryNotificationEmail(graph_grant).notify()
                graph_grant.last_email_date = today
                graph_grant.save()
