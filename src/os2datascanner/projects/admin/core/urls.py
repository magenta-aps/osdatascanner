# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.urls import path

from . import views

urlpatterns = [
    path(
            "background_job/<uuid:pk>/status",
            views.render_background_job_status_widget,
            name="background_job_status_widget"),
    path(
            "background_job/<uuid:pk>/cancel",
            views.cancel_background_job,
            name="background_job_cancel"),
]
