# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


class CoreConfig(AppConfig):
    name = 'os2datascanner.projects.admin.core'
    label = 'core'
    verbose_name = pgettext_lazy('Verbose name for core app', 'Management')
    default = True
