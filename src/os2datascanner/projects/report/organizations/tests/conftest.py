import pytest

from ..models.account import Account
from ..models.aliases import Alias, AliasType
from ..models.organization import Organization


@pytest.fixture
def olsen_banden_organization():
    return Organization.objects.create(
      name="Olsenbanden"
    )


@pytest.fixture
def egon_account(olsen_banden_organization):
    return Account.objects.create(
      username="manden_med_planen",
      first_name="Egon",
      last_name="Olsen",
      organization=olsen_banden_organization
    )


@pytest.fixture
def benny_account(olsen_banden_organization):
    return Account.objects.create(
      username="skide_godt",
      first_name="Benny",
      last_name="Frandsen",
      organization=olsen_banden_organization
    )


@pytest.fixture
def kjeld_account(olsen_banden_organization):
    return Account.objects.create(
      username="jensen123",
      first_name="Kjeld",
      last_name="Jensen",
      organization=olsen_banden_organization
    )


@pytest.fixture
def egon_email_alias(egon_account):
    return Alias.objects.create(
      account=egon_account,
      user=egon_account.user,
      _alias_type=AliasType.EMAIL,
      _value="egon@olsenbanden.dk"
    )


@pytest.fixture
def egon_remediator_alias(egon_account):
    return Alias.objects.create(
      account=egon_account,
      user=egon_account.user,
      _alias_type=AliasType.REMEDIATOR,
      _value=0
    )


@pytest.fixture
def benny_email_alias(benny_account):
    return Alias.objects.create(
      account=benny_account,
      user=benny_account.user,
      _alias_type=AliasType.EMAIL,
      _value="benny@olsenbanden.dk"
    )


@pytest.fixture
def kjeld_email_alias(kjeld_account):
    return Alias.objects.create(
      account=kjeld_account,
      user=kjeld_account.user,
      _alias_type=AliasType.EMAIL,
      _value="kjeld@olsenbanden.dk"
    )
