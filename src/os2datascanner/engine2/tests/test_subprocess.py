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
