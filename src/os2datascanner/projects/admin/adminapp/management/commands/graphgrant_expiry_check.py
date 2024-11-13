import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import gettext_lazy as _

from os2datascanner.projects.grants.models import GraphGrant


def send_expiry_notification(organization, exp_date, recipients):
    """Send an email notification about upcoming or overdue expiry."""
    subject = _("Your GraphGrant needs updating!")
    body = _(
        f"Your GraphGrant client secret has an expiration date of: {exp_date}! \n"
        "It is important you update it as soon as possible, "
        "to avoid functionality loss! \n"
        f"This email sent on behalf of OSdatascanner organization: {organization}"
    )
    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=list(recipients)
    )
    msg.send()


def is_expiring_soon(exp_date, today):
    """Determine if the expiry date is soon or overdue."""
    if exp_date:
        days_until_expiry = (exp_date - today).days
        return exp_date <= today or days_until_expiry <= 7
    return False


def get_recipients(organization):
    """Get a set of unique email recipients."""
    recipients = set(
        user.email for user in get_user_model().objects.filter(is_superuser=True) if user.email
    )
    recipients.update(
        admin.user.email for admin in organization.client.administrators.all() if admin.user.email
    )
    return recipients


class Command(BaseCommand):
    def handle(self, *args, **options):  # noqa
        today = datetime.date.today()

        for graph_grant in GraphGrant.objects.all():
            exp_date = graph_grant.expiry_date
            if is_expiring_soon(exp_date, today):
                recipients = get_recipients(graph_grant.organization)
                self.stdout.write(
                    msg="Sending GraphGrant expiring notice email to: \n"
                        f"{recipients} \n Expiry date: {exp_date}",
                    style_func=self.style.SUCCESS)
                send_expiry_notification(graph_grant.organization, exp_date, recipients)
