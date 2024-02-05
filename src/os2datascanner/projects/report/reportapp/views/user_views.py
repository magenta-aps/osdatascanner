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
import structlog
from django.conf import settings
from django.contrib import messages
from django.contrib.messages import get_messages
from django.core.exceptions import PermissionDenied
from django import forms
from django.db.models import Count
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from os2datascanner.core_organizational_structure.models import OutlookCategorizeChoices
from ...organizations.models.aliases import AliasType
from ...organizations.models import Account, AccountOutlookSetting

logger = structlog.get_logger("reportapp")


class AccountOutlookSettingForm(forms.ModelForm):

    class Meta:
        model = AccountOutlookSetting
        fields = ['categorize_email']
        widgets = {
            'categorize_email': forms.CheckboxInput(
                attrs={'class': "some-neat-css"}  # TODO: example here for how to style
            ),
        }

    def __init__(self, organization, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Both these settings means that the user should not be able to choose.
        # NONE hides this form entirely, but included here for good measure.
        if (organization.outlook_categorize_email_permission in
                (OutlookCategorizeChoices.ORG_LEVEL, OutlookCategorizeChoices.NONE)):
            # Disable field and add explanatory tool-tip explanation
            # But, do note that disabled means this field won't be included in POST data
            # read_only is an alternative, but that is not safe from users editing HTML.
            self.fields['categorize_email'].disabled = True
            self.fields['categorize_email'].widget.attrs['title'] = (
                _("Your organization has configured this setting for you, disallowing change."))


class AccountOutlookSettingView(LoginRequiredMixin, DetailView):
    context_object_name = "account"
    model = Account

    def get_object(self, queryset=None):
        if self.kwargs.get("pk") is None:
            try:
                self.kwargs["pk"] = self.request.user.account.pk
            except Account.DoesNotExist:
                raise Http404()
        elif not (self.request.user.is_superuser or
                  self.kwargs.get("pk") == self.request.user.account.pk):
            raise PermissionDenied
        return super().get_object(queryset)

    def post(self, request, *args, **kwargs):  # noqa C901, CCR001
        account = self.get_object()
        htmx_trigger = self.request.headers.get("HX-Trigger-Name")

        # Getting a queryset - which should only hold one object - but allows us to use queryset
        # methods.
        # TODO: raise something / abort, if it contains more than one object?
        outl_setting = AccountOutlookSetting.objects.filter(account=account)

        if htmx_trigger == "categorize_existing":
            # Call queryset method to sort that out
            message = outl_setting.categorize_existing()
            # Messages and logging
            logger.info(f"{account} categorized their emails manually")
            messages.add_message(
                request,
                messages.SUCCESS,
                message,
                extra_tags="auto_close"
            )

        if request.POST.get("outlook_setting", False):  # We're doing stuff in the outlook settings
            categorize_check = request.POST.get("categorize_email", False) == "on"
            match_colour = request.POST.get("match_colour")
            false_positive_colour = request.POST.get("false_positive_colour")

            # If categorization is enabled, either by POST data or ORG_LEVEL
            if (categorize_check or
                    account.organization.outlook_categorize_email_permission ==
                    OutlookCategorizeChoices.ORG_LEVEL):

                # and a category is missing
                # TODO: We only check if there is 1 or less categories, not what type of
                # categories there are ...
                if outl_setting.annotate(
                        categories=Count("outlook_categories")).filter(
                        categories__lte=1):
                    # Create/Verify that categories are populated
                    message = outl_setting.populate_setting()
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        message,
                        extra_tags="auto_close"
                    )

                # Else, we can assume that we're updating.
                # Check if one of the colours are changed
                if (outl_setting.false_positive_category.category_colour
                        != false_positive_colour) or (
                        outl_setting.match_category.category_colour
                        != match_colour):

                    message = outl_setting.update_colour(match_colour, false_positive_colour)
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        message,
                        extra_tags="auto_close"
                    )
            # Unchecking means disabling and will delete categories.
            elif not categorize_check:
                message = outl_setting.delete_categories()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    message,
                    extra_tags="auto_close"
                )

        # Used to make Django's messages framework and HTMX play ball.
        response = HttpResponse()
        response.write(
            render_to_string(
                template_name="components/feedback/snackbarNew.html",
                context={"messages": get_messages(request)},
                request=request
            )
        )

        return response


class AccountView(LoginRequiredMixin, DetailView):
    template_name = "user.html"
    context_object_name = "account"
    model = Account

    def get_object(self, queryset=None):
        if self.kwargs.get("pk") is None:
            try:
                self.kwargs["pk"] = self.request.user.account.pk
            except Account.DoesNotExist:
                raise Http404()
        elif not (self.request.user.is_superuser or
                  self.kwargs.get("pk") == self.request.user.account.pk):
            raise PermissionDenied
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if settings.MSGRAPH_ALLOW_WRITE and self.object.organization.has_categorize_permission():
            # Make sure Account has an AccountOutlookSetting object.
            AccountOutlookSetting.objects.get_or_create(account=self.object)
            # Include form in context etc.
            context["has_categorize_permission"] = True
            context["outlook_settings_form"] = AccountOutlookSettingForm(
                instance=self.object.outlook_settings,
                organization=self.object.organization
            )

        user = self.object.user
        context["user"] = user
        context["user_roles"] = [_("Remediator")] if self.object.is_remediator else None
        context["aliases"] = self.object.aliases.exclude(_alias_type=AliasType.REMEDIATOR)

        return context

    def post(self, request, *args, **kwargs):
        bool_field_status = request.POST.get("contact_check", False) == "checked"
        account = self.get_object()
        account.contact_person = bool_field_status
        account.save()
        return HttpResponse()
