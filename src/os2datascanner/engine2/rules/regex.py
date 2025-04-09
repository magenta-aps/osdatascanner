import re
from typing import Iterator, Optional

from .rule import Rule, SimpleTextRule, Sensitivity
from .utilities.context import make_context
from .utilities.properties import RulePrecedence, RuleProperties


class RegexRule(SimpleTextRule):
    type_label = "regex"
    eq_properties = ("_expression",)
    properties = RuleProperties(
        precedence=RulePrecedence.RIGHT,
        standalone=True)

    def __init__(self, expression: str, **super_kwargs):
        super().__init__(**super_kwargs)
        self._expression = expression
        self._compiled_expression = re.compile(expression)

    @property
    def presentation_raw(self) -> str:
        return 'regular expression matching "{0}"'.format(self._expression)

    def match(self, content: str) -> Optional[Iterator[dict]]:
        if content is None:
            return

        for match in self._compiled_expression.finditer(content):
            low, high = match.span()
            yield {
                "match": match.string[match.start(): match.end()],
                **make_context(match, content),

                "sensitivity": (
                    self.sensitivity.value
                    if self.sensitivity else None
                ),
            }

    def get_censor_intervals(self, context):
        for m in self._compiled_expression.finditer(context):
            any_valid_span = False
            for i in range(len(m.groups())):
                if m.span(i+1) != (-1, -1):
                    yield m.span(i+1)
                    any_valid_span = True
            if not any_valid_span:
                yield m.span()

    def to_json_object(self) -> dict:
        return dict(**super().to_json_object(), expression=self._expression)

    @staticmethod
    @Rule.json_handler(type_label)
    def from_json_object(obj: dict):
        return RegexRule(
            expression=obj["expression"],
            sensitivity=Sensitivity.make_from_dict(obj),
            name=obj["name"] if "name" in obj else None,
        )
