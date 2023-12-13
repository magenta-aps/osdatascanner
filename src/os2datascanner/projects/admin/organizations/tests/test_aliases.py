from parameterized import parameterized

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.db import IntegrityError

from os2datascanner.projects.admin.organizations.models.aliases import AliasType, Alias
from os2datascanner.projects.admin.organizations.models.account import Account
from os2datascanner.projects.admin.organizations.models.organization import Organization
from os2datascanner.core_organizational_structure.models.aliases import validate_aliastype_value
from os2datascanner.projects.admin.core.models.client import Client


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
        # Create some remediator aliases for Egon and Benny
        Alias.objects.create(account=self.egon, _alias_type=AliasType.REMEDIATOR, _value=111)
        Alias.objects.create(account=self.egon, _alias_type=AliasType.REMEDIATOR, _value=222)
        benny_alias1 = Alias(account=self.benny, _alias_type=AliasType.REMEDIATOR, _value=333)
        benny_alias2 = Alias(account=self.benny, _alias_type=AliasType.REMEDIATOR, _value=444)
        benny_alias1.save()
        benny_alias2.save()

        # Create a universal remediator alias for Egon
        Alias.objects.create(account=self.egon, _alias_type=AliasType.REMEDIATOR, _value=0)

        # Assert that only the universal remediator alias exists for Egon, and
        # that Benny still has both his aliases
        self.assertEqual(
            self.egon.aliases.filter(
                _alias_type=AliasType.REMEDIATOR).count(),
            1,
            "Found more than one remediator alias for universal remediator!")
        self.assertEqual(self.egon.aliases.filter(_alias_type=AliasType.REMEDIATOR).first(
        )._value, '0', "Non-zero value on remediator alias for universal remediator!")
        self.assertEqual(self.benny.aliases.filter(_alias_type=AliasType.REMEDIATOR).count(
        ), 2, "Found a wrong number of remediator aliases for regular remediator!")
        self.assertIn(benny_alias1, self.benny.aliases.all(),
                      "Remediator alias missing from account!")
        self.assertIn(benny_alias2, self.benny.aliases.all(),
                      "Remediator alias missing from account!")

    def test_create_remediator_aliases_for_universal_remediator(self):
        """If remediator aliases are created for an account, which is already
        a universal remediator, creating those aliases should throw an
        exception."""
        # Make Egon universal remediator
        egon_uni_alias = Alias(account=self.egon, _alias_type=AliasType.REMEDIATOR, _value=0)
        egon_uni_alias.save()

        # Assert that creating new remediator aliases for Egon raises an exception
        self.assertRaises(
            IntegrityError,
            Alias.objects.create,
            account=self.egon,
            _alias_type=AliasType.REMEDIATOR,
            _value=111,
            msg="Creating a remediator alias for a universal remediator does "
                "not raise an exception!")
