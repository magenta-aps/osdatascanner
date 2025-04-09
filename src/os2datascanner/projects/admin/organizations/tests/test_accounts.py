import pytest

from django.db.utils import IntegrityError

from ..models import Account


@pytest.mark.django_db(transaction=True)
class TestAccounts:

    def test_account_username_org_constraint(self, test_org, oluf):
        # If the test class isn't transaction marked, we'll also be throwing a
        # psycopg2.errors.UniqueViolation at test teardown. That isn't what we're looking for.
        with pytest.raises(IntegrityError):
            Account.objects.create(
                username=oluf.username,
                organization=test_org
            )


class TestAccountMethods:

    @pytest.mark.parametrize("account,initials", [
        (Account(username="superman", first_name="Clark", last_name="Kent"), "CK"),
        (Account(username="robin", first_name="Robin"), "R"),
        (Account(username="batman", last_name="Wayne"), "W"),
        (Account(username="wonder_woman"), None)
    ])
    def test_initials(self, account, initials):
        """The 'initials'-method should return the first letter from the first
        and the last name. If the account only has a first name, only one
        letter should be returned. If the account has no names, None should be
        returned."""

        assert account.initials == initials
