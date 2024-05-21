import json
import pytest

from os2datascanner.engine2.rules.rule import Rule
from ..adminapp.models.apikey import APIKey


@pytest.fixture
def api_key_good(test_org):
    return APIKey.objects.create(organization=test_org, scope="get-rule/1")


@pytest.fixture
def other_api_key(test_org2):
    return APIKey.objects.create(organization=test_org2, scope="get-rule/1")


@pytest.mark.django_db
class TestAPI:

    def test_api_success(self, client, org_rule, org2_rule, api_key_good, other_api_key):
        """Making a valid API call with the appropriate authorised key should
        succeed and return the right object."""
        for rule, key in (
                (org_rule, api_key_good), (org2_rule, other_api_key),):
            r = client.post(
                    "/api/get-rule/1",
                    {"rule_id": rule.pk},
                    "application/json",
                    HTTP_AUTHORIZATION="Bearer {0}".format(key.uuid))
            assert r.status_code == 200
            body = json.loads(r.content.decode("ascii"))
            print(body)
            assert Rule.from_json_object(body["rule"]) == rule.make_engine2_rule()

    def test_api_no_key(self, client, org_rule):
        """Making a valid API call with no key should fail with HTTP 401
        Unauthorized."""
        r = client.post(
                "/api/get-rule/1",
                {"rule_id": org_rule.pk}, "application/json")
        assert r.status_code == 401

    def test_api_invalid_header(self, client, org_rule):
        """Making a valid API call with an invalid HTTP header should fail with
        HTTP 400 Bad Request."""
        r = client.post(
                "/api/get-rule/1",
                {"rule_id": org_rule.pk}, "application/json",
                HTTP_AUTHORIZATION="Invalid INVALID")
        assert r.status_code == 400

    def test_api_invalid_key(self, client, org_rule):
        """Making a valid API call with an invalid key should fail with HTTP
        401 Unauthorized."""
        r = client.post(
                "/api/get-rule/1",
                {"rule_id": org_rule.pk}, "application/json",
                HTTP_AUTHORIZATION="Bearer INVALID")
        assert r.status_code == 401

    def test_api_wrong_key(self, client, org_rule, other_api_key):
        """Making a valid API call with a valid key for the wrong organisation
        should fail as though the object did not exist."""
        r = client.post(
                "/api/get-rule/1",
                {"rule_id": org_rule.pk}, "application/json",
                HTTP_AUTHORIZATION="Bearer {0}".format(other_api_key.uuid))
        assert r.status_code == 200
        body = json.loads(r.content.decode("ascii"))
        assert body["status"] == "fail"

    def test_api_unauthorised(self, client, api_key_good):
        """Making an API call with a valid key whose scope does not cover that
        API call should fail with HTTP 403 Forbidden."""
        r = client.post(
                "/api/get-scanner/1",
                HTTP_AUTHORIZATION="Bearer {0}".format(api_key_good.uuid))
        assert r.status_code == 403
