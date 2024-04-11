from time import time, sleep
import bisect
import signal
import logging
import threading


logger = logging.getLogger(__name__)


def _throw(ex, *args, **kwargs):
    """Raises an instance of the given exception type, optionally passing
    positional and/or keyword arguments to its constructor."""
    match args, kwargs:
        case (), {} as d if not d:
            raise ex
        case _, {} as d if not d:
            raise ex(*args)
        case (), _:
            raise ex(**kwargs)
        case _, _:
            raise ex(*args, **kwargs)


class TimerManager:
    """A TimerManager object is a multiplexer for the SIGALRM/signal.setitimer
    infrastructure, allowing many callers to schedule functions to be called at
    arbitrary points in the future -- or to cancel those calls if they're no
    longer required.

    Internally, a TimeManager maintains a queue of future function calls
    ordered by the UNIX timestamp after which they are candidates for
    execution. Amongst other things, this means that functions can be scheduled
    in any order:

    >>> tm = TimerManager.get()
    >>> tm.after(4, print, "!")
    <TimerManager.Cookie object at 0x7f4fc0bbd150>
    >>> tm.after(2, print, ", ", end="")
    <TimerManager.Cookie object at 0x7f4fc0bbd180>
    >>> tm.after(3, print, "world", end="")
    <TimerManager.Cookie object at 0x7f7372c081b0>
    >>> tm.after(1, print, "\nHello", end="")
    <TimerManager.Cookie object at 0x7f7372c081e0>
    >>> time.sleep(5)
    Hello, world!
    >>>"""

    __key = object()
    _Singleton = None

    @classmethod
    def get(cls):
        """Returns the unique TimerManager singleton, creating it if necessary.

        As signal handlers can only execute in the scope of the main thread,
        this function will return a dummy TimerManager instance that doesn't do
        anything if called on a background thread."""
        if threading.main_thread() != threading.current_thread():
            return DummyTimerManager(key=cls.__key)

        if not cls._Singleton:
            cls._Singleton = TimerManager(key=cls.__key)
        return cls._Singleton

    class Cookie:
        """A TimerManager.Cookie is an opaque object used to identify a
        function scheduled for execution by a TimerManager."""
        __slots__ = ()

    def __init__(self, *, key):
        if key is not self.__key:  # noqa
            raise TypeError

        self.stack = []
        self._pauses = []

        self._install_handler()

    def _install_handler(self):
        # Cancel any other itimer that may be running
        self._deschedule()

        return signal.signal(signal.Signals.SIGALRM, self._handler)

    def _setitimer_real(self, seconds: float):
        return signal.setitimer(signal.ITIMER_REAL, seconds)

    def _handler(self, signum, frame):
        """Handles the SIGALRM signal by checking if the functions at the head
        of the queue are ready to be called, and calling them in order if they
        are.

        If one of the functions called raises an exception, then it'll be
        allowed to bubble up, although in all cases the signal handler will
        attempt to reschedule itself for execution again."""
        try:
            while self.stack:
                (ts, op, args, kwargs, _) = self.stack[-1]
                if ts <= time():
                    self.stack.pop()
                    op(*args, **kwargs)
                else:
                    break
        finally:
            self._reschedule()

    @property
    def fires_at(self) -> float:
        """Returns the (floating-point) UNIX timestamp at which this
        TimerManager's next function call is scheduled."""
        match self.stack:
            case (*_, (ts, _, _, _, _)):
                return ts
            case _:
                return None

    @property
    def fires_in(self) -> float:
        """Returns the number of seconds in which this TimerManager's next
        function call is scheduled."""
        match self.fires_at:
            case float(ts):
                return ts - time()
            case _:
                return None

    def at(self, ts: float, op, *args, **kwargs) -> 'Cookie':
        """Arranges for this TimerManager to call a function no earlier than
        the given UNIX timestamp. (Any other positional and keyword arguments
        to this function will be passed to the function at that point.)

        Only one-shot functions are supported, although nothing prevents a
        function from scheduling another one-shot function for execution.

        The return value is a magic cookie suitable for passing to the cancel()
        method."""
        if ts is None or ts < time():
            raise ValueError

        self._deschedule()
        try:
            cookie = self.Cookie()

            # Scope for optimisation here: bisect.insort() finds the position
            # at which to insert the object in O(log n) time, but list.insert
            # still takes O(n). Groan...
            bisect.insort(
                    self.stack,
                    (ts, op, args, kwargs, cookie),
                    key=lambda entry: -entry[0])

            return cookie
        finally:
            self._reschedule()

    def after(self, seconds: float, op, *args, **kwargs) -> 'Cookie':
        """Arranges for this TimerManager to call a function in no less than
        the given number of seconds. (This method is a convenience wrapper
        around the at() method.)"""
        if seconds is None:
            raise ValueError
        return self.at(time() + seconds, op, *args, **kwargs)

    def delay(self, seconds: float):
        """Delays all scheduled function calls by the given number of
        seconds."""
        if seconds < 0:
            raise ValueError

        self._deschedule()
        try:
            # Rewriting the entire stack isn't ideal, but the alternative is
            # either a fancy data structure or a writable daataclass for the
            # sake of updating one field
            self.stack = [
                (ts + seconds, op, args, kwargs, cookie)
                for ts, op, args, kwargs, cookie in self.stack]
        finally:
            self._reschedule()

    def pause(self):
        """Suspends the timer interrupt until a paired call to the resume()
        method."""
        self._deschedule()
        self._pauses.append(time())

    def resume(self, delay=True):
        """Resumes the timer interrupt after a previous call to the pause()
        method.

        The optional delay parameter controls whether or not scheduled function
        calls should be postponed by the duration of the pause."""
        match len(self._pauses):
            case 0:
                raise AssertionError(
                        "TimerManager.resume() called without first calling"
                        " .pause()!")
            case 1:
                first_paused_at = self._pauses.pop()
                if delay is True:
                    # Work out how many seconds we were paused for...
                    seconds = time() - first_paused_at
                    # ... push back all of the timed calls by that long...
                    self.delay(seconds)
                # ... and finally clear the pause bookkeeping and resume the
                # timer
                self._reschedule()
            case _:
                self._pauses.pop()

    def cancel(self, cookie: 'Cookie') -> bool:
        """Given a cookie representing a previous call to the at() or after()
        methods, cancels the corresponding function call. The return value
        indicates whether or not the cookie identified a live call."""
        self._deschedule()
        try:
            for idx, (_, _, _, _, c) in enumerate(self.stack):
                if cookie is c:
                    del self.stack[idx]
                    return True
            else:
                return False
        finally:
            self._reschedule()

    def _reschedule(self):
        """Schedules the SIGALRM signal to be delivered at the next relevant
        time by configuring a one-shot timer against the system clock."""
        if self._pauses:
            return

        match self.fires_in:
            case float(seconds):
                # It's possible that the next function should have been
                # executed in the past. Avoid passing a negative number to
                # setitimer() by arbitrarily picking a delay of 0.1 seconds
                # in that case
                adjusted = max(seconds, 0.1)
                self._setitimer_real(adjusted)
            case None:
                pass

    def _deschedule(self):
        """Cancels the SIGALRM signal scheduled by a previous call to
        _reschedule (or by any other call to signal.setitimer)."""
        self._setitimer_real(0)

    class _Timeout:
        class __Timeout(Exception):
            pass

        __exception_pool = []

        def __init__(self, parent: 'TimerManager', seconds: float):
            self.parent = parent
            self.seconds = seconds
            self.cookie = None
            self.Timeout = type("Timeout", (self.__Timeout,), {})

        def wrap(self, func):
            """Decorator. Returns a function that enters this context manager
            before calling the given function."""
            def _wrapper(*args, **kwargs):
                with self:
                    return func(*args, **kwargs)
            return _wrapper
        __call__ = wrap

        def yield_one(self, iterator):
            """Yields an element from the given iterator under this context
            manager. (That is, each tick of the iterator is subject to the
            timeout of this object.)"""
            try:
                with self:
                    yield next(iterator)
            except StopIteration:
                pass

        def yield_all(self, iterator):
            """Repeatedly yields the result of calling yield_one. In the event
            that a Timeout exception is raised, this will propagate to the
            caller."""
            try:
                while True:
                    yield from self.yield_one(iterator)
            except StopIteration:
                pass

        def yield_some(self, iterator):
            """As yield_all, except that a Timeout exception just interrupts
            the iteration without propagating the exception further."""
            try:
                while True:
                    yield from self.yield_one(iterator)
            except (self.Timeout, StopIteration):
                pass

        def __enter__(self):
            self.cookie = self.parent.after(self.seconds, _throw, self.Timeout)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            try:
                self.parent.cancel(self.cookie)
            finally:
                self.cookie = None

    def timeout(self, seconds: float):
        """Returns a context manager that will exit with an exception if the
        context doesn't complete in the given period of time. (The exception
        type is given in the return value's "Timeout" field.)

        The context manager can also be used as a decorator."""
        return self._Timeout(self, seconds)

    class _Suspension:
        def __init__(self, parent: 'TimerManager', delay):
            self.parent = parent
            self.delay = delay

        def wrap(self, func):
            def _wrapper(*args, **kwargs):
                with self:
                    return func(*args, **kwargs)
            return _wrapper
        __call__ = wrap

        def sleep(self, seconds):
            """Runs time.sleep() under this context manager. (That is,
            scheduled function calls will be paused and optionally delayed for
            the sleep duration.)"""
            with self:
                sleep(seconds)

        def __enter__(self):
            self.parent.pause()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.parent.resume(self.delay)

    def suspension(self, delay=True):
        """Returns a context manager that pauses all scheduled function calls
        until context completion.

        The context manager can also be used as a decorator."""
        return self._Suspension(self, delay)


class DummyTimerManager(TimerManager):
    def _install_handler(self):
        logger.warning(
                "attempted to get a TimerManager on a non-main thread:"
                " not enforcing timeout operations")

    def _setitimer_real(self, _):
        pass
