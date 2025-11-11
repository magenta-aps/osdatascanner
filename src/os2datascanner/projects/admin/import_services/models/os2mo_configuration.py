from .import_service import ImportService
from .exported_mixin import Exported
from django.utils.translation import gettext_lazy as _
from os2datascanner.projects.admin.core.models.background_job import JobState


class OS2moConfiguration(Exported, ImportService):

    class Meta:
        verbose_name = _("OS2mo configuration")
        verbose_name_plural = _("OS2mo configurations")

    def start_import(self):
        from . import OS2moImportJob
        from os2datascanner.projects.admin.import_services.utils import _start_import_job

        _start_import_job(
            importjob_model=OS2moImportJob,
            lookup_filter={"organization": self.organization},
            job_kwargs={
                "organization": self.organization,
            },
            allowed_states=(
                JobState.FINISHED,
                JobState.FAILED,
                JobState.CANCELLED,
            ),
            log_name=f"OS2moConfiguration {self.pk}",
        )
