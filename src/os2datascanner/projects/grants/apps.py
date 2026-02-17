# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GrantsConfig(AppConfig):
    name = 'os2datascanner.projects.grants'
    label = 'grants'
    verbose_name = _('grants')
    default = True
