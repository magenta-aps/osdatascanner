from django.utils.translation import gettext_lazy as _

from ..models.scannerjobs.sbsysdb import SBSYSDBScanner
from .shared import Groups, ScannerForm


class SBSYSDBScannerForm(ScannerForm):

    placeholders = {
        "weblink": _("e.g. https://sbsip.vstkom.internal/a-sag/"),
        "db_server": _("e.g. sbsys.vstkom.internal"),
    }

    patterns = {
        "weblink": "(http|https)://.*"
    }

    groups = (
        Groups.GENERAL_SETTINGS,
        (
            _("SBSYS database connection settings"),
            ["db_server", "db_port", "db_name", "grant"]
        ),
        (
            _("Advanced SBSYS scan settings"),
            ["weblink"]
        ),
        Groups.SCOPE_SETTINGS,
        (
            _("Scan settings"),
            ["do_last_modified_check", "do_ocr", "rule", "exclusion_rule"]
        ),
        Groups.ADVANCED_RESULT_SETTINGS,
        Groups.SCHEDULED_EXECUTION_SETTINGS,
    )

    class Meta:
        model = SBSYSDBScanner
        exclude = ("pk", "dtstart", "validation_method",)
        widgets = {
            # "name": widgets.PasswordInput(),
        }
