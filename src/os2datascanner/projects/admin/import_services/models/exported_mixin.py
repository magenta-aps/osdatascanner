# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.db import models
from django.db.models import F, Q
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class Exported(models.Model):
    """Abstract base class for data models that are be exported.

    To support potential downtime in the receiving system, this abstract class
    retains information on when an object has been created, updated and exported
    successfully, in order to allow automated jobs to retry any failed exports
    if "last_modified" is more recent than "last_exported".
    """
    created = models.DateTimeField(
        # May need to be moved to a separate mixin eventually
        auto_now_add=True,
        verbose_name=_('created'),
    )
    last_modified = models.DateTimeField(
        # Deliberately NOT auto_now, since auto_now relies on save() and also
        # because it does not check for actual changes.
        # Set the field properly in a factory/service
        verbose_name=_('last modified'),
    )
    last_exported = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('last successful export'),
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('marked for deletion at'),
    )

    class Meta:
        abstract = True

    @classmethod
    def get_all_awaiting(cls):
        no_export = Q(last_exported__isnull=True)
        modified_after_export = Q(last_exported__lte=F('last_modified'))
        return cls.objects.filter(no_export | modified_after_export)

    @classmethod
    def get_all_deleted(cls):
        current_time = now()
        return cls.objects.filter(deleted_at__lte=current_time)
