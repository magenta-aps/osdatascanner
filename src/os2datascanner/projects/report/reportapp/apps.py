# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.apps import AppConfig


class ReportappConfig(AppConfig):
    name = "os2datascanner.projects.report.reportapp"
    label = 'os2datascanner_report'
    verbose_name = "OS2datascanner - Report"
