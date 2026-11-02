# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from uuid import UUID
import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.decorators.http import require_GET, require_POST

from os2datascanner.utils.system_utilities import time_now
from ..utilities import UserWrapper
from .models.background_job import BackgroundJob, JobState

# Paths from BackgroundJob to the Organization of each subclass that has one.
# Jobs of other subclasses are only visible to users with access to all
# organizations.
JOB_ORGANIZATION_PATHS = (
    "ldapimportjob__realm__organization",
    "msgraphimportjob__organization",
    "os2moimportjob__organization",
    "googleworkspaceimportjob__organization",
    "analysisjob__scanner__organization",
)


def get_user_job_or_404(user, pk: UUID) -> BackgroundJob:
    """Returns the BackgroundJob with the given primary key if it belongs to
    an organization the user may administer, and raises Http404 otherwise."""
    wrapper = UserWrapper(user)
    org_q = Q()
    for path in JOB_ORGANIZATION_PATHS:
        org_q |= wrapper.make_org_Q(path)
    return get_object_or_404(BackgroundJob.objects.filter(org_q), pk=pk)


def _render_job(request, job: BackgroundJob):
    response = TemplateResponse(
            request,
            "components/background_job.html",
            context={"job": job})

    just_finished = job.exec_state == JobState.FINISHED and \
        time_now() - job.changed_at < datetime.timedelta(seconds=1)

    if just_finished:
        response.headers["HX-Trigger"] = "reload-htmx"

    return response


@require_GET
@login_required
def render_background_job_status_widget(request, pk: UUID):
    return _render_job(request, get_user_job_or_404(request.user, pk))


@require_POST
@login_required
def cancel_background_job(request, pk: UUID):
    job = get_user_job_or_404(request.user, pk)
    job.cancel()
    return _render_job(request, job)
