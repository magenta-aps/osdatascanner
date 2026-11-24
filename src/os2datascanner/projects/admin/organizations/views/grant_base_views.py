# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView, UpdateView

from os2datascanner.projects.admin.adminapp.views.views import OrgRestrictedMixin
from os2datascanner.projects.admin.adminapp.views.utils.grant_mixin import (GrantExtraMixin,
                                                                            GrantModalMixin)
from os2datascanner.projects.admin.organizations.models import Organization
from os2datascanner.projects.admin.organizations.utils import get_user_org_or_404
from os2datascanner.projects.admin.utilities import UserWrapper


class _GrantOrgChoicesMixin:
    """Limits the form's organization choices to the organizations the user
    may administer."""

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["organization"].queryset = Organization.objects.filter(
                UserWrapper(self.request.user).make_org_Q("uuid"))
        return form


class _GrantOrgFromURLMixin:
    """Raises Http404 unless the user may administer the organization given by
    the "org" URL argument."""

    def dispatch(self, request, *args, **kwargs):
        get_user_org_or_404(request.user, kwargs["org"])
        return super().dispatch(request, *args, **kwargs)


class GrantCreateView(PermissionRequiredMixin, LoginRequiredMixin, _GrantOrgFromURLMixin,
                      _GrantOrgChoicesMixin, GrantModalMixin, GrantExtraMixin, CreateView):
    """Base view for creating a grant for an organization the user may
    administer."""

    def get_initial(self):
        return super().get_initial() | {"organization": self.kwargs["org"]}


class GrantUpdateView(PermissionRequiredMixin, OrgRestrictedMixin, _GrantOrgChoicesMixin,
                      GrantExtraMixin, UpdateView):
    """Base view for editing a grant of an organization the user may
    administer."""
