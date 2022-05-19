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

from django.conf import settings

from os2datascanner.engine2.model.msgraph.teams import MSGraphChatSource
from .msgraph_models import MSGraphScanner


class MSTeamsScanner(MSGraphScanner):
    """MS Teams scanner for scanning MS Teams chats and channels."""

    def get_type(self):
        return "msgraph-teams"

    def get_absolute_url(self):
        """Get the absolute URL for scanners."""
        return "/msgraph-teamsscanners/"

    def generate_sources(self):
        yield MSGraphChatSource(
            client_id=settings.MSGRAPH_APP_ID,
            tenant_id=self.tenant_id,
            client_secret=settings.MSGRAPH_CLIENT_SECRET,
        )
