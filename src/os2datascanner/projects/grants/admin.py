from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from os2datascanner.projects.utils import aes
from .models import EWSGrant, SMBGrant, GraphGrant


class AutoEncryptedField(forms.CharField):
    widget = forms.widgets.PasswordInput

    def prepare_value(self, value):
        # If it's a list, we have an actual saved instance.
        # Otherwise, we're in a Create scenario, where if non-field-errors occur, the user
        # input value would be thrown away, but visually be "unchanged".
        if value and isinstance(value, list):
            self.widget.attrs["placeholder"] = _("(unchanged)")
        elif value:
            self.widget.attrs["value"] = value

    def to_python(self, value):
        if value:
            return [c.hex()
                    for c in aes.encrypt(value, settings.DECRYPTION_HEX)]


def choose_field_value(new, old):
    match new, old:
        case new, _ if new:
            return new
        case None, old if old:
            return old
        case None, None:
            raise ValidationError(_("This field is required."))


class EWSGrantAdminForm(forms.ModelForm):
    class Meta:
        model = EWSGrant
        exclude = ("__all__")

    username = forms.CharField()  # Better than the default AdminTextField
    _password = AutoEncryptedField(required=False)

    def clean__password(self):
        return choose_field_value(
              self.cleaned_data["_password"],
              self.instance._password)


@admin.register(EWSGrant)
class EWSGrantAdmin(admin.ModelAdmin):
    fields = ["organization", "username", "_password"]
    form = EWSGrantAdminForm


class SMBGrantAdminForm(forms.ModelForm):
    class Meta:
        model = SMBGrant
        exclude = ("__all__")

    username = forms.CharField()
    domain = forms.CharField(required=False)
    _password = AutoEncryptedField(required=False)

    def clean__password(self):
        return choose_field_value(
              self.cleaned_data["_password"],
              self.instance._password)


@admin.register(SMBGrant)
class SMBGrantAdmin(admin.ModelAdmin):
    fields = ["organization", "domain", "username", "_password"]
    form = SMBGrantAdminForm


class GraphGrantForm(forms.ModelForm):
    model = GraphGrant

    _client_secret = AutoEncryptedField(required=False)

    def clean__client_secret(self):
        return choose_field_value(
              self.cleaned_data["_client_secret"],
              self.instance._client_secret)


@admin.register(GraphGrant)
class GraphGrantAdmin(admin.ModelAdmin):
    fields = ["organization", "app_id", "tenant_id", "_client_secret"]
    form = GraphGrantForm

    def get_changeform_initial_data(self, request):
        # Suppress the random UUID values GraphGrants have by default
        return {
            "app_id": "",
            "tenant_id": ""
        }
