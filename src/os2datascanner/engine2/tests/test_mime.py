# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import os.path

from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.file import FilesystemHandle


here_path = os.path.dirname(__file__)
doc_handle = FilesystemHandle.make_handle(
        os.path.join(
                here_path, "data", "msoffice", "test.doc"))
docx_handle = FilesystemHandle.make_handle(
        os.path.join(
                here_path, "data", "msoffice", "test.docx"))


class TestEngine2MIME:
    def test_doc_mime(self):
        assert doc_handle.guess_type() == "application/msword"
        with SourceManager() as sm:
            assert doc_handle.follow(sm).compute_type() == "application/msword"

    def test_docx_mime(self):
        assert docx_handle.guess_type() == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"  # noqa
        with SourceManager() as sm:
            assert docx_handle.follow(sm).compute_type() == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"  # noqa
