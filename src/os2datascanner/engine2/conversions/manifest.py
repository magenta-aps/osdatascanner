# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from .types import OutputType
from .registry import conversion

from os2datascanner.engine2.model.core import Handle, Source


@conversion(OutputType.Manifest)
def manifest_processor(resource):
    source = Source.from_handle(resource.handle)
    return [h for h in source.handles(resource._sm)
            if isinstance(h, Handle)] if source else None
