from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView
from ..admin import SMBGrantAdminForm
from ..models.smbgrant import SMBGrant


class SMBGrantForm(SMBGrantAdminForm):
    """ Form for user interaction purposes.
        Disables the Organization field. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["organization"].disabled = True


class SMBGrantCreateView(LoginRequiredMixin, CreateView):
    model = SMBGrant
    form_class = SMBGrantForm
    template_name = "grants/smbgrant_update.html"
    success_url = reverse_lazy("grant-list")

    def get_initial(self):
        return {"organization": self.kwargs.get('org')}


class SMBGrantUpdateView(LoginRequiredMixin, UpdateView):
    model = SMBGrant
    form_class = SMBGrantForm
    template_name = "grants/smbgrant_update.html"
    success_url = reverse_lazy("grant-list")
