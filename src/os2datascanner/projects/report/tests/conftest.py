import uuid
import pytest

from django.conf import settings

from os2datascanner.engine2.model.file import (
        FilesystemHandle, FilesystemSource)
from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.engine2.rules.rule import Sensitivity
from os2datascanner.engine2.utilities.datetime import parse_datetime

from os2datascanner.projects.report.organizations.models import Organization


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
def test_org():
    return Organization.objects.create(
        name="test_org",
        uuid=uuid.UUID("d92ff0c9-f066-40dc-a57e-541721b6c23e"),
    )


@pytest.fixture
def org_frag(test_org):
    return messages.OrganisationFragment(
        name=test_org.name,
        uuid=test_org.uuid,
    )


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


@pytest.fixture
def common_handle():
    return FilesystemHandle(
        FilesystemSource("/mnt/fs01.magenta.dk/brugere/af"),
        "OS2datascanner/Dokumenter/Verdensherredømme - plan.txt")


@pytest.fixture
def common_scan_spec(common_handle, common_rule):
    return messages.ScanSpecMessage(
        scan_tag=None,  # placeholder
        source=common_handle.source,
        rule=common_rule,
        configuration={},
        filter_rule=None,
        progress=None)


@pytest.fixture
def positive_match(common_scan_spec, scan_tag0, common_handle, common_rule):
    return messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(scan_tag=scan_tag0),
        handle=common_handle,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ])
