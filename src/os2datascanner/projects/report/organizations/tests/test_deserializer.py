import pytest

from os2datascanner.core_organizational_structure.utils import get_serializer
from ..models import Alias, Account, Organization


uuid_prefix = b"TEST".hex() + "-" + (b"OK".hex() + "-") * 3


@pytest.mark.django_db
class TestDeserializer:
    def setup_method(cls):
        cls.organization = Organization.objects.create(
            name="Test Organization",
        )

    def test_account_deserializer_creation(self):
        # Arrange...
        ser_class = get_serializer(Account)
        ser = ser_class(
                data=[
                    {
                        "pk": uuid_prefix + "000000000000",
                        "username": "bjkr72795@example.invalid",
                        "first_name": "Bjørn",
                        "last_name": "Kristensen",
                        "organization": self.organization.pk,
                    }
                ], many=True)

        # ... act...
        ser.is_valid(raise_exception=True)
        ser.save()

        # ... and assert
        new_acct = Account.objects.filter(username="bjkr72795@example.invalid")
        assert new_acct.exists()
        assert new_acct.get().first_name == "Bjørn"

    def test_account_deserializer_update(self):
        # Arrange...
        self.test_account_deserializer_creation()

        ser_class = get_serializer(Account)
        ser = ser_class(
                Account.objects.filter(
                        username="bjkr72795@example.invalid"),
                data=[
                    {
                        "pk": uuid_prefix + "000000000000",
                        "username": "bjkr72795@example.invalid",
                        "first_name": "Bjarne",
                        "last_name": "Kristensen",
                        "organization": self.organization.pk,
                    }
                ], many=True)

        # ... act...
        ser.is_valid(raise_exception=True)
        ser.save()

        # ... and assert
        new_acct = Account.objects.filter(username="bjkr72795@example.invalid")
        assert new_acct.get().first_name == "Bjarne"

    def test_account_alias_creation(self):
        # Arrange...
        self.test_account_deserializer_creation()

        ser_class = get_serializer(Alias)
        ser = ser_class(
                data=[
                    {
                        "pk": uuid_prefix + "000000000001",
                        "account": uuid_prefix + "000000000000",
                        "_alias_type": "email",
                        "_value": "bjkr72795@example.invalid",
                    }
                ], many=True)

        # ... act...
        ser.is_valid(raise_exception=True)
        ser.save()

        # ... and assert
        new_alias = Alias.objects.filter(
                account__username="bjkr72795@example.invalid")
        assert new_alias.exists()
        assert new_alias.get().value == "bjkr72795@example.invalid"

    def test_account_alias_update(self):
        # Arrange...
        self.test_account_alias_creation()

        ser_class = get_serializer(Alias)
        ser = ser_class(
                Alias.objects.filter(
                        _value="bjkr72795@example.invalid"),
                data=[
                    {
                        "pk": uuid_prefix + "000000000001",
                        "account": uuid_prefix + "000000000000",
                        "_alias_type": "email",
                        "_value": "bjkr72795@example.test",
                    }
                ], many=True)

        # ... act...
        ser.is_valid(raise_exception=True)
        ser.save()

        # ... and assert
        new_alias = Alias.objects.filter(
                account__username="bjkr72795@example.invalid")
        assert new_alias.get().value == "bjkr72795@example.test"
