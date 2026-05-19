# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Subprocess PDF page extractor.

Opens a PDF, navigates to a specific page, and writes its text and
embedded images as plain files in OUT_DIR:

    OUT_DIR/page.txt           (if the page has any text)
    OUT_DIR/image-1.<ext>      (if SKIP_IMAGES is "0", one per embedded image)
    OUT_DIR/image-2.<ext>
    ...

Should be invoked via run_custom() so that any errors thrown by pymupdf
the entire worker.

Usage: python -m ..._pdf_page_extract_cli IN_PATH PAGE_NUM SKIP_IMAGES OUT_DIR
    PAGE_NUM is 0-indexed.
    SKIP_IMAGES is "1" or "0".

"""

import os
import sys

from pdf_open import open_pdf_wrapped


def main(in_path: str, page_num: int, skip_images: bool, out_dir: str) -> None:
    pdf = open_pdf_wrapped(in_path)
    pdf_page = pdf[page_num]

    text = pdf_page.get_text("text")
    if text:
        with open(os.path.join(out_dir, "page.txt"), "wb") as f:
            f.write(text.encode("utf-8"))

    if not skip_images:
        for img_index, img_info in enumerate(pdf_page.get_images(full=True)):
            xref = img_info[0]
            base_image = pdf.extract_image(xref)
            if not base_image:
                continue
            filename = f"image-{img_index + 1}.{base_image['ext']}"
            with open(os.path.join(out_dir, filename), "wb") as f:
                f.write(base_image["image"])

    pdf.close()


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3] == "1", sys.argv[4])
