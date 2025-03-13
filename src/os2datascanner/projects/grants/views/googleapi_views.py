from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, CreateView
from django import forms
from os2datascanner.projects.grants.admin import AutoEncryptedField
from ..models.googleapigrant import GoogleApiGrant


class GoogleApiGrantForm(forms.ModelForm):
    class Meta:
        model = GoogleApiGrant
        # Excluding expiry date as it seems service accounts don't really expire
        # automatically but datascanner wants the field
        exclude = ("expiry_date",)

# Might be jank to have html in the help text but I think its better than
# creating checks in the template to achieve the same
    _service_account = AutoEncryptedField(
        required=False, label=_("Service Account JSON"), help_text=_(
            "To create a service account follow the segments"
            " about service accounts"
            " <a href='https://developers.google.com/workspace/guides/create-credentials'>"
            " in this guide</a>."
            " Make sure to grant it domain wide delegation"
            " if you want to scan more than one account."))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["organization"].disabled = True


class GoogleApiScannerForm(GoogleApiGrantForm):
    """ Form for use in Scanner Create/Update. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["account_name"].disabled = False
        self.fields["_service_account"].disabled = False
        self.fields["account_name"].initial = ""
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
