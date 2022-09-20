#!/usr/bin/env python
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
# OS2datascanner was developed by Magenta in collaboration with OS2 the
# Danish community of open source municipalities (https://os2.eu/).
#
# The code is currently governed by OS2 the Danish community of open
# source municipalities ( https://os2.eu/ )
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import HttpResponse

from ..models.userprofile import User, UserProfile
from ...organizations.models import Alias, Account, Organization


class UserView(TemplateView, LoginRequiredMixin):
    template_name = "user.html"
    context_object_name = "user"
    model = User

    def get_queryset(self):
        return User.objects.get(username=self.request.user)

    def get_context_data(self, **kwargs):
        user = self.request.user
        if not UserProfile.objects.filter(user=user).exists():
            if user.aliases.exists():
                user_org = user.aliases.first().account.organization
            else:
                user_org = Organization.objects.first()
            UserProfile.objects.update_or_create(
                user=user, defaults={
                    "organization": user_org})

        context = super().get_context_data(**kwargs)
        context["user_roles"] = [role._meta.verbose_name for role in User.objects.get(
            username=user.username).roles.select_subclasses().all()]
        context["aliases"] = User.objects.get(username=user.username).aliases.all()

        # Change this to only aliases from the same organization as the user.
        org_users = Account.objects.filter(organization=user.profile.organization)
        context["other_users"] = org_users

        return context


def delegate_user_matches(request):
    user = request.user
    account_uuid = request.POST.get('delegate_to')
    delegation_message = request.POST.get('delegation_message')

    if account_uuid == "none":
        user.profile.delegate_all_to = None
        user.profile.delegate_all_message = None
        user.profile.save()
    else:
        alias = Alias.objects.filter(account__uuid=account_uuid).first()
        user.profile.delegate_all_to = alias
        user.profile.delegate_all_message = delegation_message
        user.profile.save()

    return HttpResponse()
