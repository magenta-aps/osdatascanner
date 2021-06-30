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

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from exchangelib.errors import ErrorNonExistentMailbox
from mptt.models import TreeForeignKey

from os2datascanner.engine2.model.ews import EWSAccountSource
from os2datascanner.engine2.model.core import SourceManager

from .scanner_model import Scanner
from ...utils import upload_path_exchange_users


class ExchangeScanner(Scanner):
    """Scanner for Exchange Web Services accounts"""

    userlist = models.FileField(upload_to=upload_path_exchange_users)

    service_endpoint = models.URLField(max_length=256,
                                       verbose_name='Service endpoint',
                                       blank=True, default='')
    org_unit = TreeForeignKey(
        'organizations.OrganizationalUnit',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('organizational unit'),
    )

    def get_userlist_file_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.userlist.name)

    def get_type(self):
        return 'exchange'

    def get_absolute_url(self):
        """Get the absolute URL for scanners."""
        return '/exchangescanners/'

    def generate_sources(self):
        user_list = [u.decode("utf-8").strip()
                for u in self.userlist if u.strip()]
        for u in user_list:
            yield EWSAccountSource(
                    domain=self.url.lstrip('@'),
                    server=self.service_endpoint or None,
                    admin_user=self.authentication.username,
                    admin_password=self.authentication.get_password(),
                    user=u)

    def verify(self) -> bool:
        for account in self.generate_sources():
            with SourceManager() as sm:
                try:
                    exchangelib_object = sm.open(account)
                    if exchangelib_object.msg_folder_root:
                        print("OS2datascanner has access to mailbox {0}".format(
                            account.address)
                        )
                except ErrorNonExistentMailbox:
                    print("Mailbox {0} does not exits".format(account.address))
                    return False
        return True
