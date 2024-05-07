import pytest
from exchangelib import (Identity, Credentials, OAuth2Credentials)

from os2datascanner.engine2.model import ews


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
