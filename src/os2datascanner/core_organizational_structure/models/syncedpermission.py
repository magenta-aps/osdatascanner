from django.db import models
from django.utils.translation import gettext_lazy as _


class SyncedPermission(models.Model):
    """This model is not intended to ever store anything in the database.
       it only exists as a model to define permissions for. These permissions will exist both
       in the admin and report module."""

    class Meta:
        abstract = True
        permissions = [
            # None yet.
            # For this MR only. Removed before merge.
            ("very_important", _("A very important permission")),
            ("destroy_univserse", _("Allowed to destroy the universe")),
            ("universal_keys", _("Access to all Google infrastructure"))
        ]
