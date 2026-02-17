# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreOrganizationalStructureConfig(AppConfig):
    name = 'os2datascanner.core_organizational_structure'
    label = 'core_organizational_structure'
    verbose_name = _('core_organizational_structure')
    default = True
