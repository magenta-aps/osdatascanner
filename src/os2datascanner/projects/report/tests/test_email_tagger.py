# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from os2datascanner.projects.grants.models import GraphGrant
from os2datascanner.projects.report.reportapp.management.commands import (
        email_tagger)
from .generate_test_data import record_match


@pytest.fixture
def dummy_graphgrant(*, test_org):
    return GraphGrant.objects.create(
            organization=test_org,
            tenant_id="01234567-89ab-cdef-ffff-000000000001",
            app_id="01234567-89ab-cdef-ffff-000000000002",
            client_secret="INVALID")


@pytest.mark.django_db
class TestEmailTagger:
    def test_grant_selection(self, *, positive_match, dummy_graphgrant):
        # Arrange
        match_obj = record_match(positive_match)

        # Assert
        assert email_tagger.get_grant(match_obj) == dummy_graphgrant
