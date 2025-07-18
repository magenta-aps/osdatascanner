from typing import Sequence
from django import forms


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
                hidden_fields.append(bf)
            else:
                fields.append((name, bf, str(bf_errors)))

        field_dict = {name: (bf, errors) for name, bf, errors in fields}

        # Recursive builder:
        def build_items(spec):
            out = []
            for entry in spec:
                # treat any 2-tuple or 2-list [title, sub_spec] as subgroup
                if (
                    isinstance(entry, (list, tuple))
                    and len(entry) == 2
                    and isinstance(entry[1], Sequence)
                    and not isinstance(entry[0], (list, tuple))
                ):
                    title, sub_spec = entry
                    out.append({
                        "type": "group",
                        "title": title,
                        "items": build_items(sub_spec),
                    })
                else:
                    # must be a field name
                    bf, errors = field_dict[entry]
                    out.append({
                        "type": "field",
                        "bf": bf,
                        "errors": errors,
                    })
            return out

        # Build the top level:
        groups_ctx = []
        for title, spec in self.groups:
            groups_ctx.append({
                "title": title,
                "items": build_items(spec),
            })

        return {
            "form": self,
            "groups": groups_ctx,
            "hidden_fields": hidden_fields,
            "errors": top_errors,
        }
