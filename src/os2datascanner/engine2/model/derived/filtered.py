import os.path
from abc import abstractmethod
from bz2 import BZ2File
from gzip import GzipFile
from lzma import LZMAFile
from datetime import datetime
from contextlib import contextmanager

from ...conversions.types import OutputType
from ...conversions.utilities.navigable import make_values_navigable
from ..core import Source, Handle, FileResource
from .derived import DerivedSource


class FilteredSource(DerivedSource):
    def __init__(self, handle):
        super().__init__(handle)

    @classmethod
    @abstractmethod
    def _decompress(cls, stream):
        """Returns a Python file-like object that wraps the given compressed
        stream. Reading from this object will return decompressed content."""

    def handles(self, sm):
        rest, ext = os.path.splitext(self.handle.name)
        yield FilteredHandle(self, rest)

    def _generate_state(self, sm):
        yield self.handle.follow(sm)


@Source.mime_handler("application/gzip", "application/x-gzip")
class GzipSource(FilteredSource):
    type_label = "filtered-gzip"

    @classmethod
    def _decompress(cls, stream):
        return GzipFile(fileobj=stream, mode="r")


@Source.mime_handler("application/x-bzip2")
class BZ2Source(FilteredSource):
    type_label = "filtered-bz2"

    @classmethod
    def _decompress(cls, stream):
        return BZ2File(stream, mode="r")


@Source.mime_handler("application/x-xz")
class LZMASource(FilteredSource):
    type_label = "filtered-lzma"

    @classmethod
    def _decompress(cls, stream):
        return LZMAFile(stream, mode="r")


class FilteredResource(FileResource):
    def __init__(self, handle, sm):
        super().__init__(handle, sm)
        self._mr = None

    def check(self) -> bool:
        return self._get_cookie().check()

    def _poke_stream(self, s):
        """Peeks at a single byte from the compressed stream, in the process
        both checking that it's valid and populating header values."""
        s.peek(1)
        return s

    def unpack_stream(self):
        if not self._mr:
            with self.make_stream() as s:
                # Compute the size by seeking to the end of a fresh stream, in
                # the process also populating the last modification date field
                s.seek(0, 2)
                ts = datetime.fromtimestamp(s.mtime)
                self._mr = make_values_navigable(
                        {k: getattr(s, k) for k in ("mtime", "filename")} |
                        {"size": s.tell()} |
                        {OutputType.LastModified: ts})
        return self._mr

    def get_size(self):
        return self.unpack_stream()["size"]

    def get_last_modified(self):
        return self.unpack_stream().setdefault(OutputType.LastModified,
                                               super().get_last_modified())

    @contextmanager
    def make_stream(self):
        with self._get_cookie().make_stream() as s_, \
                self.handle.source._decompress(s_) as s:
            yield self._poke_stream(s)


@Handle.stock_json_handler("filtered")
class FilteredHandle(Handle):
    type_label = "filtered"
    resource_type = FilteredResource

    @property
    def presentation_name(self):
        return self.name

    @property
    def presentation_place(self):
        return str(self.source.handle)

    @property
    def sort_key(self):
        return self.source.handle.sort_key
