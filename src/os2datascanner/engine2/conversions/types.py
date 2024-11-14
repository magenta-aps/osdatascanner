from enum import Enum
from typing import Optional
from functools import wraps
from dataclasses import dataclass, field

from os2datascanner.engine2.model.core.handle import Handle
from os2datascanner.engine2.utilities.datetime import (
        parse_datetime, unparse_datetime)


@dataclass
class Link:
    url: str
    # combine public link_text with setter
    # https://stackoverflow.com/a/61191878
    link_text: Optional[str]
    _link_text: Optional[str] = field(init=False, repr=False)

    @property
    def link_text(self):
        return self._link_text

    @link_text.setter
    def link_text(self, s: Optional[str]):
        # remove newlines and extra whitespace
        if isinstance(s, str):
            s = " ".join([s.strip() for s in s.split()])
        self._link_text = s

    @classmethod
    def dump(cls, v):
        return [[link.url, link.link_text]
                for link in (v if isinstance(v, list) else [v])]

    @classmethod
    def load(cls, v):
        return [Link(url, link_text) for url, link_text in v]


def wrap_none(fn):
    """Decorator. Returns a wrapped version of the given single-argument
    function that unconditionally returns None when its argument is None."""

    @wraps(fn)
    def _wrapper(arg):
        return fn(arg) if arg is not None else None

    return _wrapper


class OutputType(Enum):
    """Conversion functions return a typed result, and the type is a member of
    the OutputType enumeration. The values associated with these members are
    simple string identifiers that can be used in serialisation formats."""
    Text = (  # str
            "text", str, str)
    LastModified = (  # datetime.datetime
            "last-modified", unparse_datetime, parse_datetime)
    ImageDimensions = (
            "image-dimensions",
            lambda dim: list(int(k) for k in dim),
            lambda dim: tuple(int(k) for k in dim))
    Links = (  # list[Link]
            "links", Link.dump, Link.load)
    Manifest = (  # list[Handle]
            "manifest",
            lambda hl: [handle.to_json_object() for handle in hl],
            lambda hl: [Handle.from_json_object(handle) for handle in hl])
    EmailHeaders = (  # dict[str, str]
            "email-headers",
            dict, dict)
    MRZ = (  # str
            "mrz", str, str)

    AlwaysTrue = (
            "fallback",
            lambda _: True, lambda _: True)
    NoConversions = (
            "dummy",
            None, None)

    def __new__(cls, value, dump, load):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.encode_json_object = wrap_none(dump)
        obj.decode_json_object = wrap_none(load)
        return obj


def encode_dict(d):
    """Given a dictionary from OutputType values to objects, returns a new
    dictionary in which each of those objects has been converted to a
    JSON-friendly representation."""
    return {t: OutputType(t).encode_json_object(v) for t, v in d.items()}


def decode_dict(d):
    """Given a dictionary from OutputType values to JSON representations of
    objects, returns a new dictionary in which each of those representations
    has been converted back to an original object."""
    return {t: OutputType(t).decode_json_object(v) for t, v in d.items()}
