# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime

import pytest

from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.conversions.types import OutputType
from os2datascanner.engine2.model._staging.sbsysdb import (
        SBSYSDBSource, SBSYSDBHandles, SBSYSDBSources)


def _make_case_handle(owner_field):
    """Builds a Case handle carrying a db_row hint that includes all three of
    the caseworker identity columns, using the given owner_field on its
    source."""
    source = SBSYSDBSource(
            "server", 1433, "SbSysNetDrift", "user", "password",
            reflect_tables=None,
            base_weblink=None,
            owner_field=owner_field)

    db_row = {
        "ID": 1,
        "Nummer": "1-2-3",
        "Titel": "A perfectly ordinary case",
        "Kommentar": "",
        "Behandler.UserPrincipalName": "bruce@kungfu.org",
        "Behandler.ObjectSid": "S-1-5-21-1-2-3-1000",
        "Behandler.LogonID": "BRUCE",
        "LastChanged": datetime(2026, 4, 13, 14, 13, 57),
        "Created": datetime(2020, 1, 1, 0, 0, 0),
        "Ansaettelsessted.Navn": "Kung Fu-afdelingen",
    }

    return SBSYSDBHandles.Case(
            source,
            db_row["Nummer"], db_row["Titel"], None,
            db_row.get("Ansaettelsessted.Navn"),
            hints={"db_row": OutputType.DatabaseRow.encode_json_object(db_row)})


class TestSBSYSDBMetadata:
    def test_required_columns_cover_all_owner_fields(self):
        """Every caseworker identity column that _generate_metadata reads must
        be fetched into the db_row hint, or the owner metadata is silently
        empty."""
        assert {
            "Behandler.UserPrincipalName",
            "Behandler.ObjectSid",
            "Behandler.LogonID",
        }.issubset(set(SBSYSDBSources.Case.required_columns))

    @pytest.mark.parametrize("owner_field,expected_key,expected_value", [
        ("upn", "user-principal-name", "bruce@kungfu.org"),
        ("SID", "sbsys-caseworker-sid", "S-1-5-21-1-2-3-1000"),
        ("logon", "windows-domain-user", "BRUCE"),
        # A source serialised before this feature existed has no owner_field,
        # and must keep behaving like the old UPN-only implementation
        (None, "user-principal-name", "bruce@kungfu.org"),
    ])
    def test_owner_metadata_for_owner_field(
            self, owner_field, expected_key, expected_value):
        """The Case resource yields exactly the owner metadata item selected by
        its source's owner_field."""
        # Arrange
        handle = _make_case_handle(owner_field)

        # Act
        with SourceManager() as sm:
            metadata = dict(handle.follow(sm)._generate_metadata())

        # Assert
        assert metadata.get(expected_key) == expected_value
        # Only the selected owner item is emitted, never the others
        owner_keys = {
            "user-principal-name",
            "sbsys-caseworker-sid",
            "windows-domain-user",
        }
        assert set(metadata) & owner_keys == {expected_key}
        # The time-based metadata is unaffected by the owner_field choice
        assert "last-modified" in metadata
        assert "datasource-creation-time" in metadata

    @pytest.mark.parametrize("owner_field,missing_column", [
        ("SID", "Behandler.ObjectSid"),
        ("logon", "Behandler.LogonID"),
    ])
    def test_no_owner_metadata_when_value_absent(
            self, owner_field, missing_column):
        """When the selected identity column has no value, no owner metadata is
        emitted (rather than an empty or bogus one)."""
        # Arrange
        handle = _make_case_handle(owner_field)
        db_row = OutputType.DatabaseRow.decode_json_object(
                handle.hint("db_row"))
        db_row[missing_column] = None
        handle._hints["db_row"] = OutputType.DatabaseRow.encode_json_object(
                db_row)

        # Act
        with SourceManager() as sm:
            metadata = dict(handle.follow(sm)._generate_metadata())

        # Assert
        owner_keys = {
            "user-principal-name",
            "sbsys-caseworker-sid",
            "windows-domain-user",
        }
        assert set(metadata) & owner_keys == set()
