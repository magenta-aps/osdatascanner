import pytest
from django.db import IntegrityError

from ...organizations.models import Organization, Account, Alias, AliasType
from ..views.utilities.document_report_utilities import is_owner


@pytest.mark.django_db
class TestUtils:

    @classmethod
    def setup_method(cls):
        org = Organization.objects.create(
            name="Test Organization",
            outlook_categorize_email_permission="NON")
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

    def test_alias_and_report_owner_no_match(self):
        """
        Test that the is_owner returns False when DocumentReport.owner doesn't match any alias for
        the given account.
        """

        # Arrange
        file_owner = "thisisnota@match.com"

        # Act/assert
        assert not is_owner(file_owner, self.account_sam)
