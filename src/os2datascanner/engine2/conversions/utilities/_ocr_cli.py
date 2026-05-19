# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Subprocess OCR worker.
Loads an image file from IN_PATH, runs pymupdf's Tesseract bindings on it,
and writes the resulting OCR text (UTF-8) to OUT_PATH. Should be invoked via
run_custom() so that any errors thrown by pymupdf or Tesseract won't kill the entire worker.
(Like a SIGSEGV or alike)
"""

import sys

import pymupdf


def main(in_path: str, out_path: str) -> None:
    pix = pymupdf.Pixmap(in_path)

    # Tesseract (apparently especially ran multi-language) can segfault on large images.
    # pix.shrink(1) halves each dimension, so loop until both fit:
    # one halving still leaves an 8000px image over the limit.
    while pix.width > 2000 or pix.height > 2000:
        pix.shrink(1)

    # Tesseract needs RGB or RGBA to function properly, so convert if needed
    if pix.colorspace.n < 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    # Tesseract also can't handle an alpha channel - remove if needed.
    if pix.alpha:
        pix = pymupdf.Pixmap(pix, 0)

    # Create a 1-page PDF in memory with an OCR text layer
    ocr_pdf_bytes = pix.pdfocr_tobytes(language="dan+eng")

    with pymupdf.open("pdf", ocr_pdf_bytes) as ocr_doc:
        with open(out_path, "wb") as f:
            f.write(ocr_doc[0].get_text().encode("utf-8"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
