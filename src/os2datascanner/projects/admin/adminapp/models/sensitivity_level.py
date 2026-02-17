# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.utils.translation import gettext_lazy as _


class Sensitivity:

    """Name space for sensitivity values."""

    def __init__(self):
        pass

    CRITICAL = 3
    HIGH = 2
    LOW = 1
    OK = 0

    choices = (
        (CRITICAL, _('Critical')),
        (HIGH, _('Problem')),
        (LOW, _('Warning')),
        (OK, _('Notification')),
    )
