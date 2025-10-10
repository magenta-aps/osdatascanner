from os2datascanner.engine2.rules.rule import Rule, SimpleRule
from os2datascanner.engine2.conversions.types import OutputType
import re


def luhn_algorithm(number: str):
    """ The luhn algorithm checks if the number could be a credit card number."""

    if " " in number:
        number = number.replace(" ", "")

    if "-" in number:
        number = number.replace("-", "")

    number_list = [int(num) for num in number]

    number_list.reverse()

    not_to_be_doubled = [number_list[i] for i in range(len(number_list)) if i % 2 == 0]

    doubled_list = [number_list[j] * 2 - 9 if number_list[j] * 2 > 9 else number_list[j] * 2
                    for j in range(len(number_list)) if j % 2 != 0]

    total = sum(not_to_be_doubled) + sum(doubled_list)

    if total % 10 == 0:
        return True

    else:
        return False


class CreditCardRule(SimpleRule):
    type_label = "credit_card"
    operates_on = OutputType.Text

    def __init__(self):
        super().__init__()
        self._expr = re.compile(
            r"[0-9]{4}([- ]?[0-9]{4}){3}"
        )

    def match(self, representation):
        """ The match function uses the regex from the CreditCardRule __init__ function and the
        luhn_algorithm function to determine if a number could be a credit card number."""
        for number in re.finditer(self._expr, representation):
            num = number.group()
            if luhn_algorithm(num):
                yield {
                    "match": num
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
