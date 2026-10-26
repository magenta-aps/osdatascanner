# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from ..forms.sbsysdb import SBSYSDBScannerForm
from ..models.scannerjobs.sbsysdb import SBSYSDBScanner
from .scanner_views import (
        ScannerList, ScannerCleanupStaleAccounts, ScannerCreateDf, ScannerUpdateDf,
        ScannerCopyDf)


class SBSYSDBScannerList(ScannerList):
    """Displays list of SBSYS scanners."""

    model = SBSYSDBScanner
    type = 'sbsys-db'


class SBSYSDBScannerCreateDF(ScannerCreateDf):
    model = SBSYSDBScanner
    form_class = SBSYSDBScannerForm


class SBSYSDBScannerUpdateDF(ScannerUpdateDf):
    model = SBSYSDBScanner
    form_class = SBSYSDBScannerForm


class SBSYSDBScannerCopyDF(ScannerCopyDf):
    model = SBSYSDBScanner
    form_class = SBSYSDBScannerForm


class SBSYSDBScannerCleanup(ScannerCleanupStaleAccounts):
    model = SBSYSDBScanner
    type = "sbsys-db"
