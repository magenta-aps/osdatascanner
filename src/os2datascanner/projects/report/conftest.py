import pytest

from os2datascanner.projects.report.organizations.models.account import Account
from os2datascanner.projects.report.organizations.models.aliases import Alias, AliasType
from os2datascanner.projects.report.organizations.models.organization import Organization


@pytest.fixture
def olsenbanden_organization():
    return Organization.objects.create(
      name="Olsen-banden"
    )


@pytest.fixture
def egon_account(olsenbanden_organization):
    return Account.objects.create(
      username="manden_med_planen",
      first_name="Egon",
      last_name="Olsen",
      organization=olsenbanden_organization
    )


@pytest.fixture
def benny_account(olsenbanden_organization):
    return Account.objects.create(
      username="skide_godt",
      first_name="Benny",
      last_name="Frandsen",
      organization=olsenbanden_organization
    )


@pytest.fixture
def kjeld_account(olsenbanden_organization):
    return Account.objects.create(
      username="jensen123",
      first_name="Kjeld",
      last_name="Jensen",
      organization=olsenbanden_organization
    )


@pytest.fixture
def bøffen_account(olsenbanden_organization):
    return Account.objects.create(
        username="bøffen",
        first_name="Fritz",
        organization=olsenbanden_organization
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


@pytest.fixture
def bøffen_email_alias(bøffen_account):
    return Alias.objects.create(
        _alias_type=AliasType.EMAIL,
        _value="bøffen@olsenbanden.dk",
        account=bøffen_account,
        user=bøffen_account.user)
