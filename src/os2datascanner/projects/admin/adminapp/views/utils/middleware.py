import datetime
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from django.conf import settings
from os2datascanner.projects.grants.models import GraphGrant
from os2datascanner.projects.admin.utilities import UserWrapper


class NotificationMiddleware:
    """Middleware for sending django messages to any view."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated and request.user.has_perm("grants.change_graphgrant"):
            check_grant_expiration(request)

        response = self.get_response(request)
        return response


def is_expiring_soon(exp_date, today):
    if exp_date:
        days_until_expiry = (exp_date - today).days
        return exp_date <= today or days_until_expiry <= settings.EXPIRATION_WARNING_THRESHOLD
    return False


def check_grant_expiration(request):
    grants = GraphGrant.objects.filter(UserWrapper(
                request.user).make_org_Q(
                org_path="organization"))

    today = datetime.date.today()
    for grant in grants:
        if is_expiring_soon(grant.expiry_date, today):
            notify_grant_expiration(request, today, grant)


def notify_grant_expiration(request, today, grant):
    msg = _("A Client Secret for Tenant: {tenant} is about to expire!").format(
        tenant=grant.tenant_id)

    session_key = f"{grant.tenant_id}_notification"

    # Check if user has already been notified of this grant this session.
    if last_notification := request.session.get(session_key):
        ts = datetime.date.fromisoformat(last_notification)

        # Only show the message once every 24h
        if (today - ts).days >= 1:
            messages.add_message(
                request,
                messages.WARNING,
                msg,
                extra_tags="manual_close"
            )
            request.session[session_key] = today.isoformat()
    else:
        messages.add_message(
            request,
            messages.WARNING,
            msg,
            extra_tags="manual_close"
        )
        request.session[session_key] = today.isoformat()
