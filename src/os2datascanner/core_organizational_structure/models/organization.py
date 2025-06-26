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
import datetime
from django.db.models import ImageField
from recurrence.fields import RecurrenceField
from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator, EmailValidator
from drf_extra_fields.fields import Base64ImageField
from ..serializer import BaseSerializer


class StatisticsPageConfigChoices(models.TextChoices):
    MANAGERS = "M", "Managers"
    DPOS = "D", "Data Protection Officers"
    SUPERUSERS = "S", "Superusers"
    NONE = "N", "None"


class SBSYSTabConfigChoices(models.TextChoices):
    NONE = "N", _("Hidden for all")
    WITH_PERMISSION = "P", _("Visible with permission")
    ALL = "A", _("Visible for all")


class SupportContactChoices(models.TextChoices):
    NONE = "NO", _("None")
    WEBSITE = "WS", _("Website")
    EMAIL = "EM", _("Email")


class DPOContactChoices(models.TextChoices):
    NONE = "NO", _("None")
    SINGLE_DPO = "SD", _("Single DPO")
    UNIT_DPO = "UD", _("Unit DPO")


class OutlookCategorizeChoices(models.TextChoices):
    ORG_LEVEL = "ORG", _("Enable automatic categorization for entire organization")
    INDIVIDUAL_LEVEL = "IND", _("Allow users to categorize emails")
    NONE = "NON", _("No categorization")


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
        include_dtstart=False,
        verbose_name=_('Email notification interval')
    )

    dtstart = models.DateField(default=datetime.date.today, verbose_name=_('schedule start time'))

    email_header_banner = ImageField(null=True, blank=True,
                                     verbose_name=_("Email header banner"))

    # Retention policy settings
    retention_policy = models.BooleanField(default=False, verbose_name=_("retention policy"))
    retention_days = models.PositiveIntegerField(
        default=30, verbose_name=_("retention days"), blank=True)

    # Outlook settings
    outlook_delete_email_permission = models.BooleanField(
        default=None, null=True,
        verbose_name=_("allow deletion of emails in Outlook directly"))

    outlook_categorize_email_permission = models.CharField(
        max_length=3,
        choices=OutlookCategorizeChoices.choices,
        default=OutlookCategorizeChoices.NONE,
        verbose_name=_("Outlook category settings"),
        help_text=_("configure whether OSdatascanner should create Outlook categories and"
                    " categorize found matches, and decide whether you want to enforce this"
                    " on an organizational level (all accounts) or leave it up to the individual.")
    )

    # Onedrive/Sharepoint
    onedrive_delete_permission = models.BooleanField(
        default=None, null=True,
        verbose_name=_("allow deletion of online drive files directly")
    )

    # smb settings
    smb_delete_permission = models.BooleanField(
        default=None, null=True,
        verbose_name=_("allow deletion of on-premise drive files directly")
    )

    # Exchange settings
    exchange_delete_permission = models.BooleanField(
        default=None, null=True,
        verbose_name=_("allow deletion of emails on Exchange server directly")
    )

    # Gmail settings
    gmail_delete_permission = models.BooleanField(
        default=None, null=True,
        verbose_name=_("allow deletion of emails in gmail directly")
    )

    # Google Drive settings
    gdrive_delete_permission = models.BooleanField(
        default=None, null=True,
        verbose_name=_("allow deletion of files in Google Drive directly")
    )

    # Access settings
    leadertab_access = models.CharField(
        max_length=1,
        choices=StatisticsPageConfigChoices.choices,
        default=StatisticsPageConfigChoices.MANAGERS,
        verbose_name=_("Leadertab access")
    )
    dpotab_access = models.CharField(
        max_length=1,
        choices=StatisticsPageConfigChoices.choices,
        default=StatisticsPageConfigChoices.DPOS,
        verbose_name=_("Dpotab access")
    )
    sbsystab_access = models.CharField(
        max_length=1,
        choices=SBSYSTabConfigChoices.choices,
        default=SBSYSTabConfigChoices.NONE,
        verbose_name=_("SBSYS tab access")
    )

    # Grant prioritization configuration
    prioritize_graphgrant = models.BooleanField(
        default=False, verbose_name=_("Prioritize MSGraph grant"), help_text=_(
            "prioritize a Microsoft Graph Grant over an EWS Service Account for example when using"
            " Exchange online rather than Exchange on-premises"))

    # Support button settings
    show_support_button = models.BooleanField(
        default=False, verbose_name=_("show support button"))
    support_contact_method = models.CharField(
        max_length=2,
        choices=SupportContactChoices.choices,
        default=SupportContactChoices.NONE,
        verbose_name=_("support contact method"),
        blank=False
    )
    support_name = models.CharField(
        max_length=100, default="IT",
        blank=True, verbose_name=_("support name"))
    support_value = models.CharField(
        max_length=1000, default="",
        blank=True, verbose_name=_("support value"))
    dpo_contact_method = models.CharField(
        max_length=2,
        choices=DPOContactChoices.choices,
        default=DPOContactChoices.NONE,
        verbose_name=_("DPO contact method"),
        blank=False
    )
    dpo_name = models.CharField(
        max_length=100, default="",
        blank=True, verbose_name=_("DPO name"))
    dpo_value = models.CharField(
        max_length=100, default="",
        blank=True, verbose_name=_("DPO value"))

    def clean(self):
        errors = {}

        # Validate support contact value based on the type
        if self.support_contact_method == SupportContactChoices.WEBSITE:
            validator = URLValidator()
        elif self.support_contact_method == SupportContactChoices.EMAIL:
            validator = EmailValidator()
        if self.support_contact_method in (
                SupportContactChoices.EMAIL,
                SupportContactChoices.WEBSITE):
            if not self.support_name:
                errors['support_name'] = _("Provide a name of the support contact.")
            try:
                validator(self.support_value)
            except Exception as e:
                errors['support_value'] = e

        if self.dpo_contact_method == DPOContactChoices.SINGLE_DPO:
            if not self.dpo_name:
                errors['dpo_name'] = _("Provide a name of the DPO.")

            try:
                EmailValidator()(self.dpo_value)
            except Exception as e:
                errors['dpo_value'] = e

        if errors:
            raise ValidationError(errors)

        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    @property
    def get_next_email_schedule_date(self):
        if not self.email_notification_schedule:
            return None

        if schedule := self.email_notification_schedule.after(
                datetime.datetime.combine(datetime.date.today(), datetime.time()),
                inc=True,
                dtstart=datetime.datetime.combine(self.dtstart, datetime.time())):

            return schedule.date()

    class Meta:
        abstract = True
        verbose_name = _('organization')
        verbose_name_plural = _('organizations')

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name} ({self.uuid})>"


class OrganizationSerializer(BaseSerializer):
    # Override to set represent_in_base64=True for serialization.
    email_header_banner = Base64ImageField(required=False,
                                           represent_in_base64=True)

    class Meta:
        fields = [
            'pk',
            'name',
            'contact_email',
            'contact_phone',
            'email_notification_schedule',
            'leadertab_access',
            'dpotab_access',
            'sbsystab_access',
            'show_support_button',
            'support_contact_method',
            'support_name',
            'support_value',
            'dpo_contact_method',
            'dpo_name',
            'dpo_value',
            'outlook_categorize_email_permission',
            'smb_delete_permission',
            'exchange_delete_permission',
            'outlook_delete_email_permission',
            'onedrive_delete_permission',
            'gmail_delete_permission',
            'gdrive_delete_permission',
            'email_header_banner',
            'dtstart',
            'retention_policy',
            'retention_days',
            'prioritize_graphgrant']
