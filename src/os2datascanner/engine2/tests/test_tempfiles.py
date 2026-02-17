# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import os.path

from os2datascanner.engine2.model.utilities import NamedTemporaryResource


class TestEngine2TempfilesTest:
    def test(self):
        test_string = "T e s t\ns t r i n g."
        with NamedTemporaryResource("test.txt") as ntr:
            path = ntr.get_path()
            directory = os.path.basename(path)
            assert not os.path.exists(path), f"temp file {path} shouldn't exist yet"
            with ntr.open("wt") as fp:
                fp.write(test_string)
            assert os.path.exists(path), f"temp file {path} was not created"
            with open(path, "rt") as fp:
                content = fp.read()
                assert content == test_string, f"temp file content '{content}' is incorrect"
        assert not os.path.exists(path), f"temp file {path} wasn't cleaned up"
        assert not os.path.exists(directory), f"temp directory {0} wasn't cleaned up"
