# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import json

from django.forms import ModelChoiceField
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from os2datascanner.projects.admin.utilities import UserWrapper
from os2datascanner.projects.admin.organizations.models.grant_extra import (GrantExtra,
                                                                            GrantExtraForm)


def grant_permission_map(field_name: str) -> str:
    grant_permission_name_map = {
        "GraphGrant": "graphgrant",
        "graph_grant": "graphgrant",
        "SMBGrant": "smbgrant",
        "smb_grant": "smbgrant",
        "EWSGrant": "ewsgrant",
        "ews_grant": "ewsgrant",
        "GoogleApiGrant": "googleapigrant",
        "google_api_grant": "googleapigrant"
    }
    return grant_permission_name_map[field_name]


def grant_create_url_map(field_name: str) -> str:
    grant_create_url_names = {
        "smb_grant": "smbgrant-create",
        "ews_grant": "ewsgrant-create",
        "graph_grant": "msgraphgrant-create",
        "google_api_grant": "googleapigrant-create",
    }
    return grant_create_url_names[field_name]


class GrantMixin:
    """Sets up the grant dropdowns on the scanner forms.

    New grants are created in a modal from the "+" next to each dropdown (see GrantModalMixin)."""

    def get_grant_form_classes(self) -> dict:
        """Override this method to return a dictionary of grant
         form classes and their corresponding field."""
        raise NotImplementedError("Subclasses should implement this method.")

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        form = super().get_form(form_class)
        user = UserWrapper(self.request.user)

        for field_name, GrantFormClass in self.get_grant_form_classes().items():
            grant_qs = GrantFormClass.Meta.model.objects.filter(user.make_org_Q())
            # Conditionally required. Should be required when there's only one option, but can't
            # be, when there's two or more. (F.e. ExchangeScanner)
            form.fields[field_name] = ModelChoiceField(grant_qs, empty_label=None,
                                                       label=form.fields[field_name].label,
                                                       required=False if
                                                       len(self.get_grant_form_classes()) >= 2
                                                       else True)

        return form


class GrantExtraMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        grant = getattr(self, 'object', None)
        if grant:
            grant_extra, _ = GrantExtra.objects.get_or_create(grant=grant)
        else:
            grant_extra = GrantExtra()

        context["extra_form"] = GrantExtraForm(self.request.POST or None, instance=grant_extra)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        grant_extra, _ = GrantExtra.objects.get_or_create(grant=self.object)
        extra_form = GrantExtraForm(self.request.POST, instance=grant_extra)

        if extra_form.is_valid():
            extra_form.save()
        else:
            return self.form_invalid(form)

        return response


class GrantModalMixin:
    """Lets a grant create view render inside a modal dialog when it's requested with htmx.
    Instead of the full page, it renders the form as a modal, and on success it returns
    204 with a "grantCreated" event rather than redirecting to the grant list."""

    modal_template_name = "components/modals/modal__create-grant.html"
    modal_id = "grant-modal"

    def get_field(self):
        """The scanner form field to update once the grant is saved."""
        return self.request.GET.get("field") or self.request.POST.get("field")

    def is_modal(self):
        # Only the modal sends "field". Other htmx requests to the view (e.g. the Graph
        # grant page's "fetch expiry date"), get the normal page:
        return self.request.headers.get("HX-Request") == "true" and bool(self.get_field())

    def get_template_names(self):
        if self.is_modal():
            return [self.modal_template_name]
        return super().get_template_names()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.is_modal():
            # The scanner form has fields with the same names (e.g. "organization"), so prefix
            # the grant form's fields to keep their ids unique on the page:
            kwargs["prefix"] = "grant"
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.is_modal():
            # Hidden fields are rendered separately by the template:
            visible = [*context["form"].visible_fields(), *context["extra_form"].visible_fields()]

            # Start in the first field the user can fill in, rather than on the close button:
            first = next((bf for bf in visible if not bf.field.disabled), None)
            if first:
                first.field.widget.attrs["autofocus"] = True

            context |= {
                "modal_id": self.modal_id,
                "close_label": _("Close without saving the grant."),
                "field": self.get_field(),
                "items": [{"type": "field", "bf": bf, "errors": bf.errors} for bf in visible],
            }
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # GrantExtraMixin returns form_invalid if the extra form doesn't validate:
        if self.is_modal() and response.status_code == 302:
            response = HttpResponse(status=204)
            response["HX-Trigger"] = json.dumps({"grantCreated": {
                "field": self.get_field(),
                "pk": str(self.object.pk),
                "label": str(self.object),
            }})
        return response
