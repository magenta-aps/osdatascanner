from io import BytesIO
import re
from typing import Optional, Union
from urllib.parse import urlsplit, urlunsplit
import requests
import structlog
from contextlib import contextmanager

from .. import factory
from .. import settings as engine2_settings
from ..utilities.datetime import parse_datetime
from ..conversions.types import OutputType
from ..conversions.utilities.navigable import (
        make_navigable, make_values_navigable)
from .core import Source, Handle, FileResource
from .utilities.sitemap import process_sitemap_url

from .utilities import crawler


logger = structlog.get_logger("engine2")
TTL: int = engine2_settings.model["http"]["ttl"]
_equiv_domains = set({"www", "www2", "m", "ww1", "ww2", "en", "da", "secure"})
# match whole words (\bWORD1\b | \bWORD2\b) and escape to handle metachars.
# It is important to match whole words; www.magenta.dk should be .magenta.dk, not
# .agta.dk
_equiv_domains_re = re.compile(
    r"\b" + r"\b|\b".join(map(re.escape, _equiv_domains)) + r"\b"
)


def rate_limit(request_function, *args, **kwargs):
    """ Wrapper function to force a proces to sleep by a requested amount,
    when a certain amount of requests are made by it """
    def _rate_limit(*args2, **kwargs2):
        return factory.make_webretrier().run(
            request_function,
            *args, *args2,
            **kwargs, **kwargs2)

    return _rate_limit


def simplify_mime_type(mime):
    r = mime.split(';', maxsplit=1)
    return r[0]


def netloc_normalize(hostname: Union[str, None]) -> str:
    "remove common subdomains from a hostname"
    if hostname:
        return _equiv_domains_re.sub("", hostname).strip(".")

    return ""


def make_head_fallback(context):
    """Returns a function equivalent to context.head -- unless the resulting
    HEAD request fails with HTTP/1.1 405 Method Not Supported, in which case
    it converts the request to a GET."""
    def _make_head_fallback(url, **kwargs):
        r = context.head(url, **kwargs)
        if r.status_code == 405:
            logger.warning(
                    f"HTTP HEAD method not available for {url},"
                    " trying GET instead")
            r = context.get(url, **kwargs)
        return r

    return _make_head_fallback


def try_make_relative(base_url, new_url):
    """Given a newly discovered absolute URL and the base URL of a WebSource,
    returns a (base URL, relative path) pair that can be used to construct a
    WebHandle (or None, if new_url isn't under base_url at all).

    Note that the returned base URL may not necessarily be the provided one. In
    particular, the domain of the base URL may be taken from the newly
    discovered one if they're judged to be equivalent."""
    base_split = urlsplit(base_url)
    new_split = urlsplit(new_url)

    if base_split.scheme == "" and base_split.netloc == "":
        logger.warning(
                "try_make_relative: attempting to fix up bare base URL",
                base_url=base_url)
        base_split = urlsplit("http://" + base_url)

    if (base_split.scheme in ("", new_split.scheme)
            # Allow http://example.com/ to link to https://example.com/, but
            # not vice-versa
            or new_split.scheme == base_split.scheme + "s"):
        scheme = new_split.scheme
    else:  # Schema mismatch
        logger.debug(
                "try_make_relative: scheme mismatch",
                base_url=base_url, new_url=new_url)
        return None

    n_n = netloc_normalize
    if (base_split.netloc == new_split.netloc
            or n_n(base_split.netloc) == n_n(new_split.netloc)):
        netloc = new_split.netloc
    else:
        logger.debug(
                "try_make_relative: netloc mismatch",
                base_url=base_url, new_url=new_url)
        return None

    base_path = base_split.path
    if not base_path.endswith("/"):
        # Make sure that a base_url of example.com/l doesn't accept a new_url
        # of example.com/lists
        base_path += "/"
    if new_split.path.startswith(base_path):
        path = new_split.path.removeprefix(base_path)
    else:
        logger.debug(
                "try_make_relative: leading path component mismatch",
                base_url=base_url, new_url=new_url)
        return None

    return (urlunsplit((scheme, netloc, base_split.path, "", "")),
            urlunsplit(("", "", path, new_split.query, "")))


class WebSource(Source):
    type_label = "web"
    eq_properties = ("_url",)

    def __init__(
            self, url: str, sitemap: str = "", exclude=None,
            sitemap_trusted=False,
            extended_hints=False,
            always_crawl=False,):

        if exclude is None:
            exclude = []

        assert url.startswith("http:") or url.startswith("https:")
        self._url = url.removesuffix("/")
        self._sitemap = sitemap
        self._exclude = exclude

        self._sitemap_trusted = sitemap_trusted
        self._extended_hints = extended_hints
        self._always_crawl = always_crawl

    def __contains__(self, other):
        # OSdatascanner considers that https://secure.example.com/b/c.txt is in
        # http://example.com/, even though these two URLs technically wouldn't
        # share a WebSource, so we need to reimplement this method in terms of
        # our try_make_relative check
        match other:
            case WebHandle(_url=url):
                return try_make_relative(self.url, url) is not None
            case _:
                return False

    def _generate_state(self, sm):
        from ... import __version__
        with requests.Session() as session:
            session.headers.update(
                {"User-Agent": f"OSdatascanner/{__version__}"
                 # Honour our heritage (and hopefully also keep
                 # this UA working for everybody who's previously
                 # whitelisted "OS2datascanner")
                 " (previously OS2datascanner)"
                 " (+https://osdatascanner.dk/agent)"}
            )
            yield session

    def censor(self) -> "WebSource":
        # XXX: we should actually decompose the URL and remove authentication
        # details from netloc
        return self

    def handles(self, sm):
        session = sm.open(self)
        wc = crawler.WebCrawler(
                self._url, session=session, ttl=TTL,
                allow_element_hints=self._extended_hints)
        if self._exclude:
            wc.exclude(*self._exclude)

        wc.add(self._url)

        if self._sitemap:
            for (address, hints) in process_sitemap_url(self._sitemap):
                if wc.is_crawlable(address):
                    wc.add(address, **hints)
            if not self._always_crawl:
                wc.freeze()

        yield from (self._prepare_handle(hints, url) for hints, url in wc.visit())

    def _prepare_handle(self, hints: dict, url: str):
        """Converts a hints dictionary and a raw URL produced by a WebCrawler into a WebHandle."""

        referrer = hints.get("referrer")

        new_hints = {k: v for k, v in hints.items() if k in ("last_modified", "content_type",
                                                             "true_url", "title", "fresh",)}

        r = WebHandle.make_handle(referrer, self._url) if referrer else None
        h = WebHandle.make_handle(url, self._url, referrer=r, hints=new_hints or None)

        if h.source == self:
            h._source = self
        return h

    @property
    def url(self):
        '''
        This method simply returns the _url property.
        Many of the tests and WebHandle.presentation_url depend on this.
        '''
        return self._url

    def to_json_object(self):
        return super().to_json_object() | {
            "url": self._url,
            "sitemap": self._sitemap,
            "exclude": self._exclude,
            "sitemap_trusted": self._sitemap_trusted,
            "extended_hints": self._extended_hints,
            "always_crawl": self._always_crawl,
        }

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        return WebSource(
            url=obj["url"],
            sitemap=obj.get("sitemap"),
            exclude=obj.get("exclude"),
            sitemap_trusted=obj.get("sitemap_trusted", False),
            extended_hints=obj.get("extended_hints", False),
            always_crawl=obj.get("always_crawl", False),
        )

    @property
    def has_trusted_sitemap(self):
        return self._sitemap and self._sitemap_trusted


SecureWebSource = WebSource


def wrap_session_send(send_m):
    """Converts a bound requests.Session.send method into one that can
    automatically react to the HTTP 405 Method Not Supported status code."""
    def _session_send(request, *args, **kwargs):
        response = send_m(request, *args, **kwargs)
        if response.status_code == 405:
            rq = response.request
            logger.warning(
                    f"got 405 Method Not Supported for {rq.method} {rq.url},"
                    " trying again with GET")
            rq.method = "GET"
            response = send_m(rq, *args, **kwargs)
        return response
    return _session_send


suspicious_terms = (
        "error", "fail", "fejl",
        "missing", "mangler", "not-found",
        "404",)
"""The terms that, if they appear in a redirect chain, OS2datascanner will take
as an indication that the original object no longer exists."""


class WebResource(FileResource):
    def __init__(self, handle, sm):
        super().__init__(handle, sm)
        self._response = None
        self._mr = None

    def _generate_metadata(self):
        _, netloc, _, _, _ = urlsplit(self.handle.source.url)
        yield "web-domain", netloc
        yield from super()._generate_metadata()

    def _get_head_raw(self):
        throttled_session_head = rate_limit(
                make_head_fallback(self._get_cookie()))
        return throttled_session_head(
                self.handle._url, allow_redirects=True)

    def check(self) -> bool:
        if (self.handle.source.has_trusted_sitemap
                and self.handle.hint("fresh")):
            return True

        context = self._get_cookie()
        th_send = wrap_session_send(
                rate_limit(
                        context.send, allow_redirects=False))

        request = requests.Request(
                method="HEAD", url=self.handle._url).prepare()
        response = th_send(request)
        count = 0
        while response.next and count < 10:
            if (not any(t in response.url for t in suspicious_terms)
                    and any(t in response.next.url for t in suspicious_terms)):
                # A term that we consider suspicious has suddenly appeared
                # in the URL between these two links in the redirect chain.
                # This is a bad sign
                logger.warning(
                        "suspicious term appeared in redirect chain,"
                        " assuming that URL is no longer valid",
                        url_a=response.url, url_b=response.next.url)
                return False
            response = th_send(response.next)
            count += 1

        if response.next:
            # There are still more links in the redirection chain, but we broke
            # out of the loop because there were too many
            raise requests.exceptions.TooManyRedirects(
                    f"exceeded {count} redirects")
        else:
            return response.ok

    def get_status(self):
        self.unpack_header()
        return self._response.status_code

    def unpack_header(self, check=False):
        if not self._response:
            self._response = self._get_head_raw()
            header = self._response.headers

            self._mr = make_values_navigable(
                    {k.lower(): v for k, v in header.items()})
            try:
                self._mr[OutputType.LastModified] = make_navigable(
                        parse_datetime(self._mr["last-modified"]),
                        parent=self._mr)
            except (KeyError, ValueError):
                pass
        if check:
            self._response.raise_for_status()
        return self._mr

    def get_size(self):
        if (self.handle.source.has_trusted_sitemap
                and self.handle.hint("fresh")):
            return 0

        return int(self.unpack_header(check=True).get("content-length", 0))

    def get_last_modified(self):
        if not (lm_hint := self.handle.hint("last_modified")):
            return self.unpack_header(check=True).setdefault(
                    OutputType.LastModified, super().get_last_modified())
        else:
            return OutputType.LastModified.decode_json_object(lm_hint)

    def compute_type(self):
        # At least for now, strip off any extra parameters the media type might
        # specify
        ct = None
        if not (ct_hint := self.handle.hint("content_type")):
            ct = self.unpack_header(check=True).get(
                    "content-type", "application/octet-stream")
        else:
            ct = ct_hint
        return simplify_mime_type(ct)

    @contextmanager
    def make_stream(self):
        # Assign session HTTP methods to variables, wrapped to constrain requests per second
        throttled_session_get = rate_limit(self._get_cookie().get)
        response = throttled_session_get(self.handle._url)
        response.raise_for_status()
        with BytesIO(response.content) as s:
            yield s


class WebHandle(Handle):
    type_label = "web"
    resource_type = WebResource

    def __init__(
            self, source: WebSource, path: str,
            referrer: Optional["WebHandle"] = None, hints=None):
        # path = path if path.startswith("/") else ("/" + path if path else "")
        path = path if path.startswith("/") else "/" + path
        super().__init__(source, path, referrer, hints)

    @property
    def presentation_name(self):
        if (title := self.hint("title")):
            return title
        return self.presentation_url

    @property
    def presentation_place(self):
        split = urlsplit(self.presentation_url)
        return split.hostname

    def __str__(self):
        return self.presentation_name

    @property
    def presentation_url(self) -> str:
        if (true_url := self.hint("true_url")):
            return true_url
        else:
            return self._url

    @property
    def _url(self) -> str:
        path = self.relative_path
        if path and not path.startswith("/"):
            path = "/" + path
        # .removesuffix is probably unnecessary, as it is already done on source._url
        return self.source.url.removesuffix("/") + path

    @property
    def sort_key(self):
        """ Returns a string to sort by.
        For a website the URL makes sense"""
        return self.presentation_url

    def to_json_object(self):
        return super().to_json_object() | {
            "hints": self._hints,
        }

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        hints = None
        if "hints" in obj:
            hints = obj["hints"]
        elif "last_modified" in obj:
            # Prior to 2023-02-21, WebHandles only supported one hint, which
            # had special treatment. Translate it to the new format
            hints = {
                "last_modified": obj["last_modified"]
            }

        referrer = obj.get("referrer", None)
        if referrer:
            if isinstance(referrer, list):
                # Prior to the 25th of June, the "referrer" field was a
                # WebHandle-only property and contained a list of URLs: after
                # that point, it became a feature of Handles in general and
                # now contains a serialised Handle. Make sure we still support
                # the old format
                if len(referrer) > 1:
                    logger.warning("discarding secondary referrers",
                                   obj=obj)

                url = referrer[0]
                scheme, netloc, path, query, fragment = urlsplit(url)
                source_url = urlunsplit((scheme, netloc, "/", "", ""))
                handle_path = urlunsplit(("", "", path[1:], query, fragment))
                referrer = WebHandle(WebSource(source_url), handle_path)
            else:
                referrer = WebHandle.from_json_object(referrer)

        return WebHandle(
                Source.from_json_object(obj["source"]), obj["path"],
                referrer=referrer, hints=hints)

    @classmethod
    def make_handle(
            cls, url: str, base_url: str = None, **kwargs) -> "WebHandle":
        su = sp = None
        if base_url:
            fv = try_make_relative(base_url, url)
            if fv:
                su, sp = fv
        if su is None and sp is None:
            split_url = urlsplit(url)
            su = f"{split_url.scheme}://{split_url.netloc}"
            sp = split_url.path
        return WebHandle(
                WebSource(su), sp, **kwargs)
