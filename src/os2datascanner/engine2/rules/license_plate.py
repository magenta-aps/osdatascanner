# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import re
from .rule import Rule, SimpleRule
from os2datascanner.engine2.conversions.types import OutputType
from .utilities.context import make_context


class DanishLicensePlateRule(SimpleRule):

    operates_on = OutputType.Text
    type_label = "license_plate"

    def __init__(self):
        super().__init__()
        self._expr = re.compile(
            r"\b([a-zA-Z]{2})(\s\d{2}\s\d{3}|\d{5}|\s\d{5}|\d{2}\s\d{3})\b"
        )

    def match(self, representation: str):
        if representation is None:
            return
        for plate in re.finditer(self._expr, representation):
            match = plate.group()
            yield {
                "match": match,
                **make_context(plate, representation)
            }

    @property
    def presentation_raw(self):
        return "License Plate"

    def to_json_object(self):
        return super().to_json_object()

    @Rule.json_handler(type_label)
    @staticmethod
    def from_json_object(obj):
        return DanishLicensePlateRule()
