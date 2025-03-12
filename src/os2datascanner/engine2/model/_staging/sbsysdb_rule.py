from enum import Enum
import operator

from os2datascanner.engine2.rules.rule import SimpleRule


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

        def __new__(cls, value, func_py, func_db=None):
            obj = object.__new__(cls)
            obj._value_ = value
            obj.func_py = func_py
            obj.func_db = func_db or func_py
            return obj

        def __call__(self, *args, **kwargs):
            return self.func_py(*args, **kwargs)

    type_label = "sbsys-db-fieldrule"
    operates_on = None

    __match_args__ = ("_field", "_op", "_value")

    def __init__(
            self, field: str, op: Op | str, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._field = field
        self._op = op if isinstance(op, self.Op) else self.Op(op)
        self._value = value

    @property
    def presentation_raw(self):
        return ":D"

    def match(self, db_row):
        if self._op(db_row[self._field], self._value):
            yield {
                "match": db_row[self._field]
            }

    def to_json_object(self):
        return NotImplemented
