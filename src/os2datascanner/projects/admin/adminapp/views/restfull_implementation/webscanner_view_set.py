from os2datascanner.projects.admin.adminapp.models.scannerjobs.webscanner_model import (
    WebScanner,
)
from os2datascanner.projects.admin.adminapp.views.restfull_implementation.forms import (
    WebScannerForm,
)
from os2datascanner.projects.admin.adminapp.views.restfull_implementation.scanner_view_set import (
    ScannerViewSet,
)
from os2datascanner.projects.admin.adminapp.views.restfull_implementation.webscanner_serializer import (
    WebscannerSerializer,
)


class WebscannerViewSet(ScannerViewSet):
    """
    A simple ViewSet for listing or retrieving webscanners.
    """

    model = WebScanner
    form_class = WebScannerForm
    serializer = WebscannerSerializer
    template_name = "os2datascanner/scanner_form.html"
    list_template_name = "os2datascanner/scanners.html"
    type = "web"
