import warnings
import structlog

from ...conversions.types import OutputType
from ..wordlists import OrderedWordlistRule
from ..rule import Rule, SimpleRule, Sensitivity
# from os2ds_rules.wordlist_rule import WordListRule

logger = structlog.get_logger("engine2")


class TurboHealthRule(SimpleRule):
    type_label = "health_turbo"
    operates_on = OutputType.Text

    def __init__(self, **super_kwargs):
        super().__init__(**super_kwargs)
        warnings.warn(
                "TurboHealthRule: WordListRule does not support Python 3.12+"
                " properly, using OrderedWordlistRule as the backend instead")
        self._rule = OrderedWordlistRule("da_20211018_laegehaandbog_stikord")

    def __getattr__(self, attr):
        return getattr(self._rule, attr)

    def match(self, *args, **kwargs):
        # The C++ library forces matches to be lower-case, so we do the same
        # here
        yield from (
                m | {
                    "match": m["match"].lower()
                } for m in self._rule.match(*args, **kwargs))

    @property
    def presentation_raw(self):
        return self._rule.presentation_raw

    def to_json_object(self):
        return super().to_json_object()

    @staticmethod
    @Rule.json_handler(type_label)
    def from_json_object(obj: dict):
        return TurboHealthRule(
                sensitivity=Sensitivity.make_from_dict(obj))
