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
from django.db import models
from rest_framework import serializers
from os2datascanner.core_organizational_structure.models import Organization as Core_Organization
from os2datascanner.core_organizational_structure.models import \
    OrganizationSerializer as Core_OrganizationSerializer
from os2datascanner.core_organizational_structure.models import OutlookCategorizeChoices

from ..seralizer import BaseBulkSerializer


class OrganizationManager(models.Manager):

    def bulk_update(self, objects, fields, **kwargs):
        updated = super().bulk_update(objects, fields, **kwargs)
        from ..models.account import Account
        # We _might_ need to do perform some extra steps here if
        # we're dealing with user impacting organization updates.
        # These should only ever be relevant on update, as an Organization is the basis of all.
        if (field_name := "outlook_categorize_email_permission") in fields:
            for organization in objects:
                outlook_categorize_email_permission = getattr(organization, field_name)
                accs_in_org = Account.objects.filter(organization=organization)

                if outlook_categorize_email_permission == OutlookCategorizeChoices.ORG_LEVEL:
                    # Make sure we have AccountOutlookSetting objects, which in this
                    # case should have categorize_email set to True.
                    # That will use bulk_create and AccountOutlookSetting will handle
                    # the creation of categories and categorize existing.
                    accs_in_org.create_account_outlook_setting(categorize_email=True)
                # Setting NONE, will 'soft' delete existing.
                elif outlook_categorize_email_permission == OutlookCategorizeChoices.NONE:
                    from ..models.account_outlook_setting import AccountOutlookSetting
                    # We'll just go straight through AccountOutlookSetting in this case.
                    AccountOutlookSetting.objects.filter(
                        account__in=accs_in_org).delete_categories()

        return updated


class Organization(Core_Organization):
    """ Core logic lives in the core_organizational_structure app. """
    serializer_class = None
    # Set manager
    objects = OrganizationManager()

    def has_categorize_permission(self) -> bool:
        return bool(
            self.outlook_categorize_email_permission in
            (OutlookCategorizeChoices.ORG_LEVEL, OutlookCategorizeChoices.INDIVIDUAL_LEVEL)
        )

    def has_email_delete_permission(self) -> bool:
        return self.outlook_delete_email_permission

    def has_file_delete_permission(self) -> bool:
        return self.onedrive_delete_permission


class OrganizationBulkSerializer(BaseBulkSerializer):
    """ Bulk create & update logic lives in BaseBulkSerializer """

    class Meta:
        model = Organization


class OrganizationSerializer(Core_OrganizationSerializer):
    pk = serializers.UUIDField(read_only=False)

    class Meta(Core_OrganizationSerializer.Meta):
        model = Organization
        list_serializer_class = OrganizationBulkSerializer


Organization.serializer_class = OrganizationSerializer
