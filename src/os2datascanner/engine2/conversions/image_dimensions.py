# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from PIL import Image

from .types import OutputType
from .registry import conversion


@conversion(OutputType.ImageDimensions,
            "image/png", "image/jpeg", "image/gif", "image/x-ms-bmp",
            # Many more MIME types have appeared for .bmp files. Groan
            "image/bmp", "image/x-bmp")
def dimensions_processor(r, **kwargs):
    try:
        with r.make_stream() as fp, Image.open(fp) as im:
            return im.width, im.height
    except OSError:
        return None
