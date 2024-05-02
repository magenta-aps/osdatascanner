import pytest
from django.contrib.auth import get_user_model

from os2datascanner.projects.admin.adminapp.models.rules import CustomRule
from os2datascanner.projects.admin.organizations.models import (
    Organization, OrganizationalUnit, Account)
from os2datascanner.projects.admin.core.models import Administrator, Client
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import Scanner, ScanStatus
from os2datascanner.projects.admin.tests.test_utilities import dummy_rule_dict


@pytest.fixture
def user():
    return get_user_model().objects.create(username='mr_userman', password='hunter2')

# First test organization


@pytest.fixture(autouse=True)
def test_org():
    client = Client.objects.create(name='test_client',
                                   contact_email="test@magenta.dk",
                                   contact_phone="12345678")
    return Organization.objects.create(
        name='test_org',
        client=client,
        uuid="3d6d288f-b75f-43e2-be33-a43803cd1243")


@pytest.fixture
def user_admin(user, test_org):
    Administrator.objects.create(user=user, client=test_org.client)
    return user


# Scanner and ScanStatus fixtures with basic rule
@pytest.fixture
def basic_rule():
    return CustomRule.objects.create(**dummy_rule_dict)


@pytest.fixture
def basic_scanner(test_org, basic_rule):
    return Scanner.objects.create(
            name=f"SomeScanner-{test_org.name}",
            organization=test_org,
            rule=basic_rule
        )


@pytest.fixture
def basic_scanstatus(basic_scanner):
    return ScanStatus.objects.create(
        scanner=basic_scanner,
        scan_tag=basic_scanner._construct_scan_tag().to_json_object())


@pytest.fixture
def basic_scanstatus_completed(basic_scanner):
    return ScanStatus.objects.create(
        scanner=basic_scanner,
        scan_tag=basic_scanner._construct_scan_tag().to_json_object(),
        total_sources=1,
        total_objects=1,
        explored_sources=1,
        scanned_objects=1)

# Test accounts and organizational units for test organization


@pytest.fixture
def familien_sand(test_org):
    return OrganizationalUnit.objects.create(name="Familien Sand", organization=test_org)


@pytest.fixture
def nisserne(test_org):
    return OrganizationalUnit.objects.create(name="Nisserne", organization=test_org)


@pytest.fixture
def oluf(test_org, familien_sand):
    oluf = Account.objects.create(
        username="oluf",
        first_name="Oluf",
        last_name="Sand",
        organization=test_org)
    oluf.units.add(familien_sand)
    return oluf


@pytest.fixture
def gertrud(test_org, familien_sand):
    gertrud = Account.objects.create(
        username="gertrud",
        first_name="Gertrud",
        last_name="Sand",
        organization=test_org)
    gertrud.units.add(familien_sand)
    return gertrud


@pytest.fixture
def benny(test_org):
    return Account.objects.create(
        username="benny",
        first_name="Benny",
        last_name="Jensen",
        organization=test_org)


@pytest.fixture
def fritz(test_org, nisserne):
    fritz = Account.objects.create(username="fritz", first_name="Fritz", organization=test_org)
    fritz.units.add(nisserne)
    return fritz


@pytest.fixture
def günther(test_org, nisserne):
    günther = Account.objects.create(
        username="günther",
        first_name="Günther",
        organization=test_org)
    günther.units.add(nisserne)
    return günther


@pytest.fixture
def hansi(test_org, nisserne):
    hansi = Account.objects.create(username="hansi", first_name="Hansi", organization=test_org)
    hansi.units.add(nisserne)
    return hansi

# Second test organization


@pytest.fixture
def test_org2():
    client = Client.objects.create(name='test_client2')
    return Organization.objects.create(name='test_org2', client=client)

# Other scanner and ScanStatus fixtures with basic rule


@pytest.fixture
def basic_scanner2(test_org2, basic_rule):
    return Scanner.objects.create(
            name=f"SomeScanner-{test_org2.name}",
            organization=test_org2,
            rule=basic_rule
        )


@pytest.fixture
def basic_scanstatus2(basic_scanner2):
    return ScanStatus.objects.create(
        scanner=basic_scanner2,
        scan_tag=basic_scanner2._construct_scan_tag().to_json_object())
