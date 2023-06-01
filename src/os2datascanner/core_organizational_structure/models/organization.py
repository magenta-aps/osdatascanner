# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2datascanner is developed by Magenta in collaboration with the OS2 public
# sector open source network <https://os2.eu/>.
#
from recurrence.fields import RecurrenceField
from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..serializer import BaseSerializer


class LeaderPageConfigChoices(models.TextChoices):
    MANAGERS = "M", "Managers"
    SUPERUSERS = "S", "Superusers"
    NONE = "N", "None"


class Organization(models.Model):
    """Stores data for a specific organization.

    An Organization represents the administrative context for a self-contained
    organization, with an optional reference to a representation of its
    hierarchical structure.

    Note that the system distinguishes between Client and Organization. This
    is to allow the case where one Client (e.g. a service provider) administers
    scans for several Organizations.

    All Organizations are related to exactly one Client.
    """

    serializer_class = None

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name=_('UUID'),
    )
    name = models.CharField(
        max_length=256,
        verbose_name=_('name'),
    )
    contact_email = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name=_('email'),
    )
    contact_phone = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name=_('phone number'),
    )

    email_notification_schedule = RecurrenceField(
        max_length=1024,
        null=True,
        blank=True,
        default="RRULE:FREQ=WEEKLY;BYDAY=FR",
        verbose_name=_('Email notification interval')
    )

    leadertab_access = models.CharField(
        max_length=1,
        choices=LeaderPageConfigChoices.choices,
        default=LeaderPageConfigChoices.MANAGERS,
    )

    class Meta:
        abstract = True
        verbose_name = _('organization')
        verbose_name_plural = _('organizations')

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name} ({self.uuid})>"


class OrganizationSerializer(BaseSerializer):
    class Meta:
        fields = ['pk', 'name', 'contact_email', 'contact_phone', 'email_notification_schedule']
