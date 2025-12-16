from ....grants.models import GoogleApiGrant
from django.db import models
from .import_service import ImportService
from .exported_mixin import Exported
from django.utils.translation import gettext_lazy as _


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
