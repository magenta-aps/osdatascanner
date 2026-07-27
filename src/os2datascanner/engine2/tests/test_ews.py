# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from unittest.mock import MagicMock, patch

import pytest
from exchangelib import (Identity, Credentials, OAuth2Credentials)

from os2datascanner.engine2.model import ews
from os2datascanner.engine2.model.ews import EWSMailResource


sources_and_credentials = [
    (
        ews.EWSAccountSource(
                "vstkom.invalid",
                "https://mail.vstkom.invalid/EWS/Exchange.asmx",
                "service_account", "53RV1C3_P455W0RD",
                "jens"),
        Credentials("service_account", "53RV1C3_P455W0RD"),
    ),
    (
        ews.EWSAccountSource(
                "vstkom.invalid",
                None,
                None, None,
                "jens",
                "cid", "tid", "csv"),
        OAuth2Credentials(
                client_id="cid", tenant_id="tid",
                client_secret="csv",
                identity=Identity(
                        primary_smtp_address="jens@vstkom.invalid")),
    ),
]


class TestEWS:
    @pytest.mark.parametrize(
            "source,credentials",
            sources_and_credentials)
    def test_credentials(self, source, credentials):
        assert source._make_credentials() == credentials

    def test_censored_credential_failure(self):
        with pytest.raises(ValueError):
            source, _ = sources_and_credentials[0]
            source.censor()._make_credentials()

    def test_source_equality(self):
        """After censoring, EWSAccountSources that refer to the same mail
        address should be equal, whether they use a Graph grant or a service
        account."""
        (old_and_busted, _), (new_hotness, _) = sources_and_credentials
        assert old_and_busted != new_hotness
        assert old_and_busted.censor() == new_hotness.censor()


class TestEWSMailResource:
    def _make_resource(self):
        handle = MagicMock()
        handle.relative_path = "folder_id.mail_id"
        return EWSMailResource(handle, MagicMock())

    def test_compute_content_identifier_is_bounded(self):
        # A Microsoft-generated notification can carry a Message-ID far
        # longer than an ordinary email's, and the database column is only
        # varchar(256).
        mock_message = MagicMock()
        mock_message.message_id = "<" + "x" * 300 + "@odspnotify>"

        resource = self._make_resource()
        with patch.object(resource, "get_message_object", return_value=mock_message):
            identifier = resource.compute_content_identifier()

        assert len(identifier) <= 256
