#!/usr/bin/env python3
# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import ipaddress


def get_client_ip(request):
    """Get the clients IP address"""

    # XXX: curl -H "X-Forwarded-For: 1.2.3.4" localhost:8020 will give the IP 1.2.3.4
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def debug_toolbar_callback(request):
    """Enable the debug toolbar if the host-ip is private"""

    # https://docs.djangoproject.com/en/3.2/ref/request-response/
    ip = ipaddress.ip_address(get_client_ip(request))
    return ip.is_private
