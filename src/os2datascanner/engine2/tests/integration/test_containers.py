import os.path
from datetime import datetime
import unittest

from os2datascanner.engine2.commands.utils import DemoSourceUtility as TestSourceUtility
from os2datascanner.engine2.model.core import (Source, SourceManager)
from os2datascanner.engine2.model.file import (
        FilesystemSource, FilesystemHandle)
from os2datascanner.engine2.model.data import DataSource
from os2datascanner.engine2.model.smbc import SMBCSource


here_path = os.path.dirname(__file__)
test_data_path = os.path.join(here_path, "..", "data", "engine2")


class Engine2ContainerTest(unittest.TestCase):
    def setUp(self) -> None:
        with open(os.path.join(test_data_path, "test-vector"), "rt") as fp:
            self.correct_content = fp.read()

    def process(self, source, sm, depth=0):
        if depth == 0:
            self.assertIsNone(
                    source.handle,
                    "{0}: unexpected backing handle".format(source))
        for handle in source.handles(sm):
            print("{0}{1}".format("  " * depth, handle))
            guessed = Source.from_handle(handle)
            computed = Source.from_handle(handle, sm)

            if computed or guessed:
                self.process(computed or guessed, sm, depth + 1)

            elif handle.name == "url":
                with handle.follow(sm).make_stream() as fp:
                    url = fp.read().decode("utf-8")
                self.process(TestSourceUtility.from_url(url), sm, depth + 1)

            elif handle.name == "test-vector" or isinstance(
                    source, DataSource):
                r = handle.follow(sm)

                self.assertTrue(
                        r.check(),
                        "check() method failed")
                reported_size = r.get_size()
                last_modified = r.get_last_modified()

                with r.make_stream() as fp:
                    stream_raw = fp.read()
                    stream_size = len(stream_raw)
                    stream_content = stream_raw.decode("utf-8")
                with r.make_path() as p, open(p, "rb") as fp:
                    file_raw = fp.read()
                    file_size = len(file_raw)
                    file_content = file_raw.decode("utf-8")

                self.assertIsInstance(
                        last_modified,
                        datetime,
                        ("{0}: last modification date value is not a"
                         "datetime.datetime").format(handle))

                self.assertEqual(
                        stream_size,
                        reported_size,
                        "{0}: model stream length invalid".format(
                                handle))
                self.assertEqual(
                        file_size,
                        reported_size,
                        "{0}: model stream length invalid".format(
                                handle))
                self.assertEqual(
                        file_raw,
                        stream_raw,
                        "{0}: model file and stream not equal".format(
                                handle))
                self.assertEqual(
                        stream_content,
                        self.correct_content,
                        "{0}: model stream invalid".format(handle))
                self.assertEqual(
                        file_content,
                        self.correct_content,
                        "{0}: model file invalid".format(handle))

    def test_local_url(self):
        with SourceManager() as sm:
            self.process(TestSourceUtility.from_url(
                "file://" + test_data_path), sm)

    def test_smbc_url(self):
        with SourceManager() as sm:
            source = TestSourceUtility.from_url(
                    "smbc://os2:swordfish@samba/general")
            self.process(source, sm)

    def test_smbc_snapshot_exclusion(self):
        with SourceManager() as sm:
            source = SMBCSource(
                    "//samba/general/backup",
                    "os2", "swordfish",
                    skip_super_hidden=False)
            self.assertEqual(
                    [k.relative_path for k in source.handles(sm)],
                    ["~snapshot/test-vector-hidden"],
                    "unskipped file not found")

            source._skip_super_hidden = True
            self.assertEqual(
                    [k.relative_path for k in source.handles(sm)],
                    [],
                    "skipped file unexpectedly found")

    def test_derived_source(self):
        with SourceManager():
            s = FilesystemSource(test_data_path)
            h = FilesystemHandle(s, "data/engine2/zip-here/test-vector.zip")

            zs = Source.from_handle(h)
            self.assertIsNotNone(
                    zs.handle,
                    "{0}: derived source has no handle".format(zs))
