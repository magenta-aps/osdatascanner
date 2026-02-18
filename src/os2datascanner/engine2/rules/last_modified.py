# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from ..conversions.types import OutputType
from .rule import Rule, SimpleRule


@Rule.register_class
class LastModifiedRule(SimpleRule):
    operates_on = OutputType.LastModified
    type_label = "last-modified"

    def __init__(self, after, synthetic=True, **super_kwargs):
        super().__init__(synthetic=synthetic, **super_kwargs)
        # Try encoding the given datetime.datetime as a JSON object; this will
        # raise a TypeError if something is wrong with it
        OutputType.LastModified.encode_json_object(after)
        self._after = after

    @property
    def after(self):
        return self._after

    @property
    def presentation_raw(self):
        return "last modified after {0}".format(
                OutputType.LastModified.encode_json_object(self.after))

    def match(self, content):
        if content is None:
            return

        if content > self.after:
            yield {
                "match": OutputType.LastModified.encode_json_object(content)
            }

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            after=OutputType.LastModified.encode_json_object(self.after),
        )

    @classmethod
    def _get_constructor_kwargs(cls, obj):
        return super()._get_constructor_kwargs(obj) | {
            "after": OutputType.LastModified.decode_json_object(obj["after"]),
        }
