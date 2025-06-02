import os.path
from abc import abstractmethod
from copy import copy, deepcopy
from typing import Mapping, Optional
import warnings
from mimetypes import guess_type

from ...utilities.i18n import gettext as _
from ...utilities.json import JSONSerialisable
from ...utilities.equality import TypePropertyEquality
from .import source as msource


_encodings_map = {
    "gzip": "application/gzip",
    "bzip2": "application/x-bzip2",
    "xz": "application/xz"
}


class Handle(TypePropertyEquality, JSONSerialisable):
    """A Handle is a reference to a leaf node in a hierarchy maintained by a
    Source. Handles can be followed to give a Resource, a concrete object.

    Although all Handle subclasses expose the same two-argument constructor,
    which takes a Source and a string representation of a path, each type of
    Source defines what its Handles and their paths mean; the only general way
    to get a meaningful Handle is the Source.handles() method (or to make a
    copy of an existing one).

    Handles are serialisable and persistent, and two different Handles with the
    same type and properties compare equal."""

    # By default, two Handles are equal if they have the same Source and the
    # same path
    eq_properties = ('_source', '_relpath',)

    @property
    @abstractmethod
    def type_label(self) -> str:
        """A label that will be used to identify JSON forms of this Handle."""

    @property
    @abstractmethod
    def resource_type(self) -> type:
        """The subclass of Resource produced when this Handle is followed."""

    def __init__(self, source: "msource.Source", relpath: str,
                 referrer: "Handle" = None,
                 hints: Optional[dict] = None):
        self._source = source
        self._relpath = relpath
        self._referrer = referrer
        self._hints = deepcopy(hints) if hints else None

    def hint(self, key: str, default=None):
        """Retrieves a named hint from this Handle.

        Hints are pieces of metadata retrieved during the exploration of a
        Source. Handle and Resource methods may use them to provide special
        behaviour or improved performance.

        Note that hints can easily become stale, especially when Handles are
        serialised and reimported, which can lead to inconsistent behaviour. Be
        sure to call Handle.clear_hints before reusing an old object in a new
        scan."""
        return (self._hints or {}).get(key, default)

    def clear_hints(self) -> "Handle":
        """Deletes all of the hints attached to this Handle, if there were any,
        and (for convenience) returns a reference to this Handle."""
        if self._hints is not None:
            self._hints.clear()
            self._hints = None
        return self

    @property
    def source(self) -> "msource.Source":
        """Returns this Handle's Source."""
        return self._source

    @property
    def relative_path(self):
        """Returns this Handle's path."""
        return self._relpath

    @property
    def name(self) -> str:
        """Returns the base name -- everything after the last '/' -- of this
        Handle's path, or "file" if the result would otherwise be empty.

        Note that the return value of this function must be a valid filesystem
        name."""
        return os.path.basename(self._relpath) or 'file'

    def guess_type(self):
        """Guesses the type of this Handle's target based on its name. (For a
        potentially better, but more expensive, guess, follow this Handle to
        get a Resource and call its compute_type() method instead.)"""
        mime, encoding = guess_type(self.name)

        if encoding:
            # The mimetypes module helpfully maps (for example) "doc.pdf.gz"
            # to "application/pdf", but we need the actual MIME type of the
            # encoded form to be able to decode it properly
            return _encodings_map.get(encoding, "application/octet-stream")
        else:
            return mime or "application/octet-stream"

    @property
    @abstractmethod
    def presentation_name(self) -> str:
        """Returns the human-readable name of this object."""

    @property
    @abstractmethod
    def presentation_place(self) -> str:
        """Returns a (perhaps localised) human-readable string representing
        the location of this Handle, for use in user interfaces (a folder, for
        example, for a filesystem file, or an archive path for a compressed
        document)."""

    @property
    def presentation_url(self):
        """Returns a URL that points to a user-meaningful webpage that
        corresponds to this Handle, if there is one.

        The returned URL is not necessarily the result of appending this
        Handle's path to the URL representation of its Source. (For example,
        this function might, for a Handle identifying an email, return a URL
        that points at that email in an appropriate webmail system.)"""
        return None

    @property
    def container_url(self):
        """Returns a URL that points to a user-meaningful webpage that
        corresponds to the container of this Handle, if there is one (a folder,
        for example, for a filesystem file)."""
        return None

    def __str__(self):
        """Returns a (perhaps localised) human-readable string representing
        this Handle: its name and its position."""
        return _("{name} (in {place})").format(
                name=self.presentation_name, place=self.presentation_place)

    @property
    def presentation(self) -> str:
        warnings.warn(
                "Handle.presentation is deprecated; use str(handle) instead",
                DeprecationWarning, stacklevel=2)
        return str(self)

    @property
    def sort_key(self) -> str:
        """Returns a string that can be used to position this object in an
        ordered list in a way that would make sense to a user. This might be,
        for example, a filesystem path or an email user@domain.

        Note that comparing sort keys across different types of Source is not
        meaningful."""
        return str(self).removesuffix(self.name).removesuffix("/")

    @property
    def referrer(self) -> Optional["Handle"]:
        """Returns this Handle's referrer or None, if there is no referrer"""
        return self._referrer

    def walk_up(self):
        """Walks backwards up the hierarchy from this point, yielding first
        this Handle, then the Handle backing the parent Source (if there is
        one), and so on."""
        yield self
        if self.source.handle:
            yield from self.source.handle.walk_up()

    @property
    def base_referrer(self) -> "Handle":
        """Returns this Handle's base referrer or self, if there is no referrer"""
        h = self
        while h:
            if h.referrer:
                h = h.referrer
            else:
                break
        return h

    @property
    def base_handle(self) -> "Handle":
        """Returns this Handle's top-most handle, which does not yield
        independent sources."""
        warnings.warn(
                "Handle.base_handle is deprecated;"
                " rewrite this code to use Handle.walk_up instead",
                DeprecationWarning, stacklevel=2)
        h = self
        while h:
            if (parent_handle := h.source.handle):
                # Check to make sure that we aren't going too far up the hierarchy
                if not parent_handle.source.yields_independent_sources:
                    h = parent_handle
                    continue
            break
        return h

    def censor(self):
        """Returns a Handle identical to this one but whose Source does not
        carry sensitive information like passwords or API keys. See the
        documentation of Source.censor for more information.

        As the Handle returned by this method is not useful for anything other
        than identifying an object, this method should normally only be used
        when transmitting a Handle to a less trusted context."""
        return self.remap({self.source: self.source.censor()})

    def follow(self, sm):
        """Follows this Handle using the state in the StateManager @sm,
        returning a concrete Resource."""
        return self.resource_type(self, sm)

    _json_handlers = {}

    def to_json_object(self):
        """Returns an object suitable for JSON serialisation that represents
        this Handle."""
        return {
            "type": self.type_label,
            "source": self.source.to_json_object(),
            "path": self.relative_path,
            # only insert referrer key:val, if value is not None
            **({"referrer": self.referrer.to_json_object()}
               if self.referrer else {}),
            "hints": self._hints,
        }

    @staticmethod
    def stock_json_handler(type_label):
        """Decorator: registers the decorated class as a simple handler
        for the type label given as an argument. The class's two-argument
        constructor will be called with a Source and a path."""
        def _stock_json_handler(cls):
            @Handle.json_handler(type_label)
            def _invoke_constructor(obj):
                return cls(
                        msource.Source.from_json_object(obj["source"]),
                        obj["path"],
                        hints=obj.get("hints"),)
            return cls
        return _stock_json_handler

    def remap(
            self,
            mapping: Mapping["msource.Source", "msource.Source"]) -> "Handle":
        remapped_source = self._source.remap(mapping)
        if remapped_source is self._source:
            # The remapping would do nothing, so there's no need to make a new
            # object
            return self
        else:
            nc = copy(self)
            nc._source = remapped_source
            return nc
