import pytest
import contextlib

from os2datascanner.engine2.model.core import Source, SourceManager
from os2datascanner.engine2.model.file import FilesystemSource
from os2datascanner.engine2.commands.utils import DemoSourceUtility as TestSourceUtility


class TestEngine2Errors:
    def test_relative_filesystemsource(self):
        with pytest.raises(ValueError):
            FilesystemSource("../../projects/admin/tests/data/")

    def test_double_mime_registration(self):
        with pytest.raises(ValueError):
            @Source.mime_handler("application/zip")
            class Dummy:
                pass

    def test_handles_failure(self, monkeypatch):
        # This might be slightly convoluted, but WebSource's 'handles' method goes through
        # WebRetrier -> ExponentialBackOffRetrier and computes sleeping time.
        # The above makes this test take incredibly long, which isn't the purpose here.
        # Perhaps this isn't the prettiest way to circumvent the issue, but it does the job for now
        monkeypatch.setattr(
            "os2datascanner.engine2.utilities.backoff.ExponentialBackoffRetrier._compute_delay", 0)

        with pytest.raises(Exception) as e, SourceManager() as sm:
            source = TestSourceUtility.from_url("http://example.invalid./")
            with contextlib.closing(source.handles(sm)) as handles:
                next(handles)
        if e:
            print(f"got expected exception for {TestSourceUtility.to_url(source)}\n{e}")
