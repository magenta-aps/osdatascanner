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
from django.db.models import Q, ExpressionWrapper, BooleanField
from django.utils.translation import gettext_lazy as _
from django.forms import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.http import HttpResponse, Http404

from os2datascanner.projects.admin.organizations.models import Organization

from .views import RestrictedListView, RestrictedCreateView, \
    RestrictedUpdateView, RestrictedDeleteView
from .validators import customrule_validator
from ..models.sensitivity_level import Sensitivity
from ..models.rules import Rule, CustomRule, RuleCategory
from ...utilities import UserWrapper


class RuleList(RestrictedListView):
    """Displays list of scanners."""

    model = CustomRule
    context_object_name = 'rules'
    template_name = 'rules.html'

    def get_system_rules(self, organization):
        system_rules = CustomRule.objects.filter(organization__isnull=True)
        if selected_categories_pks := self.request.GET.getlist("categories"):
            unselected_categories = RuleCategory.objects.exclude(pk__in=selected_categories_pks)

            system_rules = system_rules.exclude(categories__in=unselected_categories)

        system_rules = system_rules.annotate(
            connected=ExpressionWrapper(
                Q(organizations=organization),
                output_field=BooleanField()
            )
        )

        return system_rules

    def get_context_data(self):
        context = super().get_context_data()

        user = UserWrapper(self.request.user)
        organizations = Organization.objects.filter(user.make_org_Q("uuid"))
        context["organizations"] = organizations

        if org_pk := self.request.GET.get("selected_org"):
            selected_org = organizations.get(pk=org_pk)
        else:
            selected_org = organizations.first()

        context["categories"] = RuleCategory.objects.all()
        context["selected_categories"] = self.request.GET.getlist(
            "categories") or RuleCategory.objects.all()

        context["sensitivity"] = Sensitivity
        context["systemrule_list"] = self.get_system_rules(selected_org)
        context["customrule_list"] = self.get_queryset().filter(organization__isnull=False)

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

        def validate_surrounding_words_exceptions(rule):
            if "surrounding_exceptions" not in rule:
                return True
            ex_string = rule.get('surrounding_exceptions')
            # Check that the "surrounding_exceptions"-string only contains
            # alphanumeric characters or is an empty string.
            # TODO: But ... The regex does not only allow alphanumeric characters.
            # Do we only want alphanumeric characters or not?
            validated = bool(re.match(r'^[a-zA-Z0-9æøåÆØÅ,-]*$', ex_string))
            return validated

        if crule := form.cleaned_data.get('rule'):
            if not validate_exceptions_field(crule):
                form.add_error(
                    'rule', _("The 'exceptions'-string must be a "
                              "comma-separated list of 10-digit numbers."))
                raise ValidationError(_("Formatting error"), code="formatting")
            elif not validate_surrounding_words_exceptions(crule):
                form.add_error(
                    'rule', _("The 'surrounding_exceptions'-string must not "
                              "include any symbols or spaces."))
                raise ValidationError(_("Formatting error"), code="formatting")
            else:
                rule._rule = crule
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
        form.fields['rule'] = forms.JSONField(
            validators=[customrule_validator])

        return form


class RuleUpdate(RestrictedUpdateView):
    """Update a rule view."""

    model = Rule
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
        form.fields['rule'] = forms.JSONField(
            initial=self.object._rule,
            validators=[customrule_validator])

        return form


class RuleDelete(RestrictedDeleteView):
    """Delete a rule view."""
    model = Rule
    success_url = '/rules/'


class CustomRuleDelete(RuleDelete):
    model = CustomRule


class CustomRuleConnect(LoginRequiredMixin, UpdateView):
    model = CustomRule

    def post(self, request, *args, **kwargs):
        response = HttpResponse()

        self.object = self.get_object()
        organizations = Organization.objects.filter(UserWrapper(request.user).make_org_Q("uuid"))
        try:
            organization = organizations.get(uuid=request.POST.get('selected_org'))
        except Organization.DoesNotExist:
            raise Http404("User is not connected to a valid organization.")

        connection = int(request.POST.get('table-checkbox', '0')) == self.object.pk

        if connection:
            self.object.organizations.add(organization)
        else:
            self.object.organizations.remove(organization)

        return response
