from uuid import UUID
import datetime

from django.http import Http404
from django.template.response import SimpleTemplateResponse

from os2datascanner.utils.system_utilities import time_now
from .models.background_job import BackgroundJob, JobState


def render_background_job_status_widget(_, pk: UUID):

    try:
        job = BackgroundJob.objects.get(pk=pk)
        context = {
            "job": job
        }

        response = SimpleTemplateResponse(
                "components/background_job.html",
                context=context)

        just_finished = job.exec_state == JobState.FINISHED and \
            time_now() - job.changed_at < datetime.timedelta(seconds=1)

        if just_finished:
            response.headers["HX-Trigger"] = "reload-htmx"

        return response
    except BackgroundJob.DoesNotExist:
        raise Http404


def cancel_background_job(_, pk: UUID):
    try:
        job = BackgroundJob.objects.get(pk=pk)
        job.cancel()
        return render_background_job_status_widget(_, pk)
    except BackgroundJob.DoesNotExist:
        raise Http404
