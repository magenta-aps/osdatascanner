# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import django


if django.VERSION >= (3, 2):
    pass
else:
    default_app_config = 'organizations.apps.OrganizationsConfig'
