import pytest

from os2datascanner.projects.report.organizations.models.account import Account
from os2datascanner.projects.report.organizations.models.aliases import Alias, AliasType
from os2datascanner.projects.report.organizations.models.organization import Organization
from os2datascanner.projects.report.organizations.models.organizational_unit import (
    OrganizationalUnit)
from os2datascanner.projects.report.organizations.models.position import Position
from os2datascanner.core_organizational_structure.models.position import Role


@pytest.fixture
def olsenbanden_organization():
    return Organization.objects.create(
      name="Olsen-banden"
    )


@pytest.fixture
def superuser_account(olsenbanden_organization):
    return Account.objects.create(
        username="admin",
        first_name="Super",
        last_name="User",
        is_superuser=True,
        organization=olsenbanden_organization
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
def yvonne_account(olsenbanden_organization):
    return Account.objects.create(
        username="yvonne",
        first_name="Yvonne",
        last_name="Jensen",
        organization=olsenbanden_organization
    )


@pytest.fixture
def børge_account(olsenbanden_organization):
    return Account.objects.create(
        username="børge",
        first_name="Børge",
        last_name="Jensen",
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
def egon_sid_alias(egon_account):
    return Alias.objects.create(
      account=egon_account,
      user=egon_account.user,
      _alias_type=AliasType.SID,
      _value="S-1-5-21-82206942009-31-1004"
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


@pytest.fixture
def yvonne_email_alias(yvonne_account):
    return Alias.objects.create(
        _alias_type=AliasType.EMAIL,
        _value="yvonne@olsenbanden.dk",
        account=yvonne_account,
        user=yvonne_account.user)


@pytest.fixture
def børge_email_alias(børge_account):
    return Alias.objects.create(
        _alias_type=AliasType.EMAIL,
        _value="børge@olsenbanden.dk",
        account=børge_account,
        user=børge_account.user)


@pytest.fixture
def egon_shared_email_alias(egon_account):
    return Alias.objects.create(
      account=egon_account,
      user=egon_account.user,
      _alias_type=AliasType.EMAIL,
      _value="olsenbanden@olsenbanden.dk",
      shared=True
    )


@pytest.fixture
def olsenbanden_ou(olsenbanden_organization):
    return OrganizationalUnit.objects.create(
        name="Olsen-banden",
        organization=olsenbanden_organization
    )


@pytest.fixture
def kjelds_hus(olsenbanden_ou, olsenbanden_organization):
    return OrganizationalUnit.objects.create(
        name="Kjelds Hus",
        parent=olsenbanden_ou,
        organization=olsenbanden_organization
    )


@pytest.fixture
def børges_værelse(olsenbanden_ou, kjelds_hus, olsenbanden_organization):
    return OrganizationalUnit.objects.create(
        name="Børges Værelse",
        parent=kjelds_hus,
        organization=olsenbanden_organization
    )


@pytest.fixture
def olsenbanden_ou_positions(olsenbanden_ou, egon_account, benny_account, kjeld_account):
    egon = Position.employees.create(account=egon_account, unit=olsenbanden_ou),
    benny = Position.employees.create(account=benny_account, unit=olsenbanden_ou),
    kjeld = Position.employees.create(account=kjeld_account, unit=olsenbanden_ou)
    return egon, benny, kjeld


@pytest.fixture
def kjelds_hus_ou_positions(kjelds_hus, yvonne_account, kjeld_account):
    yvonne = Position.employees.create(account=yvonne_account, unit=kjelds_hus),
    kjeld = Position.employees.create(account=kjeld_account, unit=kjelds_hus)
    return yvonne, kjeld


@pytest.fixture
def børges_værelse_ou_positions(børges_værelse, børge_account):
    børge = Position.employees.create(account=børge_account, unit=børges_værelse)
    return børge


@pytest.fixture
def kun_egon_ou(egon_account, olsenbanden_organization):
    ou = OrganizationalUnit.objects.create(name="Kun Egon", organization=olsenbanden_organization)
    Position.employees.create(account=egon_account, unit=ou)
    Position.dpos.create(account=egon_account, unit=ou)
    Position.managers.create(account=egon_account, unit=ou)
    return ou


@pytest.fixture
def egon_manager_position(egon_account, olsenbanden_ou):
    return Position.objects.create(
        account=egon_account,
        unit=olsenbanden_ou,
        role=Role.MANAGER
    )


@pytest.fixture
def egon_dpo_position(egon_account, olsenbanden_ou):
    return Position.dpos.create(
        account=egon_account,
        unit=olsenbanden_ou,
    )


@pytest.fixture
def benny_dpo_position(benny_account, olsenbanden_ou):
    return Position.dpos.create(
        account=benny_account,
        unit=olsenbanden_ou,
    )

# MARVEL


@pytest.fixture
def marvel_organization():
    return Organization.objects.create(name="Marvel Cinematic Universe")


@pytest.fixture
def hulk_account(marvel_organization):
    return Account.objects.create(
        username="the_hulk",
        first_name="Bruce",
        last_name="Banner",
        organization=marvel_organization
    )


@pytest.fixture
def hulk_email_alias(hulk_account):
    return Alias.objects.create(
      account=hulk_account,
      user=hulk_account.user,
      _alias_type=AliasType.EMAIL,
      _value="hulk@marvel.com"
    )


@pytest.fixture
def avengers_ou(marvel_organization):
    return OrganizationalUnit.objects.create(name="The Avengers", organization=marvel_organization)


@pytest.fixture
def avengers_ou_positions(avengers_ou, hulk_account):
    return Position.employees.create(account=hulk_account, unit=avengers_ou)


@pytest.fixture
def hulk_dpo_position(hulk_account, avengers_ou):
    return Position.dpos.create(
        account=hulk_account,
        unit=avengers_ou
    )
