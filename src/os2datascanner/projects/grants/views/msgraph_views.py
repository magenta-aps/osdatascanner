import json
import base64
from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from os2datascanner.projects.admin.utilities import UserWrapper
from ..models.graphgrant import GraphGrant


def make_consent_url(state):
    if settings.MSGRAPH_APP_ID:
        return ("https://login.microsoftonline.com/common/adminconsent?"
                + urlencode({
                    "client_id": settings.MSGRAPH_APP_ID,
                    "scope": "https://graph.microsoft.com/.default",
                    "response_type": "code",
                    "state": base64.b64encode(json.dumps(state).encode()),
                    "redirect_uri": (
                            settings.SITE_URL + "grants/msgraph/receive/")
                }))
    else:
        return None


class MSGraphGrantRequestView(LoginRequiredMixin, TemplateView):
    """Sends the user to the Microsoft Online login system in order to permit
    OS2datascanner to access organisational mail accounts through the Graph
    API.

    Note that only Microsoft accounts with organisational administrator
    privileges can grant applications the right to access Graph resources
    without having to go through a specific user account."""
    template_name = "grants/grant_start.html"

    redirect_token = None

    def get_context_data(self, **kwargs):
        return dict(**super().get_context_data(**kwargs), **{
            "service_name": "Microsoft Online",
            "auth_endpoint": make_consent_url(
                    state={
                        "red": self.redirect_token,
                        "org": str(UserWrapper(self.request.user).get_org().pk)
                    }),
            "error": self.request.GET.get("error"),
            "error_description": self.request.GET.get("error_description")
        })


class MSGraphGrantReceptionView(LoginRequiredMixin, View):
    SUCCESS_PARAMS = ("tenant", "state", "admin_consent",)
    FAILURE_PARAMS = ("error", "error_description")

    def get(self, request):
        state = json.loads(
                base64.b64decode(
                        # "e30=" is Base64 for "{}", since you asked
                        request.GET.get("state", "e30=")))
        if not all(k in state for k in ("red", "org",)):
            return HttpResponse("state_missing", status=400)

        redirect = reverse(state["red"], kwargs=state.get("rdk", {}))
        parameters = ""
        if all(k in request.GET for k in self.SUCCESS_PARAMS):
            # The remote server has given us our grant -- hooray! Store it in
            # the database before we redirect

            GraphGrant.objects.get_or_create(
                    tenant_id=request.GET["tenant"],
                    organization_id=state["org"],
                    defaults={
                        "app_id": settings.MSGRAPH_APP_ID,
                        # Django does the right thing if you assign to a
                        # property rather than a database field. Crazy
                        "client_secret": settings.MSGRAPH_CLIENT_SECRET
                    })
        elif any(k in request.GET for k in self.FAILURE_PARAMS):
            # The remote server has not given us our grant -- boo. Pass the
            # error details back when we redirect
            parameters = "?" + urlencode(request.GET)

        return HttpResponseRedirect(redirect + parameters)
