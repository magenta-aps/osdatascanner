from uuid import UUID

from django.http import Http404
from django.template.response import SimpleTemplateResponse

from .models.background_job import BackgroundJob


def render_background_job_status_widget(pargh, pk: UUID):
    try:
        context = {
            "job": BackgroundJob.objects.get(pk=pk)
        }
        return SimpleTemplateResponse(
                "components/background_job.html",
                context=context)
    except BackgroundJob.DoesNotExist:
        raise Http404
