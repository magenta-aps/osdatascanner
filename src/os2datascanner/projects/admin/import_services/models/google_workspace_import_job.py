from django.db import models
from django.utils.translation import gettext_lazy as _

from ...core.models.background_job import BackgroundJob


class GoogleWorkspaceImportJob(BackgroundJob):

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name=_('organization'),
        related_name='googleworkspaceimportjobs'
    )

    grant = models.ForeignKey(
        'grants.GoogleApiGrant',
        on_delete=models.SET_NULL,
        verbose_name=_("Google API Grant"),
        null=True,
        blank=True,
    )

    delegated_admin_email = models.EmailField(
        verbose_name=_('Delegated admin email used for this run')
    )

    def __str__(self):
        return f"Google Workspace import for {self.organization}"

    def job_label(self) -> str:
        return "Google Workspace import job"
