from abc import abstractmethod
from typing import Mapping, Iterator
import structlog

from ... import settings
from ...utilities.json import JSONSerialisable
from ...utilities.equality import TypePropertyEquality
# from .errors import UnknownSchemeError
from .import handle as mhandle
from .utilities import takes_named_arg, SourceManager  # noqa


logger = structlog.get_logger("engine2")


class Source(TypePropertyEquality, JSONSerialisable):
    """A Source represents the root of a hierarchy to be explored. It
    constructs Handles, which represent the position of an object in the
    hierarchy.

    Sources hold all the information (if any) needed to open a connection to
    their hierarchy, but they aren't responsible for holding actual connection
    state -- that gets stashed in a SourceManager instead.

    Sources are serialisable and persistent, and two different Source objects
    with the same type and properties compare equal. (One useful consequence of
    this is that SourceManager will collapse several equal Sources together,
    only opening one of them.)"""

    def __contains__(self, h: "mhandle.Handle") -> bool:
        """Test if a handle originated from this Source"""
        return any(
                h.source == self
                for h in h.walk_up())

    @property
    @abstractmethod
    def type_label(self) -> str:
        """A label that will be used to identify JSON forms of this Source."""

    @abstractmethod
    def _generate_state(self, sm):
        """Returns a state management generator. This generator will only be
        executed once: this will yield a magic cookie representing any state
        that this Source might require. The generator will be closed when
        this state is no longer needed.

        The relevant instance properties when considering Source equality are
        normally only those properties used by this method. (The default
        implementation is conservative, however, and compares all
        properties.)"""

    @abstractmethod
    def censor(self) -> "Source":
        """Returns a version of this Source that does not carry sensitive
        information like passwords and API keys. The resulting Source will not
        necessarily carry enough information to generate a meaningful state
        object, and so will not necessarily compare equal to this one."""

    @abstractmethod
    def handles(
            self, sm: "SourceManager", *,
            rule=None) -> Iterator["mhandle.Handle"]:
        """Yields Handles corresponding to every identifiable leaf node in this
        Source's hierarchy. These Handles are generated in an undefined order.

        (For backwards compatibility, subclasses are not required to define any
        of the keyword arguments to this function. Callers must use
        introspection to check whether or not a named argument is available.)

            rule: rule | None
            The Rule for which this Source is being scanned. Sources are
            permitted to inspect the Rule to make optimised queries: for
            example, if its first component is a LastModifiedRule, the
            timestamp of that rule could be used as a pre-filter when selecting
            Handles to yield.

        Note that this method can yield Handles that correspond to
        identifiable *but non-existent* leaf nodes. These might correspond to,
        for example, a broken link on a web page, or to an object that was
        yielded by this method but was deleted before it could be examined.

        It is not necessarily the case that the value of the source property on
        a Handle yielded by this method will be this Source."""

    @property
    def yields_independent_sources(self) -> bool:
        """Indicates whether or not the Handles yielded by this Source
        represent top-level Sources that should be processed independently.
        This might be the case, for example, for a Source that queries a
        directory server and returns a Handle for each relevant account that it
        finds."""
        return False

    __mime_handlers = {}

    @staticmethod
    def mime_handler(*mimes):
        """Decorator: registers the decorated function as the handler for the
        MIME types given as arguments. This handler will be called by
        from_handle when it finds one of these MIME types.

        Subclasses should use this decorator to register their from_handle
        factory methods, if they implement such a method."""
        def _mime_handler(func):
            for mime in mimes:
                if mime in Source.__mime_handlers:
                    raise ValueError(
                            "BUG: can't register two handlers" +
                            " for the same MIME type!", mime)
                Source.__mime_handlers[mime] = func
            return func
        return _mime_handler

    @staticmethod
    def from_handle(handle, sm=None):
        """Tries to create a Source from a Handle.

        This will only work if the target of the Handle in question can
        meaningfully be interpreted as the root of a hierarchy of its own --
        for example, if it's an archive."""

        depth = 0
        for _ in handle.walk_up():
            if depth > settings.model["max_depth"]:
                logger.warning(
                        "too much recursion on handle, "
                        "not exploring any deeper",
                        handle=handle, representation=str(handle))
                return None
            depth += 1

        if not sm:
            mime = handle.guess_type()
        else:
            mime = handle.follow(sm).compute_type()
        if mime in Source.__mime_handlers:
            return Source.__mime_handlers[mime](handle)
        else:
            return None

    @property
    def handle(self):
        """If this Source was created based on a Handle (typically by the
        Source.from_handle method), then returns that Handle; otherwise,
        returns None."""
        return None

    _json_handlers = {}

    @abstractmethod
    def to_json_object(self):
        """Returns an object suitable for JSON serialisation that represents
        this Source."""
        return {
            "type": self.type_label
        }

    def remap(self, mapping: Mapping["Source", "Source"]) -> "Source":
        return mapping.get(self, self)
