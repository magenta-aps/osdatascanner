from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _

from os2datascanner.projects.admin.organizations.models.broadcasted_mixin import Broadcasted


@Broadcasted.register
class GrantExtra(models.Model):
    grant = models.OneToOneField(
            'grants.Grant',
            related_name="grant_extra",
            on_delete=models.CASCADE,
            verbose_name=_("Grant Extra")
    )
    should_broadcast = models.BooleanField(default=False,
                                           verbose_name=_("Should Broadcast"))


class GrantExtraForm(forms.ModelForm):
    class Meta:
        model = GrantExtra
        fields = ("should_broadcast",)
