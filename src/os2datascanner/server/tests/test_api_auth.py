import json
import pytest
from _pytest.monkeypatch import MonkeyPatch
from os2datascanner.server import settings
from os2datascanner.server.wsgi import dummy_1, scan_1


class TestAPIEndpoints:
    @pytest.fixture(autouse=True)
    def patch_env(self, monkeypatch: MonkeyPatch):
        monkeypatch.setitem(settings.server, "token", "token")
        monkeypatch.setitem(settings.server, "demo_token", "demo_token")

    def test_valid_token(self):
        """Test dummy_1 reponse with valid token should return 200"""
        token = settings.server.get("token")
        env = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        body = {}

        def start_response(status, headers):
            pass

        response = dummy_1(env, start_response, body)

        temp = []
        for item in response:
            temp.append(json.loads(item.decode('ascii') if isinstance(item, bytes) else item))

        assert temp[0]["status"] == "ok", "Should have returned status ok"

    def test_missing_token(self):
        """Test scan_1 should return 401 if token is missing"""
        env = {"HTTP_AUTHORIZATION": "Bearer wrong_token"}
        body = {
            "rule": {
                "type": "cpr",
            },
            "source": {
                "type": "data",
                "content": "==",
                "mime": "application/xml",
                "name": "test.txt"
            },
            "configuration": {
                "skip_mime_types": []
            }
        }
        response_status = None

        def start_response(status, headers):
            nonlocal response_status
            response_status = status

        response = scan_1(env, start_response, body)
        list(response)

        assert response_status.startswith("401"), "Should have returned 401"

    def test_incorrect_bearer(self):
        """Test scan_1 should return 400 if bearer is missing"""
        env = {"HTTP_AUTHORIZATION": "Bearer "}
        body = {
            "rule": {
                "type": "cpr",
            },
            "source": {
                "type": "data",
                "content": "==",
                "mime": "application/xml",
                "name": "test.txt"
            },
            "configuration": {
                "skip_mime_types": []
            }
        }
        response_status = None

        def start_response(status, headers):
            nonlocal response_status
            response_status = status

        response = scan_1(env, start_response, body)
        list(response)

        assert response_status.startswith("400"), "Should have returned 400"

    def test_demo_token_with_wrong_mime(self):
        """Test scan_1 should return 403 if mime is disallowed"""
        demo_token = settings.server.get("demo_token")
        env = {
            "HTTP_AUTHORIZATION": f"Bearer {demo_token}",
            "CONTENT_LENGTH": 0
        }
        body = {
            "rule": {
                "type": "cpr",
            },
            "source": {
                "type": "data",
                "content": "==",
                "mime": "application/xml",
                "name": "test.txt"
            },
            "configuration": {
                "skip_mime_types": []
            }
        }
        response_status = None

        def start_response(status, headers):
            nonlocal response_status
            response_status = status

        response = scan_1(env, start_response, body)
        list(response)

        assert response_status.startswith("403"), "Should have returned 403"

    def test_demo_token_with_wrong_type(self):
        """Test scan_1 should return 403 if type is disallowed"""
        demo_token = settings.server.get("demo_token")
        env = {
            "HTTP_AUTHORIZATION": f"Bearer {demo_token}",
            "CONTENT_LENGTH": 0
        }
        body = {
            "rule": {
                "type": "cpr",
            },
            "source": {
                "type": "something wrong",
                "content": "==",
                "mime": "application/xml",
                "name": "test.txt"
            },
            "configuration": {
                "skip_mime_types": []
            }
        }
        response_status = None

        def start_response(status, headers):
            nonlocal response_status
            response_status = status

        response = scan_1(env, start_response, body)
        list(response)

        assert response_status.startswith("403"), "Should have returned 403"

    def test_demo_token_with_disallowed_file_size(self):
        """Test scan_1 should return 403 if content length is disallowed"""
        demo_token = settings.server.get("demo_token")
        env = {
            "HTTP_AUTHORIZATION": f"Bearer {demo_token}",
            "CONTENT_LENGTH": 220000000
        }
        body = {
            "rule": {
                "type": "cpr",
            },
            "source": {
                "type": "data",
                "content": "==",
                "mime": "application/xml",
                "name": "test.txt"
            },
            "configuration": {
                "skip_mime_types": []
            }
        }
        response_status = None

        def start_response(status, headers):
            nonlocal response_status
            response_status = status

        response = scan_1(env, start_response, body)
        list(response)

        assert response_status.startswith("403"), "Should have returned 403"
