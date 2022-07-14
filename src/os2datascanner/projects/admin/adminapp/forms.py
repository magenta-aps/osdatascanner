from django import forms
from .models.rules.customrule_model import CustomRule


class CustomRuleAdminForm(forms.ModelForm):
    class Meta:
        model = CustomRule
        fields = [
            'name',
            'organization',
            'description',
            'sensitivity',
            '_rule'
            ]

        widgets = {
            '_rule': forms.TextInput()
            }
