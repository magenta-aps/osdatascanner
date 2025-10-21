from os2datascanner.engine2.rules.rule import Rule, SimpleRule
from os2datascanner.engine2.conversions.types import OutputType
from .utilities.context import make_context
import re


def luhn_algorithm(number: str):
    """ https://en.wikipedia.org/wiki/Luhn_algorithm """

    number = number.replace(" ", "")

    number = number.replace("-", "")

    number_list = [int(num) for num in number]

    number_list.reverse()

    total = 0

    for i, num in enumerate(number_list):
        if i % 2 == 0:
            total += num
        else:
            total += (2 * num - 9) if 2 * num > 9 else num * 2

    return total % 10 == 0


class CreditCardRule(SimpleRule):
    type_label = "credit_card"
    operates_on = OutputType.Text

    def __init__(self):
        super().__init__()
        self._expr = re.compile(
            r"\d{16}|\d{4}([ -])\d{4}\1\d{4}\1\d{4}"
        )

    def match(self, representation):
        """ The match function uses the regex from the CreditCardRule __init__ function and the
        luhn_algorithm function to determine if a number could be a credit card number."""
        for number in re.finditer(self._expr, representation):
            num = number.group()
            if luhn_algorithm(num):
                yield {
                    "match": num,
                    **make_context(number, representation)
                }

    def to_json_object(self):
        return super().to_json_object()

    @Rule.json_handler(type_label)
    @staticmethod
    def from_json_object(obj):
        return CreditCardRule()

    @property
    def presentation_raw(self):
        return "credit card number"
