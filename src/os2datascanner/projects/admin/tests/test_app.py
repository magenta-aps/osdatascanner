# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""
Unit tests for OS2datascanner.
"""

import pytest
from django.urls import reverse_lazy

from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import Scanner
from os2datascanner.projects.admin.adminapp.models.scannerjobs.webscanner import WebScanner
from os2datascanner.projects.admin.adminapp.models.scannerjobs.filescanner import FileScanner
from os2datascanner.projects.admin.adminapp.validate import validate_domain
from os2datascanner.projects.grants.models import SMBGrant


@pytest.mark.django_db
class TestScanner:

    """Test running a scan and domain validation."""
    # TODO: Capture the interaction so these tests can work without an
    # Internet connection! !!!

    def test_unvalidated_scannerjob_cannot_be_started(
            self, user_admin, client, invalid_web_scanner):
        """This test method is sufficient for all types of scanners."""

        client.force_login(user_admin)
        response = client.get(reverse_lazy("webscanner_askrun",
                                           kwargs={"pk": invalid_web_scanner.pk}))
        assert response.context["ok"] is False
        assert response.context["error_message"] == Scanner.NOT_VALIDATED

    def test_validate_domain(self, test_org, basic_rule):
        """Test validating domains."""
        # Make sure example.com does not validate in any of the possible
        # methods
        all_methods = [WebScanner.WEBSCANFILE, WebScanner.METAFIELD]

        for validation_method in all_methods:
            webscanner = WebScanner(
                url="http://www.example.com/",
                validation_method=validation_method,
                organization=test_org,
                pk=2, rule=basic_rule
            )
            webscanner.save()
            assert validate_domain(webscanner) is False

    def test_engine2_filescanner(self, test_org, basic_rule):
        smb_grant = SMBGrant.objects.create(username="jens",
                                            password="rigtig heste batteri haefteklamme",
                                            organization=test_org)
        scanner = FileScanner(
                unc="//ORG/SIKKERSRV",
                organization=test_org,
                smb_grant=smb_grant,
                alias="K", rule=basic_rule)

        source_generator = scanner.generate_sources()
        engine2_source = next(source_generator)

        assert engine2_source.driveletter == "K"
