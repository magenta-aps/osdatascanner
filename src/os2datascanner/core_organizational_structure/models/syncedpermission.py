from django.db import models
from django.utils.translation import gettext_lazy as _


class SyncedPermission(models.Model):
    """This model is not intended to ever store anything in the database.
       it only exists as a model to define permissions for. These permissions will exist both
       in the admin and report module."""

    class Meta:
        abstract = True
        permissions = [
            ("test_permission",
             _("This is a test permission. It does not grant access to anything."))
        ]
