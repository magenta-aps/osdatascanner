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
from django.utils.translation import ugettext_lazy as _


# TODO: rename to Imported?
class Synchronized(models.Model):
    """Abstract base class for models for which instances may be imported.

    Instances marked as being imported should only be added, modified or
    deleted as instructed by the relevant external service; instances without
    this marking may be modified freely locally.
    """

    class Meta:
        abstract = True

    automated_sync = models.BooleanField(  # TODO: better naming?
        default=False,
        verbose_name=_('automated synchronization'),  # TODO: better naming?
        help_text=_(
            'Select to allow data to be maintained automatically ' +
            '(this requires configuration of a directory service). ' +
            'PLEASE NOTE: this setting will cause data to be deleted, if the ' +
            'equivalent entry is not found - thus presumed deleted - at the source.'
        ),
    )
