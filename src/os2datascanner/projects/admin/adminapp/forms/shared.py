from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Permission
from django.db.models import Q

from os2datascanner.projects.shared.forms import GroupingModelForm
from os2datascanner.projects.admin.organizations.models import Account, Organization
from os2datascanner.projects.admin.utilities import UserWrapper
from os2datascanner.projects.admin.adminapp.models.rules import Rule

from ...organizations.models.aliases import AliasType


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

    SCOPE_SETTINGS = (
        _("Scan scope settings"),
        ["org_units", "scan_entire_org"],
    )


class RemediatorSelectMultipleWidget(forms.SelectMultiple):
    """ Select multiple widget with display of universal remediators added"""
    template_name = "components/admin_widgets/remediator_select_multiple.html"

    def __init__(self, *args, **kwargs):
        # This is, maybe a little hacky, set in the ScannerForm's __init__
        self.universal_remediators = None
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['universal_remediators'] = self.universal_remediators
        return context


class ScannerForm(GroupingModelForm):

    remediators = forms.ModelMultipleChoiceField(
                    label=_("Remediators"),
                    queryset=Account.objects.all(),  # Take org into consideration
                    required=False,
                    widget=RemediatorSelectMultipleWidget(attrs={
                        "hx-swap-oob": "true"
                    }))

    contacts = forms.ModelMultipleChoiceField(
                    label=_("Contacts"),
                    queryset=User.objects.all(),  # Should only be admins for the org or superusers
                    required=False,
                    widget=forms.SelectMultiple(attrs={
                        "hx-swap-oob": "true"
                    }))

    organization = forms.ModelChoiceField(
                    label=_("Organization"),
                    queryset=Organization.objects.all(),
                    empty_label=None,
                    widget=forms.Select(attrs={
                        "hx-swap": "none",  # Let the oob manage switching fields!
                        "hx-trigger": "change",
                        "hx-push-url": "true",
                    }))
    # Change validation_status to a RadioSelect

    rule = forms.ModelChoiceField(
                    label=_("Rule"),
                    queryset=Rule.objects.all(),
                    widget=forms.Select(attrs={
                        "hx-swap-oob": "true"
                    })
                    )

    exclusion_rule = forms.ModelChoiceField(
                    label=_("Exclusion rule"),
                    queryset=Rule.objects.all(),
                    required=False,
                    widget=forms.Select(attrs={
                        "hx-swap-oob": "true"
                    })
                    )

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

        # Only allow the user to choose between remediators related to the organization.
        # Exclude accounts which are already designated universal remediators.
        self.fields["remediators"].queryset = self.fields["remediators"].queryset.filter(
            organization=self.org).exclude(
                aliases___alias_type=AliasType.REMEDIATOR.value, aliases___value=0)

        # This might seem a litle hacky - but Django really doesn't want widgets to know
        # anything about view context data, and as so, this seems like the best option currently
        # as long as we don't want to take more control over how we render the form.
        self.fields["remediators"].widget.universal_remediators = Account.objects.filter(
            Q(organization=self.org)
            &
            Q(aliases___alias_type=AliasType.REMEDIATOR)
            & Q(aliases___value=0)
        )

        # Only allow the user to choose between contacts who are admins for the organization client
        # or superusers
        view_client_perm = Permission.objects.get(codename="view_client")
        self.fields["contacts"].queryset = self.fields["contacts"].queryset.filter(
            Q(administrator_for__client=self.org.client) |
            Q(user_permissions=view_client_perm) |
            Q(groups__permissions=view_client_perm)
        ).distinct()

        # Only allow the user to choose between rules related to the organization
        self.fields["rule"].queryset = self.fields["rule"].queryset.filter(
            # Rules belonging to the organization ...
            Q(organization_id=self.org.uuid) |
            # ... or system rules applied to the organization
            Q(organization=None, organizations__uuid=self.org.uuid)
        )

        # Only allow the user to choose between exclusion rules related to the organization
        self.fields["exclusion_rule"].queryset = self.fields["exclusion_rule"].queryset.filter(
            # Rules belonging to the organization ...
            Q(organization_id=self.org.uuid) |
            # ... or system rules applied to the organization
            Q(organization=None, organizations__uuid=self.org.uuid)
        )

        # Only allow the user to change the validation_status field with the correct permission
        if not self.user.has_perm("os2datascanner.can_validate"):
            self.fields["validation_status"].disabled = True
            self.fields["validation_status"].required = False
