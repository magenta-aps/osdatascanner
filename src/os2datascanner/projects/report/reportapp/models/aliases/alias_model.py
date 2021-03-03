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
from abc import abstractmethod
from django.db import models
from django.contrib.auth.models import User
from model_utils.managers import InheritanceManager
from ..documentreport_model import DocumentReport



class Alias(models.Model):
    objects = InheritanceManager()

    user = models.ForeignKey(User, null=False, verbose_name="Bruger",
                             related_name="aliases", on_delete=models.CASCADE)

    @property
    @abstractmethod
    def key(self):

        """Returns the metadata property name associated with this alias."""

    # Temporary solution until LDAP is rolled out
    @abstractmethod
    def value(self):

        """Returns the metadata value associated with this alias."""
     
    def save(self, *args, **kwargs):
        from ..aliasmatchrelation_model import AliasMatchRelation
        
        super().save(*args, **kwargs)
        # After save, find the saved subclass and check for key:value in DocumentReports
        alias = Alias.objects.get_subclass(pk=self.pk)

        reports = DocumentReport.objects.filter(
            data__metadata__metadata__contains = {
                str(alias.key):str(alias)
            })

        # Create AliasMatchRelation for each found report.
        [AliasMatchRelation.create_relation(self, report) for report in reports]
