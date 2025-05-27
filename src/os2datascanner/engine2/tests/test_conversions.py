import pytest
import os.path

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
