# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.apps import AppConfig


class OSdatascannerSharedConfig(AppConfig):
    # the name needs to be changed as soon as the directive is renamed to "osdatascanner"
    name = "os2datascanner.projects.shared"
    label = 'osdatascanner_shared'
    verbose_name = "OSdatascanner shared UI resources"
    default = True
