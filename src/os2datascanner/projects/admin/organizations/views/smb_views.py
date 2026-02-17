# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView
from os2datascanner.projects.grants.admin import SMBGrantAdminForm
from os2datascanner.projects.grants.models.smbgrant import SMBGrant
from os2datascanner.projects.admin.adminapp.views.utils.grant_mixin import GrantExtraMixin


class SMBGrantForm(SMBGrantAdminForm):
    """ Form for user interaction purposes.
        Disables the Organization field. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["organization"].disabled = True


class SMBGrantCreateView(PermissionRequiredMixin, LoginRequiredMixin, GrantExtraMixin, CreateView):
    model = SMBGrant
    form_class = SMBGrantForm
    permission_required = "grants.add_smbgrant"
    template_name = "grants/smbgrant_update.html"
    success_url = reverse_lazy("grant-list")

    def get_initial(self):
        return {"organization": self.kwargs.get('org')}


class SMBGrantScannerForm(SMBGrantAdminForm):
    """ Form for use in Scanner Create/Update. """
    class Meta:
        model = SMBGrant
        fields = ('__all__')


class SMBGrantUpdateView(PermissionRequiredMixin, LoginRequiredMixin, GrantExtraMixin, UpdateView):
    model = SMBGrant
    form_class = SMBGrantForm
    permission_required = "grants.change_smbgrant"
    template_name = "grants/smbgrant_update.html"
    success_url = reverse_lazy("grant-list")
