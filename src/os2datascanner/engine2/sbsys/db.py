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
def get_tables(engine: Engine) -> FacadeDict[str, Table]:
    """
    Get the SBSYS tables.

    Args:
        engine: the SQLAlchemy engine to use

    Returns:
         A dictionary-like object containing the SBSYS tables.
    """
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine, only=("Sag",))
    return metadata_obj.tables
