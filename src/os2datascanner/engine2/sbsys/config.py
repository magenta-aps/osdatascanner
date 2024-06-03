from pydantic import PositiveInt, SecretStr
from pydantic_settings import BaseSettings


class SBSYSSettings(BaseSettings):
    host: str
    port: PositiveInt
    user: str
    password: SecretStr
    database: str


def get_sbsys_settings(*args, **kwargs) -> SBSYSSettings:
    return SBSYSSettings(*args, **kwargs)
