from .views import RestrictedListView, RestrictedCreateView, \
    RestrictedUpdateView, RestrictedDeleteView
from ..models.regexrule_model import RegexRule
from ..models.regexpattern_model import RegexPattern

from django import forms
from django.db import transaction

import ipdb

class RuleList(RestrictedListView):
    """Displays list of scanners."""

    model = RegexRule
    template_name = 'os2webscanner/rules.html'


class RuleCreate(RestrictedCreateView):
    """Create a rule view."""

    model = RegexRule
    fields = ['name', 'description', 'sensitivity']

    def get_form(self, form_class=None):
        """Get the form for the view.
        All form fields will have the css class 'form-control' added.
        """
        if form_class is None:
            form_class = self.get_form_class()

        form = super().get_form(form_class)
        # Then a dynamic form to create multiple pattern fields
        # See - https://www.caktusgroup.com/blog/2018/05/07/creating-dynamic-forms-django/ (Creating a dynamic form)
        self.patterns = extract_pattern_fields(form.data)

        form.fields["pattern_0"] = forms.CharField(required=True, initial='_M463N74_DOCPR')
        form.fields["pattern_1"] = forms.CharField(required=False, initial='_M463N74_DOCPRMOD11')
        form.fields["pattern_2"] = forms.CharField(required=False, initial='_M463N74_DOCPRDOB')

        for field_name, value in self.patterns:
            form.fields[field_name] = forms.CharField(required=False, initial=value,
                                                      label='Udtryk')

        return form

    def form_valid(self, form):
        """
        validate all the form first
        :param form:
        :return:
        """
        form_cleaned_data = form.cleaned_data
        buffer = [form.cleaned_data[field_name] for field_name in form.cleaned_data if
                         field_name.startswith('pattern_')]
        form_patterns = set(buffer)

        try:
            with transaction.atomic():
                regexrule = form.save(commit=False)
                regexrule.name = form_cleaned_data['name']
                regexrule.sensitivity = form_cleaned_data['sensitivity']
                regexrule.description = form_cleaned_data['description']
                regexrule.organization = form_cleaned_data['organization']
                regexrule.save()

                for pattern in form_patterns:
                    r_ = RegexPattern.objects.create(regex=regexrule, pattern_string=pattern)
                    r_.save()

                return super().form_valid(form)
        except:
            return super().form_invalid(form)

    def get_pattern_fields(self):
        """
        Used in the template to get the field names and their values
        :return:
        """

        form_fields = self.get_form().fields
        for field_name in form_fields:
            if field_name.startswith('pattern_'):
                yield (field_name, form_fields.get(field_name).initial)

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/rules/%s/created/' % self.object.pk

    def get_cpr_settings(self):
        cpr_scan_settings = {
            'do_cpr_scan': False,
            'check_mod11': False,
            'ignore_irrelevant': False
        }

        return cpr_scan_settings


class RuleUpdate(RestrictedUpdateView):
    """Update a rule view."""

    model = RegexRule
    fields = ['name', 'description', 'sensitivity']

    def get_form(self, form_class=None):
        """Get the form for the view.

        All form fields will have the css class 'form-control' added.
        """
        if form_class is None:
            form_class = self.get_form_class()

        form = super().get_form(form_class)
        regex_patterns = self.object.patterns.all().order_by('-id')

        form.fields["pattern_0"] = forms.CharField(required=True, initial='_M463N74_DOCPR')
        form.fields["pattern_1"] = forms.CharField(required=False, initial='_M463N74_DOCPRMOD11')
        form.fields["pattern_2"] = forms.CharField(required=False, initial='_M463N74_DOCPRDOB')

        if not form.data:
            # create extra fields to hold the pattern strings
            for i in range(3, len(regex_patterns) + 3):
                field_name = 'pattern_%s' % (i,)
                form.fields[field_name] = forms.CharField(required=False,
                                                          initial=regex_patterns[i - 3].pattern_string, label='Udtryk')
        else:
            self.patterns = extract_pattern_fields(form.data)
            for field_name, value in self.patterns:
                form.fields[field_name] = forms.CharField(required=False, initial=value,
                                                          label='Udtryk')

        # assign class attribute to all fields
        for fname in form.fields:
            f = form.fields[fname]
            f.widget.attrs['class'] = 'form-control'

        return form

    def form_valid(self, form):
        """
        validate all the form first
        :param form:
        :return:
        """
        form_cleaned_data = form.cleaned_data
        form_patterns = [form.cleaned_data[field_name] for field_name in form.cleaned_data if
                         field_name.startswith('pattern_')]

        try:
            with transaction.atomic():
                self.object.patterns.all().delete()
                regexrule = form.save(commit=False)
                regexrule.name = form_cleaned_data['name']
                regexrule.sensitivity = form_cleaned_data['sensitivity']
                regexrule.description = form_cleaned_data['description']
                regexrule.organization = form_cleaned_data['organization']
                regexrule.save()

                for pattern in form_patterns:
                    r_ = RegexPattern.objects.create(regex=regexrule, pattern_string=pattern)
                    r_.save()

                return super().form_valid(form)
        except:
            return super().form_invalid(form)

    def get_pattern_fields(self):
        """
        Used in the template to get the field names and their values
        :return:
        """

        form_fields = self.get_form().fields

        for field_name in form_fields:
            if field_name.startswith('pattern_'):
                yield (field_name, form_fields.get(field_name).initial)

    def get_success_url(self):
        """The URL to redirect to after successful update."""
        return '/rules/%s/created/' % self.object.pk

    def get_cpr_settings(self):
        cpr_scan_settings = {
            'do_cpr_scan': False,
            'check_mod11': False,
            'ignore_irrelevant': False
        }

        regex_patterns = self.object.patterns.all().order_by('-id')

        form_fields = self.get_form().fields
        for field_name in form_fields:
            if field_name.startswith('pattern_'):
                if regex_patterns.get(pattern_string = _docpr()):
                    cpr_scan_settings['do_cpr_scan'] = True

                if regex_patterns.get(pattern_string = _docprmod11()):
                    cpr_scan_settings['check_mod11'] = True

                if regex_patterns.get(pattern_string = _docprdob()):
                    cpr_scan_settings['ignore_irrelevant'] = True

        ipdb.set_trace()

        return cpr_scan_settings


class RuleDelete(RestrictedDeleteView):
    """Delete a rule view."""

    model = RegexRule
    success_url = '/rules/'


'''============ Methods required by multiple views ============'''


def extract_pattern_fields(form_fields):
    if not form_fields:
        return [('pattern_3', '')] # start from 3 because 0-2 are the unique keys for CPR settings

    return [(field_name, form_fields[field_name]) for field_name in form_fields if
            field_name.startswith('pattern_')]


def _docpr():
    return "_M463N74_DOCPR"


def _docprmod11():
    return "_M463N74_DOCPRMOD11"


def _docprdob():
    return "_M463N74_DOCPRDOB"
