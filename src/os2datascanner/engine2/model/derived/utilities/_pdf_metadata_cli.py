# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Subprocess PDF metadata reader.

Opens a PDF and writes the author from its DocInfo dictionary to OUT_PATH as
UTF-8. Documents that name no author produce an empty file rather than none, so
that the caller always has something to read.

Should be invoked via run_custom() so that a segfault in pymupdf won't kill the
entire worker.

Usage: python _pdf_metadata_cli.py IN_PATH OUT_PATH
"""

import sys
from pdf_open import open_pdf_wrapped


def main(in_path: str, out_path: str) -> None:
    pdf = open_pdf_wrapped(in_path)
    try:
        # pymupdf gives None rather than a string for a field the document
        # leaves out
        author = pdf.metadata.get("author") or ""
    finally:
        pdf.close()

    # surrogatepass because the null bytes that some authoring tools put in this
    # field can come back as lone surrogates, which plain UTF-8 cannot encode.
    # The caller strips them
    with open(out_path, "wb") as f:
        f.write(author.encode("utf-8", "surrogatepass"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
