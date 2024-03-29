from os import rmdir, remove
import os.path
from tempfile import mkdtemp
from contextlib import suppress


class NamedTemporaryResource:
    def __init__(self, name):
        self._name = name
        self._dir = None

    def open(self, mode):
        return open(self.get_path(), mode)

    def size(self):
        return os.path.getsize(self.get_path())

    def get_path(self) -> str:
        if self._dir is None:
            self._dir = mkdtemp()
        return os.path.join(self._dir, self._name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, backtrace):
        if self._dir:
            with suppress(FileNotFoundError):
                remove(self.get_path())
            with suppress(FileNotFoundError):
                rmdir(self._dir)
            self._dir = None
