import pytest

from os2datascanner.projects.admin.adminapp.models.scannerjobs.webscanner import WebScanner
from os2datascanner.projects.admin.adminapp.models.scannerjobs.exchangescanner \
    import ExchangeScanner
from os2datascanner.projects.admin.adminapp.models.scannerjobs.filescanner import FileScanner


@pytest.mark.django_db
class TestScannerValidation:

    def test_filescanner_needs_revalidation(self, basic_rule):
        fs = FileScanner.objects.create(unc="//path/to/the/drive", rule=basic_rule)
        fs.unc = "//path/of/another/drive"
        assert fs.needs_revalidation

    def test_webscanner_needs_revalidation(self, basic_rule):
        ws = WebScanner.objects.create(url="https://www.example.com", rule=basic_rule)
        ws.url = "https://www.example.org"
        assert ws.needs_revalidation

    def test_exchangescanner_needs_revalidation(self, basic_rule):
        es = ExchangeScanner.objects.create(mail_domain="@webs.example", rule=basic_rule)
        es.mail_domain = "@example.invalid"
        assert es.needs_revalidation
