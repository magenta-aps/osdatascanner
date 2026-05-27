# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from django.contrib.auth.models import User

from ..adminapp.notification import (
    FinishedScannerNotificationEmail, InvalidScannerNotificationEmail)


@pytest.fixture
def ronald_mcdonald():
    return User.objects.create(username="mcd",
                               first_name="Ronald",
                               last_name="McDonald",
                               email="ronald@mcdonalds.com")


@pytest.fixture
def dr_pepper():
    return User.objects.create(username="p.md",
                               first_name="Dr.",
                               last_name="Pepper",
                               email="the_doctor@pepper.com")


@pytest.fixture
def tony_the_tiger():
    """Tony the Tiger does not use email like some old person!"""
    return User.objects.create(username="grrrrrrrrrrreat",
                               first_name="Tony",
                               last_name="The Tiger")


@pytest.mark.django_db
class TestFinishedScannerNotificationEmail:

    def test_get_users(self, basic_scanner, basic_scanstatus_completed, ronald_mcdonald, dr_pepper,
                       tony_the_tiger):
        basic_scanner.contacts.set([ronald_mcdonald, dr_pepper, tony_the_tiger])

        users = FinishedScannerNotificationEmail(basic_scanner, basic_scanstatus_completed
                                                 ).get_users()

        # Only users with an email should be returned by the method
        assert set(users) == set(basic_scanner.contacts.exclude(email=""))

    def test_get_users_no_contacts(self, basic_scanner, basic_scanstatus_completed):
        users = FinishedScannerNotificationEmail(basic_scanner, basic_scanstatus_completed
                                                 ).get_users()

        assert list(users) == []

    def test_create_context_zero_bytes_flag_true(
            self, basic_scanner, basic_scanstatus_completed, ronald_mcdonald):
        """zero_bytes is True when objects were scanned but scanned_size is 0."""
        # basic_scanstatus_completed has total_objects=1, scanned_size=0 (default)
        context = FinishedScannerNotificationEmail(
            basic_scanner, basic_scanstatus_completed).create_context(ronald_mcdonald)

        assert context["zero_bytes"] is True

    def test_create_context_zero_bytes_flag_false(
            self, basic_scanner, basic_scanstatus_completed, ronald_mcdonald):
        """zero_bytes is False when scanned_size is greater than 0."""
        basic_scanstatus_completed.scanned_size = 1024
        context = FinishedScannerNotificationEmail(
            basic_scanner, basic_scanstatus_completed).create_context(ronald_mcdonald)

        assert context["zero_bytes"] is False


@pytest.mark.django_db
class TestInvalidScannerNotificationEmail:

    def test_get_users(self, basic_scanner, ronald_mcdonald, dr_pepper, tony_the_tiger):
        basic_scanner.contacts.set([ronald_mcdonald, dr_pepper, tony_the_tiger])

        users = InvalidScannerNotificationEmail(basic_scanner).get_users()

        # Only users with an email should be returned by the method
        assert set(users) == set(basic_scanner.contacts.exclude(email=""))

    def test_get_users_no_contacts(self, basic_scanner):
        users = InvalidScannerNotificationEmail(basic_scanner).get_users()

        assert list(users) == []
