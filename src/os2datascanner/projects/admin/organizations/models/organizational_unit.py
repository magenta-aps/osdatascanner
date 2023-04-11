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

from django.db.models import Count

from os2datascanner.utils.model_helpers import ModelFactory
from os2datascanner.projects.admin.import_services.models import Imported
from os2datascanner.core_organizational_structure.models import \
    OrganizationalUnit as Core_OrganizationalUnit
from .broadcasted_mixin import Broadcasted, post_save_broadcast


class OrganizationalUnit(Core_OrganizationalUnit, Broadcasted, Imported):
    """ Core logic lives in the core_organizational_structure app.
        Additional specific logic can be implemented here. """
    factory = None

    @property
    def members_associated(self):
        return self.positions.values("account").annotate(
            count=Count("account")).values("account").count()

    @property
    def managers(self):
        return self.positions.filter(role="manager").prefetch_related("account")

    def get_root(self):
        if self.parent is None:
            return self
        else:
            return self.parent.get_root()

    def get_depth(self, curr_depth=1):
        if self.parent is None:
            return curr_depth
        else:
            return self.parent.get_depth(curr_depth=curr_depth+1)


OrganizationalUnit.factory = ModelFactory(OrganizationalUnit)


@OrganizationalUnit.factory.on_create
@OrganizationalUnit.factory.on_update
def on_organizational_unit_created_updated(objects, fields=None):
    for ou in objects:
        post_save_broadcast(None, ou)
