from django.db import models
from django.utils.translation import gettext_lazy as _


class MSGraphSharePointSite(models.Model):
    uuid = models.TextField(
        unique=True,
        verbose_name=_("site id"),
    )

    name = models.TextField(
        default="Unnamed Site",
        verbose_name=_("site name")
    )
