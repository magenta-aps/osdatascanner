import os.path

from os2datascanner.engine2.model.core import Source, SourceManager
from os2datascanner.engine2.model.file import (
        FilesystemSource, FilesystemHandle)
from os2datascanner.engine2.model.derived.zip import ZipHandle, ZipSource


here_path = os.path.dirname(__file__)
test_data_path = os.path.join(here_path, "data", "zip")


class TestZip:
    def test_encrypted_zip(self):
        # Check that all the ZipHandles we get out of an encrypted Zip file
        # actually work. (It's fine if we don't get any, but the ones we *do*
        # need to work!)
        encrypted_file = ZipSource(
                FilesystemHandle(
                        FilesystemSource(test_data_path),
                        "encrypted-test-vector.zip"))
        with SourceManager() as sm:
            for h in encrypted_file.handles(sm):
                h.follow(sm).compute_type()

    def test_infinite_recursion(self):
        endless_file = FilesystemHandle(
                FilesystemSource(test_data_path), "r.zip")

        root_source = ZipSource(endless_file)
        deeply_nested_file = ZipHandle(root_source, "r.zip")
        for _ in range(0, 9):
            deeply_nested_file = ZipHandle(
                    ZipSource(deeply_nested_file), "r.zip")

        # Nine layers of recursion is fine...
        assert Source.from_handle(deeply_nested_file) is not None

        deeply_nested_file = ZipHandle(
                ZipSource(deeply_nested_file), "r.zip")

        # ,,, but ten is too many
        assert Source.from_handle(deeply_nested_file) is None
