from ....grants.models import GoogleApiGrant
from django.db import models
from .import_service import ImportService
from .exported_mixin import Exported
from django.utils.translation import gettext_lazy as _
from os2datascanner.projects.admin.core.models.background_job import JobState


class GoogleWorkspaceConfig(Exported, ImportService):
    """
    Configuration for linking an organization to a Google Workspace API grant.

    This model stores the required setup to perform domain-wide delegated imports from
    Google Workspace.
    """
    grant = models.ForeignKey(
        GoogleApiGrant,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Google API Grant"),
    )
    delegated_admin_email = models.EmailField(
        verbose_name=_('Delegated admin email'),
        help_text=_('Admin user to impersonate when accessing Workspace APIs'),
        null=False,
        blank=False
    )

    class Meta:
        verbose_name = _("Google Workspace configuration")
        verbose_name_plural = _("Google Workspace configurations")

    def start_import(self):
        from . import GoogleWorkspaceImportJob
        from os2datascanner.projects.admin.import_services.utils import _start_import_job

        _start_import_job(
            importjob_model=GoogleWorkspaceImportJob,
            lookup_filter={"grant": self.grant},
            job_kwargs={
                "grant": self.grant,
                "organization": self.organization,
                "delegated_admin_email": self.delegated_admin_email,
            },
            allowed_states=(
                JobState.FINISHED,
                JobState.FAILED,
                JobState.CANCELLED,
                JobState.FINISHED_WITH_WARNINGS,
            ),
            log_name=f"GoogleWorkspaceConfig {self.pk}",
        )
