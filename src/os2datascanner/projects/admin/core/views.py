from uuid import UUID

from django.http import Http404
from django.template.response import SimpleTemplateResponse

from .models.background_job import BackgroundJob


def render_background_job_status_widget(_, pk: UUID):
    try:
        context = {
            "job": BackgroundJob.objects.get(pk=pk)
        }
        return SimpleTemplateResponse(
                "components/background_job.html",
                context=context)
    except BackgroundJob.DoesNotExist:
        raise Http404


def cancel_background_job(_, pk: UUID):
    try:
        job = BackgroundJob.objects.get(pk=pk)
        job.cancel()
        return render_background_job_status_widget(_, pk)
    except BackgroundJob.DoesNotExist:
        raise Http404
