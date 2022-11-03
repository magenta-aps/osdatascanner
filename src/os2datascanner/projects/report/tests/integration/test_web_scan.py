import json
import unittest
import requests
from os2datascanner.engine2.rules.cpr import CPRRule


class TestIntegrationWebScanner(unittest.TestCase):
    '''Tests the WebScanner'''

    def setUp(self):
        self.web_url = "http://nginx"
        self.token = "thisIsNotASecret"
        self.api_base_url = "http://api_server:5000"

    def test_scan_finds_all_sources(self):
        """Tests whether a scan finds all matches"""

        # Arrange
        expected_matches = 3

        headers = {
            'accept': 'application/jsonl',
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            }
        data = '{"url":' + f'"{self.web_url}"' + '}'
        rule = CPRRule()
        rule.BLACKLIST_WORDS = None
        rule_as_json = rule.to_json_object()

        # Act
        response = requests.post(
            self.api_base_url + '/parse-url/1',
            headers=headers,
            data=data)

        # Assert
        self.assertEqual(
            response.status_code,
            200,
            response.content)

        # Arrange
        source = response.json()["source"]

        data = json.dumps({
            "rule": rule_as_json,
            "source": source})

        # Act
        api_response = requests.post(
            self.api_base_url + '/scan/1',
            headers=headers,
            data=data)

        actual_matches = self.count_matches(api_response)

        # Assert
        self.assertEqual(
            response.status_code,
            200,
            response.content)

        self.assertEqual(
            actual_matches,
            expected_matches,
            f"Expected: {expected_matches} matches, got: {actual_matches}"
            )

    def count_matches(self, response):
        """Utility for counting the number of matches."""
        messages = response.content.splitlines()
        matches_list = filter(
            lambda m: m != [],
            (json.loads(msg)["matches"][0]
             if "matches" in json.loads(msg) else []
             for msg in messages))

        return sum(
            len(m["matches"])
            if m["matches"] is not None else 0
            for m in matches_list)
