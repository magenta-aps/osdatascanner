import pytest
from django.contrib.auth import get_user_model
from django.http import Http404

from ...core.models.client import Client
from ...core.models.administrator import Administrator
from ..models.account import Account
from ..models.organization import Organization, replace_nordics
from ..utils import prepare_and_publish, user_allowed


@pytest.mark.django_db
class TestReplaceSpecialCharacters:
    @pytest.mark.parametrize("input_str,expected", [
        ("tæstcåsø", "t&aelig;stc&aring;s&oslash;"),
        ("Næstved", "N&aelig;stved"),
        ("Torben", "Torben"),
        ("bLaNdInG", "bLaNdInG"),
        ("BlÆnDiNg", "Bl&AElig;nDiNg"),
        ("HÅR", "H&Aring;R"),
        ("SØVAND", "S&Oslash;VAND")
    ])
    def test_nordics_are_replaced(self, input_str, expected):
        replaced_string = replace_nordics(input_str)
        assert replaced_string == expected


@pytest.mark.django_db
class TestImportHelper:

    def test_prepare_and_publish_scope(self, test_org, gertrud):
        """Importing a new Account into an Organization does not delete that
        Organization's manually-created Accounts."""
        jens = Account(
            username="jt",
            first_name="Jens",
            last_name="Testsen",
            organization=test_org,
            imported=True,
            imported_id="jt@orgone.test"
        )

        prepare_and_publish(
            test_org,
            {"jt@orgone.test"},
            to_add=[jens],
            to_delete=[],
            to_update=[]
        )

        gertrud.refresh_from_db()
        assert gertrud.pk is not None, "manually-created Account was erroneously deleted"

    def test_prepare_and_publish_isolation(self, gertrud, other_org):
        """Importing a new Account into an Organization should have no effect
        on other Organizations."""

        jens = Account(
            username="jt",
            first_name="Jens",
            last_name="Testsen",
            organization=other_org,
            imported=True,
            imported_id="jt@orgtwo.test"
        )

        prepare_and_publish(
            other_org,
            {"jt@orgtwo.test"},
            to_add=[jens],
            to_delete=[],
            to_update=[]
        )

        gertrud.refresh_from_db()
        assert gertrud.pk is not None, "manually-created Account was erroneously deleted"


@pytest.mark.django_db
class TestUserAllowedUtil:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.user = get_user_model().objects.create(username="glados")
        self.client = Client.objects.create(name="Big Important Client")
        self.org = Organization.objects.create(name="Aperture Science", client=self.client)

    def test_client_admin_is_allowed(self, admin_user, test_org):
        """The 'user_allowed'-function should return True if the user is an
        admin for the client."""
        Administrator.objects.create(user=self.user, client=self.client)
        _, allowed = user_allowed(admin_user, test_org.slug)
        assert allowed, "Client administrator was not allowed access to client's organization!"

    def test_superuser_is_allowed(self, superuser, test_org):
        """The 'user_allowed'-function should return True if the user is a
        superuser."""
        _, allowed = user_allowed(superuser, test_org.slug)
        assert allowed, "Superuser was not allowed access to client's organization!"

    def test_unprivileged_user_is_not_allowed(self, user, test_org):
        """The 'user_allowed'-function should return False if the user is
        neither an admin for the client nor a superuser"""
        _, allowed = user_allowed(user, test_org.slug)
        assert not allowed, "Unprivileged user was allowed access to an organization!"

    def test_anonymous_user_is_not_allowed(self, anonymous_user, test_org):
        """The 'user_allowed'-function should return False if the user is
        neither an admin for the client nor a superuser"""
        _, allowed = user_allowed(anonymous_user, test_org.slug)
        assert not allowed, "Anonymous user was allowed access to an organization!"

    def test_user_allowed_function_returns_organization(self, user, test_org):
        """The 'user_allowed'-function should return the organization object
        for the given slug."""
        org, _ = user_allowed(user, test_org.slug)
        assert org == test_org, "'user_allowed'-function did not return the correct Organization!"

    def test_user_allowed_function_raises_404_on_incorrect_slug(self, user, test_org):
        """The 'user_allowed'-function should raise a 404 exception if given
        a fake slug."""
        fake_slug = f"fake{test_org.slug}fake"
        with pytest.raises(Http404):
            user_allowed(user, fake_slug)
