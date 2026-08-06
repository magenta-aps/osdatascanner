# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import unittest
from unittest.mock import Mock
from parameterized import parameterized

from os2datascanner.engine2.pipeline.utilities.filtering import is_handle_relevant
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.engine2.rules.presentation import PresentationRule
from os2datascanner.engine2.rules.meta import SizeRule
from os2datascanner.engine2.model.file import FilesystemHandle, FilesystemSource


class FilteringRuleTests(unittest.TestCase):
    """
    Tests for the Filtering/Exclusion-rule concept.

    The point of these unittests is not to test the accuracy of
    the underlying engine rule used (we have other tests for that).
    """

    def setUp(self):
        self.rule = PresentationRule(RegexRule('PRIVAT'))

    def test_handle_with_private_matches(self):
        # Arrange
        mock_handle = Mock()
        mock_handle.__str__ = Mock(return_value='C://bruger/dokumenter/PRIVAT/hemmelig.txt')
        mock_handle.hint = Mock(return_value=None)

        # Act
        actual = is_handle_relevant(mock_handle, self.rule)

        # Assert
        self.assertFalse(actual)
        mock_handle.__str__.assert_called()

    def test_handle_without_private_does_not_match(self):
        # Arrange
        mock_handle = Mock()
        mock_handle.__str__ = Mock(return_value='C://bruger/dokumenter/offentlig/griseri.txt')
        mock_handle.hint = Mock(return_value=None)

        # Act
        actual = is_handle_relevant(mock_handle, self.rule)

        # Assert
        self.assertTrue(actual)
        mock_handle.__str__.assert_called()

    def test_failing_check_is_relevant_and_logs(self):
        # Arrange
        mock_handle = Mock()
        mock_handle.__str__ = Mock(return_value='C://bruger/dokumenter/offentlig/griseri.txt')
        mock_handle.hint = Mock(return_value=None)

        mock_rule = Mock()
        mock_rule.try_match = Mock(side_effect=KeyError('BOOM!'))

        # Act
        actual = is_handle_relevant(mock_handle, self.rule)

        # Assert
        self.assertTrue(actual)
        mock_handle.__str__.assert_called()

    @parameterized.expand([
        ('5', 8, True),
        ('5', 3, False),
        (5, 8, True),
        (5, 3, False),
        ("five", 8, True),
        ("five", 3, True),
    ])
    def test_size_hint(self, size_hint, size_limit, expected):
        # Arrange
        source = FilesystemSource("/mnt/fs01.magenta.dk/brugere/af")
        handle = FilesystemHandle(
            source,
            "OS2datascanner/Dokumenter/Verdensherredømme - plan.txt"
        )
        handle._hints = {"size": size_hint}

        rule = SizeRule(size_limit)

        # Act
        actual = is_handle_relevant(handle, rule)

        # Assert
        self.assertEqual(actual, expected)
