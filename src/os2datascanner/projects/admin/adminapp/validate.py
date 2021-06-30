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
"""Domain validation functions."""

import hashlib
import re
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from .models.scannerjobs.webscanner_model import WebScanner


def _do_request(url):
    """Make a request and return the data."""
    try:
        request = Request(url, headers={"User-Agent": "OS2Webscanner"})
        r = urlopen(request)
        # TODO: We get decoding error when using utf-8. But it should be utf-8 decoded.
        return r.read().decode('latin1')
    except URLError:
        return None


def _get_validation_hash(domain):
    """Return the validation hash for the domain.

    The validation hash is based on the domain's organization's primary key.
    """
    return hashlib.md5(str(domain.organization.pk).encode('utf-8')).hexdigest()


def get_validation_str(domain, method=None):
    """Return the validation string for the domain.

    The validation string is what must be inserted by the user into a
    specific file in the root of the domain. The validation string returned is
    dependent on the domain's validation method and the domain's
    organization.
    """
    hash_str = _get_validation_hash(domain)
    if method is None:
        method = domain.validation_method
    if method == WebScanner.ROBOTSTXT:
        return "User-agent: " + hash_str + "\nDisallow:"
    elif method == WebScanner.WEBSCANFILE:
        return hash_str
    elif method == WebScanner.METAFIELD:
        return '<meta name="os2webscanner" content="' + hash_str + '" />'


def validate_domain(domain):
    """Validate a Domain by using the Domain's validation method.

    Returns True if it validated or False if it did not.
    """
    hash_str = _get_validation_hash(domain)

    validators = {
        WebScanner.ROBOTSTXT: {
            "url": "/robots.txt",
            "regex": "User-agent: " + hash_str + "(\r\n|\r|\n)Disallow:"
        },
        WebScanner.WEBSCANFILE: {
            "url": "/webscan.html",
            "regex": hash_str
        },
        WebScanner.METAFIELD: {
            "url": "/",
            "regex": '<meta name="os2webscanner" content="' + hash_str + '"'
        }
    }
    validator = validators[domain.validation_method]
    url = urljoin(domain.root_url, validator["url"])
    r = _do_request(url)
    if r is None:
        return False
    match = re.search(validator["regex"], r, re.I)
    return match is not None
