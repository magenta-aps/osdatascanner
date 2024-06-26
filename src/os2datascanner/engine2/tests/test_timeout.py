"""
Unit test for the timeout module which is part of engine2's utilities.
"""
import time
import unittest
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


class TestTimeoutLegacy(unittest.TestCase):
    """
    Test case class for engine2.utilities.timeout module.
    """

    # SECTION: TimerManager.get().timeout

    def test_timeout_raises_sends_signal_when_expired(self):
        ctx = TimerManager.get().timeout(1)
        with self.assertRaises(ctx.Timeout):
            with ctx:
                time.sleep(2)

    def test_timeout_cancels_alarm_in_due_time(self):
        result = 0
        with TimerManager.get().timeout(2):
            result += 1

        self.assertEqual(1, result)

    def test_timeout_raises_sends_signal_for_generators(self):
        ctx = TimerManager.get().timeout(1)

        def generator():
            for num in [1, 2, 3]:
                with ctx:
                    time.sleep(2)
                    yield num

        with self.assertRaises(ctx.Timeout):
            list(generator())

    # END

    # SECTION: run_with_default_timeout

    def test_run_with_timeout_no_args_no_return_finishes_in_time(self):
        (_, result) = run_with_timeout(2, lambda: time.sleep(1))
        self.assertEqual(None, result)

    def test_run_with_timeout_no_args_finishes_in_one_second(self):
        time_start = time.perf_counter()

        (finished, _) = run_with_timeout(2, lambda: time.sleep(1))

        time_elapsed = time.perf_counter() - time_start
        self.assertEqual(1, round(time_elapsed))
        self.assertTrue(finished)

    def test_run_with_timeout_no_args_retval_finishes_in_time(self):
        def func():
            time.sleep(1)
            return 1

        (finished, result) = run_with_timeout(2, func)

        self.assertTrue(finished)
        self.assertEqual(1, result)

    def test_run_with_timeout_one_arg_retval_finishes_in_time(self):
        def func(seconds):
            time.sleep(seconds)
            return seconds

        seconds = 1

        (finished, result) = run_with_timeout(2, func, seconds)

        self.assertEqual(seconds, result)
        self.assertTrue(finished)

    def test_run_with_timeout_multiple_args_retval_finishes_in_time(self):
        def func(fst, snd):
            time.sleep(fst)
            return snd

        seconds = 1

        (finished, result) = run_with_timeout(2, func, seconds, seconds)

        self.assertEqual(seconds, result)
        self.assertTrue(finished)

    def test_run_with_timeout_with_generator(self):
        def func(elements):
            for element in elements:
                yield element*2

        elements = [1, 2]

        (finished, result) = run_with_timeout(1, func, elements)

        self.assertEqual([2, 4], list(result))
        self.assertTrue(finished)

    def test_run_with_timeout_return_generator(self):
        def func(elements):
            for element in elements:
                yield element*2

        def generator():
            elements = [1, 2]
            (_, result) = run_with_timeout(1, func, elements)
            yield from result

        actual = generator()

        self.assertEqual([2, 4], list(actual))

    def test_run_with_timeout_no_args_no_return_raises_exception(self):
        time_start = time.perf_counter()

        (finished, _) = run_with_timeout(1, lambda: time.sleep(2))

        time_elapsed = time.perf_counter() - time_start
        self.assertEqual(1, round(time_elapsed))
        self.assertFalse(finished)

    def test_run_with_timeout_raises_exception_when_time_is_zero(self):
        with self.assertRaises(ValueError):
            run_with_timeout(0, lambda: time.sleep(1))

    def test_run_with_timeout_raises_exception_when_time_is_negative(self):
        with self.assertRaises(ValueError):
            run_with_timeout(-1, lambda: time.sleep(1))

    def test_run_with_timeout_raises_exception_when_time_is_none(self):
        with self.assertRaises(ValueError):
            run_with_timeout(None, lambda: time.sleep(1))

    def test_run_with_timeout_raises_exception_when_time_is_invalid_type(self):
        with self.assertRaises(TypeError):
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

        self.assertEqual([2, 4], result)

    def test_yield_from_with_timeout_produces_half_of_the_results(self):
        def func(elements):
            for element in elements:
                time.sleep(element)
                yield element*2

        elements = [1, 2]

        result = list(yield_from_with_timeout(2, func(elements)))

        self.assertEqual([2], result)

    def test_yield_from_with_timeout_generates_nothing_in_edge_case(self):
        def func(elements):
            for element in elements:
                time.sleep(1)
                yield element*2

        elements = [1, 2]

        result = list(yield_from_with_timeout(1, func(elements)))

        self.assertEqual([], result)

    def test_yield_from_with_timeout_generated_nothing_on_timeout(self):
        def func(elements):
            for element in elements:
                time.sleep(2)
                yield element*2

        elements = [1, 2]

        result = list(yield_from_with_timeout(1, func(elements)))

        self.assertEqual([], result)

    def test_yield_with_timeout_raises_exception_when_time_is_zero(self):
        def func(elements):
            for element in elements:
                time.sleep(2)
                yield element*2

        elements = [1, 2]

        with self.assertRaises(ValueError):
            run_with_timeout(0, func(elements))

    def test_yield_with_timeout_raises_exception_when_time_is_negative(self):
        def func(elements):
            for element in elements:
                time.sleep(2)
                yield element*2

        elements = [1, 2]

        with self.assertRaises(ValueError):
            run_with_timeout(-1, func(elements))

    def test_yield_with_timeout_raises_exception_when_time_is_none(self):
        def func(elements):
            for element in elements:
                time.sleep(2)
                yield element*2

        elements = [1, 2]

        with self.assertRaises(ValueError):
            run_with_timeout(None, func(elements))

    def test_yield_with_timeout_raises_exception_when_time_is_invalid_type(self):
        def func(elements):
            for element in elements:
                time.sleep(2)
                yield element*2

        elements = [1, 2]

        with self.assertRaises(TypeError):
            run_with_timeout("", func(elements))

    # END


class TestTimerManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tm = TimerManager.get()

    def test_after_basic(self):
        k = []
        self.tm.after(0.5, k.append, ":D")

        time.sleep(0.6)

        self.assertEqual(
                k,
                [":D"])

    def test_equal_time(self):
        k = []
        time_now = time.time()
        in_half_second = time_now + 0.5

        self.tm.at(in_half_second, k.append, ":D")
        self.tm.at(in_half_second, k.append, ":O")

        time.sleep(0.6)

        # Timer doesn't guarantee order, when two operations are to be called at same time
        self.assertTrue(":D" in k and ":O" in k)

    def test_pause(self):
        k = []

        with self.tm.suspension(delay=False):
            self.tm.after(0.5, k.append, ":D")
            time.sleep(0.6)

            self.assertEqual(
                    k,
                    [])

        time.sleep(0.1)
        self.assertEqual(
                k,
                [":D"])

    def test_timeout(self):
        ctx = self.tm.timeout(0.3)

        with (self.subTest(),
                self.assertRaises(ctx.Timeout),
                ctx):
            time.sleep(0.5)

        with (self.subTest(),
                ctx):
            time.sleep(0.1)

    def test_timeout_yield(self):
        def wait_and_ret(k):
            time.sleep(k / 10)
            return k * 2

        ctx = self.tm.timeout(0.35)

        with (self.subTest(),
                self.assertRaises(ctx.Timeout)):
            generator = (wait_and_ret(k) for k in [1, 2, 3, 4])
            list(ctx.yield_all(generator))

        with self.subTest():
            generator = (wait_and_ret(k) for k in [1, 2, 3, 4])
            self.assertEqual(
                    list(ctx.yield_some(generator)),
                    [2, 4, 6])

    def test_after_complicated(self):
        """Four functions scheduled to be called in a strange order are
        nonetheless called in the right order."""
        condition = threading.Condition()

        def _notify():
            with condition:
                condition.notify()

        chunks = []

        self.tm.pause()
        self.tm.after(0.4, chunks.append, "! :D")
        self.tm.after(0.1, chunks.append, "Hello")
        self.tm.after(0.3, chunks.append, "world")
        self.tm.after(0.2, chunks.append, ", ")
        self.tm.after(0.5, _notify)

        self.tm.resume()
        with condition:
            condition.wait()

        self.assertEqual(
                "".join(chunks),
                "Hello, world! :D")

    def test_nesting_outer(self):
        """If an outer timeout expires before an inner one, the outer timeout's
        distinguishable exception is raised."""
        with (self.tm.timeout(0.1) as ctx,
              self.tm.timeout(0.5)):
            with self.assertRaises(ctx.Timeout):
                time.sleep(0.2)

    def test_nesting_inner(self):
        """If an inner timeout expires before an outer one, the inner timeout's
        distinguishable exception is raised."""
        with (self.tm.timeout(0.5),
              self.tm.timeout(0.1) as cty):
            with self.assertRaises(cty.Timeout):
                time.sleep(0.2)
