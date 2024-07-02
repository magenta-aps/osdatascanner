import operator
from functools import reduce

from ..rule import Rule, SimpleRule
from ..logical import OrRule, AndRule, NotRule, CompoundRule


def compute_mss(r: Rule | None) -> set[SimpleRule]:
    """Computes the (possibly empty) minimal set of SimpleRules that must match
    for the given Rule as a whole to match."""
    match r:
        case None:  # For convenience
            return set()
        case AndRule(components=cs):
            c_sets = [compute_mss(c) for c in cs]
            return reduce(operator.or_, c_sets, set())
        case OrRule(components=cs):
            head_set, *tail_sets = [compute_mss(c) for c in cs]
            return reduce(operator.and_, tail_sets, head_set)
        case CompoundRule():
            raise ValueError(
                    f"Don't know what conjunction to use for CompoundRule {r}")
        case NotRule():
            # It's not (ha!) entirely clear how best to support negation here,
            # so let's just not for now
            return set()
        case SimpleRule():
            return {r}
        case str():  # only for testing
            return {r}
        case _:
            raise ValueError(
                    f"Rule fragment {r} was not recognised")
