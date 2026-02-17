# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.db import models
from django.db.models import F, Q
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class Imported(models.Model):
    """
    Abstract base class for models that may be imported from external services.

    Instances marked as imported should only be added, modified or
    deleted as instructed by the relevant external service; instances without
    this marking may be modified freely locally.
    """

    imported = models.BooleanField(
        default=False,
        editable=False,
        verbose_name=_('has been imported'),
    )

    # Store unique ID from external service
    imported_id = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('imported unique ID'),
    )
    # Store when last request for import was made
    last_import_requested = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('last time an update was requested'),
    )
    # Store when last successful import was made
    last_import = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('last successful import'),
    )

    class Meta:
        abstract = True

    @classmethod
    def get_all_awaiting(cls):
        no_request = Q(last_import_requested__isnull=True)
        request_in_future = Q(last_import_requested__gt=now())
        no_import = Q(last_import__isnull=True)
        outdated = Q(last_import__lte=F('last_import_requested'))
        relevant_qs = cls.objects.exclude(no_request | request_in_future)
        return relevant_qs.filter(no_import | outdated)
