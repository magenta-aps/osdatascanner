# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from .org_views import OrganizationListView, AddOrganizationView, UpdateOrganizationView, DeleteOrganizationView, OrganizationDeletionBlocked  # noqa
from .orgunit_views import OrganizationalUnitListView, OrganizationalUnitEditVisibility  # noqa
from .account_views import AccountDetailView, AccountListView, AliasCreateView, AliasDeleteView, ManagerDropdownView, DPODropdownView, OrgDPODropdownView  # noqa
from .keycloak_sso_views import SSOCreateView, SSOUpdateView, SSOErrorView  # noqa
from .grants_meta_views import GrantListView, GrantRedirectUpdateView  # noqa
from .ews_views import EWSGrantCreateView, EWSGrantUpdateView, EWSGrantScannerForm  # noqa
from .googleapi_views import GoogleApiGrantCreateView, GoogleApiGrantUpdateView, GoogleApiScannerForm  # noqa
from .msgraph_views import MSGraphGrantRequestView, MSGraphGrantReceptionView, MSGraphGrantCreateView, MSGraphGrantUpdateView, MSGraphGrantScannerForm  # noqa
from .smb_views import SMBGrantCreateView, SMBGrantUpdateView, SMBGrantScannerForm  # noqa
