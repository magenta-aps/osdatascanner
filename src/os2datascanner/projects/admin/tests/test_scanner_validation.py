from .test_utilities import dummy_rule_dict
from os2datascanner.projects.admin.adminapp.models.rules import CustomRule
from django.test import TestCase

from os2datascanner.projects.admin.adminapp.models import scannerjobs
WebScanner = scannerjobs.webscanner.WebScanner
FileScanner = scannerjobs.filescanner.FileScanner
ExchangeScanner = scannerjobs.exchangescanner.ExchangeScanner


class ScannerValidationTest(TestCase):
    def setUp(self):
        self.rule = CustomRule.objects.create(**dummy_rule_dict)

    def tearDown(self):
        scannerjobs.scanner.Scanner.objects.all().delete()
        self.rule.delete()

    def test_filescanner_needs_revalidation(self):
        fs = FileScanner.objects.create(unc="//path/to/the/drive", rule=self.rule)
        fs.unc = "//path/of/another/drive"
        self.assertTrue(
                fs.needs_revalidation,
                "change in unc did not invalidate FileScanner")

    def test_webscanner_needs_revalidation(self):
        ws = WebScanner.objects.create(url="https://www.example.com", rule=self.rule)
        ws.url = "https://www.example.org"
        self.assertTrue(
                ws.needs_revalidation,
                "change in url did not invalidate FileScanner")

    def test_exchangescanner_needs_revalidation(self):
        es = ExchangeScanner.objects.create(mail_domain="@webs.example", rule=self.rule)
        es.mail_domain = "@example.invalid"
        self.assertTrue(
                es.needs_revalidation,
                "change in mail domain did not invalidate ExchangeScanner")
