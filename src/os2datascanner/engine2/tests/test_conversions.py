# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest
import os.path

from os2datascanner.engine2.conversions.abort import current_abort_check
from os2datascanner.engine2.conversions.text.ocr import image_processor, tesseract_pymupdf
from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.file import FilesystemHandle
from os2datascanner.engine2.conversions.types import OutputType
from os2datascanner.engine2.conversions.registry import convert


class TestEngine2Conversion:
    @classmethod
    def setup_method(cls):
        sm = SourceManager()

        here_path = os.path.dirname(__file__)
        image_handle = FilesystemHandle.make_handle(
            os.path.join(here_path, "data/ocr/good/cpr.png")
        )
        html_handle = FilesystemHandle.make_handle(
            os.path.join(here_path, "data/html/simple.html")
        )
        empty_handle = FilesystemHandle.make_handle(
            os.path.join(here_path, "data/empty_file")
        )
        html_handle_w_style_and_scripts = FilesystemHandle.make_handle(
            os.path.join(here_path, "data/html/script_and_style_in_body.html")
        )

        cls._ir = image_handle.follow(sm)
        cls._hr = html_handle.follow(sm)
        cls._er = empty_handle.follow(sm)
        cls._hr_w_style_and_scripts = html_handle_w_style_and_scripts.follow(sm)

    def test_last_modified_image_handle_not_none(self):
        # Arrange -> setup_method

        # Act
        converted = convert(self._ir, OutputType.LastModified)

        # Assert
        assert converted is not None

    def test_image_dimensions(self):
        # Arrange -> setup_method

        # Act
        converted = convert(self._ir, OutputType.ImageDimensions)

        # Assert
        assert converted == (896, 896)

    def test_fallback(self):
        # Arrange -> setup_method

        # Act
        converted = convert(self._ir, OutputType.AlwaysTrue)

        # Assert
        assert converted

    def test_dummy(self):
        with pytest.raises(KeyError):
            convert(self._ir, OutputType.NoConversions)

    def test_html(self):
        # Arrange -> setup_method

        # Act
        converted = convert(self._hr, OutputType.Text)

        # Assert
        assert converted == ("\n"
                             "        \n"
                             "            This is only a test."
                             "\n"
                             "        "
                             "\n"
                             "\n            "
                             "\n                "
                             "There's one paragraph,"
                             "\n                "
                             "and then there's the other"
                             "\n                "
                             "paragraph."
                             "\n        "
                             "\n"
                             "\n "
                             "\n"
                             "    ")

    def test_empty_html(self):
        # Arrange -> setup_method

        # Act
        converted = convert(self._er, OutputType.Text, mime_override="text/html")

        # Assert
        assert converted is None

    def test_html_with_script_and_styles_in_body(self):
        converted = convert(self._hr_w_style_and_scripts, OutputType.Text,
                            mime_override="text/html")

        # Should be there
        assert "Welcome to the Test Page" in converted
        assert "I'm a red paragraph" in converted
        assert "Another paragraph that remains" in converted

        # Shouldn't be there
        assert "script" not in converted  # script tag
        assert ".highlight" not in converted  # style tag
        assert "template tag" not in converted  # template tag
        assert "JavaScript is disabled" not in converted  # noscript tag


class TestAbortableOCR:
    def test_tesseract_pymupdf_returns_none_when_aborted_before_start(self, monkeypatch):
        """tesseract_pymupdf() must return None without touching the image bytes
        when the abort check fires. But since it currently catches exceptions and returns None,
        monkeypatch it to raise SystemExit here for test purposes."""
        def _no_pixmap(*a, **kw):
            raise SystemExit("Pixmap should not be constructed when aborting")
        monkeypatch.setattr(
            "os2datascanner.engine2.conversions.text.ocr.pymupdf.Pixmap",
            _no_pixmap)

        token = current_abort_check.set(lambda: True)
        try:
            result = tesseract_pymupdf(b"anything", filetype="png")
            assert result is None
        finally:
            current_abort_check.reset(token)

    def test_image_processor_returns_none_when_aborted(self):
        """image_processor() must return None without reading the stream when
        the abort check is set.

        This is when cancellation happens just before the image is passed to tesseract.
        """
        token = current_abort_check.set(lambda: True)
        try:
            class _NeverReadResource:
                handle = type("handle", (), {"name": "test.png"})()

                def make_stream(self):
                    raise AssertionError("make_stream should not be called on abort")

            result = image_processor(_NeverReadResource())
            assert result is None
        finally:
            current_abort_check.reset(token)
