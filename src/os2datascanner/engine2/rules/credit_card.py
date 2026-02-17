# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from os2datascanner.engine2.rules.rule import Rule
from os2datascanner.engine2.rules.regex import RegexRule
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


class CreditCardRule(RegexRule):
    type_label = "credit_card"
    operates_on = OutputType.Text

    def __init__(self):
        super().__init__(expression=r"\b(\d{16})\b|\b(\d{4}[ -]\d{4}[ -]\d{4}[ -]\d{4})\b")

    def match(self, representation):
        """ The match function uses the regex from the CreditCardRule __init__ function and the
        luhn_algorithm function to determine if a number could be a credit card number."""
        if representation is None:
            return

        for number in re.finditer(self._expression, representation):
            num = number.group()
            if luhn_algorithm(num):
                yield {
                    "match": num[:4] + "X" * 12,
                    **make_context(number, representation),

                    "sensitivity": (
                        self.sensitivity.value
                        if self.sensitivity else None
                    ),
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
