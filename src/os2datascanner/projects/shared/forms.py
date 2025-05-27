from django import forms
from django.utils.translation import gettext_lazy as _


class GroupingModelForm(forms.ModelForm):
    template_name = "components/forms/grouping_model_form.html"

    # A tuple of (group title, [field...]) tuples
    # (note that these fields must also be specified explicitly or implicitly
    # through Meta.fields/exclude)
    groups = ()

    # A dictionary of (field name, placeholder text) values to populate the
    # <input ... placeholder="" /> attribute
    placeholders = {}

    # A dictionary of (field name, regular expression pattern) values to
    # populate the <input ... pattern="" /> attribute
    patterns = {}

    def patch_field(self, name: str, field: forms.Field):
        if placeholder := self.placeholders.get(name):
            field.widget.attrs |= {
                "placeholder": placeholder
            }
        if pattern := self.patterns.get(name):
            field.widget.attrs |= {
                "pattern": pattern
            }

    def get_context(self):
        # Slightly hacked-up version of the original to support grouping and to
        # allow widget attributes to be patched
        fields = []
        hidden_fields = []
        top_errors = self.non_field_errors().copy()
        for name, bf in self._bound_items():
            self.patch_field(name, bf.field)
            bf_errors = self.error_class(bf.errors, renderer=self.renderer)
            if bf.is_hidden:
                if bf_errors:
                    top_errors += [
                        _("(Hidden field %(name)s) %(error)s")
                        % {"name": name, "error": str(e)}
                        for e in bf_errors
                    ]
                hidden_fields.append(bf)
            else:
                errors_str = str(bf_errors)
                fields.append((name, bf, errors_str))

        field_dict = {name: [bf, errors] for name, bf, errors in fields}

        return {
            "form": self,
            "fields": fields,
            "groups": [(title, [field_dict[n] for n in field_names])
                       for title, field_names in self.groups],
            "hidden_fields": hidden_fields,
            "errors": top_errors,
        }
