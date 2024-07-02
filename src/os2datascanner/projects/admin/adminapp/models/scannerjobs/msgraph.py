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
# OS2Webscanner was developed by Magenta in collaboration with OS2 the
# Danish community of open source municipalities (http://www.os2web.dk/).
#
# The code is currently governed by OS2 the Danish community of open
# source municipalities ( http://www.os2web.dk/ )
import structlog

from django.db import models
from django.utils.translation import gettext_lazy as _

from os2datascanner.engine2.model.msgraph.mail import (MSGraphMailSource, MSGraphMailAccountSource,
                                                       MSGraphMailAccountHandle)
from os2datascanner.engine2.model.msgraph.files import (MSGraphFilesSource, MSGraphDriveSource,
                                                        MSGraphDriveHandle)
from os2datascanner.engine2.model.msgraph.calendar import (MSGraphCalendarSource,
                                                           MSGraphCalendarAccountSource,
                                                           MSGraphCalendarAccountHandle)
from os2datascanner.engine2.model.msgraph.teams import MSGraphTeamsFilesSource

from os2datascanner.projects.grants.models import GraphGrant
from ....organizations.models.aliases import AliasType
from .scanner import Scanner

logger = structlog.get_logger("adminapp")


def _create_user_list(org_unit):  # noqa
    """
    Creates a user list from selected organization units.
    """
    user_list = set()

    for organizational_unit in org_unit.all():
        for position in organizational_unit.positions.all():
            addresses = position.account.aliases.filter(
                _alias_type=AliasType.EMAIL.value,
            )
            if not addresses:
                logger.info(
                    f"user {position.account.username} has no email alias "
                    "connected"
                )
            else:
                for alias in addresses:
                    address = alias.value
                    user_list.add(address)

    logger.info(f"submitting scan for accounts {', '.join(user_list)}")

    return frozenset(user_list)


class MSGraphScanner(Scanner):
    grant = models.ForeignKey(GraphGrant, null=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True
        ordering = ['name']


class MSGraphMailScanner(MSGraphScanner):
    scan_deleted_items_folder = models.BooleanField(
        default=False,
        verbose_name=_('Scan deleted items folder'),
        help_text=_("Include emails in the deleted post folder"),
    )

    scan_syncissues_folder = models.BooleanField(
        default=True,
        verbose_name=_('Scan syncissues folder'),
        help_text=_("Include emails in the syncissues folder"),
    )

    scan_attachments = models.BooleanField(
        default=True,
        verbose_name=_('Scan attachments'),
        help_text=_("Scan attached files"),
    )

    supports_rule_preexec = True

    def get_type(self):
        return 'msgraph-mail'

    def get_absolute_url(self):
        """Get the absolute URL for scanners."""
        return '/msgraph-mailscanners/'

    def generate_sources(self):
        yield from (source for _, source in self.generate_sources_with_accounts())

    def generate_sources_with_accounts(self):  # noqa
        base_source = MSGraphMailSource(
                client_id=str(self.grant.app_id),
                tenant_id=str(self.grant.tenant_id),
                client_secret=self.grant.client_secret,
                scan_deleted_items_folder=self.scan_deleted_items_folder,
                scan_syncissues_folder=self.scan_syncissues_folder,
                scan_attachments=self.scan_attachments)
        for account in self.compute_covered_accounts():
            for alias in account.aliases.filter(_alias_type=AliasType.EMAIL):
                user_mail_address: str = alias.value
                yield (account, MSGraphMailAccountSource(
                    MSGraphMailAccountHandle(base_source, user_mail_address)))


class MSGraphFileScanner(MSGraphScanner):
    scan_site_drives = models.BooleanField(
            default=True, verbose_name='Scan alle SharePoint-mapper')
    scan_user_drives = models.BooleanField(
            default=True, verbose_name='Scan alle OneDrive-drev')

    def get_type(self):
        return 'msgraph-files'

    def get_absolute_url(self):
        """Get the absolute URL for scanners."""
        return '/msgraph-filescanners/'

    def generate_sources(self):
        yield from (source for _, source in self.generate_sources_with_accounts())

    def generate_sources_with_accounts(self):  # noqa
        base_source = MSGraphFilesSource(
                client_id=str(self.grant.app_id),
                tenant_id=str(self.grant.tenant_id),
                client_secret=self.grant.client_secret,
                site_drives=self.scan_site_drives,
                user_drives=False)
        if self.scan_site_drives:
            # TODO: files in a SharePoint drive do actually have an owner...
            yield None, base_source
        if self.scan_user_drives:
            for account in self.compute_covered_accounts():
                for alias in account.aliases.filter(_alias_type=AliasType.EMAIL):
                    user_mail_address: str = alias.value
                    yield (account, MSGraphDriveSource(
                        MSGraphDriveHandle(
                            base_source,
                            None,  # don't need a drive ID when we specify user_account
                            None,  # ... or a folder name :D
                            None,  # or a human name 🤨
                            user_account=user_mail_address
                        )
                    ))


class MSGraphCalendarScanner(MSGraphScanner):
    """Model for MSGraphCalendarSource."""

    def get_type(self):
        return 'msgraph-calendar'

    def get_absolute_url(self):
        """Get the absolute URL for scanners."""
        return '/msgraph-calendarscanners/'

    def generate_sources(self):
        yield from (source for _, source in self.generate_sources_with_accounts())

    def generate_sources_with_accounts(self):  # noqa
        base_source = MSGraphCalendarSource(
                client_id=str(self.grant.app_id),
                tenant_id=str(self.grant.tenant_id),
                client_secret=self.grant.client_secret)
        for account in self.compute_covered_accounts():
            for alias in account.aliases.filter(_alias_type=AliasType.EMAIL):
                user_mail_address: str = alias.value
                yield (account, MSGraphCalendarAccountSource(
                    MSGraphCalendarAccountHandle(base_source, user_mail_address)))


class MSGraphTeamsFileScanner(MSGraphScanner):

    linkable = True

    do_link_check = models.BooleanField(
        default=False,
        verbose_name=_("check dead links")
    )

    def get_type(self):
        return 'msgraph-teams-file'

    def get_absolute_url(self):
        """Get the absolute URL for scanners."""
        return '/msgraph-teams-filescanners/'

    # TODO: Expand with generate_sources_with_accounts logic if possible.
    def generate_sources(self):

        yield MSGraphTeamsFilesSource(
                client_id=str(self.grant.app_id),
                tenant_id=str(self.grant.tenant_id),
                client_secret=self.grant.client_secret)
