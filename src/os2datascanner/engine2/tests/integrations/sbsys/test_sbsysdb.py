# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from os2datascanner.engine2.model.file import FilesystemHandle, FilesystemSource
from os2datascanner.engine2.model._staging.sbsysdb import (
        SBSYSDBSource, SBSYSDBHandles, SBSYSDBSources, find_case_handle)


@pytest.fixture
def sbsys_source():
    return SBSYSDBSource(
            "sbsys-db-host", 1433, "SbSysNetDrift", "sa", "hunter2",
            reflect_tables=None, base_weblink=None)


@pytest.fixture
def case_handle(sbsys_source):
    return SBSYSDBHandles.Case(
            sbsys_source, "22.13.01-K02-3-13", "Test case", None)


@pytest.fixture
def case_derived_source(case_handle):
    return SBSYSDBSources.Case(case_handle)


@pytest.fixture
def document_handle(case_derived_source):
    return SBSYSDBHandles.Document(
            case_derived_source, "doc-1", name="bankoplysninger.docx")


@pytest.fixture
def field_handle(case_derived_source):
    return SBSYSDBHandles.Field(case_derived_source, "Titel")


class TestFindCaseHandle:
    def test_case_handle_resolves_to_itself(self, case_handle):
        assert find_case_handle(case_handle) is case_handle

    def test_document_handle_resolves_to_its_case(self, document_handle, case_handle):
        resolved = find_case_handle(document_handle)
        assert resolved is not None
        assert resolved == case_handle

    def test_field_handle_resolves_to_its_case(self, field_handle, case_handle):
        resolved = find_case_handle(field_handle)
        assert resolved is not None
        assert resolved == case_handle

    def test_non_sbsys_handle_resolves_to_none(self):
        handle = FilesystemHandle(
                FilesystemSource("/mnt/fs01.magenta.dk/brugere/af"),
                "OS2datascanner/Dokumenter/plan.txt")
        assert find_case_handle(handle) is None
