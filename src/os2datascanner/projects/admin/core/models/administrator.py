# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


class Administrator(models.Model):
    """Relates a User to the one Client that they own and manage.

    A User can be an Administrator for at most one Client. Any User who is not
    a superuser will be restricted to interact with their Client only.
    """

    user = models.OneToOneField(
        get_user_model(),
        primary_key=True,
        related_name='administrator_for',
        verbose_name=_('user'),
        on_delete=models.CASCADE,
    )
    client = models.ForeignKey(
        'Client',
        related_name='administrators',
        verbose_name=_('client'),
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _('administrator')
        verbose_name_plural = _('administrators')

    def __str__(self):
        return f"Administrator: {self.user} (for {self.client})"

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.user} (User) for {self.client} (Client)>"
