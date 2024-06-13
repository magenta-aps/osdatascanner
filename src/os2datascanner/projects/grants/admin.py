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
        if value:
            self.widget.attrs["placeholder"] = _("(unchanged)")
        else:
            pass

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


class EWSGrantForm(forms.ModelForm):
    model = EWSGrant

    username = forms.CharField()  # Better than the default AdminTextField
    _password = AutoEncryptedField(required=False)

    def clean__password(self):
        return choose_field_value(
              self.cleaned_data["_password"],
              self.instance._password)


@admin.register(EWSGrant)
class EWSGrantAdmin(admin.ModelAdmin):
    fields = ["organization", "username", "_password"]
    form = EWSGrantForm


class SMBGrantForm(forms.ModelForm):
    model = SMBGrant

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
    form = SMBGrantForm


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
