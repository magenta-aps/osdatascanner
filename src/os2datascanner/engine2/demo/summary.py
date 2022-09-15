#!/usr/bin/env python3

import sys
from math import ceil
from typing import Sequence, NamedTuple
import bisect
import statistics

from os2datascanner.engine2.model.core import Source, SourceManager

def buckets(sequence, max_buckets=10):
    per_bucket = ceil(len(sequence) / max_buckets)
    while sequence:
        yield sequence[:per_bucket]
        sequence = sequence[per_bucket:]


class TypeInfo(NamedTuple):
    mime: str  # media type (str)
    sizes: Sequence[int]  # bytes

    @property
    def count(self):
        return len(self.sizes)

    def __str__(self):
        sizes = self.sizes
        count = self.count

        return (f"{self.mime}\t{count}\t"
                f"{sum(sizes)}\t{int(statistics.mean(sizes))}\t"
                f"{int(statistics.median(sizes))}\t"
                f"{min(sizes)}\t{max(sizes)}")

    def buckets(self, max_buckets=10):
        for bucket in buckets(self.sizes, max_buckets):
            yield TypeInfo(self.mime, bucket)


def flatapp(f, *args):
    try:
        return f(v for v in args if v is not None)
    except ValueError:
        return None


def main(argv):
    sm = SourceManager()
    for url in argv:
        type_infos = {}
        source_total = 0

        try:
            source = Source.from_url(url)
        except Exception:
            continue

        print(source)
        for handle in source.handles(sm):
            source_total += 1

            file = handle.name

            if not "." in file:
                continue

            try:
                size = handle.follow(sm).get_size()
            except OSError:
                continue

            mime = handle.guess_type()
            if mime == "application/octet-stream":
                continue

            info = type_infos.setdefault(mime,
                    TypeInfo(mime=mime, sizes=[]))
            bisect.insort(info.sizes, size)

        print(source_total)

        sorted_infos = sorted(
                (t for t in type_infos.values() if t.count >= 50),
                key=lambda i: i.count)

        for info in sorted_infos:
            print(info)
            for bucket in info.buckets():
                print(f"\t{bucket}")


if __name__ == "__main__":
    main(sys.argv[1:])
