# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import uuid
import pytest

from django.conf import settings

from os2datascanner.engine2.model.file import (
        FilesystemHandle, FilesystemSource)
from os2datascanner.engine2.model._staging.sbsysdb import (
        SBSYSDBSource, SBSYSDBHandles, SBSYSDBSources)
from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.engine2.utilities.datetime import parse_datetime

from os2datascanner.projects.report.organizations.models import Organization

from ..reportapp.models.scanner_reference import ScannerReference


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
def scanner_job(test_org):
    return ScannerReference.objects.create(
            scanner_pk=1, scanner_name="Test SBSYS scanner",
            organization=test_org)


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
    return RegexRule("Vores hemmelige adgangskode er")


@pytest.fixture
def temp_settings():
    return settings


@pytest.fixture
def common_handle():
    return FilesystemHandle(
        FilesystemSource("/mnt/fs01.magenta.dk/brugere/af"),
        "OS2datascanner/Dokumenter/Verdensherredømme - plan.txt")


@pytest.fixture
def handle_with_a_very_long_name():
    return FilesystemHandle(
        FilesystemSource("/mnt/fs01.magenta.dk/brugere/af/en/gruppe/dedikerede/olsen/banden/fans/"
                         "men/vi/ser/også/feks/matador/af/og/til"),
        "OSdatascanner/Dokumenter/Og/Vedtægter/"
        "Og/Jeg/Skal/Komme/Efter/Dig/Hvor/Er/Her/Meget/Data/"
        "Er/Du/Øm/I/Musefingeren/Endnu/Spørgsmålstegn/"
        "fiktivt_filnavn_"
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.txt")


@pytest.fixture
def match_with_a_very_long_name(common_scan_spec, scan_tag0,
                                handle_with_a_very_long_name, common_rule):
    return messages.MatchesMessage(
        scan_spec=messages.replace(common_scan_spec, scan_tag=scan_tag0),
        handle=handle_with_a_very_long_name,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ])


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
        scan_spec=messages.replace(common_scan_spec, scan_tag=scan_tag0),
        handle=common_handle,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ])


@pytest.fixture
def sbsys_source():
    return SBSYSDBSource(
            "sbsys-db-host", 1433, "SbSysNetDrift", "sa", "hunter2",
            reflect_tables=None, base_weblink=None)


@pytest.fixture
def sbsys_case_handle(sbsys_source):
    return SBSYSDBHandles.Case(sbsys_source, "22.13.01-K02-3-13", "Test case", None)


@pytest.fixture
def sbsys_case_source(sbsys_case_handle):
    return SBSYSDBSources.Case(sbsys_case_handle)


@pytest.fixture
def sbsys_document_handle(sbsys_case_source):
    return SBSYSDBHandles.Document(sbsys_case_source, "doc-1", name="bankoplysninger.docx")


@pytest.fixture
def sbsys_field_handle(sbsys_case_source):
    return SBSYSDBHandles.Field(sbsys_case_source, "Titel")


@pytest.fixture
def sbsys_match_document(common_scan_spec, scan_tag0, common_rule, sbsys_document_handle):
    return messages.MatchesMessage(
        scan_spec=messages.replace(common_scan_spec, scan_tag=scan_tag0),
        handle=sbsys_document_handle,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object 1"}])
        ])


@pytest.fixture
def sbsys_match_field(common_scan_spec, scan_tag0, common_rule, sbsys_field_handle):
    return messages.MatchesMessage(
        scan_spec=messages.replace(common_scan_spec, scan_tag=scan_tag0),
        handle=sbsys_field_handle,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object 2"}])
        ])
