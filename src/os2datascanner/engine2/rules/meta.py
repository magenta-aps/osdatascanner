# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from ..conversions.types import OutputType
from .rule import Rule, SimpleRule
from .utilities.properties import RuleProperties, RulePrecedence


@Rule.register_class
class HasConversionRule(SimpleRule):
    type_label = "conversion"

    def __init__(self, target, synthetic=True, **super_kwargs):
        super().__init__(synthetic=synthetic, **super_kwargs)
        self._target = target

    @property
    def presentation_raw(self):
        return "convertible to {0}".format(self._target.value)

    @property
    def operates_on(self):
        return self._target

    def match(self, content):
        if content is None:
            return

        try:
            self._target.encode_json_object(content)
            yield {
                "match": self._target.value
            }
        except TypeError:
            pass

    def to_json_object(self):
        return dict(**super().to_json_object(), target=self._target.value)

    @classmethod
    def _get_constructor_kwargs(cls, obj):
        return super()._get_constructor_kwargs(obj) | {
            "target": OutputType(obj["target"]),
        }


@Rule.register_class
class SizeRule(SimpleRule):
    operates_on = OutputType.Size
    type_label = "size"
    properties = RuleProperties(
        precedence=RulePrecedence.LEFT,
        standalone=True)

    def __init__(self, size, synthetic=True, **super_kwargs):
        super().__init__(synthetic=synthetic, **super_kwargs)
        self._size = size

    @property
    def size(self):
        return self._size

    @property
    def presentation_raw(self):
        return "size bigger than {0}".format(self.size)

    def match(self, content):
        if content is None:
            return

        if content > self.size:
            yield {
                "match": content
            }

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            size=self.size,
        )

    @classmethod
    def _get_constructor_kwargs(cls, obj):
        return super()._get_constructor_kwargs(obj) | {
            "size": obj["size"],
        }
