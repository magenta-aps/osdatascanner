# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import os.path

from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.data import DataHandle, DataSource
from os2datascanner.engine2.model.file import (
        FilesystemHandle, FilesystemSource)
from os2datascanner.engine2.model.http import (WebHandle, WebSource)
from os2datascanner.engine2.model.derived.pdf import (
        PDFPageHandle, PDFPageResource, PDFObjectHandle)
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

    def test_pdf_metadata_does_not_preprocess_the_document(self):
        """Reading a page's metadata must not call the pre-processed copy of the
        document into being.

        Producing it is a subprocess call over the whole document, and a page
        whose matches were replayed from an identical document elsewhere reaches
        this code having never been converted here -- so the pre-processing would
        be minutes of work for one string that is the same either way."""
        # Arrange
        handle = PDFPageHandle.make(
                FilesystemHandle(test_data, "pdf/embedded-cpr.pdf"), 1)

        # Act
        with SourceManager() as sm:
            handle.follow(sm).get_metadata()

            # Assert
            assert handle.source not in sm, (
                    "reading page metadata pre-processed the whole document")

    def test_pdf_metadata_from_a_source_with_no_local_path(self):
        """The metadata has to be readable from any kind of source, not just the
        ones that happen to sit on a local disk.

        pymupdf opens a path or a bytes-like object, and nothing else -- but when
        it is handed a file object it quietly falls back to that object's .name.
        A local file's stream has one and a remote file's does not, so reading a
        stream works on a developer's laptop and fails against a real file
        share. DataSource stands in for the remote case here: its stream is a
        BytesIO, which has no .name either."""
        # Arrange
        with SourceManager() as sm:
            with FilesystemHandle(
                    test_data,
                    "pdf/embedded-cpr.pdf").follow(sm).make_stream() as fp:
                content = fp.read()

        handle = PDFPageHandle.make(
                DataHandle(
                        DataSource(content, "application/pdf"),
                        "embedded-cpr.pdf"),
                1)

        # Act
        with SourceManager() as sm:
            metadata = handle.follow(sm).get_metadata()

        # Assert
        assert metadata["pdf-author"] == "Alexander John Faithfull"

    def test_pdf_metadata_is_the_same_either_way(self):
        """The premise of the above: the DocInfo dictionary survives
        ez_save(clean=True) unchanged, so reading it from the original file and
        from the pre-processed copy give the same answer. If that ever stops
        being true, the two paths diverge and this fails."""
        # Arrange
        handle = PDFPageHandle.make(
                FilesystemHandle(test_data, "pdf/embedded-cpr.pdf"), 1)

        # Act
        with SourceManager() as sm:
            from_original = handle.follow(sm).get_metadata()

        with SourceManager() as sm:
            # Opening the derived source is what pre-processes the document, so
            # this is the state a page has just after being converted here.
            sm.open(handle.source)
            from_preprocessed = handle.follow(sm).get_metadata()

        # Assert
        assert from_original == from_preprocessed
        assert from_original["pdf-author"] == "Alexander John Faithfull"

    def test_pdf_metadata_reads_an_original_out_of_process(self, monkeypatch):
        """An original document must not be handed to pymupdf in this process.

        MuPDF answers some malformed documents with SIGSEGV rather than an
        exception, which would take the stage down in the middle of a message
        and leave that message to be redelivered. Sabotaging the in-process
        reader is what makes the difference observable: the author still comes
        back, so it was not read here."""
        # Arrange
        def explode(path):
            raise AssertionError("an original was opened in this process")

        monkeypatch.setattr(
                PDFPageResource, "_read_author", staticmethod(explode))

        handle = PDFPageHandle.make(
                FilesystemHandle(test_data, "pdf/embedded-cpr.pdf"), 1)

        # Act
        with SourceManager() as sm:
            metadata = handle.follow(sm).get_metadata()

        # Assert
        assert metadata["pdf-author"] == "Alexander John Faithfull"

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
