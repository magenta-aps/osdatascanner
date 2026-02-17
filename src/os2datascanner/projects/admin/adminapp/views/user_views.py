# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.views.generic import DetailView, UpdateView, RedirectView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy


class UserAccessMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        user_pk = kwargs.get("pk")
        if request.user.is_authenticated and not request.user.pk == user_pk:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class MyUserView(LoginRequiredMixin, RedirectView):
    pattern_name = "user"

    def get_redirect_url(self, *args, **kwargs):
        pk = self.request.user.pk
        return super().get_redirect_url(*args, pk=pk, **kwargs)


class UserDetailView(UserAccessMixin, DetailView):
    model = get_user_model()
    template_name = "components/user/user_detail.html"
    context_object_name = "user"


class UserUpdateView(UserAccessMixin, PermissionRequiredMixin, UpdateView):
    model = get_user_model()
    template_name = "components/user/user_edit.html"
    context_object_name = "user"
    permission_required = "auth.change_user"
    fields = (
        "first_name",
        "last_name",
        "email"
    )

    def get_success_url(self):
        url = reverse_lazy("user", kwargs={"pk": self.kwargs.get("pk")})
        return url
