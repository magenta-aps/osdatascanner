# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

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
                                           verbose_name=_("Synchronize to report module"))
    previous_should_broadcast = False

    def save(self, *args, **kwargs):
        try:
            self.previous_should_broadcast = GrantExtra.objects.get(pk=self.pk).should_broadcast
        except GrantExtra.DoesNotExist:
            # This GrantExtra is just now being created -- nothing more to do!
            pass
        super().save(*args, **kwargs)


class GrantExtraForm(forms.ModelForm):
    class Meta:
        model = GrantExtra
        fields = ("should_broadcast",)
