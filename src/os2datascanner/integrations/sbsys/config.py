from pydantic import PositiveInt, SecretStr
from pydantic_settings import BaseSettings


class SBSYSSettings(BaseSettings):
    sbsys_host: str
    sbsys_port: PositiveInt
    sbsys_user: str
    sbsys_password: SecretStr
    sbsys_database: str


def get_sbsys_settings(*args, **kwargs) -> SBSYSSettings:
    return SBSYSSettings(*args, **kwargs)
