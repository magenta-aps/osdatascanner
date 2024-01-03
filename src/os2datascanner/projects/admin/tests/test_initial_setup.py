import pytest

from django.core.management import call_command
from django.contrib.auth.models import User

from ..core.models.client import Client
from ..organizations.models.organization import Organization
from ..organizations.models.account import Account


@pytest.mark.django_db
class TestInitialSetup:

    @classmethod
    def call_command(self, *args, **kwargs):
        call_command(
            "initial_setup",
            *args,
            **kwargs,
        )

    def test_atomicity(self):
        # Arrange
        User.objects.create(username="duplicate")

        # Act
        try:
            self.call_command(client_name="unique", org_name="unique", username="duplicate")
        except BaseException:
            pass

        # Assert
        with pytest.raises(Client.DoesNotExist):
            Client.objects.get(name="unique")
        with pytest.raises(Organization.DoesNotExist):
            Organization.objects.get(name="unique")
        assert User.objects.get(username="duplicate")

    def test_client_created(self):
        self.call_command(client_name="client")

        assert Client.objects.get(name="client")

    def test_client_contact_info(self):
        self.call_command(client_name="client", email="test@example.net", phone="12345678")

        client = Client.objects.get(name="client")
        assert client.contact_email == "test@example.net"
        assert client.contact_phone == "12345678"

    def test_org_created(self):
        self.call_command(org_name="org")

        assert Organization.objects.get(name="org")

    def test_user_account_created(self):
        self.call_command(username="user")

        assert User.objects.get(username="user")
        assert Account.objects.get(username="user")

    def test_user_is_super(self):
        self.call_command(username="user")

        user = User.objects.get(username="user")
        assert user.is_superuser

    def test_user_is_staff(self):
        self.call_command(username="user")

        user = User.objects.get(username="user")
        assert user.is_staff

    def test_all_arguments(self):
        try:
            self.call_command(client_name="client", org_name="org", email="test@example.net",
                              phone="12345678", password="swordfish", username="user")
        except BaseException:
            pytest.fail("Unexpected Error")
