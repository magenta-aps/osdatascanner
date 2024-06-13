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
import os
import chardet
import structlog

from django.db import models
from django.conf import settings

from exchangelib.errors import ErrorNonExistentMailbox
from os2datascanner.engine2.model.ews import EWSAccountSource
from os2datascanner.engine2.model.core import SourceManager

from os2datascanner.projects.grants.models import GraphGrant
from ....organizations.models.account import Account
from ....organizations.models.aliases import AliasType
from ...utils import upload_path_exchange_users
from ..authentication import Authentication
from .scanner import Scanner

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


class ExchangeScanner(Scanner):
    """Scanner for Exchange Web Services accounts"""

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

    grant = models.ForeignKey(
            GraphGrant, null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def needs_revalidation(self):
        try:
            return ExchangeScanner.objects.get(
                    pk=self.pk).mail_domain != self.mail_domain
        except ExchangeScanner.DoesNotExist:
            return False

    def get_userlist_file_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.userlist.name)

    def get_type(self):
        return "exchange"

    def get_absolute_url(self):
        """Get the absolute URL for scanners."""
        return "/exchangescanners/"

    def compute_covered_accounts(self):
        # A Scanner that uses a userlist file shouldn't have a populated
        # covered_accounts field, so return QuerySet.none() in that case
        if self.userlist and not self.org_unit.exists():
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

        match (self.grant, self.authentication):
            # Prefer GraphGrant if we have one...
            case (GraphGrant(), _) if settings.MSGRAPH_EWS_AUTH:
                constructor_param_base |= {
                    "admin_user": None,
                    "admin_password": None,

                    "client_id": str(self.grant.app_id),
                    "tenant_id": str(self.grant.tenant_id),
                    "client_secret": self.grant.client_secret,
                }
            # ... but use the Authentication object if we don't (as long as it
            # actually has a username)
            case (_, Authentication(username=u)) if u:
                constructor_param_base |= {
                    "admin_user": self.authentication.username,
                    "admin_password": self.authentication.get_password(),
                }
            case _:
                raise ValueError("No authentication method available")

        def _make_source(**kwargs):
            return EWSAccountSource(
                    **constructor_param_base,
                    **kwargs)

        if (covered_accounts := self.compute_covered_accounts()).exists():
            for account in covered_accounts:
                # Only try to scan mail addresses that belong to the domain
                # associated with this scanner
                for alias in account.aliases.filter(
                        _alias_type=AliasType.EMAIL,
                        _value__iendswith=self.mail_domain):
                    user_mail_address: str = alias.value
                    local_part = user_mail_address.split("@", maxsplit=1)[0]
                    yield (account, _make_source(user=local_part))
        elif self.userlist:
            user_list = get_users_from_file(self.userlist)
            for u in user_list:
                yield (None, _make_source(user=u))
        else:
            raise ValueError("No users available")

    def verify(self) -> bool:
        for account in self.generate_sources():
            with SourceManager() as sm:
                try:
                    exchangelib_object = sm.open(account)
                    if exchangelib_object.msg_folder_root:
                        logger.info(
                            "OS2datascanner has access to mailbox {0}".format(
                                account.address
                            )
                        )
                except ErrorNonExistentMailbox:
                    logger.info("Mailbox {0} does not exits".format(account.address))
                    return False
        return True
