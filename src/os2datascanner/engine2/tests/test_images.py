import pytest
import os.path

from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.file import FilesystemSource
from os2datascanner.engine2.conversions import convert
from os2datascanner.engine2.conversions.types import OutputType

here_path = os.path.dirname(__file__)
test_data_path = os.path.join(here_path, "data", "ocr")
expected_size = (896, 896)
expected_result = "131016-9996"


class TestEngine2Images:
    def test_ocr_conversions(self):
        fs = FilesystemSource(os.path.join(test_data_path, "good"))
        with SourceManager() as sm:
            for h in fs.handles(sm):
                resource = h.follow(sm)
                assert convert(resource, OutputType.Text) == expected_result

    def test_corrupted_ocr(self):
        fs = FilesystemSource(os.path.join(test_data_path, "corrupted"))
        with SourceManager() as sm:
            for h in fs.handles(sm):
                resource = h.follow(sm)
                assert convert(resource, OutputType.Text) is None

    @pytest.mark.parametrize("test_data_path, expected_size", [
        (os.path.join(test_data_path, "good"), expected_size),
        (os.path.join(test_data_path, "corrupted"), expected_size),
        (os.path.join(test_data_path, "large"), (4000, 4000)),
    ])
    def test_size_computation(self, test_data_path, expected_size):
        fs = FilesystemSource(test_data_path)
        with SourceManager() as sm:
            for h in fs.handles(sm):
                resource = h.follow(sm)
                size = convert(resource, OutputType.ImageDimensions)
                if size is None:
                    if "rgba32" in h.relative_path:
                        # Pillow RGBA bug detected -- skipping
                        continue
                assert size == expected_size

    def test_downscaling_conversions(self):
        """ Tests images larger than 2000x2000 (which will be downscaled) still
            produce expected result. """
        fs = FilesystemSource(os.path.join(test_data_path, "large"))
        with SourceManager() as sm:
            for h in fs.handles(sm):
                resource = h.follow(sm)
                assert convert(resource, OutputType.Text) == expected_result
