from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView

from ..admin import EWSGrantAdminForm
from ..models.ewsgrant import EWSGrant


class EWSGrantForm(EWSGrantAdminForm):
    """ Form for user interaction purposes.
        Disables the Organization field. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["organization"].disabled = True


class EWSGrantCreateView(LoginRequiredMixin, CreateView):
    model = EWSGrant
    form_class = EWSGrantForm
    template_name = "grants/ewsgrant_update.html"
    success_url = reverse_lazy("grant-list")

    def get_initial(self):
        return {"organization": self.kwargs.get('org')}


class EWSGrantUpdateView(LoginRequiredMixin, UpdateView):
    model = EWSGrant
    form_class = EWSGrantForm
    template_name = "grants/ewsgrant_update.html"
    success_url = reverse_lazy("grant-list")
