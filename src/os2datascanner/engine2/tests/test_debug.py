import signal
import pytest


from os2datascanner.utils.debug import (
        backtrace_dbg_func, debug_helper, add_debug_function,
        remove_debug_function, register_debug_signal)


class Counter:
    def __init__(self):
        self._count = 0

    def incr(self, *args, **kwargs):
        self._count += 1

    def __int__(self):
        return self._count


@pytest.fixture(autouse=True, scope="class")
def setup():
    register_debug_signal(signal.SIGTRAP)
    remove_debug_function(backtrace_dbg_func)


class TestDebug:
    def test_debug_function(self):
        """Functions can be registered as debug functions."""

        counter = Counter()
        add_debug_function(counter.incr)

        signal.raise_signal(signal.SIGTRAP)
        signal.raise_signal(signal.SIGTRAP)

        assert int(counter) == 2, "debug function not called"

    def test_debug_helper(self):
        """Functions can be temporarily registered as debug functions."""
        counter = Counter()
        with debug_helper(counter.incr):
            signal.raise_signal(signal.SIGTRAP)
            assert int(counter) == 1, "debug function not called"
        signal.raise_signal(signal.SIGTRAP)
        assert int(counter) == 1, "debug function called after deregistration"

    def test_nested_debug_helpers(self):
        """Several functions can be temporarily registered as debug functions
        at the same time."""
        c1, c2 = Counter(), Counter()
        with debug_helper(c1.incr):
            signal.raise_signal(signal.SIGTRAP)  # c1 incremented
            with debug_helper(c2.incr):
                signal.raise_signal(signal.SIGTRAP)  # c1 and c2 incremented

        signal.raise_signal(signal.SIGTRAP)  # neither counter incremented

        assert int(c1) == 2, "nested debug functions not called correctly"
        assert int(c2) == 1, "nested debug functions not called correctly"
