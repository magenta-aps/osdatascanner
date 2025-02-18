"""
Unit test for the timeout module which is part of engine2's utilities.
"""
import time
import pytest
import threading
from os2datascanner.utils.timer import TimerManager


def run_with_timeout(seconds: float, func, *args, **kwargs):
    with TimerManager.get().timeout(seconds) as ctx:
        try:
            return (True, func(*args, **kwargs))
        except ctx.Timeout:
            return (False, None)


def yield_from_with_timeout(seconds: float, it):
    result = []

    ctx = TimerManager.get().timeout(seconds)

    try:
        while True:
            with ctx:
                result.append(next(it))
    except (ctx.Timeout, StopIteration):
        return result


class TestTimeoutLegacy:
    """
    Test case class for engine2.utilities.timeout module.
    """

    # SECTION: TimerManager.get().timeout

    def test_timeout_raises_sends_signal_when_expired(self):
        ctx = TimerManager.get().timeout(1)
        with pytest.raises(ctx.Timeout):
            with ctx:
                time.sleep(2)

    def test_timeout_cancels_alarm_in_due_time(self):
        result = 0
        with TimerManager.get().timeout(2):
            result += 1

        assert result == 1

    def test_timeout_raises_sends_signal_for_generators(self):
        ctx = TimerManager.get().timeout(1)

        def generator():
            for num in [1, 2, 3]:
                with ctx:
                    time.sleep(2)
                    yield num

        with pytest.raises(ctx.Timeout):
            list(generator())

    # END

    # SECTION: run_with_default_timeout

    def test_run_with_timeout_no_args_no_return_finishes_in_time(self):
        (_, result) = run_with_timeout(2, lambda: time.sleep(1))
        assert result is None

    def test_run_with_timeout_no_args_finishes_in_one_second(self):
        time_start = time.perf_counter()

        (finished, _) = run_with_timeout(2, lambda: time.sleep(1))

        time_elapsed = time.perf_counter() - time_start
        assert round(time_elapsed) == 1
        assert finished is True

    def test_run_with_timeout_no_args_retval_finishes_in_time(self):
        def func():
            time.sleep(1)
            return 1

        (finished, result) = run_with_timeout(2, func)

        assert finished is True
        assert result == 1

    def test_run_with_timeout_one_arg_retval_finishes_in_time(self):
        def func(seconds):
            time.sleep(seconds)
            return seconds

        seconds = 1

        (finished, result) = run_with_timeout(2, func, seconds)

        assert result == seconds
        assert finished is True

    def test_run_with_timeout_multiple_args_retval_finishes_in_time(self):
        def func(fst, snd):
            time.sleep(fst)
            return snd

        seconds = 1

        (finished, result) = run_with_timeout(2, func, seconds, seconds)

        assert result == seconds
        assert finished is True

    def test_run_with_timeout_with_generator(self):
        def func(elements):
            for element in elements:
                yield element*2

        elements = [1, 2]

        (finished, result) = run_with_timeout(1, func, elements)

        assert list(result) == [2, 4]
        assert finished is True

    def test_run_with_timeout_return_generator(self):
        def func(elements):
            for element in elements:
                yield element*2

        def generator():
            elements = [1, 2]
            (_, result) = run_with_timeout(1, func, elements)
            yield from result

        actual = generator()

        assert list(actual) == [2, 4]

    def test_run_with_timeout_no_args_no_return_raises_exception(self):
        time_start = time.perf_counter()

        (finished, _) = run_with_timeout(1, lambda: time.sleep(2))

        time_elapsed = time.perf_counter() - time_start
        assert round(time_elapsed) == 1
        assert finished is False

    def test_run_with_timeout_raises_exception_when_time_is_zero(self):
        with pytest.raises(ValueError):
            run_with_timeout(0, lambda: time.sleep(1))

    def test_run_with_timeout_raises_exception_when_time_is_negative(self):
        with pytest.raises(ValueError):
            run_with_timeout(-1, lambda: time.sleep(1))

    def test_run_with_timeout_raises_exception_when_time_is_none(self):
        with pytest.raises(ValueError):
            run_with_timeout(None, lambda: time.sleep(1))

    def test_run_with_timeout_raises_exception_when_time_is_invalid_type(self):
        with pytest.raises(TypeError):
            run_with_timeout("", lambda: time.sleep(1))

    # END

    # SECTION: yield_from_with_timeout

    def test_yield_from_with_timeout_succeeds_within_time_limit(self):
        def func(elements):
            for element in elements:
                time.sleep(1)
                yield element*2

        elements = [1, 2]

        result = list(yield_from_with_timeout(2, func(elements)))

        assert result == [2, 4]

    def test_yield_from_with_timeout_produces_half_of_the_results(self):
        def func(elements):
            for element in elements:
                time.sleep(element)
                yield element*2

        elements = [1, 2]

        result = list(yield_from_with_timeout(2, func(elements)))

        assert result == [2]

    def test_yield_from_with_timeout_generates_nothing_in_edge_case(self):
        def func(elements):
            for element in elements:
                time.sleep(1)
                yield element*2

        elements = [1, 2]

        result = list(yield_from_with_timeout(1, func(elements)))

        assert result == []

    def test_yield_from_with_timeout_generated_nothing_on_timeout(self):
        def func(elements):
            for element in elements:
                time.sleep(2)
                yield element*2

        elements = [1, 2]

        result = list(yield_from_with_timeout(1, func(elements)))

        assert result == []

    def test_yield_with_timeout_raises_exception_when_time_is_zero(self):
        def func(elements):
            for element in elements:
                time.sleep(2)
                yield element*2

        elements = [1, 2]

        with pytest.raises(ValueError):
            run_with_timeout(0, func(elements))

    def test_yield_with_timeout_raises_exception_when_time_is_negative(self):
        def func(elements):
            for element in elements:
                time.sleep(2)
                yield element*2

        elements = [1, 2]

        with pytest.raises(ValueError):
            run_with_timeout(-1, func(elements))

    def test_yield_with_timeout_raises_exception_when_time_is_none(self):
        def func(elements):
            for element in elements:
                time.sleep(2)
                yield element*2

        elements = [1, 2]

        with pytest.raises(ValueError):
            run_with_timeout(None, func(elements))

    def test_yield_with_timeout_raises_exception_when_time_is_invalid_type(self):
        def func(elements):
            for element in elements:
                time.sleep(2)
                yield element*2

        elements = [1, 2]

        with pytest.raises(TypeError):
            run_with_timeout("", func(elements))

    # END


@pytest.fixture(scope="session")
def tm():
    return TimerManager.get()


class TestTimerManager:
    def test_after_basic(self, tm):
        k = []
        tm.after(0.5, k.append, ":D")

        time.sleep(0.6)

        assert k == [":D"]

    def test_equal_time(self, tm):
        k = []
        time_now = time.time()
        in_half_second = time_now + 0.5

        tm.at(in_half_second, k.append, ":D")
        tm.at(in_half_second, k.append, ":O")

        time.sleep(0.6)

        # Timer doesn't guarantee order, when two operations are to be called at same time
        assert ":D" in k
        assert ":O" in k

    def test_pause(self, tm):
        k = []

        with tm.suspension(delay=False):
            tm.after(0.5, k.append, ":D")
            time.sleep(0.6)

            assert k == []

        time.sleep(0.1)
        assert k == [":D"]

    def test_timeout(self, tm):
        ctx = tm.timeout(0.3)

        with pytest.raises(ctx.Timeout), ctx:
            time.sleep(0.5)

    def test_no_timeout(self, tm):
        ctx = tm.timeout(0.3)

        with ctx:
            time.sleep(0.1)

    def wait_and_ret(self, k):
        time.sleep(k / 10)
        return k * 2

    def test_timeout_yield(self, tm):
        ctx = tm.timeout(0.35)

        with pytest.raises(ctx.Timeout):
            generator = (self.wait_and_ret(k) for k in [1, 2, 3, 4])
            list(ctx.yield_all(generator))

    def test_yield(self, tm):
        ctx = tm.timeout(0.35)

        generator = (self.wait_and_ret(k) for k in [1, 2, 3, 4])
        assert list(ctx.yield_some(generator)) == [2, 4, 6]

    def test_after_complicated(self, tm):
        """Four functions scheduled to be called in a strange order are
        nonetheless called in the right order."""
        condition = threading.Condition()

        def _notify():
            with condition:
                condition.notify()

        chunks = []

        tm.pause()
        tm.after(0.4, chunks.append, "! :D")
        tm.after(0.1, chunks.append, "Hello")
        tm.after(0.3, chunks.append, "world")
        tm.after(0.2, chunks.append, ", ")
        tm.after(0.5, _notify)

        tm.resume()
        with condition:
            condition.wait()

        assert "".join(chunks) == "Hello, world! :D"

    def test_nesting_outer(self, tm):
        """If an outer timeout expires before an inner one, the outer timeout's
        distinguishable exception is raised."""
        with (tm.timeout(0.1) as ctx,
              tm.timeout(0.5)):
            with pytest.raises(ctx.Timeout):
                time.sleep(0.2)

    def test_nesting_inner(self, tm):
        """If an inner timeout expires before an outer one, the inner timeout's
        distinguishable exception is raised."""
        with (tm.timeout(0.5),
              tm.timeout(0.1) as cty):
            with pytest.raises(cty.Timeout):
                time.sleep(0.2)
