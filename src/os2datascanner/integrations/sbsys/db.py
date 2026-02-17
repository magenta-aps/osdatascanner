# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from functools import cache

from pydantic import PositiveInt, SecretStr
from sqlalchemy import Engine, create_engine, Table, MetaData
from sqlalchemy.util import FacadeDict


def get_engine(
    host: str,
    port: PositiveInt,
    user: str,
    password: SecretStr,
    database: str,
) -> Engine:
    return create_engine(
        f"mssql+pymssql://{user}:{password.get_secret_value()}"
        f"@{host}:{port}/{database}"
    )


@cache
def get_tables(
        engine: Engine,
        only: tuple[str] = ("Sag,")) -> FacadeDict[str, Table]:
    """
    Get the SBSYS tables.

    Args:
        engine: the SQLAlchemy engine to use

    Returns:
         A dictionary-like object containing the SBSYS tables.
    """
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine, only=only)
    return metadata_obj.tables
