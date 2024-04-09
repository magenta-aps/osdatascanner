import pytest
from django.contrib.auth.models import User

from os2datascanner.projects.report.organizations.models import (Account, Alias,
                                                                 Organization, OrganizationalUnit,
                                                                 Position)

from ..management.commands.event_collector import event_message_received_raw


@pytest.mark.django_db
class TestEventCollector:

    @pytest.fixture(autouse=True)
    def setup_fixture(self, create_message):
        with pytest.raises(StopIteration):
            # This function is a generator, so we need to treat it like one.
            next(event_message_received_raw(create_message))

    # CREATE #

    def test_event_collector_create_account(self, create_message_account_body):
        # Arrange/Act is performed through the fixtures.
        for account in create_message_account_body:
            # Assert: filters for every obj, unpacking all their expected params.
            assert Account.objects.filter(**account).exists() is True

            # Assert: We have to remember the User
            assert User.objects.filter(
                username=account.get("username"),
                first_name=account.get("first_name"),
                last_name=account.get("last_name"),
            ).exists() is True

    def test_event_collector_create_alias(self, create_message_alias_body):
        # Arrange/Act is performed through the fixtures.
        for alias in create_message_alias_body:
            # Assert: filters for every obj, unpacking all their expected params.
            assert Alias.objects.filter(**alias).exists() is True

    def test_event_collector_create_org(self, create_message_org_body):
        # Arrange/Act is performed through the fixtures.
        for org in create_message_org_body:
            # Assert: filters for every obj, unpacking all their expected params.
            assert Organization.objects.filter(**org).exists() is True

    def test_event_collector_create_ou(self, create_message_ou_body):
        # Arrange/Act is performed through the fixtures.
        for ou in create_message_ou_body:
            assert OrganizationalUnit.objects.filter(**ou).exists() is True

    def test_event_collector_create_position(self, create_message_position_body):
        # Arrange/Act is performed through the fixtures.
        for position in create_message_position_body:
            # Assert: filters for every obj, unpacking all their expected params.
            assert Position.objects.filter(**position).exists() is True

    # UPDATE #

    def test_event_collector_update_in_order(
            self, update_message_in_order, update_message_account_body_in_order,
            update_message_alias_body_in_order, update_message_ou_body_in_order,
            update_message_position_body_in_order, update_message_org_body_in_order):

        # Arrange is performed through the fixtures.

        # Act
        with pytest.raises(StopIteration):
            next(event_message_received_raw(update_message_in_order))

        # Assert
        for account in update_message_account_body_in_order:
            # Assert: filters for every obj, unpacking all their expected params.
            assert Account.objects.filter(**account).exists() is True
            # Assert: We have to remember the User
            assert User.objects.filter(
                username=account.get("username"),
                first_name=account.get("first_name"),
                last_name=account.get("last_name"),
            ).exists() is True

        for alias in update_message_alias_body_in_order:
            # Assert: filters for every obj, unpacking all their expected params.
            assert Alias.objects.filter(**alias).exists() is True

        for org in update_message_org_body_in_order:
            # Assert: filters for every obj, unpacking all their expected params.
            assert Organization.objects.filter(**org).exists() is True

        for ou in update_message_ou_body_in_order:
            assert OrganizationalUnit.objects.filter(**ou).exists() is True

        for position in update_message_position_body_in_order:
            # Assert: filters for every obj, unpacking all their expected params.
            assert Position.objects.filter(**position).exists() is True

    def test_event_collector_update_not_in_order(
            self, update_message_not_in_order, update_message_account_body_not_in_order,
            update_message_alias_body_not_in_order, update_message_ou_body_not_in_order,
            update_message_position_body_not_in_order, update_message_org_body_not_in_order):

        # Arrange; Via fixture

        # Act
        with pytest.raises(StopIteration):
            next(event_message_received_raw(update_message_not_in_order))

        # Assert
        for account in update_message_account_body_not_in_order:
            # Assert: filters for every obj, unpacking all their expected params.
            assert Account.objects.filter(**account).exists() is True
            assert User.objects.filter(
                username=account.get("username"),
                first_name=account.get("first_name"),
                last_name=account.get("last_name"),
            ).exists() is True

        for alias in update_message_alias_body_not_in_order:
            # Assert: filters for every obj, unpacking all their expected params.
            assert Alias.objects.filter(**alias).exists() is True

        for org in update_message_org_body_not_in_order:
            # Assert: filters for every obj, unpacking all their expected params.
            assert Organization.objects.filter(**org).exists() is True

        for ou in update_message_ou_body_not_in_order:
            assert OrganizationalUnit.objects.filter(**ou).exists() is True

        for position in update_message_position_body_not_in_order:
            # Assert: filters for every obj, unpacking all their expected params.
            assert Position.objects.filter(**position).exists() is True
