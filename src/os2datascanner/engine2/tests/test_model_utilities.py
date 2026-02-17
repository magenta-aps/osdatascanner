# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from os2datascanner.engine2.model.core.utilities import takes_named_arg


class TestModelUtilities:
    def test_positional_arg_success(self):
        # Arrange

        def dummyfunc(par_zero, par_one, par_two, par_three):
            pass

        # Assert
        assert takes_named_arg(dummyfunc, "par_two")

    def test_positional_arg_failure(self):
        # Arrange

        def dummyfunc(par_zero, par_one, par_two, par_three):
            pass

        # Assert
        assert not takes_named_arg(dummyfunc, "par_four")

    def test_keyword_arg_success(self):
        # Arrange

        def dummyfunc(par_zero, par_one, *, par_two, par_three):
            pass

        # Assert
        assert takes_named_arg(dummyfunc, "par_two")

    def test_hybrid_arg_success(self):
        # Arrange

        def dummyfunc(par_zero, par_one, *, par_two, par_three):
            pass

        # Assert
        assert takes_named_arg(dummyfunc, "par_one")

    def test_wildcard_arg_success(self):
        # Arrange

        def dummyfunc(par_zero, par_one, par_two, **kwargs):
            pass

        # Assert
        for par in ("par_zero", "par_one", "par_two", "par_three"):
            assert takes_named_arg(dummyfunc, par)
