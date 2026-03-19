from .rule import Rule, SimpleRule, Sensitivity
from ..conversions.types import OutputType
from .utilities.properties import RuleProperties, RulePrecedence


@Rule.register_class
class PresentationRule(SimpleRule):
    type_label = "presentation_regex"
    operates_on = OutputType.Presentation
    properties = RuleProperties(
        precedence=RulePrecedence.UNDEFINED,
        standalone=True,
    )

    def __init__(self, rule: Rule, **kwargs):
        super().__init__(**kwargs)
        if not rule:
            raise ValueError("Couldn't construct PresentationRule: No rule given")
        self._rule = rule

    @property
    def presentation_raw(self) -> str:
        return 'presentation matching rule "{0}"'.format(self._rule)

    def match(self, presentation: str):
        representations = {OutputType.Text.value: presentation}
        conclusion, all_matches = self._rule.try_match(representations)

        if conclusion is True:
            for _, rms in all_matches:
                yield from (r for r in rms if r["match"])

    def to_json_object(self):
        return super().to_json_object() | {
            "rule": self._rule.to_json_object(),
        }

    def flatten(self):
        return {self} | self._rule.flatten()

    @classmethod
    def from_json_object(cls, obj):
        return cls(
            rule=Rule.from_json_object(obj["rule"]),

            sensitivity=Sensitivity.make_from_dict(obj),
            name=obj["name"] if "name" in obj else None,
        )
