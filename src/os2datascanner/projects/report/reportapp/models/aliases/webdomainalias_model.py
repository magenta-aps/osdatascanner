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

from django.db import models

from .alias_model import Alias


class WebDomainAlias(Alias):

    domain = models.TextField(verbose_name="Web-domænenavn")
    
    # Temporary solution until LDAP is rolled out
    value = models.TextField(verbose_name="Web-domænenavn", null=True)

    key = "web-domain"
    def __str__(self):
        return self.domain

    class Meta:
        verbose_name_plural = "Web domain aliases"
