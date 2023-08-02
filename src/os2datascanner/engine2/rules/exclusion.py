from .rule import Rule, Sensitivity, SimpleRule
from ..conversions.types import OutputType
from ..model.core import Handle


class ExclusionRule(SimpleRule):
    '''
    This rule uses another rule to match against the
    presentation of a Handle, e.g. a file path or a URL.

    This can be used to exclude certain paths from begin scanned.
    '''
    type_label = "exclusion"

    operates_on = OutputType.Presentation

    def __init__(self, rule: Rule, **kwargs):
        super().__init__(**kwargs)
        self._rule = rule

    def match(self, value: Handle):
        yield from self._rule.match(value.presentation_name)

    def to_json_object(self):
        return super().to_json_object() | {
            "rule": self._rule.to_json_object(),
        }

    @classmethod
    def from_json_object(cls, obj):
        return cls(
            rule=Rule.from_json_object(obj["rule"]),
            sensitivity=Sensitivity.make_from_dict(obj),
            name=obj["name"] if "name" in obj else None)

    @property
    def presentation_raw(self):
        return (f'presentation matches the rule "{self._rule.presentation}"')


Rule.json_handler(ExclusionRule.type_label)(ExclusionRule.from_json_object)
