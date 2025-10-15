from abc import ABC, abstractmethod
from typing import Any
from inspect import signature, Parameter

from ..model.core.errors import UnknownSchemeError, DeserialisationError


class JSONSerialisable(ABC):
    """Classes that extend the abstract base class JSONSerialisable can convert
    themselves to and from JSON-serialisable objects."""

    @property
    @classmethod
    @abstractmethod
    def _json_handlers(cls) -> dict:
        """A dictionary of the JSON handlers registered with this class.
        Immediate subclasses should implement this as a class attribute
        containing an empty dictionary."""
        pass

    @abstractmethod
    def to_json_object(self):
        """Returns an object suitable for JSON serialisation that represents
        this object."""

    @classmethod
    def json_handler(cls, type_label):
        """Decorator: registers the decorated function as the handler for the
        type label given as an argument. This handler will be called by
        from_json_object when it finds this type label.

        Subclasses should use this decorator to register their from_json_object
        factory methods."""
        def _json_handler(func):
            if type_label in cls._json_handlers:
                raise ValueError(
                        "BUG: can't register two handlers" +
                        " for the same JSON type label!", type_label)
            cls._json_handlers[type_label] = func
            return func
        return _json_handler

    @classmethod
    def from_json_object(cls, obj):
        """Converts a JSON representation of an object, as returned by the
        to_json_object method, back into an object."""
        try:
            tl = obj["type"]
            if tl not in cls._json_handlers:
                raise UnknownSchemeError(tl)
            return cls._json_handlers[tl](obj)
        except KeyError as k:
            tl = obj.get("type", None)
            raise DeserialisationError(tl, k.args[0])

    _Suppress = object()

    @classmethod
    def register_class(cls, klass):
        """Registers a class for automatic constructor invocation. Classes so
        registered do not need to call Rule.json_handler, but should override
        the _get_constructor_kwargs class method."""
        if any(p.kind == Parameter.POSITIONAL_ONLY
               for p in signature(klass).parameters.values()):
            raise TypeError(
                    "Automatic constructor invocation is not supported for"
                    " classes with required positional parameters")

        def _handler(obj):
            kwargs = klass._get_constructor_kwargs(obj)
            return klass(**{k: v for k, v in kwargs.items()
                            if v is not cls._Suppress})

        cls.json_handler(klass.type_label)(_handler)
        return klass

    @classmethod
    def _get_constructor_kwargs(cls, obj) -> dict[str, Any]:
        """Extracts constructor keyword arguments from the given JSON
        representation of an object. (A key mapped to the special value
        cls._Suppress will not be passed to the constructor at all.)"""
        return {}
