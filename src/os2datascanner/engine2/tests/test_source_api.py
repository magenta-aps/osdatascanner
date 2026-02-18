import types
import pytest
from typing import Iterator
from inspect import isabstract

from os2datascanner.engine2.model.core import Source


def enumerate_all_subclasses(c: type) -> Iterator[type]:
    for sc in c.__subclasses__():
        yield sc
        yield from enumerate_all_subclasses(sc)


class TestSourceAPI:
    @pytest.mark.parametrize(
            "source_type",
            [k for k in enumerate_all_subclasses(Source) if not isabstract(k)])
    def test_parameter_ignoring(self, source_type):
        """All concrete implementations of Source.handles ignore any keyword
        arguments they don't support."""
        assert isinstance(
                source_type.handles(
                        strange_and_alien_keyword_argument=4,
                        nothing_supports_this="i swear",
                        biscuit_count=2 ** 32,

                        # We're never going to iterate over this generator, so
                        # dummy values of self and sm are fine
                        self=None, sm=None),
                types.GeneratorType)
