import sys
import hashlib

from os2datascanner.engine2.model.core import (
        Handle, Source, Resource, SourceManager)
from .utils import DemoSourceUtility


def get_hash(r: Resource, algo=hashlib.md5):
    with r.make_stream() as fp:
        checksum = algo(fp.read())
    return checksum.hexdigest()


def make_duplicate_map(s: Source, sm: SourceManager):
    hashes = {}
    for handle in s.handles(sm):
        try:
            content_hash = get_hash(handle.follow(sm))
        except Exception:
            print("***", handle)
            continue
        hashes.setdefault(content_hash, []).append(handle)
    return hashes


def main(app_name, *urls):
    sm = SourceManager()

    for url in urls:
        s = DemoSourceUtility.from_url(url)
        hm = make_duplicate_map(s, sm)

        unique_files = len(hm)
        total_files = 0
        for paths in hm.values():
            total_files += len(paths)
            if len(paths) == 1: 
                continue
            head, *tail = paths
            print(f"{head} ({len(tail)} duplicate(s))")
            for t in tail:
                print(f"\t{t}")

        print(f"{total_files} total files, of which {unique_files} unique.")
        print("--")


if __name__ == "__main__":
    main(*sys.argv)
