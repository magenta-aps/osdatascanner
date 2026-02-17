# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from pydantic import SecretStr
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from os2datascanner.integrations.sbsys.db import get_engine, get_tables


def test_get_engine():
    # Act
    engine = get_engine(
        host="sbsys.magenta.dk",
        port=7777,
        user="user",
        password=SecretStr("secret"),
        database="drift",
    )

    # Assert
    url = engine.url
    assert url.drivername == "mssql+pymssql"
    assert url.host == "sbsys.magenta.dk"
    assert url.port == 7777
    assert url.username == "user"
    assert url.password == "secret"
    assert url.database == "drift"


def test_get_tables():
    """
    Test that the get_tables function is working by using an in-memory
    SQLite DB containing a single table with a single column.
    """

    # Arrange
    engine = create_engine("sqlite:///:memory:")
    Base = declarative_base()

    class Sag(Base):
        __tablename__ = "Sag"
        id: Mapped[int] = mapped_column(primary_key=True)

    Base.metadata.create_all(engine)

    # Act
    tables = get_tables(engine)

    # Assert
    assert "Sag" in tables
