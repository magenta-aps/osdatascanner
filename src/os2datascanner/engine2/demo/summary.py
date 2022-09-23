#!/usr/bin/env python3

import sys
from math import ceil
from typing import Sequence, NamedTuple
import bisect
import statistics
import json

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

    def buckets(self, max_buckets=4):
        for bucket in buckets(self.sizes, max_buckets):
            yield TypeInfo(self.mime, bucket)

    def get_stats(self):
        sizes = self.sizes
        count = self.count
        return self.mime, count, sum(sizes), int(
            statistics.mean(sizes)), int(
            statistics.median(sizes)), min(sizes), max(sizes)


def flatapp(f, *args):
    try:
        return f(v for v in args if v is not None)
    except ValueError:
        return None


def main(argv, breakpoint=None):
    sm = SourceManager()
    for url in argv:
        type_infos = {}
        source_total = 0

        try:
            source = Source.from_url(url)
        except Exception:
            continue

        for n, handle in enumerate(source.handles(sm)):
            if breakpoint and n >= int(breakpoint):
                break
            source_total += 1

            file = handle.name

            if "." not in file:
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

        sorted_infos = sorted(
                (t for t in type_infos.values() if t.count >= 50),
                key=lambda i: i.count)
        data_list = []
        names = ["type", "n_files", "total_size", "mean", "median", "min", "max"]
        for info in sorted_infos:
            print(info)
            stats = info.get_stats()
            data = {names[i]: stats[i] for i in range(len(names))}
            buckets = []
            for n, bucket in enumerate(info.buckets()):
                bucket_stats = bucket.get_stats()
                bucket_dict = {names[i]: bucket_stats[i] for i in range(len(names))}
                bucket_dict["name"] = f'bucket_{n+1}'
                buckets.append(bucket_dict)
                print(f"\t{bucket}")
            data["buckets"] = buckets
            data_list.append(data)

        with open(f"data_{url}.json", "w") as f:
            json.dumps(data_list, f)
        print(f"File with data from {url} saved")


if __name__ == "__main__":
    args = sys.argv[1:]
    main([args[0]], *args[1:])
