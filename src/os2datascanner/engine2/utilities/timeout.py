"""
Module containing utilities for managing code execution timeouts.
"""
import signal
import logging
import warnings
import threading
import contextlib

from os2datascanner.engine2 import settings as engine2_settings

logger = logging.getLogger("os2datascanner.engine2.pipeline.run_stage")


class SignalAlarmException(BaseException):
    """
    Generic Exception for handling timeouts with SIGALRM.
    Primarily intented for internal use in the 'timeout' utility module.
    """


def _signal_timeout_handler(signum, frame):
    """
    Simply raises a SignalAlarmException which works as a timeout
    implementation with signal.alarm().
    The arguments 'signum' and 'frame' are required for registering
    the function as a signal handler, but they are unused.
    """
    raise SignalAlarmException()


def run_with_timeout(time_limit, fn, *args, **kwargs):
    """
    Runs the function 'fn' with '*args'.
    If the function does not finish within the 'time_limit',
    a SignalAlarmException is thrown and the function returns.
    """
    with _timeout(time_limit):
        try:
            return (True, fn(*args, **kwargs))
        except SignalAlarmException:
            return (False, None)


def run_with_default_timeout(fn, *args, **kwargs):
    """
    Utility wrapper for 'run_with_timeout'.

    Runs the function 'fn' with '*args'.
    If the function does not finish within the limit defined in the settings for engine2,
    a SignalAlarmException is raised and the function returns.
    """
    return run_with_timeout(engine2_settings.subprocess["timeout"], fn, *args, **kwargs)


_SIGNAL_FORBIDDEN = object()


def _timeout_start(seconds: float):
    """Arranges for a SignalAlarmException to be raised on the main thread at
    a certain number of seconds in the future. Every call to _timeout_start
    should be coupled with an eventual call to _timeout_stop to reset the
    signal handler to its previous state.

    Note that this function does nothing if"""
    if threading.main_thread() == threading.current_thread():
        handler = signal.signal(signal.SIGALRM, _signal_timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, seconds)
        return handler
    else:
        warnings.warn(
                "ignoring _timeout_start call on a background thread; the "
                "requested timeout will not be enforced",
                UserWarning, stacklevel=2)
        return _SIGNAL_FORBIDDEN


def _timeout_stop(handler):
    if handler != _SIGNAL_FORBIDDEN:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, handler)


def _compute_next(seconds, iterable):
    handler = None
    try:
        handler = _timeout_start(seconds)
        return (False, next(iterable))
    except SignalAlarmException:
        return (True, None)
    finally:
        _timeout_stop(handler)


def yield_from_with_timeout(time_limit, iterable):
    """
    Utility for wrapping lazy generators in timeout that forces eager evaluation.
    """
    result = []

    try:
        while True:
            (timeout, element) = _compute_next(time_limit, iterable)
            if not timeout:
                result.append(element)
            else:
                logger.warning("An object was skipped due to timeout.")
    except StopIteration:
        return result


def yield_from_with_default_timeout(iterable):
    return yield_from_with_timeout(engine2_settings.subprocess["timeout"], iterable)


@contextlib.contextmanager
def _timeout(seconds: float):
    """
    Uses signal.itimer() to set an alarm to send a SIGALRM after 'seconds' and then yields.
    If more than 'seconds' elapses, a SignalAlarmException is raised.
    Otherwise, the alarm is cancelled and the handler is removed.
    """
    if seconds is None:
        raise ValueError()

    if seconds <= 0:
        raise ValueError()

    original_handler = _timeout_start(seconds)

    try:
        yield
    except GeneratorExit:
        return
    finally:
        _timeout_stop(original_handler)
