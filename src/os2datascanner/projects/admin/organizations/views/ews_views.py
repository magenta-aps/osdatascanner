# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.urls import reverse_lazy

from os2datascanner.projects.grants.admin import EWSGrantAdminForm
from os2datascanner.projects.grants.models.ewsgrant import EWSGrant
from .grant_base_views import GrantCreateView, GrantUpdateView


class EWSGrantForm(EWSGrantAdminForm):
    """ Form for user interaction purposes.
        Disables the Organization field. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["organization"].disabled = True


class EWSGrantCreateView(GrantCreateView):
    model = EWSGrant
    form_class = EWSGrantForm
    permission_required = "grants.add_ewsgrant"
    template_name = "grants/ewsgrant_update.html"
    success_url = reverse_lazy("grant-list")


class EWSGrantUpdateView(GrantUpdateView):
    model = EWSGrant
    form_class = EWSGrantForm
    permission_required = "grants.change_ewsgrant"
    template_name = "grants/ewsgrant_update.html"
    success_url = reverse_lazy("grant-list")
