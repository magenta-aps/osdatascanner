import warnings
import structlog

from ...conversions.types import OutputType
# from os2ds_rules import CPRDetector
from ..rule import Rule, SimpleRule, Sensitivity
from ..cpr import CPRRule


logger = structlog.get_logger("engine2")


class TurboCPRRule(SimpleRule):
    type_label = "cpr_turbo"
    operates_on = OutputType.Text

    def __init__(self,
                 modulus_11: bool = False,
                 examine_context: bool = False,
                 **super_kwargs):
        super().__init__(**super_kwargs)
        warnings.warn(
                "TurboCPRRule: CPRDetector does not support Python 3.12+"
                " properly, using CPRRule as the backend instead")
        self._modulus_11 = modulus_11
        self._examine_context = examine_context
        self._rule = CPRRule()

    def __getattr__(self, attr):
        return getattr(self._rule, attr)

    def match(self, *args, **kwargs):
        yield from self._rule.match(*args, **kwargs)

    @property
    def presentation_raw(self):
        return self._rule.presentation_raw

    def to_json_object(self) -> dict:
        return super().to_json_object() | {
            "modulus_11": self._modulus_11,
            "examine_context": self._examine_context,
        }

    @staticmethod
    @Rule.json_handler(type_label)
    def from_json_object(obj: dict):
        return TurboCPRRule(
            modulus_11=obj.get("modulus_11", True),
            examine_context=obj.get("examine_context", False),
            sensitivity=Sensitivity.make_from_dict(obj),
            name=obj.get("name"),
        )
