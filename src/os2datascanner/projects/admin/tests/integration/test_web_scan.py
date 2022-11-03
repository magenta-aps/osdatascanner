import unittest
from recurrence.base import Recurrence
from os2datascanner.projects.admin.adminapp.models.rules.cprrule import CPRRule
from os2datascanner.projects.admin.adminapp.models.scannerjobs.webscanner import WebScanner

from os2datascanner.projects.admin.organizations.models.organization import Organization
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import ScanStatus


class TestIntegrationWebScan(unittest.TestCase):
    """Integration tests for Webscanner."""

    def setUp(self) -> None:
        self.web_url = "http://nginx"
        self.organization = Organization.objects.first()
        # For cleaning up db models used during testing
        self.scanner_objects = []

    def tearDown(self) -> None:
        for scanner in self.scanner_objects:
            scanner.delete()

    def test_scan_finds_all_sources(self):
        """Tests whether a scan finds all files in a websource."""

        # Arrange
        name = "Test Webscan"
        recurrence = Recurrence()
        webscanner, _ = WebScanner.objects.get_or_create(
            name=name,
            url=self.web_url,
            validation_status=True,
            do_last_modified_check=False,
            organization=self.organization,
            schedule=recurrence,
            download_sitemap=False,
        )

        cpr = CPRRule.objects.first()
        webscanner.rules.set([cpr])
        self.scanner_objects.append(webscanner)

        # Act
        scan_tag = webscanner.run()
        scan_status = ScanStatus.objects.filter(
            scan_tag=scan_tag).first()
        while not scan_status.finished:
            scan_status.refresh_from_db()

        # Assert
        expected_sources = 1
        actual_sources = scan_status.explored_sources
        self.assertEqual(
            actual_sources,
            expected_sources,
            f"Expected sources: {expected_sources}, got: {actual_sources}"
            )

        expected_objects = 21
        actual_objects = scan_status.scanned_objects
        self.assertEqual(
            actual_objects,
            expected_objects,
            f"Expected objects: {expected_objects}, got: {actual_objects}"
            )
