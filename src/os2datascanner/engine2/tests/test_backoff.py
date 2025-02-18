from time import sleep
import pytest

from os2datascanner.engine2.utilities.backoff import (
        Testing, ExponentialBackoffRetrier as EBRetrier,
        TimeoutRetrier)


class EtiquetteBreach(Exception):
    pass


class ImpoliteClientFauxPas(EtiquetteBreach):
    pass


class ImpatientClientFauxPas(ImpoliteClientFauxPas):
    pass


class TestBackoff:
    def test_base_failure(self):
        with pytest.raises(ImpatientClientFauxPas):
            Testing.requires_k_seconds(8, ImpatientClientFauxPas)(
                    2, 3, scale_factor=4)

    def test_eventual_success(self):
        operation = Testing.requires_k_seconds(8, ImpatientClientFauxPas)
        assert EBRetrier(ImpatientClientFauxPas).run(operation, 2, 3, scale_factor=4) == 20

    def test_timeout_failure(self):
        with pytest.raises(TimeoutError):
            TimeoutRetrier(
                    seconds=5.0,
                    max_tries=2, warn_after=1).run(sleep, 6.0)

    def test_timeout_success(self):
        TimeoutRetrier(
                seconds=7.0,
                max_tries=2, warn_after=1).run(sleep, 6.0)

    def test_base_class_success(self):
        operation = Testing.requires_k_seconds(8, ImpatientClientFauxPas)
        assert EBRetrier(EtiquetteBreach).run(operation, 2, 3, scale_factor=4) == 20

    def test_impatient_failure1(self):
        operation = Testing.requires_k_seconds(8, ImpatientClientFauxPas)
        with pytest.raises(ImpatientClientFauxPas):
            EBRetrier(ImpatientClientFauxPas, max_tries=3).run(
                    operation, 2, 3, scale_factor=4)

    def test_impatient_failure2(self):
        operation = Testing.requires_k_attempts(11, ImpatientClientFauxPas)
        call_counter = 0
        with pytest.raises(ImpatientClientFauxPas):

            def _try_counting():
                nonlocal call_counter
                try:
                    return operation(2, 3, scale_factor=4)
                finally:
                    call_counter += 1
            EBRetrier(
                    ImpatientClientFauxPas,
                    base=0.0125, ceiling=1, max_tries=10).run(_try_counting)
        assert call_counter == 10
