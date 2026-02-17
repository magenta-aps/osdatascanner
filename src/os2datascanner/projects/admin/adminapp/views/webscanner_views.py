# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from .scanner_views import (
    ScannerList,
    ScannerCreateDf,
    ScannerUpdateDf,
    ScannerCopyDf)
from ..forms.webscanner import WebScannerForm
from ..models.scannerjobs.webscanner import WebScanner


class WebScannerList(ScannerList):
    """Displays list of web scanners."""

    model = WebScanner
    type = 'web'


class WebScannerCreate(ScannerCreateDf):
    model = WebScanner
    form_class = WebScannerForm


class WebScannerCopy(ScannerCopyDf):
    """Create a new copy of an existing WebScanner"""
    model = WebScanner
    form_class = WebScannerForm


class WebScannerUpdate(ScannerUpdateDf):
    model = WebScanner
    form_class = WebScannerForm
