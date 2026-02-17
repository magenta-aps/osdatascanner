# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

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
        _("Scan scope"),
        ["scan_scope_mode"],
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


class ScanScopeMixin(forms.Form):
    """
    Opt-in mixin for scanners that support OU scoping.

    Features:
      - Radio-based UI for scope selection
      - Nested rendering of org_units
      - Mapping scan_scope_mode -> scan_entire_org
    """

    class ScanScopeRadioWidget(forms.RadioSelect):
        template_name = "components/admin_widgets/scan_scope_radio.html"

        def __init__(self, *args, **kwargs):
            # BoundField for org_units is injected by the mixin
            # so the widget template can render it inline.
            self.org_units_bound_field = None
            super().__init__(*args, **kwargs)

        def get_context(self, name, value, attrs):
            ctx = super().get_context(name, value, attrs)
            ctx["org_units"] = self.org_units_bound_field
            return ctx

    scan_scope_mode = forms.ChoiceField(
        label="",  # Group legend is used instead of field label.
        choices=(
            ("all", _("Scan all accounts in organization")),
            ("select", _("Select organizational units to scan")),
        ),
        widget=ScanScopeRadioWidget,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_scan_scope()

    def _setup_scan_scope(self):
        # Bound POST data takes precedence over instance/initial state.
        if self.is_bound:
            mode = self.data.get("scan_scope_mode")
        else:
            # Derive initial mode from legacy scan_entire_org.
            scan_entire = self.initial.get("scan_entire_org")
            if scan_entire is None:
                scan_entire = getattr(self.instance, "scan_entire_org", None)
            mode = "all" if scan_entire else "select"

        self.fields["scan_scope_mode"].initial = mode

        # Hide legacy checkbox — value is controlled via radio UI.
        if "scan_entire_org" in self.fields:
            self.fields["scan_entire_org"].widget = forms.HiddenInput()

        # Inject BoundField so widget template can render org_units inline.
        if "org_units" in self.fields:
            self.fields["scan_scope_mode"].widget.org_units_bound_field = self["org_units"]

    field_order = ["scan_scope_mode", "scan_entire_org"]

    def clean_scan_entire_org(self):
        mode = self.cleaned_data.get("scan_scope_mode")

        if mode:
            return mode == "all"
        return self.cleaned_data.get("scan_entire_org")

    def clean(self):
        cleaned_data = super().clean()
        scan_entire_org = cleaned_data.get("scan_entire_org")
        org_units = cleaned_data.get("org_units")

        if "org_units" in self.fields:
            if not scan_entire_org and not (org_units and org_units.exists()):
                self.add_error(
                    "org_units",
                    _(
                        "Select one or more organizational units, "
                        "or choose to scan the entire organization."
                    )
                )

        return cleaned_data


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
                    }))

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

        # Restrict org-specific fields to the selected org (if present)
        for name in ("grant", "org_units"):
            if name not in self.fields:
                continue
            field = self.fields[name]
            field.queryset = field.queryset.filter(organization=self.org)
            field.widget.attrs["hx-swap-oob"] = "true"

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
