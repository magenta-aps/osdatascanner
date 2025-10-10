from . import logical
from .rule import Rule


def __or(self, rhs):
    match rhs:
        case Rule():
            return logical.OrRule.make(self, rhs)
        case _:
            return NotImplemented


def __and(self, rhs):
    match rhs:
        case Rule():
            return logical.AndRule.make(self, rhs)
        case _:
            return NotImplemented


def __invert(self):
    return logical.NotRule.make(self)


Rule.__or__ = Rule.__ror__ = __or
Rule.__and__ = Rule.__rand__ = __and
Rule.__invert__ = __invert


def make_repr(joiner):
    def __repr(self):
        return "(" + joiner.join([repr(c) for c in self._components]) + ")"
    return __repr


logical.AndRule.__repr__ = make_repr(" & ")
logical.OrRule.__repr__ = make_repr(" | ")
