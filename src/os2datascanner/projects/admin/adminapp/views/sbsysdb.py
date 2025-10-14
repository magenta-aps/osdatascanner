from django.views.generic import CreateView, UpdateView
from django.utils.translation import gettext_lazy as _

from ..forms.sbsysdb import SBSYSDBScannerForm
from ..models.scannerjobs.sbsysdb import SBSYSDBScanner
from ..models.scannerjobs.scanner import Scanner
from ...organizations.models import Account, AliasType
from .scanner_views import (
        ScannerList, ScannerViewType, ScannerCleanupStaleAccounts, _FormMixin)


class SBSYSDBScannerList(ScannerList):
    """Displays list of web scanners."""

    model = SBSYSDBScanner
    type = 'sbsys-db'


class SBSYSDBScannerCreateDF(_FormMixin, CreateView):
    scanner_view_type = ScannerViewType.CREATE
    model = SBSYSDBScanner
    form_class = SBSYSDBScannerForm


class SBSYSDBScannerUpdateDF(_FormMixin, UpdateView):
    scanner_view_type = ScannerViewType.UPDATE
    model = SBSYSDBScanner
    form_class = SBSYSDBScannerForm
    edit = True  # compat

    def get_initial(self):
        return self.initial | {
            "remediators": Account.objects.filter(
                    aliases___alias_type=AliasType.REMEDIATOR.value,
                    aliases___value=str(self.object.pk))
        }


class SBSYSDBScannerCopyDF(_FormMixin, CreateView):
    scanner_view_type = ScannerViewType.COPY
    model = SBSYSDBScanner
    form_class = SBSYSDBScannerForm

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


class SBSYSDBScannerCleanup(ScannerCleanupStaleAccounts):
    model = SBSYSDBScanner
    type = "sbsys-db"
