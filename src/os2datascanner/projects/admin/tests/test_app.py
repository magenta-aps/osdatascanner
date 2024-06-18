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
"""
Unit tests for OS2datascanner.
"""

import pytest

from os2datascanner.projects.admin.adminapp.models.authentication import Authentication
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import Scanner
from os2datascanner.projects.admin.adminapp.models.scannerjobs.webscanner import WebScanner
from os2datascanner.projects.admin.adminapp.models.scannerjobs.filescanner import FileScanner
from os2datascanner.projects.admin.adminapp.validate import validate_domain


@pytest.mark.django_db
class TestScanner:

    """Test running a scan and domain validation."""
    # TODO: Capture the interaction so these tests can work without an
    # Internet connection! !!!

    def test_unvalidated_scannerjob_cannot_be_started(
            self, user_admin, client, invalid_web_scanner):
        """This test method is sufficient for all types of scanners."""

        client.force_login(user_admin)
        response = client.get("/webscanners/" + str(invalid_web_scanner.pk) + "/askrun/")
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
        authentication = Authentication(username="jens")
        authentication.set_password("rigtig heste batteri haefteklamme")
        scanner = FileScanner(
                unc="//ORG/SIKKERSRV",
                organization=test_org,
                authentication=authentication,
                alias="K", rule=basic_rule)

        source_generator = scanner.generate_sources()
        engine2_source = next(source_generator)

        assert engine2_source.driveletter == "K"
