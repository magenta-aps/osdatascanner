from enum import Enum
import operator
from functools import partial

from sqlalchemy.sql.expression import func as sql_func
from sqlalchemy.types import String

from os2datascanner.engine2.rules.rule import Rule, SimpleRule, Sensitivity
from os2datascanner.engine2.conversions.types import OutputType


def maybe(*descriptors):
    """Returns a function that attempts to apply one of the given descriptors
    to its argument, returning the argument unchanged if that was not
    possible."""

    def _maybe(v):
        for descriptor in descriptors:
            try:
                return descriptor(v)
            except TypeError:
                pass
        return v

    return _maybe


_maybe_lower = maybe(str.lower)


def _in(column, value, case_sensitive=False):
    if isinstance(column.type, String) and not case_sensitive:
        return sql_func.lower(column).in_(
                [_maybe_lower(v) for v in value])
    else:
        return column.in_(value)


class SBSYSDBRule(SimpleRule):
    class Op(Enum):
        EQ = ("eq", operator.eq)
        NEQ = ("neq", operator.ne)
        LT = ("lt", operator.lt)
        LTE = ("lte", operator.le)
        GT = ("gt", operator.gt)
        GTE = ("gte", operator.ge)

        CONTAINS = (
                "contains",
                lambda haystack, needle: needle in haystack,
                lambda column, value: column.contains(value))
        ICONTAINS = (
                "icontains",
                lambda haystack, needle: (
                        needle.casefold() in haystack.casefold()),
                lambda column, value: column.icontains(value))

        IN = (
                "in",
                lambda needle, haystack: needle in haystack,
                partial(_in, case_sensitive=True))

        IIN = (
                "iin",
                lambda needle, haystack: any(
                        _maybe_lower(needle) == _maybe_lower(h)
                        for h in haystack),
                partial(_in, case_sensitive=False))

        def __new__(cls, value, func_py, func_db=None):
            obj = object.__new__(cls)
            obj._value_ = value
            obj.func_py = func_py
            obj.func_db = func_db or func_py
            return obj

        def __call__(self, *args, **kwargs):
            return self.func_py(*args, **kwargs)

    type_label = "sbsys-db-fieldrule"
    operates_on = OutputType.DatabaseRow

    __match_args__ = ("_field", "_op", "_value")

    def __init__(
            self, field: str, op: Op | str, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._field = field
        self._op = op if isinstance(op, self.Op) else self.Op(op)
        self._value = value if not isinstance(value, list) else tuple(value)

    @property
    def presentation_raw(self):
        return ":D"

    def match(self, db_row):
        if self._op(db_row[self._field], self._value):
            yield {
                "match": db_row[self._field]
            }

    def to_json_object(self):
        return super().to_json_object() | {
            "field": self._field,
            "operator": self._op.value,
            "value": (
                    self._value
                    if not isinstance(self._value, tuple)
                    else list(self._value))
        }

    @Rule.json_handler(type_label)
    @staticmethod
    def from_json_object(obj):
        return SBSYSDBRule(
                obj["field"],
                obj["operator"],
                obj["value"],

                sensitivity=Sensitivity.make_from_dict(obj),
                name=obj.get("name"))
