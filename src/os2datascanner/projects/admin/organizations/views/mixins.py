# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.http import Http404
from django.utils.translation import gettext_lazy as _

from ..utils import get_user_org_or_404, user_allowed


class ClientAdminMixin:
    """Mixin for making sure, that the requesting user is either an admin for
    the client, for which they are requesting data, or is a superuser."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        org, allowed = user_allowed(request.user, kwargs['org_slug'])
        # Add the organization to the kwargs for future use.
        self.kwargs['org'] = org
        if allowed:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404(
                _("Account not found.")
                )


class UserOrgFromURLMixin:
    """Mixin that sets self.kwargs["organization"] to the organization given
    by the "org_id" URL argument, and raises Http404 unless the user may
    administer it. Place it after LoginRequiredMixin."""

    def dispatch(self, request, *args, **kwargs):
        self.kwargs["organization"] = get_user_org_or_404(request.user, kwargs["org_id"])
        return super().dispatch(request, *args, **kwargs)
