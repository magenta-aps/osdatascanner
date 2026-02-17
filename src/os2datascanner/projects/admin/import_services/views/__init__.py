# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from .ldap_config_views import LDAPAddView, LDAPUpdateView, LDAPImportView, LDAPTestConnectionView  # noqa
from .keycloak_api_views import verify_connection, verify_authentication  # noqa
from .msgraph_config_views import MSGraphAddView, MSGraphUpdateView, MSGraphImportView  # noqa
from .os2mo_config_views import OS2moAddView, OS2moUpdateView, OS2moImportView  # noqa
from .google_workspace_views import GoogleWorkspaceAddView, GoogleWorkspaceUpdateView, GoogleWorkspaceImportView  # noqa
