from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
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


class SMBGrantCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = SMBGrant
    form_class = SMBGrantForm
    permission_required = "grants.add_smbgrant"
    template_name = "grants/smbgrant_update.html"
    success_url = reverse_lazy("grant-list")

    def get_initial(self):
        return {"organization": self.kwargs.get('org')}


class SMBGrantScannerForm(SMBGrantAdminForm):
    """ Form for use in Scanner Create/Update. """
    class Meta:
        model = SMBGrant
        fields = ('__all__')


class SMBGrantUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = SMBGrant
    form_class = SMBGrantForm
    permission_required = "grants.change_smbgrant"
    template_name = "grants/smbgrant_update.html"
    success_url = reverse_lazy("grant-list")
