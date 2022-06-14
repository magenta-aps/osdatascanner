import unittest

from os2datascanner.engine2.utilities.backoff import (
        Testing, ExponentialBackoffRetrier as EBRetrier,
        WebRetrier)

from requests.exceptions import HTTPError


class EtiquetteBreach(Exception):
    pass


class ImpoliteClientFauxPas(EtiquetteBreach):
    pass


class ImpatientClientFauxPas(ImpoliteClientFauxPas):
    pass


class TestBackoff(unittest.TestCase):
    def test_base_failure(self):
        with self.assertRaises(ImpatientClientFauxPas):
            Testing.requires_k_seconds(8, ImpatientClientFauxPas)(
                    2, 3, scale_factor=4)

    def test_eventual_success(self):
        operation = Testing.requires_k_seconds(8, ImpatientClientFauxPas)
        self.assertEqual(
                EBRetrier(ImpatientClientFauxPas).run(
                        operation, 2, 3, scale_factor=4),
                20)

    def test_base_class_success(self):
        operation = Testing.requires_k_seconds(8, ImpatientClientFauxPas)
        self.assertEqual(
                EBRetrier(EtiquetteBreach).run(
                        operation, 2, 3, scale_factor=4),
                20)

    def test_impatient_failure1(self):
        operation = Testing.requires_k_seconds(8, ImpatientClientFauxPas)
        with self.assertRaises(ImpatientClientFauxPas):
            EBRetrier(ImpatientClientFauxPas, max_tries=3).run(
                    operation, 2, 3, scale_factor=4)

    def test_impatient_failure2(self):
        operation = Testing.requires_k_attempts(11, ImpatientClientFauxPas)
        call_counter = 0
        with self.assertRaises(ImpatientClientFauxPas):

            def _try_counting():
                nonlocal call_counter
                try:
                    return operation(2, 3, scale_factor=4)
                finally:
                    call_counter += 1
            EBRetrier(
                    ImpatientClientFauxPas,
                    base=0.0125, ceiling=1, max_tries=10).run(_try_counting)
        self.assertEqual(
                call_counter,
                10,
                "called the function too few times(?)")


class TestWebRetrier(unittest.TestCase):

    def setup(self):
        self.e429 = HTTPError('error')
        self.e429.response = unittest.mock.MagicMock()
        self.e429.response.status_code = 429
        self.e429.response.header['retry-after'] = 0.1

    def test_eventual_success_webretrier(self):
        operation = Testing.requires_k_seconds(8, self.e429)
        self.assertEqual(
                WebRetrier(self.e429).run(
                        operation, 2, 3, scale_factor=4),
                20)
