from django import forms
from django.utils.translation import gettext_lazy as _

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
                    required=False)

    organization = forms.ModelChoiceField(
                    queryset=Organization.objects.all(),
                    empty_label=None,
                    widget=forms.Select(attrs={
                        "hx-get": "",
                        "hx-swap": "outerHTML",
                        "hx-target": ".content",
                        "hx-select": ".content",
                        "hx-trigger": "change",
                    })
                    )
    # Change validation_status to a RadioSelect

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.org = kwargs.pop("org")
        super().__init__(*args, **kwargs)

        user = UserWrapper(self.user)
        self.fields["organization"].queryset = self.fields["organization"].queryset.filter(
            user.make_org_Q("uuid")
        ).order_by("name")
        self.fields["organization"].initial = self.org.uuid

        self.fields["remediators"].queryset = self.fields["remediators"].queryset.filter(
            organization=self.org
        )

        if not self.user.has_perm("os2datascanner.can_validate"):
            self.fields.pop("validation_status")
            general_settings = self.groups[0][1]
            if "validation_status" in general_settings:
                general_settings.remove("validation_status")
