# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import os
import chardet
import structlog

from django.db import models
from django.conf import settings
from django.utils.translation import pgettext_lazy
from django.utils.translation import gettext_lazy as _

from exchangelib.errors import ErrorNonExistentMailbox
from os2datascanner.engine2.model.ews import EWSCalendarSource
from os2datascanner.engine2.model.core import SourceManager

from os2datascanner.projects.grants.models import GraphGrant, EWSGrant
from ....organizations.models.account import Account
from ...utils import upload_path_exchange_users
from .scanner import Scanner
from os2datascanner.engine2.rules.dict_lookup import EmailHeaderRule

logger = structlog.get_logger("adminapp")


def get_users_from_file(userlist):
    position = userlist.tell()
    try:
        content = userlist.read()
        ed = chardet.detect(content)
        if not (encoding := ed["encoding"]):
            raise ValueError
        else:
            return [stripped_line
                    for line in content.decode(encoding).split("\n")
                    if (stripped_line := line.strip())]
    finally:
        # Make sure we don't actually consume the bytes we read!
        userlist.seek(position)


class ExchangeCalendarScanner(Scanner):
    """Scanner for Exchange Web Services accounts"""

    @staticmethod
    def enabled():
        return settings.ENABLE_EXCHANGECALENDARSCAN

    mail_domain = models.CharField(max_length=2048, blank=False, verbose_name='Domain')

    userlist = models.FileField(
        null=True,
        blank=True,
        upload_to=upload_path_exchange_users,
    )

    service_endpoint = models.URLField(
        max_length=256,
        verbose_name="Service endpoint",
        blank=True,
        default=""
    )

    graph_grant = models.ForeignKey(
            GraphGrant, null=True, blank=True, on_delete=models.SET_NULL,
            verbose_name=_("Graph grant")
    )

    ews_grant = models.ForeignKey(
            EWSGrant, null=True, blank=True, on_delete=models.SET_NULL,
            verbose_name=_("EWS grant")
    )

    scan_attachments = models.BooleanField(
        default=True,
        verbose_name=_('Scan attachments'),
        help_text=_("Scan attachments"),
    )

    def get_userlist_file_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.userlist.name)

    @staticmethod
    def get_type():
        return "exchangecalendar"

    def compute_covered_accounts(self):
        # A Scanner that uses a userlist file shouldn't have a populated
        # covered_accounts field, so return QuerySet.none() in that case
        if self.userlist and not self.org_units.exists():
            return Account.objects.none()
        else:
            return super().compute_covered_accounts()

    def generate_sources(self):
        yield from (source for _, source in self.generate_sources_with_accounts())

    def generate_sources_with_accounts(self):
        constructor_param_base = {
            "domain": self.mail_domain.lstrip("@"),
            "server": self.service_endpoint or None,
        }

        if self.ews_grant and not self.organization.prioritize_graphgrant:
            constructor_param_base |= {
                "admin_user": self.ews_grant.username,
                "admin_password": self.ews_grant.password,
                }
        elif self.graph_grant:
            constructor_param_base |= {
                "admin_user": None,
                "admin_password": None,

                "client_id": str(self.graph_grant.app_id),
                "tenant_id": str(self.graph_grant.tenant_id),
                "client_secret": self.graph_grant.client_secret,
                }
        else:
            raise ValueError("No authentication method available")

        def _make_source(**kwargs):
            return EWSCalendarSource(
                    **constructor_param_base,
                    **kwargs)

        if (covered_accounts := self.compute_covered_accounts()).exists():
            for account in covered_accounts:
                # Only try to scan mail addresses that belong to the domain
                # associated with this scanner
                user_mail_address: str = account.email
                if user_mail_address:
                    local_part = user_mail_address.split("@", maxsplit=1)[0]
                    yield account, _make_source(user=local_part, scan_attachments=self.scan_attachments)
        elif self.userlist:
            user_list = get_users_from_file(self.userlist)
            for u in user_list:
                yield None, _make_source(user=u, scan_attachments=self.scan_attachments)
        else:
            raise ValueError("No users available")

    def verify(self) -> bool:
        for account in self.generate_sources():
            with SourceManager() as sm:
                try:
                    exchangelib_object = sm.open(account)
                    if exchangelib_object.msg_folder_root:
                        logger.info(
                            "OS2datascanner has access to calendar for {0}".format(
                                account.address
                            )
                        )
                except ErrorNonExistentMailbox:
                    logger.info("Calendar for {0} does not exits".format(account.address))
                    return False
        return True

    object_name = pgettext_lazy("unit of scan", "calendar event")
    object_name_plural = pgettext_lazy("unit of scan", "calendar events")

    class Meta:
        verbose_name = _("Exchange Calendar scanner")