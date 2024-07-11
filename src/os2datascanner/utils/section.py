class ReentrableSection:
    """A ReentrableSection is a fancy counter wrapped in a context manager:
    entering the context increments the counter, and leaving it decrements it.
    (It can also be used as a decorator to force a function to always execute
    in the context.)

    The intention of this class is to enable something like the "critical
    section" pattern, where unexpected side-effects or inputs from the outside
    world are suppressed under the section."""

    def __init__(self):
        self._entry_count = 0

    @property
    def count(self) -> int:
        return self._entry_count

    def wrap(self, func):
        def _wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return _wrapper

    def __call__(self, func):
        return self.wrap(func)

    def __bool__(self) -> bool:
        return self.count != 0

    def __enter__(self):
        self._entry_count += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._entry_count -= 1


"""Enter the suppress_django_signals section to stop the administration system
from reacting to Django signals. (Useful when you're preparing a transaction
object and don't want operations to be duplicated.)"""
suppress_django_signals = ReentrableSection()
