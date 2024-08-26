import pytest

from django.conf import settings

from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.engine2.rules.rule import Sensitivity
from os2datascanner.engine2.utilities.datetime import parse_datetime


@pytest.fixture
def time0():
    return "2020-10-28T13:51:49+01:00"


@pytest.fixture
def time1():
    return "2020-10-28T14:21:27+01:00"


@pytest.fixture
def time2():
    return "2020-10-28T14:36:20+01:00"


@pytest.fixture
def org_frag():
    return messages.OrganisationFragment(
        name="test_org", uuid="d92ff0c9-f066-40dc-a57e-541721b6c23e")


@pytest.fixture
def scan_tag0(time0, org_frag):
    return messages.ScanTagFragment(
        scanner=messages.ScannerFragment(
                pk=22, name="Dummy test scanner"),
        time=parse_datetime(time0),
        user=None, organisation=org_frag)


@pytest.fixture
def scan_tag1(time1, org_frag):
    return messages.ScanTagFragment(
        scanner=messages.ScannerFragment(
                pk=22, name="Dummy test scanner"),
        time=parse_datetime(time1),
        user=None, organisation=org_frag)


@pytest.fixture
def common_rule():
    return RegexRule("Vores hemmelige adgangskode er",
                     sensitivity=Sensitivity.WARNING)


@pytest.fixture
def temp_settings():
    return settings
