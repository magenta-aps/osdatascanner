from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    """
    Modified version of the default django user.
    Can be forced to change password
    """
    change_password = models.BooleanField(
        default=False,
        verbose_name=_("Skift password"),
    )
