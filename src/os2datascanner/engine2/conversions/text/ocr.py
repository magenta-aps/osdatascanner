# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import os
import structlog
from subprocess import PIPE, DEVNULL
import pymupdf

from ... import settings as engine2_settings
from ....utils.system_utilities import run_custom
from ..types import OutputType
from ..registry import conversion

logger = structlog.get_logger("engine2")


def tesseract_pymupdf(image_bytes, filetype=None):
    """
    Performs OCR on in-memory image bytes using pymupdf's Tesseract bindings.
    It automatically downscales large images to improve performance.
    """
    try:
        # Create a Pixmap object from the image bytes
        pix = pymupdf.Pixmap(image_bytes)

        # Check dimensions and downscale if necessary
        if pix.width > 2000 or pix.height > 2000:
            pix.shrink(1)

        # Tesseract needs RGB or RGBA to function properly, so convert if needed
        if pix.colorspace.n < 3:  # n=1 for grayscale, n=3 for RGB, n=4 for RGBA
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)

        # Tesseract also can't handle an alpha channel - remove if needed.
        if pix.alpha:
            pix = pymupdf.Pixmap(pix, 0)

        # Create a 1-page PDF in memory with an OCR text layer
        ocr_pdf_bytes = pix.pdfocr_tobytes(
            language="dan+eng"
        )

        with pymupdf.open("pdf", ocr_pdf_bytes) as ocr_doc:
            ocr_result = ocr_doc[0].get_text().strip()
            if ocr_result:
                return ocr_result
            else:
                return None

    except Exception as e:
        logger.warning(f"OCR failed for image stream (type: {filetype}): {e}")
        # If pymupdf fails to process the image, return None
        return None


def tesseract_cli(path, dest="stdout", *args):
    """
    Wrapper for the tesseract command-line tool for specialized conversions.
    (Currently used for MRZ only)
    """
    result = run_custom(
            [
                "tesseract",
                *engine2_settings.tesseract["extra_args"],
                *args,
                path, dest
            ],
            universal_newlines=True,
            stdout=PIPE,
            stderr=DEVNULL,
            timeout=engine2_settings.subprocess["timeout"],
            isolate_tmp=True,
            # Disables multithreading for tesseract, which may lead to better performance.
            env=os.environ | {"OMP_THREAD_LIMIT": "1"})
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        return None


@conversion(OutputType.Text,
            "image/png", "image/jpeg", "image/gif", "image/x-ms-bmp",
            "image/bmp", "image/x-bmp")
def image_processor(r):
    """
    Uses pymupdf's tesseract bindings to extract text from common image types using in-memory OCR.
    Downscales large images to prevent timeouts and improve performance.
    """
    with r.make_stream() as stream:
        image_bytes = stream.read()
    # Get the file extension from the resource's handle name
    file_ext = r.handle.name.split('.')[-1].lower()
    return tesseract_pymupdf(image_bytes, filetype=file_ext)
