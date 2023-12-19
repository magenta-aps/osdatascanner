from django import forms
# from django.utils.translation import gettext_lazy as _

from .models.scannerjobs.scanner import Scanner


class BaseScannerForm(forms.ModelForm):
    class Meta:
        model = Scanner
        fields = '__all__'
        localized_fields = '__all__'
