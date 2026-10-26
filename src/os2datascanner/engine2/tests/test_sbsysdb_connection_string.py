# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from sqlalchemy import make_url

from os2datascanner.engine2.model._staging.sbsysdb import SBSYSDBSource


def _make_source(
        server="sbsys.example.com", port=1433, db="SbSysNetDrift",
        user="user", password="password"):
    return SBSYSDBSource(
            server, port, db, user, password,
            reflect_tables=None,
            base_weblink=None)


def test_connection_string_uses_pymssql_driver():
    url = make_url(_make_source()._make_connection_string())

    assert url.drivername == "mssql+pymssql"


def test_connection_string_components():
    url = make_url(_make_source()._make_connection_string())

    assert url.host == "sbsys.example.com"
    assert url.port == 1433
    assert url.database == "SbSysNetDrift"
    assert url.username == "user"
    assert url.password == "password"


@pytest.mark.parametrize("user, password", [
    ("user", "p@ssword"),
    ("user", "pass:word"),
    ("user", "pass/word"),
    ("user", "pass#word"),
    ("user", "pass%word"),
    ("user", "pass?word"),
    (r"DOMAIN\user", "password"),
    ("user@domain.example", "password"),
])
def test_connection_string_credentials_round_trip(user, password):
    url = make_url(
            _make_source(user=user, password=password)
            ._make_connection_string())

    assert url.username == user
    assert url.password == password
