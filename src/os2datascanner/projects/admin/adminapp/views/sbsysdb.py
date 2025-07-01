from django.views.generic import CreateView, UpdateView

from ..forms.sbsysdb import SBSYSDBScannerForm
from ..models.scannerjobs.sbsysdb import SBSYSDBScanner
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


class SBSYSDBScannerUpdateDF(_Form_Mixin, UpdateView):
    scanner_view_type = ScannerViewType.UPDATE


class SBSYSDBScannerCopyDF(_Form_Mixin, CreateView):
    scanner_view_type = ScannerViewType.COPY

    def get_initial(self):
        return super().get_initial()
