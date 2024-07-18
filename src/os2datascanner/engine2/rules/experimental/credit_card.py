import re
from ..rule import SimpleRule
from ...conversions.types import OutputType

def luhn_algorithm(num: str):
    """Computes the Luhn check digit for a given string of digits. (The last
    digit of virtually all credit and debit card numbers is a Luhn check
    digit.)"""
    double = (len(num) % 2 == 1)
    tot = 0
    for ch in num:
        v = int(ch) * (2 if double else 1)
        tot += sum(int(c) for c in str(v))
        double = not double
    return 10 - (tot % 10)


class CreditCardRule(SimpleRule):
    operates_on = OutputType.Text

    def __init__(self):
        self._expr = re.compile(
                r"[0-9]{4}([- ]?[0-9]{4}){3}")

    def match(self, representation: str):
        for mo in self._expr.finditer(representation):
            # Canonicalise the joiners away
            num = "".join(ch for ch in mo.group() if ch.isdigit())

            # See if the check digit is what we expect
            if str(luhn_algorithm(num[:-1])) == num[-1]:
                yield {
                    "match": num
                }

    def to_json_object(self):
        return super().to_json_object()
