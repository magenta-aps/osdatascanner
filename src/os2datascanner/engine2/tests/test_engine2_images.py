import os.path
import unittest

from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.file import FilesystemSource
from os2datascanner.engine2.conversions import convert
from os2datascanner.engine2.conversions.types import OutputType

here_path = os.path.dirname(__file__)
test_data_path = os.path.join(here_path, "data", "ocr")
expected_size = (896, 896)
expected_result = "131016-9996"


class TestEngine2Images(unittest.TestCase):
    def test_ocr_conversions(self):
        fs = FilesystemSource(os.path.join(test_data_path, "good"))
        with SourceManager() as sm:
            for h in fs.handles(sm):
                resource = h.follow(sm)
                self.assertEqual(
                        convert(resource, OutputType.Text),
                        expected_result,
                        "{0}: content failed".format(h))

    def test_corrupted_ocr(self):
        fs = FilesystemSource(os.path.join(test_data_path, "corrupted"))
        with SourceManager() as sm:
            for h in fs.handles(sm):
                resource = h.follow(sm)
                self.assertEqual(
                        convert(resource, OutputType.Text),
                        None,
                        "{0}: error handling failed".format(h))

    def test_size_computation(self):
        fs = FilesystemSource(test_data_path)
        with SourceManager() as sm:
            for h in fs.handles(sm):
                resource = h.follow(sm)
                size = convert(resource, OutputType.ImageDimensions)
                if size is None:
                    if "rgba32" in h.relative_path:
                        self.skipTest("Pillow RGBA bug detected -- skipping")
                self.assertEqual(
                        size,
                        expected_size,
                        "{0}: size failed")
