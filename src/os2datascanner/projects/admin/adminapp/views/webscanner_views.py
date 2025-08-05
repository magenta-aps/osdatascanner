# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2datascanner is developed by Magenta in collaboration with the OS2 public
# sector open source network <https://os2.eu/>.
#
from .scanner_views import (
    ScannerBase,
    ScannerCopy,
    ScannerList,
    ScannerCreateDf,
    ScannerUpdateDf)
from ..forms.webscanner import WebScannerForm
from ..models.scannerjobs.webscanner import WebScanner


class WebScannerList(ScannerList):
    """Displays list of web scanners."""

    model = WebScanner
    type = 'web'


web_scanner_fields = [
    'url',
    'download_sitemap',
    'sitemap_url',
    'sitemap',
    'do_link_check',
    'exclude_urls',
    'reduce_communication',
    'always_crawl',
]


class WebScannerCreate(ScannerCreateDf):
    model = WebScanner
    form_class = WebScannerForm


class WebScannerCopy(ScannerCopy):
    """Create a new copy of an existing WebScanner"""

    model = WebScanner
    type = 'web'
    fields = ScannerBase.fields + web_scanner_fields


class WebScannerUpdate(ScannerUpdateDf):
    model = WebScanner
    form_class = WebScannerForm
