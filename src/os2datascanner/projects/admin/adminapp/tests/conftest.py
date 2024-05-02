import pytest
from django.contrib.auth import get_user_model

from os2datascanner.projects.admin.adminapp.models.rules import CustomRule

from ...organizations.models import Organization
from ...core.models import Administrator, Client
from ..models.scannerjobs.scanner import Scanner, ScanStatus
from ...tests.test_utilities import dummy_rule_dict


@pytest.fixture
def user():
    return get_user_model().objects.create(username='mr_userman', password='hunter2')

# First test organization


@pytest.fixture(autouse=True)
def test_org():
    client = Client.objects.create(name='test_client')
    return Organization.objects.create(name='test_org', client=client)


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
