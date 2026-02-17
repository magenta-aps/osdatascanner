# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import os.path
from subprocess import PIPE

from os2datascanner.utils.system_utilities import run_custom


class TestSubprocess:
    def test_tmp_isolation(self):
        """A program run without the isolate_tmp flag can create long-lived
        temporary files, and a program run with it cannot."""
        sp = run_custom(
                ["mktemp"], encoding="ascii", stdout=PIPE)
        temp_path = sp.stdout.strip()
        assert os.path.exists(temp_path)
        os.unlink(temp_path)

        sp = run_custom(
                ["mktemp"], encoding="ascii", stdout=PIPE, isolate_tmp=True)
        temp_path = sp.stdout.strip()
        assert not os.path.exists(temp_path)
