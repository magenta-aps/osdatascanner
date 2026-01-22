import io
import mimetypes
import string
from tempfile import TemporaryDirectory
import pymupdf
from ... import settings as engine2_settings
from ...utilities.i18n import gettext as _
from ..core import Handle, Resource, Source
from .derived import DerivedSource
from .utilities.extraction import (should_skip_images,
                                   MD5DeduplicationFilter,
                                   TinyImageFilter)

PAGE_TYPE = "application/x.os2datascanner.pdf-page"
WHITESPACE_PLUS = string.whitespace + "\0"


def _open_pdf_wrapped(obj):
    pdf = pymupdf.open(obj)
    if pdf.is_encrypted:
        # Some PDFs are "encrypted" with an empty password: give that a shot...
        if pdf.authenticate("") == 0:
            raise RuntimeError("Failed to decrypt PDF")
    return pdf


@Source.mime_handler("application/pdf")
class PDFSource(DerivedSource):
    type_label = "pdf"

    def _generate_state(self, sm):
        with self.handle.follow(sm).make_path() as path:
            # Explicitly download the file here for the sake of PDFPageSource,
            # which needs a local filesystem path to pass to pdftohtml
            if engine2_settings.pdf["PREPROCESS_PDF"]:
                with TemporaryDirectory() as outputdir:
                    converted_path = "{0}/ez_save.pdf".format(outputdir)
                    pdf = pymupdf.open(path)
                    pdf.ez_save(converted_path, clean=True)
                    pdf.close()
                    yield converted_path
            else:
                yield path

    def handles(self, sm):
        pdf = _open_pdf_wrapped(sm.open(self))
        for page_num in range(len(pdf)):
            yield PDFPageHandle(self, str(page_num + 1))


class PDFPageResource(Resource):
    def _generate_metadata(self):
        pdf = _open_pdf_wrapped(self._sm.open(self.handle.source))
        # Some PDF authoring tools helpfully stick null bytes into the
        # author field. Make sure we remove these
        author = pdf.metadata.get("author", "").strip(WHITESPACE_PLUS)
        pdf.close()
        if author:
            yield "pdf-author", str(author)

    def check(self) -> bool:
        page = int(self.handle.relative_path)
        with self.handle.source._make_stream(self._sm) as fp:
            reader = _open_pdf_wrapped(fp)
            return 0 < page <= len(reader)

    def compute_type(self):
        return PAGE_TYPE


@Handle.stock_json_handler("pdf-page")
class PDFPageHandle(Handle):
    type_label = "pdf-page"
    resource_type = PDFPageResource

    @property
    def presentation_name(self):
        return _("page {page_nr}").format(page_nr=int(self.relative_path))

    @property
    def presentation_place(self):
        return str(self.source.handle)

    def __str__(self):
        return _("{page_desc} of {file}").format(
                page_desc=self.presentation_name, file=self.presentation_place)

    @property
    def sort_key(self):
        "Return the file path of the document"
        return self.source.handle.sort_key

    def guess_type(self):
        return PAGE_TYPE

    @classmethod
    def make(cls, handle: Handle, page: int):
        return PDFPageHandle(PDFSource(handle), str(page))


@Source.mime_handler(PAGE_TYPE)
class PDFPageSource(DerivedSource):
    type_label = "pdf-page"
    derived_from = PDFPageHandle

    # TODO: Determine "searchable" pdf's. I.e. scanned pages with an already OCRed text layer
    # underneath, and avoid double-working that.

    def _generate_state(self, sm):
        # produces a dictionary mapping virtual filenames to their
        # byte content. This avoids writing temporary files to disk.
        page = int(self.handle.relative_path) - 1
        pdf = pymupdf.open(sm.open(self.handle.source))
        extracted_data = {}
        pdf_page = pdf[page]

        # 1. Extract text into memory
        text = pdf_page.get_text("text")
        if text:
            extracted_data["page.txt"] = text.encode("utf-8")

        if not should_skip_images(sm.configuration):
            # 2. Extract images into memory
            for img_index, img_info in enumerate(pdf_page.get_images(full=True)):
                xref = img_info[0]
                base_image = pdf.extract_image(xref)
                if not base_image:
                    continue

                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = f"image-{img_index + 1}.{image_ext}"
                extracted_data[image_filename] = image_bytes

        pdf.close()

        # Apply filters to the in-memory data before yielding
        filtered_data = MD5DeduplicationFilter.apply_dict(extracted_data)
        filtered_data = TinyImageFilter.apply_dict(filtered_data)
        yield filtered_data

    def handles(self, sm):
        # The cookie is now a dictionary of in-memory objects
        for p in sm.open(self):
            yield PDFObjectHandle(self, p)


class PDFObjectResource(Resource):
    def _generate_metadata(self):
        # Suppress the superclass implementation of this method -- generated
        # files have no interesting metadata
        yield from ()

    def check(self) -> bool:
        """Check if the object exists in the parent source's in-memory dict."""
        content_dict = self._sm.open(self.handle.source)
        return self.handle.relative_path in content_dict

    def compute_type(self):
        """Guess the MIME type from the object's filename."""
        # Fallback to octet-stream for unknown types
        mime, _ = mimetypes.guess_type(self.handle.name)
        return mime or "application/octet-stream"

    def get_last_modified(self):
        page_source: PDFPageSource = self.handle.source
        document_source: PDFSource = page_source.handle.source
        res = document_source.handle.follow(self._sm)
        return res.get_last_modified()

    def make_stream(self):
        """
        Return a file-like object for the in-memory content.
        """
        content_dict = self._sm.open(self.handle.source)
        return io.BytesIO(content_dict[self.handle.relative_path])


@Handle.stock_json_handler("pdf-object")
class PDFObjectHandle(Handle):
    type_label = "pdf-object"
    resource_type = PDFObjectResource

    @property
    def sort_key(self):
        return self.source.handle.sort_key

    def guess_type(self):
        """Guess the MIME type from the object's filename."""
        mime, _ = mimetypes.guess_type(self.name)
        return mime or "application/octet-stream"

    @property
    def presentation_name(self):
        mime = self.guess_type()
        page = str(self.source.handle.presentation_name)
        container = self.source.handle.source.handle.presentation_name

        if mime.startswith("text/"):
            return _("text on {page} of {file}").format(
                    page=page, file=container)
        elif mime.startswith("image/"):
            return _("image on {page} of {file}").format(
                    page=page, file=container)
        else:
            return _("unknown object on {page} of {file}").format(
                    page=page, file=container)

    @property
    def presentation_place(self):
        return str(self.source.handle.source.handle.presentation_place)

    def __str__(self):
        return _("{name} (on {place})").format(
                name=self.presentation_name, place=self.presentation_place)

    @classmethod
    def make(cls, handle: Handle, page: int, name: str):
        return PDFObjectHandle(
                PDFPageSource(PDFPageHandle.make(handle, page)), name)
