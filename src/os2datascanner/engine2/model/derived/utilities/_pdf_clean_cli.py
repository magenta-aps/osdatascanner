# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Subprocess PDF cleaning worker.
Runs pymupdf's ez_save(clean=True) on the input PDF and writes the result
to the output path. Should be invoked via run_custom() so that any errors thrown by pymupdf
won't kill the entire worker.
"""

import sys
from pdf_open import open_pdf_wrapped


def main(in_path: str, out_path: str) -> None:
    pdf = open_pdf_wrapped(in_path)

    # Tagged-PDF structure trees from some producers can trigger SIGSEGV
    # in MuPDF's stext extractor. The tree is screen-reader
    # metadata, and as such not relevant for us. We remove it as a precaution.
    pdf.xref_set_key(pdf.pdf_catalog(), "StructTreeRoot", "null")

    # Run ez_save (which corresponds to mutool clean)
    pdf.ez_save(out_path, clean=True)
    pdf.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
