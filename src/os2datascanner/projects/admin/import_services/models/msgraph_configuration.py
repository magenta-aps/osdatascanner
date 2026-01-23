from django.db import models

from os2datascanner.projects.grants.models import GraphGrant

from .import_service import ImportService
from .exported_mixin import Exported
from django.utils.translation import gettext_lazy as _
from os2datascanner.projects.admin.core.models.background_job import JobState


class MSGraphConfiguration(Exported, ImportService):
    grant = models.ForeignKey(GraphGrant, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _("MSGraph configuration")
        verbose_name_plural = _("MSGraph configurations")

    def start_import(self):
        from . import MSGraphImportJob
        from os2datascanner.projects.admin.import_services.utils import _start_import_job

        _start_import_job(
            importjob_model=MSGraphImportJob,
            lookup_filter={"grant": self.grant},
            job_kwargs={
                "grant": self.grant,
                "organization": self.organization,
            },
            allowed_states=(
                JobState.FINISHED,
                JobState.FAILED,
                JobState.CANCELLED,
            ),
            log_name=f"MSGraphConfiguration {self.pk}",
        )
