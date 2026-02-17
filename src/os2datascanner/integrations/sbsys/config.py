# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

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
