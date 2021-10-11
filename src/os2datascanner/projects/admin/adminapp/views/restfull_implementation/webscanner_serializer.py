from os2datascanner.projects.admin.adminapp.models.scannerjobs.webscanner_model import (
    WebScanner,
)
from os2datascanner.projects.admin.adminapp.views.restfull_implementation.scanner_serializer import (
    ScannerSerializer,
)


class WebscannerSerializer(ScannerSerializer):
    """This Class serializes the data and can act as a form"""

    class Meta:
        model = WebScanner
        type = "web"
        fields = "__all__"
