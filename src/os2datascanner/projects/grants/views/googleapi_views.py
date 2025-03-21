from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, CreateView
from django import forms
from ..models.googleapigrant import GoogleApiGrant
from ..admin import AutoEncryptedFileField


class GoogleApiGrantForm(forms.ModelForm):
    class Meta:
        model = GoogleApiGrant
        fields = ["organization", "_service_account"]
        readonly_fields = ("last_updated",)

    _service_account = AutoEncryptedFileField(
        required=True, label=_("Service Account JSON File"), help_text=_(
            "To create a service account follow the segments"
            " about service accounts"
            " <a href='https://developers.google.com/workspace/guides/create-credentials'>"
            " in this guide</a>."
            " Make sure to grant it domain wide delegation."),
    )

    last_updated = forms.CharField(max_length=255, required=False, label=_("Last Updated"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["organization"].disabled = True
        self.fields["last_updated"].disabled = True
        if self.instance.last_updated:
            self.fields["last_updated"].initial = self.instance.last_updated.strftime(
                "%d/%m-%Y %H:%M")
        else:
            self.fields["last_updated"].widget = forms.HiddenInput()
            self.fields["last_updated"].label = ""


class GoogleApiScannerForm(GoogleApiGrantForm):
    """ Form for use in Scanner Create/Update. """
    class Meta:
        model = GoogleApiGrant
        fields = ["organization", "_service_account"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["organization"].disabled = False
        self.fields["_service_account"].disabled = False
        self.fields["_service_account"].initial = ""


class GoogleApiGrantCreateView(LoginRequiredMixin, CreateView):
    model = GoogleApiGrant
    form_class = GoogleApiGrantForm
    template_name = "grants/googleapigrant_update.html"
    success_url = reverse_lazy('grant-list')

    def get_initial(self):
        return {
            "organization": self.kwargs.get('org'),
        }


class GoogleApiGrantUpdateView(LoginRequiredMixin, UpdateView):
    model = GoogleApiGrant
    form_class = GoogleApiGrantForm
    template_name = "grants/googleapigrant_update.html"
    success_url = reverse_lazy('grant-list')
