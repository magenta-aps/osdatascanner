from typing import Optional, Iterator

from .rule import Rule, Sensitivity
from .regex import RegexRule

sick_leave_regex = (r"(jeg har feber)|(er indlagt)|(blevet indlagt)"
                    r"|(\b[^(be|af)]kræft[^(er|else)]\b)|(sygedag)|(tarm)"
                    r"|(\bUnder the weather\b)|(\bMaveproblemer\b)|(Ikke på toppen)"
                    r"|(skadestue)|(hospitalet\b)")


class SickLeaveRule(RegexRule):
    type_label = "sick_leave"

    def __init__(self, **super_kwargs):
        super().__init__(sick_leave_regex, **super_kwargs)

    @property
    def presentation_raw(self) -> str:
        return "Sick leave"

    def match(self, content: str) -> Optional[Iterator[dict]]:
        if content is None:
            return

        for m in self._compiled_expression.finditer(content):
            begin, end = m.span()
            context_begin = max(begin - 50, 0)
            context_end = min(end + 50, len(content))
            yield {
                "match": m.group(),
                "offset": begin,
                "context": content[context_begin:context_end],
                "context_offset": min(begin, 50),
            }

    @staticmethod
    @Rule.json_handler(type_label)
    def from_json_object(obj: dict):
        return SickLeaveRule(
            name=obj.get("name"),
            sensitivity=Sensitivity.make_from_dict(obj),
        )
