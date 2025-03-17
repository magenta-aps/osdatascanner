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
        # Excluding expiry date as it seems service accounts don't really expire
        # automatically but datascanner wants the field
        exclude = ("expiry_date", )

# Might be jank to have html in the help text but I think its better than
# creating checks in the template to achieve the same
    _service_account = AutoEncryptedFileField(
        required=False, label=_("Service Account JSON File"), help_text=_(
            "To create a service account follow the segments"
            " about service accounts"
            " <a href='https://developers.google.com/workspace/guides/create-credentials'>"
            " in this guide</a>."
            " Make sure to grant it domain wide delegation"
            " if you want to scan more than one account."
            " You can either copy the contents of your service account file"
            " Into this box or upload the file using the 'upload' button."))

    # improve drag and drop
    # improve feedback
    # widget for last updated so user knows stuff happens

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["organization"].disabled = True


class GoogleApiScannerForm(GoogleApiGrantForm):
    """ Form for use in Scanner Create/Update. """
    class Meta:
        model = GoogleApiGrant
        exclude = ('expiry_date',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["organization"].disabled = False
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["last_modified"] = self.object.last_modified
        return context
