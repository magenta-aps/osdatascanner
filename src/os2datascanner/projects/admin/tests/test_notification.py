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
