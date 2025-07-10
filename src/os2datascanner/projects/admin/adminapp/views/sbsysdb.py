from django.views.generic import CreateView, UpdateView
from django.utils.translation import gettext_lazy as _

from ..forms.sbsysdb import SBSYSDBScannerForm
from ..models.scannerjobs.sbsysdb import SBSYSDBScanner
from ..models.scannerjobs.scanner import Scanner
from ...organizations.models import Account, AliasType
from .utils.remediators import reconcile_remediators
from .scanner_views import ScannerList, ScannerViewType


class SBSYSDBScannerList(ScannerList):
    """Displays list of web scanners."""

    model = SBSYSDBScanner
    type = 'sbsys-db'


class _Form_Mixin:
    model = SBSYSDBScanner
    form_class = SBSYSDBScannerForm
    template_name = "components/forms/grouping_model_form_wrapper.html"


class SBSYSDBScannerCreateDF(_Form_Mixin, CreateView):
    scanner_view_type = ScannerViewType.CREATE

    def form_valid(self, form):
        rv = super().form_valid(form)
        reconcile_remediators(form.cleaned_data["remediators"], self.object)
        return rv


class SBSYSDBScannerUpdateDF(_Form_Mixin, UpdateView):
    scanner_view_type = ScannerViewType.UPDATE

    def get_initial(self):
        return self.initial | {
            "remediators": Account.objects.filter(
                    aliases___alias_type=AliasType.REMEDIATOR.value,
                    aliases___value=str(self.object.pk))
        }

    def form_valid(self, form):
        rv = super().form_valid(form)
        reconcile_remediators(form.cleaned_data["remediators"], self.object)
        return rv


class SBSYSDBScannerCopyDF(_Form_Mixin, CreateView):
    scanner_view_type = ScannerViewType.COPY

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())

    def get_initial(self):
        new_name = self.get_object().name
        while Scanner.objects.unfiltered().filter(name=new_name).exists():
            new_name += " " + _("Copy")

        return super().get_initial() | {
            "remediators": Account.objects.filter(
                    aliases___alias_type=AliasType.REMEDIATOR.value,
                    aliases___value=str(self.get_object().pk)),

            # Copied scannerjobs should be "Invalid" by default
            # to avoid being able to misuse this feature.
            "validation_status": Scanner.INVALID,
            "name": new_name
        }

    def form_valid(self, form):
        rv = super().form_valid(form)
        reconcile_remediators(form.cleaned_data["remediators"], self.object)
        return rv
