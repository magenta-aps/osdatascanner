#!/usr/bin/env python
# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import structlog

from urllib.parse import urlencode
from django.conf import settings


logger = structlog.get_logger("reportapp")


def oidc_op_logout_url_method(request):
    logout_url = settings.LOGOUT_URL
    return_to_url = settings.LOGOUT_REDIRECT_URL
    return logout_url + '?' + urlencode({'redirect_uri': return_to_url,
                                         'client_id': settings.OIDC_RP_CLIENT_ID})
