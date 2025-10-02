# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2datascanner is developed by Magenta in collaboration with the OS2 public
# sector open source network <https://os2.eu/>.
#

from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import modelform_factory
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, TemplateView, DetailView, RedirectView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.edit import ModelFormMixin, DeleteView
from django.conf import settings
from django.urls import reverse_lazy

from os2datascanner.projects.admin.utilities import UserWrapper
from ..models.scannerjobs.dropboxscanner import DropboxScanner
from ..models.scannerjobs.exchangescanner import ExchangeScanner
from ..models.scannerjobs.filescanner import FileScanner
from ..models.scannerjobs.gmail import GmailScanner
from ..models.scannerjobs.sbsysscanner import SbsysScanner
from ..models.scannerjobs.msgraph import (
    MSGraphFileScanner,
    MSGraphMailScanner,
    MSGraphCalendarScanner,
    MSGraphTeamsFileScanner,
    MSGraphSharepointScanner)
from ..models.scannerjobs.webscanner import WebScanner
from ..models.scannerjobs.googledrivescanner import GoogleDriveScanner
from ..models.scannerjobs.googleshareddrivescannner import GoogleSharedDriveScanner

import structlog


logger = structlog.get_logger("adminapp")


def _hide_csrf_token_and_password(d):
    """Return a shallow copy of *d* without the `csrfmiddlewaretoken` key."""
    new = dict(**d)
    new.pop("csrfmiddlewaretoken", None)
    new.pop("password", None)
    return new


class RestrictedListView(LoginRequiredMixin, ListView):
    def get_queryset(self, **kwargs):
        """Restrict to the organization of the logged-in user."""
        return super().get_queryset().filter(
            UserWrapper(
                self.request.user).make_org_Q(
                org_path=kwargs.get(
                    "org_path",
                    "organization")))


class GuideView(TemplateView):
    template_name = "guide.html"

    def dispatch(self, request, *args, **kwargs):
        if settings.MANUAL_PAGE:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404()


# Create/Update/Delete Views.
class RestrictedCreateView(LoginRequiredMixin, CreateView):
    """Base class for create views that are limited by user organization."""

    def post(self, request, *args, **kwargs):
        logger.info(
            f"Create issued to {self.__class__.__name__}",
            request_data=_hide_csrf_token_and_password(dict(request.POST)),
            user=str(request.user),
            **kwargs,
        )
        return super().post(request, *args, **kwargs)

    def get_form_fields(self):
        """Get the list of fields to use in the form for the view."""
        fields = [f for f in self.fields]
        return fields

    def get_form(self, form_class=None):
        """Get the form for the view."""
        fields = self.get_form_fields()
        form_class = modelform_factory(self.model, fields=fields)
        kwargs = self.get_form_kwargs()
        form = form_class(**kwargs)
        return form

    def form_valid(self, form):
        """Validate the form."""
        user = self.request.user
        if not user.is_superuser:
            self.object = form.save(commit=False)

        return super().form_valid(form)


class OrgRestrictedMixin(LoginRequiredMixin):
    """Mixin class for views with organization-restricted queryset."""

    def get_queryset(self, **kwargs):
        """Get queryset filtered by user's organization."""
        return super().get_queryset().filter(
                UserWrapper(self.request.user).make_org_Q(org_path=kwargs.get(
                    "org_path",
                    "organization")))


class OrgRestrictedFormMixin(OrgRestrictedMixin, ModelFormMixin):
    """Mixin class for views with organizaiton-restricted queryset and form
    fields."""

    def get_form_fields(self):
        """Get the list of fields to use in the form for the view."""
        if not self.fields:
            return []
        fields = [f for f in self.fields]

        return fields


class RestrictedUpdateView(OrgRestrictedFormMixin, UpdateView):
    """Base class for updateviews restricted by organiztion."""

    def post(self, request, *args, **kwargs):
        logger.info(
            f"Update issued to {self.__class__.__name__}",
            request_data=_hide_csrf_token_and_password(dict(request.POST)),
            user=str(request.user),
            **kwargs,
        )
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        """Get the form for the view."""
        fields = self.get_form_fields()
        form_class = modelform_factory(self.model, fields=fields)
        kwargs = self.get_form_kwargs()
        form = form_class(**kwargs)
        return form

    def form_valid(self, form):
        """Validate the form."""
        user = self.request.user
        if not user.is_superuser:
            self.object = form.save(commit=False)

        return super().form_valid(form)


class RestrictedDetailView(OrgRestrictedMixin, DetailView):
    """Base class for detailviews restricted by organiztion."""


class RestrictedDeleteView(OrgRestrictedMixin, DeleteView):
    """Base class for deleteviews restricted by organiztion."""

    def post(self, request, *args, **kwargs):
        logger.info(
            f"Delete issued to {self.__class__.__name__}",
            user=str(request.user),
            **kwargs,
        )
        return super().post(request, *args, **kwargs)


class DialogSuccess(TemplateView):
    """View that handles success for iframe-based dialogs."""

    template_name = 'components/modals/dialogsuccess.html'

    type_map = {
        'webscanners': WebScanner,
        'filescanners': FileScanner,
        'exchangescanners': ExchangeScanner,
        'dropboxscanners': DropboxScanner,
        'msgraphfilescanners': MSGraphFileScanner,
        'msgraphmailscanners': MSGraphMailScanner,
        'msgraphcalendarscanners': MSGraphCalendarScanner,
        'msgraphteamsfilescanners': MSGraphTeamsFileScanner,
        'msgraphsharepointscanners': MSGraphSharepointScanner,
        'googledrivescanners': GoogleDriveScanner,
        'googleshareddrivescanners': GoogleSharedDriveScanner,
        'gmailscanners': GmailScanner,
        'sbsysscanners': SbsysScanner,
    }

    def get_context_data(self, **kwargs):
        """Setup context for the template."""
        context = super().get_context_data(**kwargs)
        model_type = self.args[0]
        pk = self.args[1]
        created = self.args[2] == 'created'
        if model_type not in self.type_map:
            raise Http404
        model = self.type_map[model_type]
        item = get_object_or_404(model, pk=pk)
        context['item_description'] = item.verbose_name
        context['action'] = _("created") if created else _("saved")
        context['reload_url'] = '/' + model_type + '/'
        return context


class IndexView(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        model_and_url_list = [
            (WebScanner, reverse_lazy("webscanners")),
            (FileScanner, reverse_lazy("filescanners")),
            (ExchangeScanner, reverse_lazy("exchangescanners")),
            (GoogleDriveScanner, reverse_lazy("googledrivescanners")),
            (GmailScanner, reverse_lazy("gmailscanners")),
            (MSGraphMailScanner, reverse_lazy("msgraphmailscanners")),
            (MSGraphFileScanner, reverse_lazy("msgraphfilescanners")),
            (MSGraphCalendarScanner, reverse_lazy("msgraphcalendarscanners")),
            (MSGraphTeamsFileScanner, reverse_lazy("msgraphteamsfilescanners")),
            (MSGraphSharepointScanner, reverse_lazy("msgraphsharepointscanners")),
            (SbsysScanner, reverse_lazy("sbsysscanners"))
        ]

        for model, url in model_and_url_list:
            if model.enabled():
                return url
        else:
            # We will only reach this point if the above for-loop gets to finish.
            raise Http404(_("No scanner types are enabled for this installation"))
