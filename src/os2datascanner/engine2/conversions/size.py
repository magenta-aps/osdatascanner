# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from .types import OutputType
from .registry import conversion


@conversion(OutputType.Size, "application/pdf")
def size_processor(resource):
    if hasattr(resource, "get_size"):
        return resource.get_size()
    else:
        return None
