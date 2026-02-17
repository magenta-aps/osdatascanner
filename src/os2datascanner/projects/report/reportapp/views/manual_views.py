# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class ManualMainView(LoginRequiredMixin, TemplateView):
    template_name = "manual.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = self.request.user.account.organization
        context["organization"] = organization
        context["categorization"] = organization.has_categorize_permission()
        context["file_delete"] = organization.has_msgraph_file_delete_permission()
        return context
