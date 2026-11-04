# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.utils.translation import gettext_lazy as _

from ..models.scannerjobs.filescanner import FileScanner
from .shared import Excludes, Groups, GrantSelectWidget, ScannerForm


class FileScannerForm(ScannerForm):

    placeholders = {
        "unc": _("e.g. //network-domain/top-folder"),
        "alias": _("e.g. P"),
    }

    groups = (
        Groups.GENERAL_SETTINGS,
        (
            _("File scanner settings"),
            [
                "unc",
                "alias",
                "smb_grant",
                (
                    _("Advanced file scanner settings"),
                    ["skip_super_hidden", "unc_is_home_root"]
                ),
            ]
        ),
        (
            _("Scan settings"),
            [
                "rule",
                "do_last_modified_check",
                Groups.FILE_SETTINGS,
            ]
        ),
        Groups.ADVANCED_RESULT_SETTINGS,
        Groups.SCHEDULED_EXECUTION_SETTINGS,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The model field allows null but not blank, so a ModelForm would make it required:
        self.fields["alias"].required = False

    class Meta:
        model = FileScanner
        exclude = Excludes.BASE + Excludes.ORG_UNITS
        widgets = {
            "smb_grant": GrantSelectWidget,
        }
