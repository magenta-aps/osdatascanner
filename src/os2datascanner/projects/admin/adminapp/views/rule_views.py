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
# OS2datascanner is developed by Magenta in collaboration with the OS2 public
# sector open source network <https://os2.eu/>.
#
import re

from django import forms
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.forms import ValidationError

from os2datascanner.projects.admin.organizations.models import Organization

from .views import RestrictedListView, RestrictedCreateView, \
    RestrictedUpdateView, RestrictedDeleteView
from ..models.sensitivity_level import Sensitivity
from ..models.rules import Rule, CustomRule
from ...utilities import UserWrapper


class RuleList(RestrictedListView):
    """Displays list of scanners."""

    model = Rule
    context_object_name = 'rules'
    template_name = 'rules.html'

    def get_context_data(self):
        context = super().get_context_data()

        context["sensitivity"] = Sensitivity
        context["systemrule_list"] = self.get_queryset().filter(customrule__isnull=True)
        context["customrule_list"] = self.get_queryset().filter(customrule__isnull=False)

        return context


class RuleCreate(RestrictedCreateView):
    """Create a rule view."""

    model = Rule
    fields = ['name', 'description', 'sensitivity', 'organization']

    @staticmethod
    def _save_rule_form(form):
        rule = form.save(commit=False)
        rule.name = form.cleaned_data['name']
        rule.sensitivity = form.cleaned_data['sensitivity']
        rule.description = form.cleaned_data['description']

        def validate_exceptions_field(rule):
            if "exceptions" not in rule:
                return True
            ex_string = rule.get('exceptions')
            # Checks that the "exceptions"-string constists of comma-separated
            # 10-digit numbers or an empty string.
            validated = ex_string == "" or bool(re.match(r'^\d{10}(,\d{10})*$', ex_string))
            return validated

        if crule := form.cleaned_data.get('rule'):
            if ('exceptions' not in crule) or validate_exceptions_field(crule):
                rule._rule = crule
            else:
                form.add_error(
                    'rule', _("The 'exceptions'-string must be a "
                              "comma-separated list of 10-digit numbers."))
                raise ValidationError(_("Formatting error"), code="formatting")
        rule.save()
        return rule

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = UserWrapper(self.request.user)
        org_qs = Organization.objects.filter(user.make_org_Q("uuid"))
        form.fields['organization'].queryset = org_qs
        form.fields['organization'].empty_label = None

        return form

    def form_valid(self, form):
        """
        validate all the form first
        :param form:
        :return:
        """
        try:
            with transaction.atomic():
                RuleCreate._save_rule_form(form)
                return super().form_valid(form)
        except Exception:
            return super().form_invalid(form)


class CustomRuleCreate(RuleCreate):
    model = CustomRule
    template_name = "components/rules/customrule_form.html"
    fields = ['name', 'description', 'sensitivity', 'organization']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['rule'] = forms.JSONField()

        return form


class RuleUpdate(RestrictedUpdateView):
    """Update a rule view."""

    model = Rule
    edit = True
    fields = ['name', 'description', 'sensitivity', 'organization']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = UserWrapper(self.request.user)
        org_qs = Organization.objects.filter(user.make_org_Q("uuid"))
        form.fields['organization'].queryset = org_qs
        form.fields['organization'].empty_label = None

        return form

    def form_valid(self, form):
        """
        validate all the form first
        :param form:
        :return:
        """
        try:
            with transaction.atomic():
                RuleCreate._save_rule_form(form)
                return super().form_valid(form)
        except Exception:
            return super().form_invalid(form)


class CustomRuleUpdate(RuleUpdate):
    model = CustomRule
    fields = ['name', 'description', 'sensitivity', 'organization']
    template_name = "components/rules/customrule_form.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['rule'] = forms.JSONField(initial=self.object._rule)

        return form


class RuleDelete(RestrictedDeleteView):
    """Delete a rule view."""
    model = Rule
    success_url = '/rules/'


class CustomRuleDelete(RuleDelete):
    model = CustomRule


'''============ Methods required by multiple views ============'''


def extract_pattern_fields(form_fields):
    if not form_fields:
        return [('pattern_0', '')]

    return [(field_name, form_fields[field_name]) for field_name in form_fields if
            field_name.startswith('pattern_')]
