import typing


class Counter:
    """A Counter is a trivial increment-only wrapper around an integer value.
    (It's intended for use as an optional argument to generators so they can
    indicate to their caller how many values they have yielded.)"""

    def __init__(self, value: int = 0):
        self._value = value

    def incr(self):
        """Increments the counter."""
        self._value += 1

    def __int__(self):
        return self._value

    def __bool__(self):
        return bool(int(self))

    @classmethod
    def try_incr(cls, v: typing.Optional['Counter']):
        """Increments the given Counter (or does nothing, if given None)."""
        if v is not None:
            v.incr()
