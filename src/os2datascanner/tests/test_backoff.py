from time import time
import unittest

from os2datascanner.engine2.utilities.backoff import run_with_backoff


class EtiquetteBreach(Exception):
    pass


class ImpoliteClientFauxPas(EtiquetteBreach):
    pass


class ImpatientClientFauxPas(ImpoliteClientFauxPas):
    pass


class TestBackoff(unittest.TestCase):
    def setUp(self):
        self.reset_busy_time()

    def fail_if_too_busy(self):
        now = time()
        try:
            if now - self.last_call_at < 7:
                raise ImpatientClientFauxPas()
            else:
                return "Successful result"
        finally:
            self.last_call_at = now

    def reset_busy_time(self):
        self.last_call_at = time()

    def test_base_failure(self):
        with self.assertRaises(ImpatientClientFauxPas):
            self.fail_if_too_busy()

    def test_eventual_success(self):
        self.assertEqual(
                run_with_backoff(
                        self.fail_if_too_busy, ImpatientClientFauxPas)[0],
                "Successful result")

    def test_base_class_success(self):
        self.assertEqual(
                run_with_backoff(
                        self.fail_if_too_busy, EtiquetteBreach)[0],
                "Successful result")

    def test_impatient_failure1(self):
        with self.assertRaises(ImpatientClientFauxPas):
            run_with_backoff(
                    self.fail_if_too_busy, ImpatientClientFauxPas,
                    max_tries=3)

    def test_impatient_failure2(self):
        with self.assertRaises(ImpatientClientFauxPas):
            run_with_backoff(
                    self.fail_if_too_busy, ImpatientClientFauxPas,
                    base=0.0125)

    def test_memory(self):
        first_start = time()
        # This call should take ~15 (1+2+4+8) seconds, and we should succeed
        # after first backing off four times
        result, params = run_with_backoff(
                self.fail_if_too_busy, ImpatientClientFauxPas)
        first_duration = time() - first_start
        self.assertEqual(
                params["count"],
                4)

        self.reset_busy_time()

        # Now that we have those results (i.e., now that we don't need to try
        # backoff durations of 1, 2, and 4 seconds), we should always be able
        # to finish more quickly (in ~8 seconds)
        second_start = time()
        run_with_backoff(
                self.fail_if_too_busy, ImpatientClientFauxPas, **params)
        second_duration = time() - second_start

        # Strictly speaking we should be 7 seconds faster, but saying 6 gives
        # us a 14% margin of error in case the CI system is having a tough day
        self.assertTrue(
                (second_duration + 6) < first_duration,
                "learned backoff slower than naive backoff(?)")
