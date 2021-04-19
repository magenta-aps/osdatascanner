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

from django.db import models
from django.utils.translation import ugettext_lazy as _


# TODO: better name for this class? "Exportable" perhaps?
class Exported(models.Model):
    """Abstract base class for data models that are be exported.

    To support potential downtime in the receiving system, this abstract class
    retains information on when an object has been created, updated and exported
    successfully, in order to allow automated jobs to retry any failed exports
    if "last_modified" is more recent than "last_exported".
    """
    created = models.DateTimeField(
        # May need to be moved to a separate mixin eventually
        auto_now_add=True,
        verbose_name=_('created'),
    )
    last_modified = models.DateTimeField(
        # Deliberately NOT auto_now, since auto_now relies on save() and also
        # because it does not check for actual changes.
        # Set the field properly in a factory/service
        verbose_name=_('last modified'),
    )
    last_exported = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('last successful export'),
    )
    # TODO: do we need fields for deletion too? See also TODO on Realm

    class Meta:
        abstract = True
