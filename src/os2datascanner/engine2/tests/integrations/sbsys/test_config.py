# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from _pytest.monkeypatch import MonkeyPatch
from pydantic import SecretStr

from os2datascanner.integrations.sbsys.config import get_sbsys_settings


def test_settings(monkeypatch: MonkeyPatch):
    # Arrange
    monkeypatch.setenv("SBSYS_HOST", "sbsys.magenta.dk")
    monkeypatch.setenv("SBSYS_PORT", 7777)
    monkeypatch.setenv("SBSYS_USER", "user")
    monkeypatch.setenv("SBSYS_PASSWORD", "secret")
    monkeypatch.setenv("SBSYS_DATABASE", "drift")

    # Act
    settings = get_sbsys_settings()

    # Assert
    assert settings.sbsys_host == "sbsys.magenta.dk"
    assert settings.sbsys_port == 7777
    assert settings.sbsys_user == "user"
    assert settings.sbsys_password == SecretStr("secret")
    assert settings.sbsys_database == "drift"
