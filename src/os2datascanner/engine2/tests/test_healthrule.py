# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from os2datascanner.engine2.rules.experimental.health_rule import (
        TurboHealthRule)


class TestTurboHealthRule:
    def test_health_term_in_content(self):
        """
        A basic unit test to make sure that TurboHealthRule finds
        the same matches as the new OrderedWordListRule would with
        the same dataset.
        """
        # Arrange
        rule = TurboHealthRule()
        content = "Cancer er en grim sygdom."
        expected = ["cancer", "sygdom"]

        # Act
        actual = list(rule.match(content))

        # Assert
        assert len(actual) == len(expected)
        for i, m in enumerate(actual):
            assert m["match"] == expected[i]
