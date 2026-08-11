# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from ..conversions.types import OutputType
from .rule import Rule, SimpleRule


class NeverMatchesRule(SimpleRule):
    """NeverMatchesRule matches nothing: it returns no results for any content,
    and it claims to operate on an OutputType for which no conversions are
    defined.

    It can be used to force the pipeline to completely explore a Source without
    actually performing any other work along the way."""

    operates_on = OutputType.NoConversions
    type_label = "dummy"

    @property
    def presentation_raw(self):
        return "unconditional failure"

    def match(self, content):
        yield from []

    def to_json_object(self):
        return super().to_json_object()

    @staticmethod
    @Rule.json_handler(type_label)
    def from_json_object(obj):
        return NeverMatchesRule(name=obj["name"] if "name" in obj else None)


class AlwaysMatchesRule(SimpleRule):
    """AlwaysMatchesRule matches everything: it unconditionally returns True as
    a match for every input, and it operates on an OutputType which defines a
    single trivial conversion from every input object to True."""

    operates_on = OutputType.AlwaysTrue
    type_label = "fallback"

    @property
    def presentation_raw(self):
        return "unconditional success"

    def match(self, content):
        yield {
            "match": True
        }

    def to_json_object(self):
        return super().to_json_object()

    @staticmethod
    @Rule.json_handler(type_label)
    def from_json_object(obj):
        return AlwaysMatchesRule(name=obj["name"] if "name" in obj else None)


class BuggyRule(SimpleRule):
    """BuggyRule raises an exception when it's asked to match something."""

    operates_on = OutputType.AlwaysTrue
    type_label = "buggy"

    @property
    def presentation_raw(self):
        return "unconditional crash"

    def match(self, content):
        getattr(None, str(content))

    def to_json_object(self):
        return super().to_json_object()

    @staticmethod
    @Rule.json_handler(type_label)
    def from_json_object(obj):
        return BuggyRule(
                name=obj["name"] if "name" in obj else None)
