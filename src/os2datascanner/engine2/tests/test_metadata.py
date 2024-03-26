import os.path

from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.file import (
        FilesystemHandle, FilesystemSource)
from os2datascanner.engine2.model.http import (WebHandle, WebSource)
from os2datascanner.engine2.model.derived.pdf import (
        PDFPageHandle, PDFObjectHandle)
from os2datascanner.engine2.model.derived.libreoffice import (
        LibreOfficeSource, LibreOfficeObjectHandle)


test_data = FilesystemSource(os.path.join(os.path.dirname(__file__), "data"))


class TestMetadata:
    def test_odt_extraction(self):
        # Arrange
        handle = LibreOfficeObjectHandle(
                LibreOfficeSource(
                        FilesystemHandle(
                                test_data, "libreoffice/embedded-cpr.odt")),
                "embedded-cpr.html")
        # Act
        with SourceManager() as sm:
            metadata = handle.follow(sm).get_metadata()

        assert metadata["od-creator"] == "Alexander John Faithfull"

    def test_pdf_extraction(self):
        # Arrange
        handle = PDFObjectHandle.make(
                FilesystemHandle(test_data, "pdf/embedded-cpr.pdf"),
                1, "page.txt")
        # Act
        with SourceManager() as sm:
            metadata = handle.follow(sm).get_metadata()

        # Assert
        assert metadata["pdf-author"] == "Alexander John Faithfull"

    def test_weird_pdf_metadata(self):
        """Null bytes in PDF metadata should be automatically removed."""
        # Arrange
        handle = PDFPageHandle.make(
                FilesystemHandle(test_data, "pdf/null-byte-in-author.pdf"), 1)
        # Act
        with SourceManager() as sm:
            metadata = handle.follow(sm).get_metadata()

        # Assert
        assert metadata["pdf-author"] == "Alexander John Faithfull"

    def test_no_author_pdf_metadata(self):
        # Arrange
        handle = PDFPageHandle.make(
            FilesystemHandle(test_data, "pdf/null-byte-no-author.pdf"), 1)

        # Act/Assert
        with SourceManager() as sm:
            assert len([v for k, v in handle.follow(sm)._generate_metadata()]) == 0

    def test_web_domain_extraction(self, monkeypatch):
        # TODO: Should probably be generalized soon (also done in test_errors.py)
        monkeypatch.setattr(
            "os2datascanner.engine2.utilities.backoff.ExponentialBackoffRetrier._compute_delay", 0)

        # Arrange/Act
        with SourceManager() as sm:
            metadata = WebHandle(
                    WebSource("https://www.example.invalid./"),
                    "/cgi-bin/test.pl").follow(sm).get_metadata()
        # Assert
        assert metadata.get("web-domain") == "www.example.invalid."
