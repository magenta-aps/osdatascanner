# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from os2datascanner.projects.grants.models import EWSGrant, GoogleApiGrant, GraphGrant, SMBGrant


@pytest.mark.django_db
class TestEncryptedFieldsAllowEmpty:
    """Regression tests for #64726: encrypted fields on Grants must be
    allowed to be empty, and nothing should break when they are."""

    def test_empty_service_account_reads_as_none(self, test_org):
        grant = GoogleApiGrant.objects.create(organization=test_org)

        assert grant.service_account is None
        assert grant.account_name is None
        assert grant.service_account_dict is None

    def test_empty_service_account_str_does_not_raise(self, test_org):
        grant = GoogleApiGrant.objects.create(organization=test_org)

        assert str(grant)

    def test_empty_service_account_does_not_break_clean_of_other_grants(
            self, test_org, google_api_grant):
        # A pre-existing grant with an empty service account (e.g. one still
        # being set up) must not prevent validating a different, properly
        # configured grant for the same organization.
        GoogleApiGrant.objects.create(organization=test_org)

        google_api_grant.full_clean()

    def test_setting_service_account_to_empty_string_stores_none(self, test_org):
        grant = GoogleApiGrant(organization=test_org)
        grant.service_account = ""

        assert grant._service_account is None
        assert grant.service_account is None

    def test_empty_client_secret_reads_as_none(self, test_org):
        grant = GraphGrant(organization=test_org)

        assert grant.client_secret is None

    def test_empty_ews_password_reads_as_none(self, test_org):
        grant = EWSGrant(username="keyChainGuy", organization=test_org)

        assert grant.password is None
        assert str(grant)

    def test_empty_smb_password_reads_as_none(self, test_org):
        grant = SMBGrant(username="MrMicrosoft", organization=test_org)

        assert grant.password is None
        assert str(grant)
