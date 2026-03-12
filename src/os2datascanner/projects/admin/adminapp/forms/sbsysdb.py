# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.utils.translation import gettext_lazy as _

from ..models.scannerjobs.sbsysdb import SBSYSDBScanner
from .shared import Groups, ScannerForm, ScanScopeMixin


class SBSYSDBScannerForm(ScanScopeMixin, ScannerForm):

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
            [
                "db_server",
                "db_port",
                "db_name",
                "grant",
                (
                    _("Advanced SBSYS scan settings"),
                    ["weblink"]
                ),
            ]
        ),
        (
            _("Scan settings"),
            [
                "do_last_modified_check",
                "do_ocr",
                "rule",
                "max_pdf_size",
                Groups.SCOPE_SETTINGS,
            ]
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
