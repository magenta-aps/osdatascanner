from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView

from os2datascanner.projects.grants.admin import EWSGrantAdminForm
from os2datascanner.projects.grants.models.ewsgrant import EWSGrant


class EWSGrantForm(EWSGrantAdminForm):
    """ Form for user interaction purposes.
        Disables the Organization field. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["organization"].disabled = True


class EWSGrantScannerForm(EWSGrantAdminForm):
    """ Form for use in Scanner Create/Update. """
    class Meta:
        model = EWSGrant
        fields = ('__all__')


class EWSGrantCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = EWSGrant
    form_class = EWSGrantForm
    permission_required = "grants.add_ewsgrant"
    template_name = "grants/ewsgrant_update.html"
    success_url = reverse_lazy("grant-list")

    def get_initial(self):
        return {"organization": self.kwargs.get('org')}


class EWSGrantUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = EWSGrant
    form_class = EWSGrantForm
    permission_required = "grants.change_ewsgrant"
    template_name = "grants/ewsgrant_update.html"
    success_url = reverse_lazy("grant-list")
