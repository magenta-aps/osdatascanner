from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Permission
from django.db.models import Q

from os2datascanner.projects.shared.forms import GroupingModelForm
from os2datascanner.projects.admin.organizations.models import Account, Organization
from os2datascanner.projects.admin.utilities import UserWrapper


class Groups:
    GENERAL_SETTINGS = (
        _("General settings"),
        ["name", "organization", "validation_status"],
    )

    RESULT_SETTINGS = (
        _("Result settings"),
        ["contacts", "only_notify_superadmin", "keep_false_positives"],
    )

    ADVANCED_RESULT_SETTINGS = (
        _("Result settings"),
        ["contacts", "remediators", "only_notify_superadmin",
         "keep_false_positives"],
    )

    SCHEDULED_EXECUTION_SETTINGS = (
        _("Scheduled execution settings"),
        ["schedule"],
    )


class ScannerForm(GroupingModelForm):

    remediators = forms.ModelMultipleChoiceField(
                    queryset=Account.objects.all(),  # Take org into consideration
                    required=False,
                    widget=forms.SelectMultiple(attrs={
                        "hx-swap-oob": "true"
                    }))

    contacts = forms.ModelMultipleChoiceField(
                    queryset=User.objects.all(),  # Should only be admins for the org or superusers
                    required=False,
                    widget=forms.SelectMultiple(attrs={
                        "hx-swap-oob": "true"
                    }))

    organization = forms.ModelChoiceField(
                    queryset=Organization.objects.all(),
                    empty_label=None,
                    widget=forms.Select(attrs={
                        "hx-swap": "none",  # Let the oob manage switching fields!
                        "hx-trigger": "change",
                        "hx-push-url": "true",
                    }))
    # Change validation_status to a RadioSelect

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.org = kwargs.pop("org")
        self.this_url = kwargs.pop("this_url")
        super().__init__(*args, **kwargs)

        # Make sure changes to the organization field calls the correct view
        self.fields["organization"].widget.attrs["hx-get"] = self.this_url

        # Only allow the user to choose between organizations they have access to.
        user = UserWrapper(self.user)
        self.fields["organization"].queryset = self.fields["organization"].queryset.filter(
            user.make_org_Q("uuid")
        ).order_by("name")
        self.fields["organization"].initial = self.org.uuid

        # Only allow the user to choose between remediators related to the organization
        self.fields["remediators"].queryset = self.fields["remediators"].queryset.filter(
            organization=self.org)

        # Only allow the user to choose between contacts who are admins for the organization client
        # or superusers
        view_client_perm = Permission.objects.get(codename="view_client")
        self.fields["contacts"].queryset = self.fields["contacts"].queryset.filter(
            Q(administrator_for__client=self.org.client) |
            Q(user_permissions=view_client_perm) |
            Q(groups__permissions=view_client_perm)
        )

        # Only allow the user to change the validation_status field with the correct permission
        if not self.user.has_perm("os2datascanner.can_validate"):
            self.fields["validation_status"].disabled = True
            self.fields["validation_status"].required = False
