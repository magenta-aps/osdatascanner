import pytest
from io import StringIO

from django.core.management import call_command
from django.contrib.auth.models import User
from django.conf import settings

from ..core.models.client import Client
from ..organizations.models.organization import Organization
from ..organizations.models.account import Account
from ..adminapp.models.rules import CustomRule


@pytest.mark.django_db
class TestInitialSetup:

    @classmethod
    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "initial_setup",
            *args,
            stderr=StringIO(),
            stdout=out,
            **kwargs,
        )

        return out.getvalue()

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
        """Check that a client is created, and that it contains the default field values."""

        # Act
        self.call_command()
        client = Client.objects.first()

        # Assert
        assert client.name == settings.NOTIFICATION_INSTITUTION
        assert client.contact_email == ''
        assert client.contact_phone == ''

    def test_client_contact_info(self):
        self.call_command(client_name="client", email="test@example.net", phone="12345678")

        client = Client.objects.get(name="client")
        assert client.contact_email == "test@example.net"
        assert client.contact_phone == "12345678"

    def test_duplicate_client(self, test_client):
        """When attempting to create a client with a duplicate name, exit gracefully."""

        self.call_command(client_name=test_client.name)

        assert Client.objects.count() == 1

    def test_org_created(self):
        """Check that an organization is created, and that it contains the default field values."""
        # Act
        self.call_command()
        org = Organization.objects.first()

        # Assert
        assert org.name == settings.NOTIFICATION_INSTITUTION
        assert org.contact_email is None
        assert org.contact_phone is None

    def test_user_account_created(self):
        # Act
        self.call_command()
        user = User.objects.first()
        account = Account.objects.first()

        # Assert
        assert user.username == "os"
        assert user.check_password("setup")
        assert account.username == "os"

    def test_user_is_super(self):
        self.call_command(username="user")

        user = User.objects.get(username="user")
        assert user.is_superuser

    def test_user_is_staff(self):
        self.call_command(username="user")

        user = User.objects.get(username="user")
        assert user.is_staff

    def test_account_is_super(self):
        self.call_command(username="account")

        account = Account.objects.get(username="account")
        assert account.is_superuser

    def test_all_arguments(self):
        try:
            self.call_command(client_name="client", org_name="org", email="test@example.net",
                              phone="12345678", password="swordfish", username="user")
        except BaseException:
            pytest.fail("Unexpected Error")

    def test_warning_on_default_password(self):
        """When creating a user with a default password, display a warning."""

        stdout = self.call_command()

        assert "Default password used. CHANGE THIS IMMEDIATELY" in stdout

    def test_cpr_rule_org_is_set(self):
        """When creating cprrule, test whether it's associated with the correct organization."""

        # Act
        self.call_command()
        rule = CustomRule.objects.get(name="CPR regel")

        # Assert
        assert rule.organizations.get() == Organization.objects.get(name="DUMMY")
