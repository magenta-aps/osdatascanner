# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from os2datascanner.utils.resources import get_resource_folder

from .types import OutputType
from .registry import conversion
from .text.ocr import tesseract_cli


@conversion(OutputType.MRZ, "image/png", "image/jpeg")
def image_processor(r):
    with r.make_path() as p:
        return tesseract_cli(p, "stdout",
                             "--oem", "1",
                             "--tessdata-dir",
                             str(get_resource_folder() / "downloads" / "tessdata"),
                             "-l", "mrz")
