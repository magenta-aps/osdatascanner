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

from django.utils.translation import ugettext_lazy as _
from django.db.models.query_utils import Q
from ..documentreport import DocumentReport
from .role import Role


class DefaultRole(Role):
    """The DefaultRole role's filter accepts all matches that have not already
    been resolved and whose metadata can be associated with one of the user's
    aliases.

    (This role *can*, and should, be explicitly associated with users, but the
    system will also use its behaviour as a fallback if users don't have any
    other roles.)"""

    def filter(self, document_reports):
        aliases = self.user.aliases.all()
        results = DocumentReport.objects.none()
        for alias in aliases:
            result = document_reports.filter(Q(alias_relation=alias.pk))
            # Merges django querysets together
            results = results | result
            # If another user has delegated matches to this user, include these as well.
            if alias.delegate_all_from.all().exists():
                for profile in alias.delegate_all_from.iterator():
                    other_aliases = profile.user.aliases.all()
                    for other_alias in other_aliases:
                        other_result = document_reports.filter(Q(alias_relation=other_alias.pk))
                        results = results | other_result
        return results

    class Meta:
        verbose_name = _("default role")
