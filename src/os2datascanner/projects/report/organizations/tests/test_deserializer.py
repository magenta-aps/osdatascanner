import pytest

from os2datascanner.core_organizational_structure.utils import get_serializer
from ..models import Alias, Account, Organization, OrganizationalUnit

uuid_prefix = b"TEST".hex() + "-" + (b"OK".hex() + "-") * 3


@pytest.mark.django_db
class TestDeserializer:
    def setup_method(cls):
        cls.organization = Organization.objects.create(
            name="Test Organization",
        )
        cls.alonso = Account.objects.create(pk=uuid_prefix + "000000000001",
                                            username="Alonso@example.invalid",
                                            first_name="Alonso",
                                            last_name="Buggie",
                                            organization=cls.organization)
        cls.ou_02 = OrganizationalUnit.objects.create(
            pk=uuid_prefix + "000000000002",
            name="OU_02",
            organization=cls.organization
        )
        cls.ou_03 = OrganizationalUnit.objects.create(
            pk=uuid_prefix + "000000000003",
            name="OU_03",
            organization=cls.organization
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

    def test_account_deserializer_bulk_update(self):
        # TODO: mimics event_collector should  refactor to actually use event_message_received_raw
        # Arrange...
        self.test_account_deserializer_creation()
        ser_class = get_serializer(Account)
        pk_list = []

        data = [
            {
                "pk": uuid_prefix + "000000000000",
                "username": "bjkr72795@example.invalid",
                "first_name": "Bjørn",
                "last_name": "Kristensen",
                "organization": self.organization.pk,
                "manager": None,
                "is_superuser": False,
            },
            {
                "pk": uuid_prefix + "000000000001",
                "username": "Alonso@example.invalid",
                "first_name": "Alfredo",
                "last_name": "Buggie",
                "organization": self.organization.pk,
                "manager": None,
                "is_superuser": False,
            },

        ]
        for obj in data:
            pk_list.append(obj.get("pk"))
        ser_objs = ser_class(Account.objects.filter(pk__in=pk_list), data=data, many=True)

        # Act
        ser_objs.is_valid(raise_exception=True)
        ser_objs.save()

        # Assert
        assert Account.objects.get(pk=uuid_prefix + "000000000000").first_name == "Bjørn"
        assert Account.objects.get(pk=uuid_prefix + "000000000001").first_name == "Alfredo"

    def test_ou_deserializer_bulk_update(self):
        # TODO: mimics event_collector should  refactor to actually use event_message_received_raw
        # Arrange
        ser_class = get_serializer(OrganizationalUnit)
        pk_list = []

        data = [
            {
                "pk": uuid_prefix + "000000000002",
                "organization": self.organization.pk,
                "name": "Titanic",
                "parent": None,
                "lft": 0,
                "rght": 0,
                "tree_id": 1,
                "level": 0
            },
            {
                "pk": uuid_prefix + "000000000003",
                "organization": self.organization.pk,
                "name": "Iceberg",
                "parent": None,
                "lft": 0,
                "rght": 0,
                "tree_id": 1,
                "level": 0
            },
        ]
        for obj in data:
            pk_list.append(obj.get("pk"))
        ser_objs = ser_class(
            OrganizationalUnit.objects.filter(pk__in=pk_list), data=data, many=True)

        # Act
        ser_objs.is_valid(raise_exception=True)
        ser_objs.save()

        # Assert
        assert OrganizationalUnit.objects.get(pk=uuid_prefix + "000000000002").name == "Titanic"
        assert OrganizationalUnit.objects.get(pk=uuid_prefix + "000000000003").name == "Iceberg"

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
