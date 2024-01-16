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
        Alias.objects.create(
            user=self.user_sam,
            _alias_type=AliasType.SID,
            _value="S-DIG"
        )
        Alias.objects.create(
            user=self.user_sam,
            _alias_type=AliasType.EMAIL,
            _value="sam_single@saml.com"
        )

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
