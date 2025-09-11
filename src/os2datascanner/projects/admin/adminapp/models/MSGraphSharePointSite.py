from django.db import models
from django.utils.translation import gettext_lazy as _


class MSGraphSharePointSite(models.Model):
    uuid = models.TextField(
        verbose_name=_("site id"),
    )

    name = models.TextField(
        default="Unnamed Site",
        verbose_name=_("site name")
    )

    graph_grant = models.ForeignKey(
        'grants.GraphGrant',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_('MSGraph Grant')
    )

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('organization'),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['uuid', 'organization'],
                name='unique_sp_site_organization',
            )
        ]

        verbose_name = _('SharePoint site')
        verbose_name_plural = _('SharePoint sites')
