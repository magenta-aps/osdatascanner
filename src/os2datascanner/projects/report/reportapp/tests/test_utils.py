import pytest
from django.db import IntegrityError

from ...organizations.models import Organization, Account, Alias, AliasType
from ..utils import get_or_create_user_aliases


@pytest.fixture(scope="class")
def saml_user_data():
    user_data = {
        'email': ['sam_single@saml.com'],
        'username': ['Sam'],
        'first_name': ['Sam Single'],
        'last_name': ['Sign-On'],
        'sid': ['S-DIG']}
    return user_data


@pytest.mark.django_db
class TestUtils:

    @classmethod
    def setup_method(cls):
        org = Organization.objects.create(name="Test Organization")
        account_sam = Account.objects.create(username="Sam",
                                             first_name="Sam Single",
                                             last_name="Sign-On",
                                             organization=org)

        cls.account_sam = account_sam
        cls.user_sam = account_sam.user

        account_jack = Account.objects.create(username="sam_jack",
                                              first_name="Jack",
                                              last_name="Samurai",
                                              organization=org)
        cls.account_jack = account_jack
        cls.user_jack = account_jack.user

    def test_email_alias_is_created(self, saml_user_data):
        # Arrange / Act
        get_or_create_user_aliases(saml_user_data)

        # Assert
        assert Alias.objects.filter(
            _value="sam_single@saml.com", _alias_type=AliasType.EMAIL).exists() is True

    def test_sid_alias_is_created(self, saml_user_data):
        # Arrange / Act
        get_or_create_user_aliases(saml_user_data)

        # Assert
        assert Alias.objects.filter(
            _value="S-DIG", _alias_type=AliasType.SID).exists() is True

    def test_aliases_are_related_to_user(self, saml_user_data):
        # Arrange / Act
        get_or_create_user_aliases(saml_user_data)

        # Assert
        assert self.user_sam.aliases.count() == 2

    def test_aliases_are_related_to_account(self, saml_user_data):
        # Arrange / Act
        get_or_create_user_aliases(saml_user_data)

        # Assert
        assert self.account_sam.aliases.count() == 2

    def test_existing_alias_doesnt_duplicate(self, saml_user_data):
        # Arrange
        Alias.objects.create(
            user=self.user_sam,
            account=self.account_sam,
            _alias_type=AliasType.SID,
            _value="S-DIG"
        )
        Alias.objects.create(
            user=self.user_sam,
            account=self.account_sam,
            _alias_type=AliasType.EMAIL,
            _value="sam_single@saml.com"
        )

        # Act
        get_or_create_user_aliases(saml_user_data)

        # Assert
        assert self.user_sam.aliases.count() == 2

    def test_existing_aliases_only_related_to_user(self, saml_user_data):
        # Arrange
        Alias(
            user=self.user_sam,
            _alias_type=AliasType.SID,
            _value="S-DIG"
        ).save(prevent_mismatch=False)  # Needed to force creation of alias without account
        Alias(
            user=self.user_sam,
            _alias_type=AliasType.EMAIL,
            _value="sam_single@saml.com"
        ).save(prevent_mismatch=False)  # Needed to force creation of alias without account

        # Act
        get_or_create_user_aliases(saml_user_data)

        # Assert
        # These aliases should now be connected to the Account object as well.
        # I.e. there should only be two aliases; not four
        assert self.user_sam.aliases.count() == 2

    def test_existing_aliases_only_related_to_account(self, saml_user_data):
        # This isn't possible due to DB constraints - Should raise IntegrityError
        with pytest.raises(IntegrityError):  # "Assert"
            # Arrange
            Alias.objects.create(
                account=self.account_sam,
                _alias_type=AliasType.SID,
                _value="S-DIG"
            )
            Alias.objects.create(
                acccount=self.account_sam,
                _alias_type=AliasType.EMAIL,
                _value="sam_single@saml.com"
            )
            # Act
            get_or_create_user_aliases(saml_user_data)

    def test_user_and_user_acccount_alias_exists_will_clean_up(self, saml_user_data):
        # Arrange
        #  We could potentially see a situation, where both the aliases
        #  Alias(user=A, account=A.account) and Alias(user=A) exist.
        Alias.objects.create(
            user=self.user_sam,
            account=self.account_sam,
            _alias_type=AliasType.SID,
            _value="S-DIG"
        )
        Alias(
            user=self.user_sam,
            _alias_type=AliasType.SID,
            _value="S-DIG"
        ).save(prevent_mismatch=False)  # Needed to force creation of alias without account
        # Act
        get_or_create_user_aliases(saml_user_data)
        # Assert
        assert Alias.objects.filter(_alias_type=AliasType.SID).count() == 1

    def test_creating_alias_with_no_account(self):
        """Creating an alias with no account should throw an exception."""
        with pytest.raises(IntegrityError):
            Alias.objects.create(
                user=self.user_sam,
                _alias_type=AliasType.SID,
                _value="S-DIG"
                )

    def test_updating_aliases_with_a_mismatched_account(self):
        # Arrange
        Alias.objects.create(
            user=self.user_sam,
            account=self.account_sam,
            _alias_type=AliasType.SID,
            _value="S-DIG")
        Alias.objects.create(
            user=self.user_sam,
            account=self.account_sam,
            _alias_type=AliasType.EMAIL,
            _value="sam@sam.sam")
        Alias.objects.create(
            user=self.user_jack,
            account=self.account_jack,
            _alias_type=AliasType.EMAIL,
            _value="jack@samurai.co.uk")

        with pytest.raises(IntegrityError):  # Assert
            # Act
            Alias.objects.all().update(account=self.account_jack)

    def test_updating_aliases_with_a_mismatched_account_with_ids(self):
        # Arrange
        Alias.objects.create(
            user=self.user_sam,
            account=self.account_sam,
            _alias_type=AliasType.SID,
            _value="S-DIG")
        Alias.objects.create(
            user=self.user_sam,
            account=self.account_sam,
            _alias_type=AliasType.EMAIL,
            _value="sam@sam.sam")
        Alias.objects.create(
            user=self.user_jack,
            account=self.account_jack,
            _alias_type=AliasType.EMAIL,
            _value="jack@samurai.co.uk")

        with pytest.raises(IntegrityError):  # Assert
            # Act
            Alias.objects.all().update(account_id=self.account_jack.uuid)

    def test_bulk_creating_mismatched_aliases(self):
        # Arrange
        objs = [
            Alias(
                user=self.user_sam,
                account=self.account_sam,
                _alias_type=AliasType.SID,
                _value="S-DIG"),
            Alias(
                user=self.user_sam,
                account=self.account_sam,
                _alias_type=AliasType.EMAIL,
                _value="sam@sam.sam"),
            Alias(
                user=self.user_jack,
                account=self.account_jack,
                _alias_type=AliasType.EMAIL,
                _value="jack@samurai.co.uk"),
            Alias(
                user=self.user_jack,
                account=self.account_sam,
                _alias_type=AliasType.EMAIL,
                _value="jack@sam.sam")]

        with pytest.raises(IntegrityError):  # Assert
            # Act
            Alias.objects.bulk_create(objs, ignore_conflicts=False)

    def test_bulk_creating_mismatched_aliases_ignore_conflicts(self):
        # Arrange
        objs = [
            Alias(
                user=self.user_sam,
                account=self.account_sam,
                _alias_type=AliasType.SID,
                _value="S-DIG"),
            Alias(
                user=self.user_sam,
                account=self.account_sam,
                _alias_type=AliasType.EMAIL,
                _value="sam@sam.sam"),
            Alias(
                user=self.user_jack,
                account=self.account_jack,
                _alias_type=AliasType.EMAIL,
                _value="jack@samurai.co.uk"),
            Alias(
                user=self.user_jack,
                account=self.account_sam,
                _alias_type=AliasType.EMAIL,
                _value="jack@sam.sam")]

        # Act
        Alias.objects.bulk_create(objs, ignore_conflicts=True)

        # Assert
        # Only three of the four aliases should be created
        assert list(Alias.objects.all()) == objs[:3]

    def test_saving_mismatched_alias(self):
        # Arrange
        mismatched_alias = Alias(
            user=self.user_jack,
            account=self.account_sam,
            _alias_type=AliasType.EMAIL,
            _value="jack@sam.sam")

        with pytest.raises(IntegrityError):  # Assert
            # Act
            mismatched_alias.save()
