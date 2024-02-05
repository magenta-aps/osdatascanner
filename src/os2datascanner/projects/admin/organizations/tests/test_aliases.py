from parameterized import parameterized

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from os2datascanner.projects.admin.organizations.models.aliases import AliasType, Alias
from os2datascanner.projects.admin.organizations.models.account import Account
from os2datascanner.projects.admin.organizations.models.organization import Organization
from os2datascanner.core_organizational_structure.models.aliases import validate_aliastype_value
from os2datascanner.projects.admin.core.models import Client, Administrator


class AliasTypeTest(TestCase):

    def setUp(self) -> None:
        self.test_values = {
            'valid_email': 'test@magenta.dk',
            'invalid_email': "this is not an email",
            'valid_sid': "S-1-5-21-3623811015-3361044348-30300820-1013",
            'invalid_sid': "42",
        }

    def test_member_creation(self):
        for member in AliasType:
            print("Member: »", member)
            self.assertIsInstance(member, AliasType)

    @parameterized.expand([
        ('Valid email', AliasType.EMAIL, 'valid_email'),
        ('Valid SID', AliasType.SID, 'valid_sid'),
        ('Invalid email as Generic', AliasType.GENERIC, 'invalid_email'),
        ('Invalid SID as Generic', AliasType.GENERIC, 'invalid_sid'),
    ])
    def test_validators_pass(self, _, alias_type, value_key):
        value = self.test_values[value_key]
        self.assertIsNone(validate_aliastype_value(alias_type, value))

    @parameterized.expand([
        ('Invalid email', AliasType.EMAIL, 'invalid_email'),
        ('Invalid SID', AliasType.SID, 'invalid_sid'),
    ])
    def test_validators_fail(self, _, alias_type, value_key):
        value = self.test_values[value_key]
        with self.assertRaises(ValidationError):
            validate_aliastype_value(alias_type, value)


class AliasTest(TestCase):
    def setUp(self):
        client = Client.objects.create(name="Olsen Banden")
        olsen_banden = Organization.objects.create(name="Olsen Banden", client=client)
        self.egon = Account.objects.create(username="egon", organization=olsen_banden)
        self.benny = Account.objects.create(username="benny", organization=olsen_banden)

    def test_create_universal_remediator_alias(self):
        """Test that creating a remediator alias for a user will delete all
        other remediator aliases for that user."""
        # Arrange: Create some remediator aliases for Egon
        Alias.objects.create(account=self.egon, _alias_type=AliasType.REMEDIATOR, _value=111)
        Alias.objects.create(account=self.egon, _alias_type=AliasType.REMEDIATOR, _value=222)

        # Act: Create a universal remediator alias for Egon
        Alias.objects.create(account=self.egon, _alias_type=AliasType.REMEDIATOR, _value=0)

        # Assert that only the universal remediator alias exists for Egon
        self.assertEqual(
            self.egon.aliases.filter(
                _alias_type=AliasType.REMEDIATOR).count(),
            1,
            "Found more than one remediator alias for universal remediator!")

    def test_create_remediator_aliases_for_universal_remediator(self):
        """If remediator aliases are created for an account, which is already
        a universal remediator, creating those aliases should throw an
        exception."""
        # Arrange: Make Egon universal remediator
        Alias.objects.create(account=self.egon, _alias_type=AliasType.REMEDIATOR, _value=0)

        # Act and assert that creating new remediator aliases for Egon raises an exception
        self.assertRaises(
            IntegrityError,
            Alias.objects.create,
            account=self.egon,
            _alias_type=AliasType.REMEDIATOR,
            _value=111,
            msg="Creating a remediator alias for a universal remediator does "
                "not raise an exception!")


class AliasViewsTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="baby_sun")
        self.client.force_login(self.user)

        self.tt_client = Client.objects.create(name="Teletubbies")
        self.tt_org = Organization.objects.create(name="Teletubbies", client=self.tt_client)
        self.tinkywinky = Account.objects.create(username="tinkywinky", organization=self.tt_org)

        self.ta_client = Client.objects.create(name="The Avengers")
        self.ta_org = Organization.objects.create(name="The Avengers", client=self.ta_client)
        self.ironman = Account.objects.create(
            username="ironman",
            first_name="Tony",
            organization=self.ta_org)

    def test_add_alias_view_superuser(self):
        """A superuser should be able to add aliases to any account, no matter
        the organization."""

        # Arrange
        self.user.is_superuser = True
        self.user.save()
        url_tinkywinky = reverse_lazy(
            'create-alias',
            kwargs={
                'org_slug': self.tt_org.slug,
                'acc_uuid': self.tinkywinky.uuid})
        url_ironman = reverse_lazy(
            'create-alias',
            kwargs={
                'org_slug': self.ta_org.slug,
                'acc_uuid': self.ironman.uuid})

        # Act
        self.client.post(url_tinkywinky,
                         {'_alias_type': AliasType.GENERIC,
                          '_value': 'teletubby-world.se'})
        self.client.post(url_ironman,
                         {'_alias_type': AliasType.EMAIL,
                          '_value': 'tony@stark.co.uk'})

        # Assert
        self.assertEqual(
            self.tinkywinky.aliases.count(),
            1,
            f"Expected one alias, but found {self.tinkywinky.aliases.count()}")
        self.assertEqual(
            self.tinkywinky.aliases.first()._value,
            'teletubby-world.se',
            f"Expected alias value 'teleubby-world.se' \
                but found '{self.tinkywinky.aliases.first()._value}'")
        self.assertEqual(
            self.ironman.aliases.count(),
            1,
            f"Expected one alias, but found {self.tinkywinky.aliases.count()}")
        self.assertEqual(
            self.ironman.aliases.first()._value,
            'tony@stark.co.uk',
            f"Expected alias value 'tony@stark.co.uk' \
                but found '{self.ironman.aliases.first()._value}'")

    def test_add_alias_client_administrator(self):
        """An administrator for a client should be able to add aliases to
        accounts related to that client."""

        # Arrange
        Administrator.objects.create(user=self.user, client=self.tt_client)
        url_tinkywinky = reverse_lazy(
            'create-alias',
            kwargs={
                'org_slug': self.tt_org.slug,
                'acc_uuid': self.tinkywinky.uuid})

        # Act
        self.client.post(url_tinkywinky,
                         {'_alias_type': AliasType.GENERIC,
                          '_value': 'teletubby-world.se'})

        # Assert
        self.assertEqual(
            self.tinkywinky.aliases.count(),
            1,
            f"Expected one alias, but found {self.tinkywinky.aliases.count()}")
        self.assertEqual(
            self.tinkywinky.aliases.first()._value,
            'teletubby-world.se',
            f"Expected alias value 'teleubby-world.se' \
                but found '{self.tinkywinky.aliases.first()._value}'")

    def test_add_alias_client_foreign_administrator(self):
        """An administrator for a client should not be able to add aliases to
        accounts related to another client."""

        # Arrange
        Administrator.objects.create(user=self.user, client=self.ta_client)
        url_tinkywinky = reverse_lazy(
            'create-alias',
            kwargs={
                'org_slug': self.tt_org.slug,
                'acc_uuid': self.tinkywinky.uuid})

        # Act
        response = self.client.post(
            url_tinkywinky, {
                '_alias_type': AliasType.GENERIC, '_value': 'teletubby-world.se'})

        # Assert
        self.assertEqual(
            response.status_code,
            404,
            f"Expected 404 status code, but got {response.status_code}")

    def test_add_alias_unprivileged_user(self):
        """An unprivileged user should not be able to add aliases."""

        # Arrange
        url_tinkywinky = reverse_lazy(
            'create-alias',
            kwargs={
                'org_slug': self.tt_org.slug,
                'acc_uuid': self.tinkywinky.uuid})

        # Act
        response = self.client.post(
            url_tinkywinky, {
                '_alias_type': AliasType.GENERIC, '_value': 'teletubby-world.se'})

        # Assert
        self.assertEqual(
            response.status_code,
            404,
            f"Expected 404 status code, but got {response.status_code}")

    def test_add_alias_anonymous_user(self):
        """Anonymous users should be redirected to login."""

        # Arrange
        self.client.logout()
        url_tinkywinky = reverse_lazy(
            'create-alias',
            kwargs={
                'org_slug': self.tt_org.slug,
                'acc_uuid': self.tinkywinky.uuid})

        # Act
        response = self.client.post(
            url_tinkywinky, {
                '_alias_type': AliasType.GENERIC, '_value': 'teletubby-world.se'})

        # Assert
        self.assertEqual(
            response.status_code,
            302,
            f"Expected 302 status code, but got {response.status_code}")

    def test_delete_alias_superuser(self):
        """Superusers should be able to delete all aliases."""

        # Arrange
        self.user.is_superuser = True
        self.user.save()
        alias = Alias.objects.create(
            account=self.tinkywinky,
            _alias_type=AliasType.GENERIC,
            _value='teletubby-world.se')
        url = reverse_lazy(
            'delete-alias',
            kwargs={
                'org_slug': self.tt_org.slug,
                'acc_uuid': self.tinkywinky.uuid,
                'pk': alias.uuid})

        # Act
        self.client.post(url)

        # Assert
        self.assertEqual(
            self.tinkywinky.aliases.count(),
            0,
            f"Did not expect any aliases, but found {self.tinkywinky.aliases.count()}")

    def test_delete_alias_client_administrator(self):
        """Administrators for a client should be able to delete aliases for
        accounts related to the same client."""

        # Arrange
        Administrator.objects.create(user=self.user, client=self.tt_client)
        alias = Alias.objects.create(
            account=self.tinkywinky,
            _alias_type=AliasType.GENERIC,
            _value='teletubby-world.se')
        url = reverse_lazy(
            'delete-alias',
            kwargs={
                'org_slug': self.tt_org.slug,
                'acc_uuid': self.tinkywinky.uuid,
                'pk': alias.uuid})

        # Act
        self.client.post(url)

        # Assert
        self.assertEqual(
            self.tinkywinky.aliases.count(),
            0,
            f"Did not expect any aliases, but found {self.tinkywinky.aliases.count()}")

    def test_delete_alias_client_foreign_administrator(self):
        """Administrators for a client should not be able to delete aliases for
        accounts related to another client."""

        # Arrange
        Administrator.objects.create(user=self.user, client=self.ta_client)
        alias = Alias.objects.create(
            account=self.tinkywinky,
            _alias_type=AliasType.GENERIC,
            _value='teletubby-world.se')
        url = reverse_lazy(
            'delete-alias',
            kwargs={
                'org_slug': self.tt_org.slug,
                'acc_uuid': self.tinkywinky.uuid,
                'pk': alias.uuid})

        # Act
        response = self.client.post(url)

        # Assert
        self.assertEqual(
            self.tinkywinky.aliases.count(),
            1,
            f"Axepcted 1 alias, but found {self.tinkywinky.aliases.count()}")
        self.assertEqual(
            response.status_code,
            404,
            f"Expected 404 status code, but got {response.status_code}")

    def test_delete_alias_unprivileged_user(self):
        """Unprivileged users should not be able to delete any aliases."""

        # Arrange
        alias = Alias.objects.create(
            account=self.tinkywinky,
            _alias_type=AliasType.GENERIC,
            _value='teletubby-world.se')
        url = reverse_lazy(
            'delete-alias',
            kwargs={
                'org_slug': self.tt_org.slug,
                'acc_uuid': self.tinkywinky.uuid,
                'pk': alias.uuid})

        # Act
        response = self.client.post(url)

        # Assert
        self.assertEqual(
            self.tinkywinky.aliases.count(),
            1,
            f"Axepcted 1 alias, but found {self.tinkywinky.aliases.count()}")
        self.assertEqual(
            response.status_code,
            404,
            f"Expected 404 status code, but got {response.status_code}")

    def test_delete_alias_anonymous_user(self):
        """Anonymous users should be redirected to login."""

        # Arrange
        self.client.logout()
        alias = Alias.objects.create(
            account=self.tinkywinky,
            _alias_type=AliasType.GENERIC,
            _value='teletubby-world.se')
        url = reverse_lazy(
            'delete-alias',
            kwargs={
                'org_slug': self.tt_org.slug,
                'acc_uuid': self.tinkywinky.uuid,
                'pk': alias.uuid})

        # Act
        response = self.client.post(url)

        # Assert
        self.assertEqual(
            response.status_code,
            302,
            f"Expected 302 status code, but got {response.status_code}")
