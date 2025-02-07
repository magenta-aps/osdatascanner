from abc import abstractmethod
from enum import Enum
import json
from typing import Union, Optional, Tuple, Iterator, Callable, Any, Iterable
from itertools import islice

from .utilities.properties import RulePrecedence, RuleProperties
from ..utilities.json import JSONSerialisable
from ..utilities.equality import TypePropertyEquality
from ..conversions.types import OutputType


class Sensitivity(Enum):
    """Rules have an optional property called "sensitivity", whose values are
    given by the Sensitivity enumeration. This property has no particular
    significance for the rule engine, but user interfaces might wish to present
    matches differently based on it."""
    INFORMATION = 0
    NOTICE = 250
    WARNING = 500
    PROBLEM = 750
    CRITICAL = 1000

    @staticmethod
    def make_from_dict(obj):
        if "sensitivity" in obj and obj["sensitivity"] is not None:
            return Sensitivity(obj["sensitivity"])
        else:
            return None

    @property
    def presentation(self):
        """Returns a (perhaps localised) human-readable string representing
        this Rule, for use in user interfaces."""
        # XXX: interim hack
        return sensitivity_labels["da"].get(self, self.name)


# XXX: this is a hack that should be replaced by real translation support once
# we get that sorted out
sensitivity_labels = {
    "da": {
        Sensitivity.INFORMATION: "Information",
        Sensitivity.NOTICE: "Notifikation",
        Sensitivity.WARNING: "Advarsel",
        Sensitivity.PROBLEM: "Problem",
        Sensitivity.CRITICAL: "Kritisk"
    }
}


class Rule(TypePropertyEquality, JSONSerialisable):
    """A Rule represents a test to be applied to a representation of an
    object.

    Rules cannot necessarily be evaluated directly, but they can always be
    broken apart to find an evaluable component; see the split() and
    try_match() methods.

    If you're not sure which class your new rule should inherit from, then use
    SimpleRule."""
    properties = RuleProperties(
        precedence=RulePrecedence.UNDEFINED,
        standalone=True)

    def __init__(self, *, sensitivity=None, name=None):
        self._sensitivity = sensitivity
        self._name = name

    @property
    def presentation(self) -> str:
        """Returns a (perhaps localised) human-readable string representing
        this Rule, for use in user interfaces."""
        return self._name or self.presentation_raw

    @property
    @abstractmethod
    def presentation_raw(self) -> str:
        """Returns a presentation form of this Rule based on its properties."""

    @property
    def sensitivity(self) -> Optional[Sensitivity]:
        """Returns the sensitivity value of this Rule, if one was specified."""
        return self._sensitivity

    @property
    @abstractmethod
    def type_label(self) -> str:
        """A label that will be used to identify JSON forms of this Rule."""

    @abstractmethod
    def split(self) -> Tuple['SimpleRule',
                             Union['SimpleRule', bool], Union['SimpleRule', bool]]:
        """Splits this Rule.

        Splitting a Rule produces a SimpleRule, suitable for immediate
        evaluation, and two continuation Rules. The first of these, the
        positive continuation, is the Rule that should be executed next if the
        SimpleRule finds a match; the second, the negative continuation, should
        be executed if no match was found.

        (Following a chain of continuations will always eventually reduce to
        True, if the rule as a whole has matched, or False if it has not.)"""

    def try_match(
            self,
            get_representation: Union[Callable[[str], Optional[Any]], dict],
            *, obj_limit=None):
        """Reduces this Rule as much as possible, given a helper function that
        can (attempt to) produce new representations when required. When the
        content of a representation is not available, the helper function
        should raise a KeyError. (For convenience, this function also accepts a
        dictionary; in this case it'll use its __getitem__ method.)

        Returns the (possibly trivial) continuation left over, along with a
        list of [(SimpleRule, list of match object)] pairs representing the
        rules that were executed by this method and their results. (By default,
        all of the match objects yielded by each SimpleRule will be collected;
        if you don't care about getting them all, you can set a cut-off with
        the obj_limit keyword argument to improve performance.)

        Note that this method can optimise the reduction of this Rule; the
        result of a SimpleRule might be cached and reused, for example."""
        if isinstance(get_representation, dict):
            get_representation = get_representation.__getitem__

        here = self
        matches = {}
        while not isinstance(here, bool):
            head, pve, nve = here.split()
            try:
                required_form = get_representation(head.operates_on.value)
            except KeyError:
                # Our helper callback can't produce the data we need. Stop
                # evaluating rules and return what we have to the caller
                break
            if head not in matches:
                matches[head] = list(
                        islice(head.match(required_form), obj_limit))
            here = pve if matches[head] else nve
        return (here, list(matches.items()))

    @abstractmethod
    def flatten(self) -> set['SimpleRule']:
        """Reduces this Rule to the set of SimpleRules that it references."""

    _json_handlers = {}

    @abstractmethod
    def to_json_object(self):
        """Returns an object suitable for JSON serialisation that represents
        this Rule."""
        return {
            "type": self.type_label,
            "sensitivity": self.sensitivity.value if self.sensitivity else None,
            "name": self._name
        }

    def __str__(self):
        return self.presentation

    def __repr__(self):
        return (f"Rule.from_json_object("
                f"{json.dumps(self.to_json_object())})")


class SimpleRule(Rule):
    """A SimpleRule is a rule that can be evaluated. Splitting it produces the
    trivial positive and negative continuations True and False.

    If you're not sure which class your new rule should inherit from, then use
    this one."""

    def split(self):
        return self, True, False

    @property
    @abstractmethod
    def operates_on(self) -> OutputType:
        """The type of input expected by this SimpleRule."""

    @abstractmethod
    def match(self, content) -> Iterator[dict]:
        """Yields zero or more dictionaries suitable for JSON serialisation,
        each of which represents one match of this SimpleRule against the
        provided content. Matched content should appear under the dictionary's
        "match" key."""

    def flatten(self):
        return {self}


class SimpleTextRule(SimpleRule):
    """A SimpleTextRule is a SimpleRule that operates on text."""
    operates_on = OutputType.Text

    @abstractmethod
    def get_censor_intervals(self, context: str) -> Iterable[tuple[int, int]]:
        """Given context for a match, returns an iterable of intervals that should be censored.
        Intervals should be left-inclusive and right-exclusive"""
        return []
