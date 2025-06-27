import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse_lazy

from os2datascanner.projects.admin.organizations.models.aliases import AliasType, Alias
from os2datascanner.projects.admin.organizations.models.account import Account
from os2datascanner.core_organizational_structure.models.aliases import validate_aliastype_value


@pytest.mark.django_db
class TestAliasBehaviour:

    def test_member_creation(self):
        for member in AliasType:
            assert isinstance(member, AliasType)

    @pytest.mark.parametrize("_, alias_type, value_key", [
        ('Valid email', AliasType.EMAIL, 'valid_email'),
        ('Valid SID', AliasType.SID, 'valid_sid'),
        ('Invalid email as Generic', AliasType.GENERIC, 'invalid_email'),
        ('Invalid SID as Generic', AliasType.GENERIC, 'invalid_sid'),
    ])
    def test_validators_pass(self, _, alias_type, value_key):
        test_values = {
            'valid_email': 'test@magenta.dk',
            'invalid_email': "this is not an email",
            'valid_sid': "S-1-5-21-3623811015-3361044348-30300820-1013",
            'invalid_sid': "42",
        }
        value = test_values[value_key]
        assert validate_aliastype_value(alias_type, value) is None

    @pytest.mark.parametrize("_, alias_type, value_key", [
        ('Invalid email', AliasType.EMAIL, 'invalid_email'),
        ('Invalid SID', AliasType.SID, 'invalid_sid'),
    ])
    def test_validators_fail(self, _, alias_type, value_key):
        test_values = {
            'invalid_email': "this is not an email",
            'invalid_sid': "42",
        }
        value = test_values[value_key]
        with pytest.raises(ValidationError):
            validate_aliastype_value(alias_type, value)

    def test_create_universal_remediator_alias(self, egon):
        """Test that creating a remediator alias for a user will delete all
        other remediator aliases for that user."""

        # Arrange: Create some remediator aliases for Egon
        Alias.objects.create(account=egon, _alias_type=AliasType.REMEDIATOR, _value=111)
        Alias.objects.create(account=egon, _alias_type=AliasType.REMEDIATOR, _value=222)

        # Act: Create a universal remediator alias for Egon
        Alias.objects.create(account=egon, _alias_type=AliasType.REMEDIATOR, _value=0)

        # Assert that only the universal remediator alias exists for Egon
        assert egon.aliases.filter(_alias_type=AliasType.REMEDIATOR).count() == 1

    def test_create_remediator_aliases_for_universal_remediator(self, egon):
        """If remediator aliases are created for an account, which is already
        a universal remediator, creating those aliases should throw an
        exception."""

        # Arrange: Make Egon universal remediator
        Alias.objects.create(account=egon, _alias_type=AliasType.REMEDIATOR, _value=0)

        # Act and assert that creating new remediator aliases for Egon raises an exception
        with pytest.raises(IntegrityError):
            Alias.objects.create(account=egon, _alias_type=AliasType.REMEDIATOR, _value=111)

    def test_add_alias_view_superuser(self, superuser, client, egon, gertrud):
        """A superuser should be able to add aliases to any account, no matter
        the organization."""

        # Arrange
        client.force_login(superuser)

        url1 = reverse_lazy('create-alias', kwargs={'org_slug':
                                                    egon.organization.slug, 'acc_uuid': egon.uuid})
        url2 = reverse_lazy(
            'create-alias',
            kwargs={
                'org_slug': gertrud.organization.slug,
                'acc_uuid': gertrud.uuid})
        # Act
        client.post(url1, {'_alias_type': AliasType.GENERIC, '_value': 'teletubby-world.se'})
        client.post(url2, {'_alias_type': AliasType.EMAIL, '_value': 'tony@stark.co.uk'})

        # Assert
        assert not egon.organization == gertrud.organization
        assert egon.aliases.count() == 1
        assert egon.aliases.first()._value == 'teletubby-world.se'
        assert gertrud.aliases.count() == 1
        assert gertrud.aliases.first()._value == 'tony@stark.co.uk'

    def test_add_alias_client_administrator(self, client, user_admin):
        """An administrator for a client should be able to add aliases to
        accounts related to that client."""
        client.force_login(user_admin)

        # Arrange
        tinkywinky = Account.objects.create(
            username="tinkywinky",
            organization=user_admin.administrator_for.client.organizations.first())

        url = reverse_lazy(
            'create-alias',
            kwargs={
                'org_slug': user_admin.administrator_for.client.organizations.first().slug,
                'acc_uuid': tinkywinky.uuid})

        # Act
        client.post(url, {'_alias_type': AliasType.GENERIC, '_value': 'teletubby-world.se'})

        # Assert
        assert tinkywinky.aliases.count() == 1
        assert tinkywinky.aliases.first()._value == 'teletubby-world.se'

    def test_add_alias_client_foreign_administrator(
            self, user_admin, client, other_org, other_client):
        """An administrator for a client should not be able to add aliases to
        accounts related to another client."""

        # Arrange
        client.force_login(user_admin)
        tinkywinky = Account.objects.create(username="tinkywinky", organization=other_org)
        url = reverse_lazy('create-alias', kwargs={'org_slug': other_org.slug,
                                                   'acc_uuid': tinkywinky.uuid})

        # Act
        response = client.post(url, {'_alias_type': AliasType.GENERIC,
                                     '_value': 'teletubby-world.se'})

        assert response.status_code == 404

    def test_add_alias_unprivileged_user(self, user, client, gertrud):
        """An unprivileged user should not be able to add aliases."""
        # Arrange
        client.force_login(user)

        url = reverse_lazy('create-alias', kwargs={'org_slug': gertrud.organization.slug,
                                                   'acc_uuid': gertrud.uuid})

        # Act
        response = client.post(url, {'_alias_type': AliasType.GENERIC,
                                     '_value': 'teletubby-world.se'})

        assert response.status_code == 404

    def test_add_alias_anonymous_user(self, client, test_org):
        """Anonymous users should be redirected to login."""

        # Arrange
        tinkywinky = Account.objects.create(username="tinkywinky", organization=test_org)

        url = reverse_lazy('create-alias', kwargs={'org_slug': test_org.slug,
                                                   'acc_uuid': tinkywinky.uuid})

        # Act
        response = client.post(url, {'_alias_type': AliasType.GENERIC,
                                     '_value': 'teletubby-world.se'})

        assert response.status_code == 302

    def test_delete_alias_superuser(self, superuser, client, gertrud):
        """Superusers should be able to delete all aliases."""

        # Arrange
        client.force_login(superuser)

        alias = Alias.objects.create(account=gertrud, _alias_type=AliasType.GENERIC,
                                     _value='teletubby-world.se')

        url = reverse_lazy('delete-alias', kwargs={'org_slug': gertrud.organization.slug,
                                                   'acc_uuid': gertrud.uuid, 'pk': alias.uuid})

        # Act
        client.post(url)

        # Assert
        assert gertrud.aliases.count() == 0

    def test_delete_alias_client_administrator(self, user_admin, client, test_org, gertrud):
        """Administrators for a client should be able to delete aliases for
        accounts related to the same client."""

        # Arrange
        client.force_login(user_admin)

        alias = Alias.objects.create(
            account=gertrud,
            _alias_type=AliasType.GENERIC,
            _value='teletubby-world.se')
        url = reverse_lazy(
            'delete-alias',
            kwargs={
                'org_slug': gertrud.organization.slug,
                'acc_uuid': gertrud.uuid,
                'pk': alias.uuid})

        # Act
        client.post(url)

        # Assert
        assert gertrud.aliases.count() == 0

    def test_delete_alias_client_foreign_administrator(
            self, user_admin, client, other_org, other_client):
        """Administrators for a client should not be able to delete aliases for
        accounts related to another client."""

        # Arrange
        client.force_login(user_admin)

        tinkywinky = Account.objects.create(username="tinkywinky", organization=other_org)

        alias = Alias.objects.create(account=tinkywinky, _alias_type=AliasType.GENERIC,
                                     _value='teletubby-world.se')

        url = reverse_lazy('delete-alias', kwargs={'org_slug': tinkywinky.organization.slug,
                                                   'acc_uuid': tinkywinky.uuid, 'pk': alias.uuid})

        # Act
        response = client.post(url)

        # Assert
        assert tinkywinky.aliases.count() == 1
        assert response.status_code == 404

    def test_delete_alias_unprivileged_user(self, user, client, gertrud):
        """Unprivileged users should not be able to delete any aliases."""

        # Arrange
        client.force_login(user)

        alias = Alias.objects.create(account=gertrud, _alias_type=AliasType.GENERIC,
                                     _value='teletubby-world.se')
        url = reverse_lazy('delete-alias', kwargs={'org_slug': gertrud.organization.slug,
                                                   'acc_uuid': gertrud.uuid, 'pk': alias.uuid})
        # Act
        response = client.post(url)

        # Assert
        assert gertrud.aliases.count() == 1, "Expected 1 alias"
        assert response.status_code == 404

    def test_delete_alias_anonymous_user(self, client, gertrud):
        """Anonymous users should be redirected to login."""

        # Arrange
        alias = Alias.objects.create(account=gertrud, _alias_type=AliasType.GENERIC,
                                     _value='teletubby-world.se')

        url = reverse_lazy('delete-alias', kwargs={'org_slug': gertrud.organization.slug,
                                                   'acc_uuid': gertrud.uuid, 'pk': alias.uuid})
        # Act
        response = client.post(url)

        # Assert
        assert response.status_code == 302
