from enum import Enum
import operator
from functools import partial

from sqlalchemy.sql.expression import func as sql_func
from sqlalchemy.types import String

from os2datascanner.engine2.rules.rule import Rule, SimpleRule
from os2datascanner.engine2.utilities.i18n import gettext as _
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


@Rule.register_class
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
        prefix = '{db_field}'

        rhs_is_db_field = False
        match self._value:
            case str() as s if s.startswith("&"):
                rhs_is_db_field = True
                value = _("the database field '{db_field}'").format(
                        db_field=s[1:])
            case str() as s if s.startswith("\\"):
                value = repr(s[1:])
            case v:
                value = repr(v)

        Op = SBSYSDBRule.Op
        match (self._op, self._value):
            case (Op.EQ, True) | (Op.NEQ, False):
                format_str = prefix + _(" is true")
            case (Op.EQ, False) | (Op.NEQ, True):
                format_str = prefix + _(" is false")
            case (Op.EQ, _) if rhs_is_db_field:
                format_str = prefix + _(" is equal to {value}")
            case (Op.EQ, _):
                format_str = prefix + _(" is {value}")

            case (Op.NEQ, _) if rhs_is_db_field:
                format_str = prefix + _(" is not equal to {value}")
            case (Op.NEQ, _):
                format_str = prefix + _(" is not {value}")

            case (Op.LT, _):
                format_str = prefix + _(" is less than {value}")
            case (Op.LTE, _):
                format_str = prefix + _(" is less than or equal to {value}")
            case (Op.GT, _):
                format_str = prefix + _(" is greater than {value}")
            case (Op.GTE, _):
                format_str = prefix + _(" is greater than or equal to {value}")
            case (Op.CONTAINS, _):
                format_str = prefix + _(" contains {value}")
            case (Op.ICONTAINS, _):
                format_str = prefix + _(
                        " contains {value} (case-insensitively)")
            case (Op.IN, _):
                format_str = prefix + _(" is found in {value}")
            case (Op.IIN, _):
                format_str = prefix + _(
                        " is found (case-insensitively) in {value}")

        match self._field:
            case "?Age?":
                db_field = _("the number of days since the last update")
            case _:
                db_field = self._field

        return format_str.format(db_field=db_field, value=value)

    def match(self, db_row):
        match self._value:
            case str() as s if s.startswith("&"):
                rhs = db_row[s[1:]]
            case str() as s if s.startswith("\\"):
                rhs = s[1:]
            case v:
                rhs = v

        if self._op(db_row[self._field], rhs):
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

    @classmethod
    def _get_constructor_kwargs(cls, obj):
        return super()._get_constructor_kwargs(obj) | {
            "field": obj["field"],
            "op": obj["operator"],
            "value": obj["value"],
        }
