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

        cls._ir = image_handle.follow(sm)
        cls._hr = html_handle.follow(sm)
        cls._er = empty_handle.follow(sm)

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
