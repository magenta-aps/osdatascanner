from io import BytesIO
import os.path
import email
from contextlib import contextmanager

from ...utilities.i18n import gettext as _
from ..core import Source, Handle, FileResource
from ..utilities.mail import get_safe_filename, decode_encoded_words
from .derived import DerivedSource


def _parts_are_text_body(parts):
    return (len(parts) == 2
            and parts[0].get_content_type() == "text/plain"
            and parts[1].get_content_type() == "text/html")


@Source.mime_handler("message/rfc822")
class MailSource(DerivedSource):
    type_label = "mail"

    def _generate_state(self, sm):
        with self.handle.follow(sm).make_stream() as fp:
            yield email.message_from_bytes(
                    fp.read(), policy=email.policy.default)

    @classmethod
    def _filename_from_part(cls, part):
        filename = part.get_filename()
        if part.is_attachment():
            # "Why don't we just use sanitise_path here?", I hear you
            # ask. The answer: because we actually know which bit is
            # the filename and which bit is the MIME tree walk at this
            # point, and that's the hard bit of the process
            filename = get_safe_filename(filename)

        return filename

    def handles(self, sm):  # noqa: CCR001
        def _process_message(path, part):
            if part.is_multipart():
                st = part.get_content_subtype()
                parts = part.get_payload()
                # XXX: this is a slightly hacky implementation of multipart/
                # alternative, but we don't know what task we're being asked to
                # perform and so we can't do any better
                if st == "alternative" and _parts_are_text_body(parts):
                    yield from _process_message(path + ["1"], parts[1])
                else:
                    for idx, part in enumerate(parts):
                        yield from _process_message(path + [str(idx)], part)
            else:
                filename = self._filename_from_part(part)

                # Do not yield a handle for an attached file, if we want to
                # skip attached files.
                if part.is_attachment() and \
                        hasattr(self.handle, 'scan_attachments') and \
                        self.handle.scan_attachments is False:
                    # Don't yield anything: We don't care about attached files!
                    pass
                else:
                    full_path = "/".join(path + [filename or ''])
                    yield MailPartHandle(self, full_path, part.get_content_type())
        yield from _process_message([], sm.open(self))


class MailPartResource(FileResource):
    def __init__(self, handle, sm):
        super().__init__(handle, sm)
        self._fragment = None

    def check(self) -> bool:
        # XXX: this implementation probably never returns True (_get_fragment
        # is likely to raise an exception before it returns None)
        return self._get_fragment() is not None

    def _get_fragment(self):
        if not self._fragment:
            where = self._get_cookie()
            path = self.handle.relative_path.split("/")[:-1]
            while path:
                next_idx, path = int(path[0]), path[1:]
                where = where.get_payload()[next_idx]
            self._fragment = where
        return self._fragment

    def get_last_modified(self):
        return self.handle.source.handle.follow(self._sm).get_last_modified()

    def get_size(self):
        with self.make_stream() as s:
            initial = s.seek(0, 1)
            try:
                s.seek(0, 2)
                return s.tell()
            finally:
                s.seek(initial, 0)

    @contextmanager
    def make_stream(self):
        yield BytesIO(self._get_fragment().get_payload(decode=True))


def sanitise_path(p: str) -> str:
    """Sanitises the path value associated with a MailPartHandle, which should
    consist of one or more indexed steps on a MIME tree walk followed by an
    optional filename. (The return value will definitely consist of that.)"""
    out = []
    components = p.lstrip("/").split("/")
    while components:
        head, tail = components[0], components[1:]
        try:
            int(head)
            # OK, this path component is a valid integer, and so is presumably
            # part of our MIME tree walk. Preserve it and move on
            out.append(head)
        except ValueError:
            # We've met a path component that isn't part of the walk. At this
            # point we bail out: the last remaining component is a filename and
            # everything else is irrelevant
            filename = components[-1]
            out.append(filename)
            break
        components = tail
    return "/".join(out)


class MailPartHandle(Handle):
    type_label = "mail-part"
    resource_type = MailPartResource

    def __init__(self, source, path, mime):
        super().__init__(source, path)
        self._mime = mime

    @property
    def _path_name(self):
        return os.path.basename(self.relative_path)

    @property
    def presentation_name(self):
        container = self.source.handle.presentation_name
        if (raw_name := self._path_name):
            name = decode_encoded_words(raw_name)
            return _("attachment \"{filename}\" in {mail}").format(
                    filename=name, mail=container)
        else:
            # This is a message body. Use its subject
            return container

    @property
    def sort_key(self):
        return self.source.handle.sort_key

    @property
    def presentation_place(self):
        return self.source.handle.presentation_place

    def guess_type(self):
        if self._mime != "application/octet-stream":
            return self._mime
        else:
            # If this mail part has a completely generic type, then see if our
            # filename-based detection can manage anything better
            return super().guess_type()

    def to_json_object(self):
        return dict(**super().to_json_object(), mime=self._mime)

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return MailPartHandle(
                Source.from_json_object(obj["source"]),
                sanitise_path(obj["path"]),
                obj["mime"])
