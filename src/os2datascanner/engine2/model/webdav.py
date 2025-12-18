from io import BytesIO
from lxml import etree
from typing import Iterable
from urllib.parse import urljoin, unquote
from dateutil import parser as dateparser
from contextlib import contextmanager

from ..utilities.i18n import gettext as _
from os2datascanner.utils.token_caller import TokenCaller
from os2datascanner.engine2.model.core import (
        Source, SourceManager, Handle, FileResource)


def _xp(e, path: str) -> list[str]:
    return e.xpath(
            path,
            namespaces={
               "webdav": "DAV:"
            },
            smart_strings=False)


def response_to_3ple(response: etree.Element):
    match _xp(response, "webdav:href/text()"):
        case [pv]:
            path = pv
        case _:
            path = ""

    *properties, = _xp(response, "webdav:propstat/webdav:prop/*")
    # If the {webdav}collection element exists, then this item is a
    # folder
    is_folder = bool(
            _xp(response,
                "webdav:propstat/webdav:prop"
                "/webdav:resourcetype/webdav:collection"))
    return path.lstrip("/"), is_folder, {
        p.tag: p.text
        for p in properties if p.text is not None
    }


class TrivialDAVClient(TokenCaller):
    """A TrivialDAVClient is a thin wrapper on top of TokenCaller that adds
    support for the WebDAV methods OSdatascanner uses, as well as a few utility
    functions built on those methods."""
    _PARSER = etree.XMLParser(resolve_entities=False)

    def _propfind(self, *args, **kwargs):
        return self._session.request("propfind", *args, **kwargs)

    def propfind(self, tail: str, **kwargs):
        return self._request(self._propfind, tail, **kwargs)

    def ls(self, tail: str = "") -> Iterable[tuple[str, bool, dict[str, str]]]:
        """For every entry in the specified directory, yields a 3-tuple of
        the entry's path, whether or not the entry is a directory, and a dict
        containing hints from the server about that entry."""
        response = self.propfind(tail, headers={"depth": "1"}, check=False)
        if not response.content or response.status_code not in (207,):
            return
        root = etree.parse(BytesIO(response.content), parser=self._PARSER)
        for response in _xp(root, "/webdav:multistatus/webdav:response"):
            yield response_to_3ple(response)


@Source.register_class
class WebDAVSource(Source):
    """A WebDAVSource exposes the contents of a web server that supports
    WebDAV, a set of extra HTTP methods that support treating a website like a
    filesystem.

    (The only extra method that OSdatascanner uses is PROPFIND, which provides
    machine-readable XML directory listings.)"""
    type_label = "webdav"

    def __init__(self, base_url: str):
        self._base_url = base_url

    def _generate_state(self, sm: SourceManager):
        yield TrivialDAVClient(
                TrivialDAVClient.null_token_creator, self._base_url)

    def censor(self):
        return self

    def handles(self, sm: SourceManager):
        dav = sm.open(self)

        visited = set()
        directories = [""]
        while directories:
            directory = directories.pop(0)
            visited.add(directory)
            for path, is_folder, properties in dav.ls(directory):
                if path and not is_folder:
                    yield WebDAVHandle(
                            self, path, hints=properties)
                elif path not in visited and path not in directories:
                    directories.insert(0, path)

    def to_json_object(self):
        return super().to_json_object() | {
            "base_url": self._base_url
        }

    @classmethod
    def _get_constructor_kwargs(cls, obj):
        return super()._get_constructor_kwargs(obj) | {
            "base_url": obj["base_url"]
        }


class WebDAVResource(FileResource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._props = None

    def _make_url(self):
        return urljoin(
                self.handle.source._base_url,
                self.handle.relative_path)

    def _get_props(self):
        if not self._props:
            (_, _, self._props), = self._get_cookie().ls(self._make_url())
        return self._props

    def check(self):
        response = self._get_cookie().head(self._make_url())
        return response.status_code not in (404, 410,)

    def get_size(self):
        if (size := self.handle.hint("{DAV:}getcontentlength")):
            return int(size)
        else:
            return int(self._get_props()["{DAV:}getcontentlength"])

    def get_last_modified(self):
        lm = self.handle.hint("{DAV:}getlastmodified")
        if not lm:
            lm = self._get_props()["{DAV:}getlastmodified"]
        return dateparser.parse(lm)

    @contextmanager
    def make_stream(self):
        body = self._get_cookie().get(self._make_url())
        body.raise_for_status()
        with BytesIO(body.content) as fp:
            yield fp


class WebDAVHandle(Handle):
    resource_type = WebDAVResource
    type_label = "webdav"

    def __init__(self, source, rel_path, **kwargs):
        super().__init__(source, rel_path, **kwargs)

    @property
    def pn(self) -> (str, str):
        return tuple(self.relative_path.rsplit("/", maxsplit=1))

    @property
    def presentation_name(self):
        if (name := self.hint("{DAV:}displayname")):
            return name
        else:
            _, name = self.pn
            return unquote(name)

    @property
    def presentation_place(self):
        folder, name = self.pn
        return _("WebDAV folder '{folder}'").format(folder=folder)

    def to_json_object(self):
        return super().to_json_object()

    @Handle.json_handler(type_label)
    @staticmethod
    def from_json_object(obj):
        return WebDAVHandle(
                Source.from_json_object(obj["source"]),
                obj["relative_path"])
