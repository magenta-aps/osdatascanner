import json
import base64
from urllib.parse import urlencode

from django import forms
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import UpdateView
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.dateparse import parse_datetime
from os2datascanner.projects.admin.utilities import UserWrapper
from os2datascanner.projects.grants.admin import AutoEncryptedField, choose_field_value
from requests import HTTPError

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
    redirect_kwargs = None

    def get_context_data(self, **kwargs):
        return dict(**super().get_context_data(**kwargs), **{
            "service_name": "Microsoft Online",
            "auth_endpoint": make_consent_url(
                    state={
                        "red": self.redirect_token,
                        "rdk": self.redirect_kwargs,
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


class MSGraphGrantForm(forms.ModelForm):
    class Meta:
        model = GraphGrant
        exclude = ("__all__")

    _client_secret = AutoEncryptedField(required=False)
    expiry_date = forms.DateField(widget=forms.widgets.DateInput(
        attrs={"type": "date", }, format="%Y-%m-%d",),
        required=False
    )

    def clean__client_secret(self):
        return choose_field_value(
              self.cleaned_data["_client_secret"],
              self.instance._client_secret)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["_client_secret"].initial = "dummy"
        self.fields["expiry_date"].initial = self.instance.expiry_date

        self.fields["organization"].disabled = True
        self.fields["tenant_id"].disabled = True
        # Todo: Maybe we'll want to let client_id be editable.
        self.fields["app_id"].disabled = True


def get_secret_end_date(client_secret, end_date, graph_caller, graph_grant):
    res = (graph_caller.get(
        f"applications?$filter=(appId eq '{graph_grant.app_id}')&$select=passwordCredentials")
           .json().get("value"))
    for pwc in res:
        for secret in pwc.get("passwordCredentials", []):
            if client_secret.startswith(secret.get("hint")):
                end_date = parse_datetime(secret.get("endDateTime")).date()

    return end_date


class MSGraphGrantUpdateView(LoginRequiredMixin, UpdateView):
    model = GraphGrant
    form_class = MSGraphGrantForm
    template_name = "grants/grant_update.html"
    success_url = reverse_lazy('organization-list')

    def get(self, request, *args, **kwargs):
        self.end_date = kwargs.get("end_date")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        is_htmx = self.request.headers.get("HX-Request", False) == "true"

        if is_htmx:
            htmx_trigger = self.request.headers.get("HX-Trigger-Name")
            if htmx_trigger == "fetch-expiry-date":
                gg = self.get_object()
                end_date = gg.expiry_date  # Defining variable, as it's used in the return
                client_secret = request.POST.get("_client_secret")

                from os2datascanner.engine2.model.msgraph.utilities import MSGraphSource
                GraphCaller = MSGraphSource.GraphCaller

                try:
                    if client_secret:
                        # Secret has been changed.
                        # Initiate GraphCaller with new secret.
                        gg.client_secret = client_secret
                        gc = GraphCaller(gg.make_token)
                        end_date = get_secret_end_date(client_secret, end_date, gc, gg)
                    else:
                        # Secret is the same
                        gc = GraphCaller(gg.make_token)
                        end_date = get_secret_end_date(gg.client_secret, end_date, gc, gg)

                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        f"Fetched end date: {end_date}",
                        extra_tags="auto_close"
                    )

                except HTTPError as e:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        e,
                        extra_tags="auto_close"
                    )
                return self.get(request, *args, end_date=end_date)

        else:
            return super().post(request, *args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()

        if self.request.method == "POST" and self.request.headers.get(
                "HX-Request", False) == "true":
            # request.POST is an immutable querydict, copying to circumvent.
            post_copy = self.request.POST.copy()
            post_copy["expiry_date"] = self.end_date

            kwargs.update({
                'data': post_copy,
            })

        return kwargs
