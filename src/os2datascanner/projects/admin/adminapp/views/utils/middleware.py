import datetime

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from os2datascanner.projects.grants.models import GraphGrant
from os2datascanner.projects.admin.utilities import UserWrapper
from os2datascanner.projects.admin.adminapp.utils import is_expiring_soon


class NotificationMiddleware:
    """Middleware for sending django messages to any view."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated and request.user.has_perm("grants.change_graphgrant"):
            # Skip middleware for HTMX requests
            if not request.headers.get('HX-Request'):
                check_grant_expiration(request)

        response = self.get_response(request)
        return response


def check_grant_expiration(request):
    grants = GraphGrant.objects.filter(UserWrapper(
                request.user).make_org_Q())

    today = datetime.date.today()
    for grant in grants:
        if is_expiring_soon(grant.expiry_date, today) and request.user in grant.contacts.iterator():
            notify_grant_expiration(request, today, grant)


def notify_grant_expiration(request, today, grant):
    msg = _("Microsoft Graph-grant for Tenant: {tenant} is about to expire!").format(
        tenant=grant.tenant_id)

    notifications = request.session.get('notifications', {})

    # Check if user has already been notified of this grant.
    if msg in notifications:
        ts = datetime.date.fromisoformat(notifications[msg])
        # Only show the message once a day.
        if (today - ts).days <= 1:
            # User was notified recently, don't show again
            return

    # Check if message is already queued.
    storage = messages.get_messages(request)
    existing_messages = [m.message for m in storage]
    storage.used = False

    if msg in existing_messages:
        # Message is already queued, nothing to do.
        return

    messages.add_message(
        request,
        messages.WARNING,
        msg,
        extra_tags="manual_close track_notification"
    )


@require_POST
def track_notification(request):
    message = request.POST.get('message')

    notifications = request.session.get('notifications', {})

    # Register timestamp when user interacts with message.
    notifications[message] = datetime.date.today().isoformat()
    request.session['notifications'] = notifications
    request.session.modified = True

    return JsonResponse({'status': 'ok'})
