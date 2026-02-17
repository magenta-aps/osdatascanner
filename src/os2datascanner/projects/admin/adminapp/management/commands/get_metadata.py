# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Reads metadata from one or more files."""

import os.path

import argparse
from django.core.management.base import BaseCommand

from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.file import FilesystemHandle


def valid_path(path):
    if os.path.exists(path):
        return path
    else:
        raise argparse.ArgumentTypeError(
                "'{0}': No such file or directory".format(path))


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            'FILE',
            type=valid_path,
            nargs='+',
            help='the path to a document to read metadata from',
        )

    def handle(self, **kwargs):
        with SourceManager() as sm:
            for path in kwargs['FILE']:
                r = FilesystemHandle.make_handle(path).follow(sm)
                metadata = r.get_metadata()
                print("{0}: {1}".format(path, metadata))
