import re

from ..conversions.types import OutputType
from .rule import Rule, SimpleRule, Sensitivity


def luhn_algorithm(num: str):
    double = (len(num) % 2 == 1)
    tot = 0
    for ch in num:
        v = int(ch) * (2 if double else 1)
        tot += sum(int(c) for c in str(v))
        double = not double
    return 10 - (tot % 10)


class CreditCardRule(SimpleRule):
    """
    Rule for detecting Credit Card numbers based on Luhn's
    algorithm for calculating checksums.
    """
    operates_on = OutputType.Text
    type_label = "creditcard"

    def __init__(self):
        self._expr = re.compile(
                r"[0-9]{4}([- ]?[0-9]{4}){3}")

    def match(self, content: str):
        for mo in self._expr.finditer(content):
            # Canonicalisation
            num = "".join(ch for ch in mo.group() if ch.isdigit())

            # Check that the control digit matches
            if str(luhn_algorithm(num[:-1])) == num[-1]:
                begin, end = mo.span()
                context_begin = max(begin - 50, 0)
                context_end = min(end + 50, len(content))
                yield {
                    "match": num,
                    "offset": begin,
                    "context": content[context_begin:context_end],
                    "context_offset": min(begin, 50)
                }

    def to_json_object(self) -> dict:
        return super().to_json_object()

    @staticmethod
    @Rule.json_handler(type_label)
    def from_json_object(obj: dict):
        return CreditCardRule(
            sensitivity=Sensitivity.make_from_dict(obj),
            name=obj["name"] if "name" in obj else None,
        )
