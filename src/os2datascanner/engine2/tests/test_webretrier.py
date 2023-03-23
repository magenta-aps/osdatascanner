import unittest
from unittest.mock import Mock
import requests

from os2datascanner.engine2.utilities.backoff import WebRetrier


class TestWebretrier(unittest.TestCase):

    def setUp(self):
        self.retrier = WebRetrier()

    def test_should_retry(self):
        # See if the function response with a correct retry code
        ex = requests.exceptions.HTTPError(
            response=Mock(status_code=429),
            request=Mock()
        )
        self.assertTrue(self.retrier._should_retry(ex))

    def test_should_retry_not(self):
        # See if the function response with an incorrect retry code
        ex = requests.exceptions.HTTPError(
            response=Mock(status_code=100),
            request=Mock()
        )
        self.assertFalse(self.retrier._should_retry(ex))

    def test_test_return_value_with_retry_code(self):
        # See if the function passes with an exception
        response = requests.Response()
        response.status_code = 503
        with self.assertRaises(requests.exceptions.HTTPError):
            self.retrier._test_return_value(response)

    def test_test_return_value_with_response(self):
        # Checks that the function response with a response
        response = requests.Response()
        response.status_code = 200
        self.assertEqual(self.retrier._test_return_value(response), response)

    def test_test_return_value(self):
        # Checks that the function do not response with a wrong value
        self.assertNotEqual(self.retrier._test_return_value(41), 42)
