from django.test import TestCase
from parameterized import parameterized
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import Http404

from ...core.models.client import Client
from ...core.models.administrator import Administrator
from ..models.account import Account
from ..models.organization import Organization, replace_nordics

from ..utils import prepare_and_publish, user_allowed


class ReplaceSpecialCharactersTest(TestCase):
    @parameterized.expand([
        ("tæstcåsø", "t&aelig;stc&aring;s&oslash;"),
        ("Næstved", "N&aelig;stved"),
        ("Torben", "Torben"),
        ("bLaNdInG", "bLaNdInG"),
        ("BlÆnDiNg", "Bl&AElig;nDiNg"),
        ("HÅR", "H&Aring;R"),
        ("SØVAND", "S&Oslash;VAND")
    ])
    def test_nordics_are_replaced(self, input, expected):
        """
        A string containing 'æ', 'ø' and/or 'å' will have those
        instances replaced according to
        https://www.thesauruslex.com/typo/eng/enghtml.htm
        """
        replaced_string = replace_nordics(input)
        self.assertEqual(replaced_string, expected)


class ImportHelperTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.client = Client.objects.create(
                name="Common Client")
        cls.org1 = Organization.objects.create(
                client=cls.client,
                name="Org One")
        cls.org2 = Organization.objects.create(
                client=cls.client,
                name="Org Two")

    def setUp(self):
        self.mikkel = Account.objects.create(
                username="mt@orgone.test",
                first_name="Mikkel", last_name="Testsen",
                organization=self.org1)

    def test_prepare_and_publish_scope(self):
        """Importing a new Account into an Organization does not delete that
        Organization's manually-created Accounts."""

        jens = Account(
                username="jt",
                first_name="Jens", last_name="Testsen",
                organization=self.org1,

                imported=True,
                imported_id="jt@orgone.test")

        prepare_and_publish(
                self.org1,
                {"jt@orgone.test"},
                to_add=[jens],
                to_delete=[],
                to_update=[])

        self.mikkel.refresh_from_db()
        self.assertIsNotNone(
                self.mikkel.pk,
                "manually-created Account was erroneously deleted")

    def test_prepare_and_publish_isolation(self):
        """Importing a new Account into an Organization should have no effect
        on other Organizations."""

        jens = Account(
                username="jt",
                first_name="Jens", last_name="Testsen",
                organization=self.org2,

                imported=True,
                imported_id="jt@orgtwo.test")

        prepare_and_publish(
                self.org2,
                {"jt@orgtwo.test"},
                to_add=[jens],
                to_delete=[],
                to_update=[])

        self.mikkel.refresh_from_db()
        self.assertIsNotNone(
                self.mikkel.pk,
                "manually-created Account was erroneously deleted")


class UserAllowedUtilTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = get_user_model().objects.create(username="glados")
        # Create a client and an organization
        self.client = Client.objects.create(name="Big Important Client")
        self.org = Organization.objects.create(name="Aperture Science", client=self.client)

    def test_client_admin_is_allowed(self):
        """The 'user_allowed'-function should return True if the user is an
        admin for the client."""
        # Arrange: Make the user admin for the client
        Administrator.objects.create(user=self.user, client=self.client)

        # Act: Call the 'user_allowed'-function
        _, allowed = user_allowed(self.user, self.org.slug)

        # Assert that the user is allowed
        self.assertTrue(
            allowed,
            "Client administrator was not allowed access to client's organization!")

    def test_superuser_is_allowed(self):
        """The 'user_allowed'-function should return True if the user is a
        superuser."""
        # Arrange: Make the user a superuser
        self.user.is_superuser = True
        self.user.save()

        # Act: Call the 'user_allowed'-function
        _, allowed = user_allowed(self.user, self.org.slug)

        # Assert that the user is allowed
        self.assertTrue(allowed, "Superuser was not allowed access to client's organization!")

    def test_unprivileged_user_is_not_allowed(self):
        """The 'user_allowed'-function should return False if the user is
        neither an admin for the client or a superuser"""
        # Arrange: Everything is arranged -- the user has no privileges

        # Act: Call the 'user_allowed'-function
        _, allowed = user_allowed(self.user, self.org.slug)

        # Assert that the user is allowed
        self.assertFalse(allowed, "Unprivileged user was allowed access to an organization!")

    def test_anonymous_user_is_not_allowed(self):
        """The 'user_allowed'-function should return False if the user is
        neither an admin for the client or a superuser"""
        # Arrange: Initialize anonymous user
        anon_user = AnonymousUser()

        # Act: Call the 'user_allowed'-function
        _, allowed = user_allowed(anon_user, self.org.slug)

        # Assert that the user is allowed
        self.assertFalse(allowed, "Anonymous user was allowed access to an organization!")

    def test_user_allowed_function_returns_organization(self):
        """The 'user_allowed'-function should return the organization object
        for the given slug."""
        # Arrange: Nothing to arrange

        # Act: Call the 'user_allowed'-function with a real slug
        org, _ = user_allowed(self.user, self.org.slug)

        # Assert that the returned org is correct
        self.assertEqual(
            org,
            self.org,
            "'user_allowed'-function did not return the correct Organization!")

    def test_user_allowed_function_raises_404_on_incorrect_slug(self):
        """The 'user_allowed'-function should raise a 404 exception if given
        a fake slug."""
        # Arrange: Make a fake slug
        fake_slug = f"fake{self.org.slug}fake"

        # Act and Assert: The 'user_allowed'-function should raise an exception
        # when given a fake slug
        self.assertRaises(Http404, user_allowed, self.user, fake_slug)
