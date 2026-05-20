# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pymupdf


def open_pdf_wrapped(obj):
    """Open a PDF via pymupdf. If the document is encrypted, try empty
    password, raise RuntimeError if that doesn't work. Returns the open
    pymupdf.Document otherwise. """
    pdf = pymupdf.open(obj)
    if pdf.is_encrypted:
        # Some PDFs are "encrypted" with an empty password: give that a shot...
        if pdf.authenticate("") == 0:
            raise RuntimeError("Failed to decrypt PDF")
    return pdf
